"""Discovery session routes. All routes require authentication."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.project import ProjectUser, ProjectUserStatus
from app.models.session import DiscoverySession, SessionStatus
from app.models.user import User
from app.schemas.session import (
    AssessmentSubmit,
    PhaseSummaryApproval,
    PhaseSummaryAction,
    SessionMessageRequest,
    SessionMessageResponse,
    SessionReportResponse,
    SessionResponse,
)
from app.schemas.user import UserResponse
from app.services.auth import get_current_user_dependency
from app.services.discovery import (
    calculate_style_profile,
    detect_out_of_scope,
    generate_final_report,
    generate_phase_summary,
    get_assistant_reply,
    get_phase_initial_question,
    get_phase_system_prompt,
    get_phase_transition_message,
    review_and_approve_summary,
)

router = APIRouter(prefix="/api/session", tags=["sessions"])


def _get_or_create_active_session(db: Session, current_user: User) -> tuple[DiscoverySession, ProjectUser]:
    """Find user's ACTIVE ProjectUser, get or create DiscoverySession. Returns (session, project_user). Raises 404 if no active project."""
    project_user = (
        db.query(ProjectUser)
        .filter(
            ProjectUser.user_id == current_user.id,
            ProjectUser.status == ProjectUserStatus.ACTIVE,
        )
        .options(joinedload(ProjectUser.project), joinedload(ProjectUser.session))
        .first()
    )
    if not project_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active project assignment",
        )
    if not project_user.project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    session = project_user.session
    if session is None:
        session = DiscoverySession(
            project_user_id=project_user.id,
            status=SessionStatus.NOT_STARTED,
            current_phase=1,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        db.refresh(project_user)
    return session, project_user


def _session_to_response(session: DiscoverySession) -> SessionResponse:
    """Build SessionResponse from DiscoverySession, including pending_phase_summary and all_messages."""
    pending = None
    if isinstance(session.phase_summaries, dict):
        pending = session.phase_summaries.get(f"{session.current_phase}_pending")
    all_messages = session.all_messages if session.all_messages is not None else []
    return SessionResponse(
        id=session.id,
        current_phase=session.current_phase,
        status=session.status.value,
        started_at=session.started_at,
        completed_at=session.completed_at,
        pending_phase_summary=pending,
        all_messages=all_messages,
    )


def _user_to_response(user: User) -> UserResponse:
    """Build UserResponse from User (no password)."""
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        assessment_completed=user.assessment_completed,
        created_at=user.created_at,
    )


@router.post("/assessment", response_model=UserResponse)
def post_assessment(
    body: AssessmentSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency),
) -> UserResponse:
    """Submit communication style assessment. Saves profile to user and sets assessment_completed=True."""
    profile = calculate_style_profile(body.responses)
    current_user.style_profile = profile
    current_user.assessment_completed = True
    db.commit()
    db.refresh(current_user)
    return _user_to_response(current_user)


@router.get("", response_model=SessionResponse)
def get_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency),
) -> SessionResponse:
    """Get current user's active discovery session. Creates one if none exists (user must have ACTIVE ProjectUser)."""
    session, _ = _get_or_create_active_session(db, current_user)
    return _session_to_response(session)


