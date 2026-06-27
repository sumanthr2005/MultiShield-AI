"""Pydantic models used by the Discord bot.

These models validate the payloads sent to MultiShield AI and the responses
received back from the FastAPI backend.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


DecisionLabel = Literal["safe", "review", "block"]
EnforcementAction = Literal["allow", "warn", "delete"]


class AnalysisEvidence(BaseModel):
    source: str
    snippet: str | None = None
    score: float = Field(ge=0.0, le=1.0)


class AnalysisResult(BaseModel):
    analysis_id: str
    agent: str
    label: str
    risk_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    decision: DecisionLabel
    explanation: str
    evidence: list[AnalysisEvidence] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExplainabilityResponse(BaseModel):
    analysis_id: str
    explanation: str
    contributing_factors: list[str] = Field(default_factory=list)
    recommended_next_steps: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ModerationResponse(BaseModel):
    analysis_id: str
    action: DecisionLabel
    rationale: str
    recommended_reviewers: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowResponse(BaseModel):
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


class MessageMetadata(BaseModel):
    guild_id: int
    channel_id: int
    message_id: int
    author_id: int
    author_name: str
    message_link: str
    attachment_urls: list[str] = Field(default_factory=list)
    attachment_names: list[str] = Field(default_factory=list)


class MessageScanOutcome(BaseModel):
    action: EnforcementAction
    risk_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str
    moderator_summary: str
    workflow_responses: list[WorkflowResponse] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
