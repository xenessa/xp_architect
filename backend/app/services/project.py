"""Project service: CRUD and project-user operations."""

import uuid
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.project import Project, ProjectUser, ProjectUserStatus
from app.models.session import DiscoverySession, SessionStatus
from app.models.user import User, UserRole
from app.schemas.project import (
    ProjectCreate,
    ProjectProgressResponse,
    ProjectUpdate,
    ProjectUserResponse,
)
from app.services.auth import hash_password


def create_project(db: Session, user_id: UUID, project_data: ProjectCreate) -> Project:
    """Create a new project with created_by set to user_id."""
    project = Project(
        name=project_data.name,
        description=project_data.description,
        scope=project_data.scope,
        instructions=project_data.instructions,
        start_date=project_data.start_date,
        end_date=project_data.end_date,
        created_by=user_id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_user_projects(db: Session, user_id: UUID) -> list[Project]:
    """Return all projects created by the given user."""
    stmt = select(Project).where(Project.created_by == user_id).order_by(Project.created_at.desc())
    return db.execute(stmt).scalars().all()


def get_project(db: Session, project_id: UUID) -> Project | None:
    """Return project by id, with project_users, user, and discovery session loaded."""
    stmt = (
        select(Project)
        .where(Project.id == project_id)
        .options(
            joinedload(Project.project_users).joinedload(ProjectUser.user),
            joinedload(Project.project_users).joinedload(ProjectUser.session),
        )
    )
    return db.execute(stmt).unique().scalars().first()


def update_project(
    db: Session,
    project_id: UUID,
    project_data: ProjectUpdate,
) -> Project | None:
    """Update project by id. Returns updated project or None if not found."""
    project = db.get(Project, project_id)
    if not project:
        return None
    data = project_data.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


def add_user_to_project(
    db: Session,
    project_id: UUID,
    email: str,
    name: str,
) -> ProjectUser:
    """Add a user to the project. If User exists with that email, link as ACTIVE. Otherwise create ProjectUser with invited_email/invited_name and invite_token (user_id=None)."""
    email_clean = (email or "").strip().lower()
    if not email_clean:
        raise ValueError("Email is required")

    user = db.execute(select(User).where(func.lower(User.email) == email_clean)).scalar_one_or_none()

    if user:
        # User exists: link directly as ACTIVE (no invite)
        existing = db.execute(
            select(ProjectUser).where(
                ProjectUser.project_id == project_id,
                ProjectUser.user_id == user.id,
            )
        ).scalars().first()
        if existing:
            return existing
        project_user = ProjectUser(
            project_id=project_id,
            user_id=user.id,
            status=ProjectUserStatus.ACTIVE,
            invite_token=None,
            invited_email=None,
            invited_name=None,
        )
        project_user.activated_at = datetime.now(timezone.utc)
    else:
        # No user: create ProjectUser with invite only (user_id=None)
        existing = db.execute(
            select(ProjectUser).where(
                ProjectUser.project_id == project_id,
                func.lower(ProjectUser.invited_email) == email_clean,
            )
        ).scalars().first()
        if existing:
            return existing
        project_user = ProjectUser(
            project_id=project_id,
            user_id=None,
            status=ProjectUserStatus.INVITED,
            invite_token=str(uuid.uuid4()),
            invited_email=email_clean,
            invited_name=(name or "").strip() or None,
        )
    db.add(project_user)
    db.commit()
    db.refresh(project_user)
    return project_user


def activate_project_user(
    db: Session,
    project_id: UUID,
    user_id: UUID,
) -> ProjectUser | None:
    """Set project user status to ACTIVE and set activated_at. Returns ProjectUser or None."""
    project_user = db.execute(
        select(ProjectUser).where(
            ProjectUser.project_id == project_id,
            ProjectUser.user_id == user_id,
        )
    ).scalars().first()
    if not project_user:
        return None
    project_user.status = ProjectUserStatus.ACTIVE
    project_user.activated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(project_user)
    return project_user


def get_project_progress(db: Session, project_id: UUID) -> ProjectProgressResponse:
    """Return progress counts for the project."""

    # Get all project users with their sessions
    project_users = db.execute(
        select(ProjectUser)
        .options(joinedload(ProjectUser.session))
        .where(ProjectUser.project_id == project_id)
    ).unique().scalars().all()

    total = len(project_users)
    not_started = 0
    in_progress = 0
    completed = 0

    for pu in project_users:
        # No session yet (not registered or hasn't started discovery)
        if not pu.session:
            not_started += 1
            continue

        status = pu.session.status
        if status == SessionStatus.NOT_STARTED:
            not_started += 1
        elif status == SessionStatus.COMPLETED:
            completed += 1
        else:  # IN_PROGRESS
            in_progress += 1

    return ProjectProgressResponse(
        total_users=total,
        not_started=not_started,
        in_progress=in_progress,
        completed=completed,
    )


def project_user_to_response(pu: ProjectUser) -> ProjectUserResponse:
    """Build ProjectUserResponse from ProjectUser with discovery progress."""
    if pu.user:
        email = pu.user.email
        name = pu.user.name
    else:
        email = pu.invited_email or ""
        name = pu.invited_name or ""

    # Get discovery session info
    discovery_status: str | None = None
    current_phase: int | None = None
    phases_approved: list[int] = []

    if pu.session:
        discovery_status = pu.session.status.value if pu.session.status else None
        current_phase = pu.session.current_phase
        # phase_summaries is a dict like {"1": "summary text", "2": "summary text"}
        if pu.session.phase_summaries:
            phases_approved = [int(k) for k in pu.session.phase_summaries.keys()]

    return ProjectUserResponse(
        id=pu.id,
        user_id=pu.user_id,
        email=email,
        name=name,
        status=pu.status,
        invited_at=pu.invited_at,
        activated_at=pu.activated_at,
        invite_token=pu.invite_token,
        discovery_status=discovery_status,
        current_phase=current_phase,
        phases_approved=phases_approved,
    )
