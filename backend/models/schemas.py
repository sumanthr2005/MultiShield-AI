"""Pydantic request and response schemas.

The schemas form the contract between the API layer and the application layer.
They are intentionally explicit so each modality can evolve without breaking
the others.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


AgentName = Literal["text", "image", "audio", "fusion", "explainability", "moderation"]
DecisionLabel = Literal["safe", "review", "block"]
UserRole = Literal["admin", "moderator", "analyst", "auditor", "viewer", "system"]
FeedbackStatus = Literal["new", "triaged", "accepted", "rejected"]
RetrainingJobStatus = Literal["queued", "running", "completed", "failed"]


def _analysis_id_factory() -> str:
    return str(uuid4())


class BasePayload(BaseModel):
    """Shared metadata accepted by all detection endpoints."""

    metadata: dict[str, Any] = Field(default_factory=dict)


class TextAnalysisRequest(BasePayload):
    text: str = Field(min_length=1, description="User supplied text to inspect.")
    language: str | None = Field(default=None, description="Optional language hint.")


class ImageAnalysisRequest(BasePayload):
    image_reference: str = Field(description="A URL, object-store key, or file identifier.")
    ocr_text: str | None = Field(default=None, description="Optional OCR text extracted from the image.")


class AudioAnalysisRequest(BasePayload):
    audio_reference: str = Field(description="A URL, object-store key, or file identifier.")
    transcript: str | None = Field(default=None, description="Optional ASR transcript.")


class FusionAnalysisRequest(BasePayload):
    text: str | None = None
    image_reference: str | None = None
    audio_reference: str | None = None
    ocr_text: str | None = None
    transcript: str | None = None
    modality_weights: dict[str, float] = Field(default_factory=dict)


class DetectionEvidence(BaseModel):
    source: str
    snippet: str | None = None
    score: float = Field(ge=0.0, le=1.0)


class AnalysisResult(BaseModel):
    analysis_id: str = Field(default_factory=_analysis_id_factory)
    agent: AgentName
    label: str
    risk_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    decision: DecisionLabel
    explanation: str
    evidence: list[DetectionEvidence] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ExplainabilityRequest(BaseModel):
    analysis_result: AnalysisResult


class ExplainabilityResponse(BaseModel):
    analysis_id: str
    explanation: str
    contributing_factors: list[str] = Field(default_factory=list)
    recommended_next_steps: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ModerationRequest(BaseModel):
    analysis_result: AnalysisResult


class ModerationResponse(BaseModel):
    analysis_id: str
    action: DecisionLabel
    rationale: str
    recommended_reviewers: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class UserCreateRequest(BaseModel):
    email: str
    display_name: str
    role: UserRole = "moderator"


class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    role: UserRole
    is_active: bool
    created_at: datetime


class ApiKeyCreateRequest(BaseModel):
    user_id: str
    name: str
    scopes: list[str] = Field(default_factory=list)


class ApiKeyResponse(BaseModel):
    id: str
    user_id: str
    name: str
    key_prefix: str
    scopes: list[str] = Field(default_factory=list)
    is_active: bool
    expires_at: datetime | None = None
    created_at: datetime
    plaintext_key: str | None = None


class PrincipalResponse(BaseModel):
    user_id: str
    email: str
    display_name: str
    role: UserRole
    scopes: list[str] = Field(default_factory=list)
    api_key_id: str


class FeedbackCreateRequest(BaseModel):
    analysis_id: str
    label: str
    comment: str | None = None
    confidence_rating: float | None = Field(default=None, ge=0.0, le=1.0)
    is_actionable: bool = True
    status: FeedbackStatus = "new"


class FeedbackResponse(BaseModel):
    id: str
    analysis_id: str
    label: str
    comment: str | None = None
    confidence_rating: float | None = None
    is_actionable: bool
    status: FeedbackStatus
    created_at: datetime


class RetrainingJobCreateRequest(BaseModel):
    name: str
    notes: str | None = None
    source_window_days: int = Field(default=30, ge=1, le=365)


class RetrainingJobResponse(BaseModel):
    id: str
    name: str
    status: RetrainingJobStatus
    dataset_path: str | None = None
    model_version: str | None = None
    notes: str | None = None
    created_at: datetime
    completed_at: datetime | None = None


class NotificationResponse(BaseModel):
    id: str
    recipient: str | None = None
    channel: str
    subject: str
    delivery_status: str
    created_at: datetime


class AnalyticsSummaryResponse(BaseModel):
    window_days: int
    total_analyses: int
    total_feedback: int
    active_feedback: int
    total_users: int
    total_api_keys: int
    total_retraining_jobs: int
    open_retraining_jobs: int
    decision_breakdown: dict[str, int]
    role_breakdown: dict[str, int]
    feedback_breakdown: dict[str, int]
    usage_by_route: dict[str, int]


class WorkflowResponse(BaseModel):
    """Response returned by the LangGraph execution pipeline."""

    workflow_id: str
    route: str
    route_confidence: float = Field(ge=0.0, le=1.0)
    text_result: AnalysisResult | None = None
    image_result: AnalysisResult | None = None
    fusion_result: AnalysisResult | None = None
    explainability_result: ExplainabilityResponse | None = None
    moderation_result: ModerationResponse | None = None
    confidence_score: float = Field(ge=0.0, le=1.0)
    trace: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    status: Literal["completed", "failed"] = "completed"


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "MultiShield AI"
    version: str = "1.0.0"
    environment: str = "development"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ReadinessResponse(BaseModel):
    status: str = "ok"
    service: str = "MultiShield AI"
    version: str = "1.0.0"
    environment: str = "development"
    database: str = "ok"
    redis: str = "ok"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AuditLogResponse(BaseModel):
    id: str
    event_type: str
    action: str | None = None
    actor_id: str | None = None
    actor_role: str | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    request_id: str | None = None
    ip_address: str | None = None
    payload: dict[str, Any]
    created_at: datetime
