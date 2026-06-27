"""Shared LangGraph workflow state definitions."""

from __future__ import annotations

import operator
from typing import Annotated, Any, NotRequired, TypedDict

from backend.models.schemas import AnalysisResult, ExplainabilityResponse, ModerationResponse


class MultiShieldWorkflowState(TypedDict, total=False):
    """Mutable state passed between LangGraph nodes.

    The reducer annotations on list fields let each node append trace and error
    details without clobbering previous node output.
    """

    workflow_id: str
    text: NotRequired[str | None]
    image_reference: NotRequired[str | None]
    ocr_text: NotRequired[str | None]
    metadata: NotRequired[dict[str, Any]]
    modality_weights: NotRequired[dict[str, float]]
    route: NotRequired[str]
    route_confidence: NotRequired[float]
    pending_modalities: NotRequired[list[str]]
    processed_modalities: Annotated[list[str], operator.add]
    text_result: NotRequired[AnalysisResult | None]
    image_result: NotRequired[AnalysisResult | None]
    fusion_result: NotRequired[AnalysisResult | None]
    explainability_result: NotRequired[ExplainabilityResponse | None]
    moderation_result: NotRequired[ModerationResponse | None]
    confidence_score: NotRequired[float]
    status: NotRequired[str]
    trace: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]
