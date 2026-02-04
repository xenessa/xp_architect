"""Authentication routes: register, login, me."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.project import ProjectUser, ProjectUserStatus
from app.models.user import User, UserRole
from app.schemas.user import TokenWithUser, UserCreate, UserLogin, UserResponse
from app.services.auth import (
    create_access_token,
    get_current_user_dependency,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def user_to_response(user: User) -> UserResponse:
    """Build UserResponse from User model (no password)."""
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        assessment_completed=user.assessment_completed,
        created_at=user.created_at,
    )


@router.post("/register", response_model=UserResponse)
def register(
    body: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Create a new user. If invite_token is provided, validate it and link user to project."""
    print(f"DEBUG register: role={body.role}, invite_token={body.invite_token}")
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    project_user = None
    if body.invite_token:
        project_user = (
            db.query(ProjectUser)
            .filter(ProjectUser.invite_token == body.invite_token)
            .first()
        )
        if not project_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired invite token",
            )
        if project_user.user_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invite token already used",
            )

    name = (body.name or "").strip()
    if not name and project_user and project_user.invited_name:
        name = (project_user.invited_name or "").strip()
    if not name:
        name = "Stakeholder"

    # Determine role. Invited registrations are always stakeholders.
    if body.invite_token:
        role = UserRole.STAKEHOLDER
    else:
        role_str = (body.role or "").strip().upper()
        if role_str == "SA":
            role = UserRole.SA
        else:
            role = UserRole.STAKEHOLDER

    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        name=name,
        role=role,
    )
    db.add(user)
    db.flush()

    if body.invite_token and project_user:
        project_user.user_id = user.id
        project_user.status = ProjectUserStatus.ACTIVE
        project_user.activated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(user)
    return user_to_response(user)


@router.get("/invite/{token}")
def get_invite_details(token: str, db: Session = Depends(get_db)):
    """Get invited user details from invite token (for pre-populating registration form)."""
    project_user = (
        db.query(ProjectUser)
        .options(joinedload(ProjectUser.project))
        .filter(ProjectUser.invite_token == token)
        .first()
    )
    if not project_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired invite token",
        )
    if project_user.user_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invite has already been used",
        )
    return {
        "email": project_user.invited_email,
        "name": project_user.invited_name,
        "project_name": project_user.project.name if project_user.project else None,
    }


@router.post("/login", response_model=TokenWithUser)
def login(
    body: UserLogin,
    db: Session = Depends(get_db),
) -> TokenWithUser:
    """Login with email and password. Returns JWT access token and user object."""
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return TokenWithUser(
        access_token=create_access_token(user.id),
        token_type="bearer",
        user=user_to_response(user),
    )


@router.get("/me", response_model=UserResponse)
def me(
    current_user: User = Depends(get_current_user_dependency),
) -> UserResponse:
    """Return the current authenticated user (requires valid JWT)."""
    return user_to_response(current_user)
