"""Project management routes for Solution Architects. All routes require SA role."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_sa_role
from app.models.project import Project, ProjectUser
from app.models.session import DiscoverySession, SessionStatus
from app.models.user import User
from app.schemas.project import (
    ConsolidatedReportResponse,
    ProjectCreate,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectProgressResponse,
    ProjectResponse,
    ProjectUpdate,
    ProjectUserAdd,
    ProjectUserResponse,
    StakeholderDiscoveryResultsResponse,
)
from app.services.project import (
    activate_project_user,
    add_user_to_project,
    create_project,
    get_project,
    get_project_progress,
    get_user_projects,
    project_user_to_response,
    update_project,
)
from app.services.discovery import generate_consolidated_report, generate_final_report

router = APIRouter(prefix="/api/projects", tags=["projects"])


def project_to_response(p: Project) -> ProjectResponse:
    """Build ProjectResponse from Project model (without progress stats)."""
    return ProjectResponse(
        id=p.id,
        name=p.name,
        description=p.description,
        scope=p.scope,
        instructions=p.instructions,
        start_date=p.start_date,
        end_date=p.end_date,
        created_by=p.created_by,
        created_at=p.created_at,
    )


@router.get("", response_model=ProjectListResponse)
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sa_role),
) -> ProjectListResponse:
    """List all projects created by the current SA with progress stats."""
    projects = get_user_projects(db, current_user.id)
    project_responses: list[ProjectResponse] = []

    for p in projects:
        progress = get_project_progress(db, p.id)
        completion_percentage = (
            round(progress.completed / progress.total_users * 100, 1)
            if progress.total_users > 0
            else 0.0
        )
        response = ProjectResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            scope=p.scope,
            instructions=p.instructions,
            start_date=p.start_date,
            end_date=p.end_date,
            created_by=p.created_by,
            created_at=p.created_at,
            total_users=progress.total_users,
            completed_users=progress.completed,
            completion_percentage=completion_percentage,
        )
        project_responses.append(response)

    return ProjectListResponse(projects=project_responses)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project_route(
    body: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sa_role),
) -> ProjectResponse:
    """Create a new project. Sets created_by to current user."""
    project = create_project(db, current_user.id, body)
    return project_to_response(project)


@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project_detail(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sa_role),
) -> ProjectDetailResponse:
    """Get project details including users list and completion stats."""
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    if project.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    users = [project_user_to_response(pu) for pu in project.project_users]
    progress = get_project_progress(db, project_id)
    return ProjectDetailResponse(
        project=project_to_response(project),
        users=users,
        progress=progress,
    )


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project_route(
    project_id: UUID,
    body: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sa_role),
) -> ProjectResponse:
    """Update project. Only owner can update."""
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    if project.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not the project owner",
        )
    updated = update_project(db, project_id, body)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project_to_response(updated)


@router.post("/{project_id}/users", response_model=ProjectUserResponse, status_code=status.HTTP_201_CREATED)
def add_user_to_project_route(
    project_id: UUID,
    body: ProjectUserAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sa_role),
) -> ProjectUserResponse:
    """Add a user to the project. Creates User if email doesn't exist, creates ProjectUser with INVITED and invite_token."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    if project.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not the project owner",
        )
    project_user = add_user_to_project(db, project_id, body.email, body.name)
    return project_user_to_response(project_user)


@router.post("/{project_id}/users/{user_id}/activate", response_model=ProjectUserResponse)
def activate_user_route(
    project_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sa_role),
) -> ProjectUserResponse:
    """Set project user status to ACTIVE (activation; email flow comes later)."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    if project.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not the project owner",
        )
    project_user = activate_project_user(db, project_id, user_id)
    if not project_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project user not found",
        )
    db.refresh(project_user)
    return project_user_to_response(project_user)


@router.get("/{project_id}/progress", response_model=ProjectProgressResponse)
def get_progress_route(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sa_role),
) -> ProjectProgressResponse:
    """Get project progress: total_users, not_started, in_progress, completed."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    if project.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return get_project_progress(db, project_id)


