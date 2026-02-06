"""Project-related Pydantic schemas."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.project import ProjectUserStatus


class ProjectCreate(BaseModel):
    """Schema for creating a project."""

    name: str
    description: str | None = None
    scope: str
    instructions: str | None = None
    start_date: date
    end_date: date


class ProjectUpdate(BaseModel):
    """Schema for updating a project (all fields optional)."""

    name: str | None = None
    description: str | None = None
    scope: str | None = None
    instructions: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class ProjectResponse(BaseModel):
    """Schema for project in responses."""

    id: UUID
    name: str
    description: str | None
    scope: str
    instructions: str | None
    start_date: date
    end_date: date
    created_by: UUID
    created_at: datetime
    total_users: int | None = None
    completed_users: int | None = None
    completion_percentage: float | None = None

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    """List of projects."""

    projects: list[ProjectResponse]


class ProjectUserAdd(BaseModel):
    """Schema for adding a user to a project."""

    email: str
    name: str


class ProjectUserResponse(BaseModel):
    """Schema for project user in responses."""

    id: UUID
    user_id: UUID | None
    email: str
    name: str
    status: ProjectUserStatus
    invited_at: datetime
    activated_at: datetime | None
    invite_token: str | None = None
    discovery_status: str | None = None  # "NOT_STARTED", "IN_PROGRESS", "COMPLETED"
    current_phase: int | None = None  # 1-4
    phases_approved: list[int] = []  # List of phase numbers that have approved summaries

    model_config = {"from_attributes": True}


class ProjectProgressResponse(BaseModel):
    """Schema for project progress stats."""

    total_users: int
    not_started: int
    in_progress: int
    completed: int


class ProjectDetailResponse(BaseModel):
    """Project with users list and progress stats."""

    project: ProjectResponse
    users: list[ProjectUserResponse]
    progress: ProjectProgressResponse


class StakeholderDiscoveryResultsResponse(BaseModel):
    """Phase summaries and final report for a single stakeholder's discovery session."""

    phase_summaries: dict[str, str]
    final_report: str | None = None


class ConsolidatedReportResponse(BaseModel):
    """Consolidated discovery report synthesizing findings from all stakeholders."""

    report_content: str
    generated_at: datetime
    stakeholder_count: int
