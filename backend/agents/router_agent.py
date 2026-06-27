"""Router agent for the MultiShield AI LangGraph workflow.

The router inspects the incoming payload, determines which modality agents
should run, and assigns an execution plan that LangGraph can follow. This keeps
the graph deterministic and auditable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from backend.models.schemas import FusionAnalysisRequest


RouteName = Literal["text_analysis", "image_analysis", "fusion", "error"]


@dataclass(slots=True)
class RouteDecision:
    """Structured decision returned by the router agent."""

    next_step: RouteName
    route_confidence: float
    reason: str
    pending_modalities: list[str]


class RouterAgent:
    """Determine which agent should execute first."""

    name = "router"

    async def route(self, payload: FusionAnalysisRequest | dict[str, Any]) -> RouteDecision:
        if isinstance(payload, dict):
            text = payload.get("text")
            image_reference = payload.get("image_reference")
            audio_reference = payload.get("audio_reference")
        else:
            text = payload.text
            image_reference = payload.image_reference
            audio_reference = payload.audio_reference

        pending_modalities: list[str] = []
        if text:
            pending_modalities.append("text")
        if image_reference:
            pending_modalities.append("image")
        if audio_reference:
            pending_modalities.append("audio")

        if not pending_modalities:
            return RouteDecision(
                next_step="error",
                route_confidence=0.1,
                reason="At least one modality input is required.",
                pending_modalities=[],
            )

        next_step = "text_analysis" if "text" in pending_modalities else "image_analysis"
        route_confidence = 0.98 if len(pending_modalities) > 1 else 0.93
        return RouteDecision(
            next_step=next_step,
            route_confidence=route_confidence,
            reason="Routing based on the modalities supplied in the request.",
            pending_modalities=pending_modalities,
        )