@router.get(
    "/{project_id}/stakeholders/{user_id}/discovery-results",
    response_model=StakeholderDiscoveryResultsResponse,
)
def get_stakeholder_discovery_results(
    project_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sa_role),
) -> StakeholderDiscoveryResultsResponse:
    """Return phase summaries and final discovery report for a stakeholder on this project."""
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    if project.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Find the ProjectUser for this project/user
    project_user = None
    for pu in project.project_users:
        if pu.user_id == user_id:
            project_user = pu
            break

    print(
        f"[projects.get_stakeholder_discovery_results] project_id={project_id} user_id={user_id} "
        f"project_user={'found' if project_user else 'NOT FOUND'} "
        f"project_users_count={len(project.project_users)}"
    )

    if not project_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stakeholder not found for this project",
        )

    session: DiscoverySession | None = project_user.session
    if not session:
        print("[projects.get_stakeholder_discovery_results] No session for project_user")
        return StakeholderDiscoveryResultsResponse(phase_summaries={}, final_report=None)

    # Extract approved (non-pending) phase summaries from stored data
    raw_summaries = session.phase_summaries or {}
    phase_summaries: dict[str, str] = {}
    for k, v in raw_summaries.items():
        if str(k).endswith("_pending"):
            continue
        if isinstance(v, str):
            phase_summaries[str(k)] = v
        elif isinstance(v, dict) and isinstance(v.get("content"), str):
            phase_summaries[str(k)] = v["content"]

    # Generate final report on-the-fly (not stored in DB)
    final_report: str | None = None
    if session.status == SessionStatus.COMPLETED and phase_summaries:
        try:
            scope = project.scope
            final_report = generate_final_report(
                phase_summaries, scope, session.flagged_items or []
            )
        except Exception as e:
            print(f"[projects.get_stakeholder_discovery_results] generate_final_report error: {e}")
            final_report = None

    response = StakeholderDiscoveryResultsResponse(
        phase_summaries=phase_summaries,
        final_report=final_report,
    )
    print(
        f"[projects.get_stakeholder_discovery_results] session.status={session.status.value} "
        f"phase_summaries_keys={list(phase_summaries.keys())} has_final_report={final_report is not None} "
        f"response_keys={list(response.phase_summaries.keys())}"
    )
    return response


@router.get(
    "/{project_id}/consolidated-report",
    response_model=ConsolidatedReportResponse,
)
def get_consolidated_report(
    project_id: UUID,
    regenerate: bool = Query(False, description="Force regenerate the report"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sa_role),
) -> ConsolidatedReportResponse:
    """Get the consolidated discovery report for a project.

    Fetches all completed discovery sessions, synthesizes findings via Claude,
    and returns the report. Caches the result in the database unless regenerate=True.
    """
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    if project.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Gather completed sessions
    stakeholder_data: list[dict] = []
    for pu in project.project_users:
        if not pu.session or pu.session.status != SessionStatus.COMPLETED:
            continue
        session = pu.session
        name = pu.user.name if pu.user else pu.invited_name or ""
        email = pu.user.email if pu.user else pu.invited_email or ""
        raw_summaries = session.phase_summaries or {}
        phase_summaries: dict[str, str] = {}
        for k, v in raw_summaries.items():
            if str(k).endswith("_pending"):
                continue
            if isinstance(v, str):
                phase_summaries[str(k)] = v
        final_report: str | None = None
        if phase_summaries:
            final_report = generate_final_report(
                phase_summaries,
                project.scope,
                session.flagged_items or [],
            )
        stakeholder_data.append({
            "name": name or email or "Unknown",
            "email": email,
            "phase_summaries": phase_summaries,
            "final_report": final_report or "",
        })

    if not stakeholder_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one stakeholder must have completed discovery to generate the consolidated report.",
        )

    # Use cached report if available and not regenerating
    if not regenerate and project.consolidated_report and project.consolidated_report_generated_at:
        return ConsolidatedReportResponse(
            report_content=project.consolidated_report,
            generated_at=project.consolidated_report_generated_at,
            stakeholder_count=len(stakeholder_data),
        )

    # Generate and store
    report_content = generate_consolidated_report(project.scope, stakeholder_data)
    project.consolidated_report = report_content
    project.consolidated_report_generated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(project)

    return ConsolidatedReportResponse(
        report_content=report_content,
        generated_at=project.consolidated_report_generated_at,
        stakeholder_count=len(stakeholder_data),
    )


@router.put("/{project_id}/stakeholders/{user_id}/deactivate", response_model=ProjectUserResponse)
def deactivate_stakeholder(
    project_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sa_role),
) -> ProjectUserResponse:
    """Set a stakeholder's project participation status to INACTIVE."""
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    if project.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    project_user = (
        db.query(ProjectUser)
        .filter(ProjectUser.project_id == project_id, ProjectUser.user_id == user_id)
        .first()
    )
    if not project_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stakeholder not found for this project",
        )

    project_user.status = ProjectUserStatus.INACTIVE
    db.commit()
    db.refresh(project_user)
    return project_user_to_response(project_user)


@router.delete("/{project_id}/stakeholders/{user_id}", response_model=ProjectUserResponse)
def delete_stakeholder(
    project_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sa_role),
) -> ProjectUserResponse:
    """Remove a stakeholder from the project. Do not allow deleting completed stakeholders."""
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    if project.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    project_user = (
        db.query(ProjectUser)
        .filter(ProjectUser.project_id == project_id, ProjectUser.user_id == user_id)
        .first()
    )
    if not project_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stakeholder not found for this project",
        )

    if project_user.status == ProjectUserStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a stakeholder who has completed discovery. Deactivate them instead.",
        )

    response = project_user_to_response(project_user)
    db.delete(project_user)
    db.commit()
    return response
