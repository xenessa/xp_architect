"""Discovery session routes for stakeholders. All routes require authentication."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.project import Project, ProjectUser, ProjectUserStatus
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
    generate_phase_break_offer_message,
    generate_phase_summary,
    get_assistant_reply,
    get_phase_initial_question,
    get_phase_system_prompt,
    get_phase_transition_message,
    review_and_approve_summary,
)

router = APIRouter(prefix="/api/session", tags=["session"])


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


def _get_or_create_session_for_user(
    db: Session,
    current_user: User,
    project_id: UUID | None = None,
) -> tuple[DiscoverySession, Project, ProjectUser]:
    """Get current user's ProjectUser (ACTIVE) and their DiscoverySession (create if missing). Returns (session, project, project_user)."""
    q = db.query(ProjectUser).filter(ProjectUser.user_id == current_user.id, ProjectUser.status == ProjectUserStatus.ACTIVE)
    if project_id is not None:
        q = q.filter(ProjectUser.project_id == project_id)
    project_user = q.options(joinedload(ProjectUser.project), joinedload(ProjectUser.session)).first()
    if not project_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active project assignment found",
        )
    if not project_user.project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    session = project_user.session
    if session is None:
        session = DiscoverySession(project_user_id=project_user.id)
        db.add(session)
        db.commit()
        db.refresh(session)
    return session, project_user.project, project_user


@router.post("/assessment", response_model=UserResponse)
def submit_assessment(
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
    project_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency),
) -> SessionResponse:
    """Get current user's active discovery session. If none exists but user has an ACTIVE ProjectUser, create one. Optional project_id to pick project."""
    session, _, _ = _get_or_create_session_for_user(db, current_user, project_id)
    return _session_to_response(session)


@router.post("/message", response_model=SessionMessageResponse)
def send_message(
    body: SessionMessageRequest,
    project_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency),
) -> SessionMessageResponse:
    """Send a message in the discovery session. Uses conduct_phase logic: one turn, out-of-scope detection, save to session.all_messages."""
    session, project, project_user = _get_or_create_session_for_user(db, current_user, project_id)
    if session.status == SessionStatus.COMPLETED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session already completed")

    scope = project.scope
    style_profile = current_user.style_profile if current_user.style_profile else {}

    # Start session if first message
    if session.status == SessionStatus.NOT_STARTED:
        session.status = SessionStatus.IN_PROGRESS
        session.started_at = datetime.now(timezone.utc)
        # Prepend phase transition and initial question if no messages yet
        transition = get_phase_transition_message(session.current_phase)
        initial_q = get_phase_initial_question(session.current_phase)
        session.all_messages = [
            {"role": "assistant", "content": transition.strip()},
            {"role": "assistant", "content": initial_q},
        ]
        db.flush()

    messages = list(session.all_messages or [])
    user_content = body.message.strip()
    if not user_content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message cannot be empty")

    # Out-of-scope detection
    out_of_scope = detect_out_of_scope(scope, user_content)
    if out_of_scope:
        session.flagged_items = list(session.flagged_items or [])
        session.flagged_items.append(
            {"phase": session.current_phase, "mention": out_of_scope, "user_input": user_content}
        )

    messages.append({"role": "user", "content": user_content})

    system_prompt = get_phase_system_prompt(session.current_phase, scope, style_profile)

    try:
        assistant_message = get_assistant_reply(system_prompt, messages)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Claude request failed: {str(e)}",
        )

    marker = "[PHASE_COMPLETE]"
    phase_complete_suggested = marker in assistant_message
    visible_message = assistant_message.replace(marker, "").strip()

    messages.append({"role": "assistant", "content": visible_message})
    session.all_messages = messages
    db.commit()
    db.refresh(session)

    return SessionMessageResponse(
        assistant_message=visible_message,
        phase_completed=False,
        summary=None,
        message=visible_message,
        phase_complete_suggested=phase_complete_suggested,
    )


@router.post("/next-phase", response_model=SessionResponse)
def next_phase(
    project_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency),
) -> SessionResponse:
    """Move to next phase: generate summary for current phase and return it for approval."""
    session, project, project_user = _get_or_create_session_for_user(db, current_user, project_id)
    if session.status == SessionStatus.COMPLETED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session already completed")

    scope = project.scope
    style_profile = current_user.style_profile if current_user.style_profile else {}
    phase_num = session.current_phase
    messages = session.all_messages or []

    summary = generate_phase_summary(phase_num, messages, scope, style_profile, phase_documents=None)
    if not summary:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Failed to generate phase summary")

    summaries = dict(session.phase_summaries or {})
    summaries[f"{phase_num}_pending"] = summary
    session.phase_summaries = summaries
    db.commit()
    db.refresh(session)

    return _session_to_response(session)


@router.post("/approve-summary", response_model=SessionResponse)
def approve_summary(
    body: PhaseSummaryApproval,
    project_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency),
) -> SessionResponse:
    """Approve, request changes, or add details to the pending phase summary. Uses review_and_approve_summary logic."""
    session, project, project_user = _get_or_create_session_for_user(db, current_user, project_id)
    if session.status == SessionStatus.COMPLETED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session already completed")

    phase_num = session.current_phase
    summaries = dict(session.phase_summaries or {})
    pending_key = f"{phase_num}_pending"
    initial_summary = summaries.get(pending_key)
    if not initial_summary:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No pending summary to approve")

    scope = project.scope
    style_profile = current_user.style_profile if current_user.style_profile else {}

    if body.action == PhaseSummaryAction.approve:
        summaries[str(phase_num)] = initial_summary
        del summaries[pending_key]
        session.phase_summaries = summaries
        # Add a break-offer transition message based on the approved summary
        next_phase_num: int | None = None if phase_num >= 4 else phase_num + 1
        break_message = generate_phase_break_offer_message(
            phase_num=phase_num,
            approved_summary=initial_summary,
            next_phase_num=next_phase_num,
        )
        all_messages = list(session.all_messages or [])
        all_messages.append({"role": "assistant", "content": break_message})
        session.all_messages = all_messages
        if phase_num >= 4:
            session.status = SessionStatus.COMPLETED
            session.completed_at = datetime.now(timezone.utc)
        else:
            session.current_phase = phase_num + 1
        db.commit()
        db.refresh(session)
        return _session_to_response(session)

    revised = review_and_approve_summary(
        phase_num,
        initial_summary,
        scope,
        style_profile,
        body.action.value,
        body.feedback,
    )
    if revised:
        summaries[pending_key] = revised
        session.phase_summaries = summaries
        db.commit()
        db.refresh(session)

    return _session_to_response(session)


@router.get("/report", response_model=SessionReportResponse)
def get_report(
    project_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency),
) -> SessionReportResponse:
    """Generate final discovery report. Only available when session is completed."""
    session, project, project_user = _get_or_create_session_for_user(db, current_user, project_id)
    if session.status != SessionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session must be completed to generate report",
        )

    # Use only approved phase summaries (no _pending keys)
    phase_summaries = {k: v for k, v in (session.phase_summaries or {}).items() if not str(k).endswith("_pending")}
    report_content = generate_final_report(phase_summaries, project.scope, session.flagged_items or [])
    return SessionReportResponse(report_content=report_content)
