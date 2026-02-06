"""Discovery session Pydantic schemas."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class PhaseSummaryAction(str, Enum):
    """Action for phase summary approval."""

    approve = "approve"
    request_changes = "request_changes"
    add_details = "add_details"


class AssessmentSubmit(BaseModel):
    """Communication style assessment submission. responses: list of {question, ranks: {A,B,C,D}}."""

    responses: list[dict]


class SessionResponse(BaseModel):
    """Discovery session state for API responses."""

    id: UUID
    current_phase: int
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    pending_phase_summary: str | None = None  # when awaiting approval
    all_messages: list[dict] = []  # conversation history [{role, content}, ...]
    is_first_visit: bool | None = None

    model_config = {"from_attributes": True}


class SessionMessageRequest(BaseModel):
    """Request body for sending a message in the session."""

    message: str


class SessionMessageResponse(BaseModel):
    """Response after sending a message: Claude reply and optional phase completion."""

    assistant_message: str
    phase_completed: bool = False
    summary: str | None = None  # when phase just completed, summary for approval
    message: str
    phase_complete_suggested: bool = False


class PhaseSummaryApproval(BaseModel):
    """Request body for approving/revising phase summary."""

    action: PhaseSummaryAction
    feedback: str | None = None  # for request_changes or add_details


class SessionReportResponse(BaseModel):
    """Final discovery report content."""

    report_content: str
