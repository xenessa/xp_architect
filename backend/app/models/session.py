"""DiscoverySession and SessionDocument models for discovery session application."""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class SessionStatus(str, enum.Enum):
    """Status of a discovery session."""

    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class DiscoverySession(Base):
    """Discovery session for a single project user (one session per project user)."""

    __tablename__ = "discovery_sessions"

    __table_args__ = (
        CheckConstraint(
            "current_phase >= 1 AND current_phase <= 4",
            name="ck_discovery_sessions_current_phase_range",
        ),
        Index("ix_discovery_sessions_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    project_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project_users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    current_phase: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus),
        default=SessionStatus.NOT_STARTED,
        nullable=False,
    )
    all_messages: Mapped[list[Any]] = mapped_column(
        JSON,
        default=lambda: [],
        nullable=False,
    )
    phase_summaries: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=lambda: {},
        nullable=False,
    )
    flagged_items: Mapped[list[Any]] = mapped_column(
        JSON,
        default=lambda: [],
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    project_user: Mapped["ProjectUser"] = relationship(
        "ProjectUser",
        back_populates="session",
    )
    documents: Mapped[list["SessionDocument"]] = relationship(
        "SessionDocument",
        back_populates="session",
    )


class SessionDocument(Base):
    """Document uploaded during a discovery session (per phase)."""

    __tablename__ = "session_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("discovery_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    phase_num: Mapped[int] = mapped_column(
        Integer,
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
    file_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    session: Mapped["DiscoverySession"] = relationship(
        "DiscoverySession",
        back_populates="documents",
    )


if TYPE_CHECKING:
    from app.models.project import ProjectUser