@router.post("/message", response_model=SessionMessageResponse)
def post_message(
    body: SessionMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency),
) -> SessionMessageResponse:
    """Send a message in the discovery session. Handles phase commands (next/next phase/move on) by generating summary."""
    session, project_user = _get_or_create_active_session(db, current_user)
    if session.status == SessionStatus.COMPLETED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session already completed")

    scope = project_user.project.scope
    style_profile = current_user.style_profile if current_user.style_profile else {}

    # BEGIN_SESSION: AI initiates the conversation (no user message stored)
    user_content = body.message.strip()
    if user_content == "BEGIN_SESSION" and session.status == SessionStatus.NOT_STARTED:
        session.status = SessionStatus.IN_PROGRESS
        session.started_at = datetime.now(timezone.utc)
        initial_question = get_phase_initial_question(1)
        greeting = (
            "Welcome to your discovery session! I'm here to learn about your work so we can "
            "design the best solution for you.\n\n"
            + initial_question
        )
        session.all_messages = [{"role": "assistant", "content": greeting}]
        db.commit()
        db.refresh(session)
        return SessionMessageResponse(
            assistant_message=greeting,
            phase_completed=False,
            summary=None,
            message=greeting,
            phase_complete_suggested=False,
        )

    # RESUME_SESSION: AI re-engages when user returns (no user message stored)
    if user_content == "RESUME_SESSION" and session.status == SessionStatus.IN_PROGRESS:
        all_messages = list(session.all_messages or [])
        if not all_messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No conversation to resume",
            )
        system_prompt = get_phase_system_prompt(
            session.current_phase, scope, style_profile
        )
        resume_instruction = (
            "\n\nThe user has returned to continue their discovery session. "
            "Briefly acknowledge their return, summarize where you left off (1-2 sentences), "
            "and continue with your next question. Don't repeat questions already asked."
        )
        system_prompt = system_prompt + resume_instruction
        try:
            assistant_message = get_assistant_reply(system_prompt, all_messages)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Claude request failed: {str(e)}",
            )
        marker = "[PHASE_COMPLETE]"
        phase_complete_suggested = marker in assistant_message
        visible_message = assistant_message.replace(marker, "").strip()

        all_messages.append({"role": "assistant", "content": visible_message})
        session.all_messages = all_messages
        db.commit()
        db.refresh(session)
        return SessionMessageResponse(
            assistant_message=visible_message,
            phase_completed=False,
            summary=None,
            message=visible_message,
            phase_complete_suggested=phase_complete_suggested,
        )

    # BEGIN_PHASE: AI starts the new phase after summary approval (no user message stored)
    if user_content == "BEGIN_PHASE" and session.status == SessionStatus.IN_PROGRESS:
        phase_num = session.current_phase
        system_prompt = get_phase_system_prompt(phase_num, scope, style_profile)
        phase_instruction = (
            "\n\nYou are starting Phase "
            + str(phase_num)
            + " of the discovery session. "
            "Review the conversation so far and begin this phase appropriately. "
            "Briefly acknowledge the transition, then ask your first question for this phase."
        )
        system_prompt = system_prompt + phase_instruction
        all_messages = list(session.all_messages or [])
        all_messages.append({"role": "user", "content": "I'm ready to continue to the next phase."})
        try:
            assistant_message = get_assistant_reply(system_prompt, all_messages)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Claude request failed: {str(e)}",
            )
        all_messages.pop()

        marker = "[PHASE_COMPLETE]"
        phase_complete_suggested = marker in assistant_message
        visible_message = assistant_message.replace(marker, "").strip()

        all_messages.append({"role": "assistant", "content": visible_message})
        session.all_messages = all_messages
        db.commit()
        db.refresh(session)
        return SessionMessageResponse(
            assistant_message=visible_message,
            phase_completed=False,
            summary=None,
            message=visible_message,
            phase_complete_suggested=phase_complete_suggested,
        )

    # Start session on first activity (for any other first message)
    if session.status == SessionStatus.NOT_STARTED:
        session.status = SessionStatus.IN_PROGRESS
        session.started_at = datetime.now(timezone.utc)
        transition = get_phase_transition_message(session.current_phase)
        initial_q = get_phase_initial_question(session.current_phase)
        session.all_messages = [
            {"role": "assistant", "content": transition.strip()},
            {"role": "assistant", "content": initial_q},
        ]
        db.flush()

    # Copy JSON fields for mutation
    all_messages = list(session.all_messages or [])
    user_content = body.message.strip()
    if not user_content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message cannot be empty")

    # Phase completion commands
    if user_content.lower() in ["next", "next phase", "move on"]:
        summary = generate_phase_summary(
            session.current_phase,
            all_messages,
            scope,
            style_profile,
            phase_documents=None,
        )
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to generate phase summary",
            )
        # Store pending summary for approve-summary
        phase_summaries = dict(session.phase_summaries or {})
        phase_summaries[f"{session.current_phase}_pending"] = summary
        session.phase_summaries = phase_summaries
        session.all_messages = all_messages
        db.commit()
        db.refresh(session)
        summary_message = "Summary generated. Please approve or request changes via POST /api/session/approve-summary."
        return SessionMessageResponse(
            assistant_message=summary_message,
            phase_completed=True,
            summary=summary,
            message=summary_message,
            phase_complete_suggested=False,
        )

    all_messages.append({"role": "user", "content": user_content})
    system_prompt = get_phase_system_prompt(session.current_phase, scope, style_profile)

    try:
        assistant_message = get_assistant_reply(system_prompt, all_messages)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Claude request failed: {str(e)}",
        )

    # Out-of-scope detection
    out_of_scope = detect_out_of_scope(scope, user_content)
    if out_of_scope:
        flagged = list(session.flagged_items or [])
        flagged.append(
            {"phase": session.current_phase, "mention": out_of_scope, "user_input": user_content}
        )
        session.flagged_items = flagged

    marker = "[PHASE_COMPLETE]"
    phase_complete_suggested = marker in assistant_message
    visible_message = assistant_message.replace(marker, "").strip()

    all_messages.append({"role": "assistant", "content": visible_message})
    session.all_messages = all_messages
    db.commit()
    db.refresh(session)

    return SessionMessageResponse(
        assistant_message=visible_message,
        phase_completed=False,
        summary=None,
        message=visible_message,
        phase_complete_suggested=phase_complete_suggested,
    )


