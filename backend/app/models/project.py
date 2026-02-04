"""Project, ProjectFile, and ProjectUser models for discovery session application."""

import enum
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.session import DiscoverySession
    from app.models.user import User


class ProjectUserStatus(str, enum.Enum):
    """Status of a user's participation in a project."""

    INVITED = "INVITED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


class Project(Base):
    """Project with scope, instructions, and dates."""

    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    scope: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    instructions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    created_by_user: Mapped["User"] = relationship(
        "User",
        back_populates="created_projects",
        foreign_keys=[created_by],
    )
    project_users: Mapped[list["ProjectUser"]] = relationship(
        "ProjectUser",
        back_populates="project",
    )
    files: Mapped[list["ProjectFile"]] = relationship(
        "ProjectFile",
        back_populates="project",
    )
    sessions: Mapped[list["DiscoverySession"]] = relationship(
        "DiscoverySession",
        viewonly=True,
        secondary="project_users",
        primaryjoin="Project.id == ProjectUser.project_id",
        secondaryjoin="ProjectUser.id == DiscoverySession.project_user_id",
    )


class ProjectFile(Base):
    """File attached to a project (e.g. S3 or local path)."""

    __tablename__ = "project_files"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    file_path: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )
    file_size: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="files",
    )


class ProjectUser(Base):
    """Association of a user to a project with invite/activation state."""

    __tablename__ = "project_users"

    __table_args__ = (
        Index("ix_project_users_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    status: Mapped[ProjectUserStatus] = mapped_column(
        Enum(ProjectUserStatus),
        default=ProjectUserStatus.INVITED,
        nullable=False,
    )
    invite_token: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
    )
    invited_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    invited_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    invited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    activated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="project_users",
    )
    user: Mapped["User | None"] = relationship(
        "User",
        back_populates="project_users",
    )
    session: Mapped["DiscoverySession | None"] = relationship(
        "DiscoverySession",
        back_populates="project_user",
        uselist=False,
    )
