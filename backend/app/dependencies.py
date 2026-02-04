"""FastAPI dependency functions."""

from fastapi import Depends, HTTPException, status

from app.models.user import User, UserRole
from app.services.auth import get_current_user_dependency


def require_sa_role(
    current_user: User = Depends(get_current_user_dependency),
) -> User:
    """Require that the current user has SA role. Raise 403 otherwise."""
    if current_user.role != UserRole.SA:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solution Architect role required",
        )
    return current_user