@router.post("/approve-summary", response_model=SessionResponse)
def post_approve_summary(
    body: PhaseSummaryApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency),
) -> SessionResponse:
    """Approve, request changes, or add details to the pending phase summary."""
    session, project_user = _get_or_create_active_session(db, current_user)
    if session.status == SessionStatus.COMPLETED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session already completed")

    phase_num = session.current_phase
    phase_summaries = dict(session.phase_summaries or {})
    pending_key = f"{phase_num}_pending"
    pending_summary = phase_summaries.get(pending_key)

    if body.action == PhaseSummaryAction.approve:
        if not pending_summary:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No pending summary to approve",
            )
        phase_summaries[str(phase_num)] = pending_summary
        if pending_key in phase_summaries:
            del phase_summaries[pending_key]
        session.phase_summaries = phase_summaries
        if phase_num >= 4:
            session.status = SessionStatus.COMPLETED
            session.completed_at = datetime.now(timezone.utc)
        else:
            session.current_phase = phase_num + 1
        db.commit()
        db.refresh(session)
        return _session_to_response(session)

    # request_changes or add_details
    if not pending_summary:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending summary to revise",
        )
    scope = project_user.project.scope
    style_profile = current_user.style_profile if current_user.style_profile else {}
    revised = review_and_approve_summary(
        phase_num,
        pending_summary,
        scope,
        style_profile,
        body.action.value,
        body.feedback,
    )
    if revised:
        phase_summaries[pending_key] = revised
        session.phase_summaries = phase_summaries
        db.commit()
        db.refresh(session)
    return _session_to_response(session)


@router.get("/report", response_model=SessionReportResponse)
def get_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency),
) -> SessionReportResponse:
    """Generate final discovery report. Only when session is completed."""
    session, project_user = _get_or_create_active_session(db, current_user)
    if session.status != SessionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session not completed",
        )
    scope = project_user.project.scope
    phase_summaries = {k: v for k, v in (session.phase_summaries or {}).items() if not str(k).endswith("_pending")}
    report_content = generate_final_report(phase_summaries, scope, session.flagged_items or [])
    return SessionReportResponse(report_content=report_content)
