"""LangGraph implementation for the MultiShield AI multi-agent workflow."""

from __future__ import annotations

from uuid import uuid4

from langgraph.graph import END, START, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.agents.explainability_agent import ExplainabilityAgent
from backend.agents.fusion_agent import FusionAgent
from backend.agents.image_agent import ImageAgent
from backend.agents.moderation_agent import ModerationAgent
from backend.agents.router_agent import RouterAgent
from backend.agents.text_agent import TextAgent
from backend.models.schemas import (
    FusionAnalysisRequest,
    ImageAnalysisRequest,
    TextAnalysisRequest,
    WorkflowResponse,
)
from backend.services.analysis_repository import AnalysisRepository
from backend.utils.config import Settings
from backend.utils.errors import ProcessingError, ValidationError
from backend.utils.logger import get_logger
from backend.workflows.state import MultiShieldWorkflowState


class MultiShieldWorkflow:
    """Build and run the LangGraph execution pipeline."""

    def __init__(
        self,
        settings: Settings,
        session_factory: async_sessionmaker[AsyncSession],
        router_agent: RouterAgent | None = None,
        text_agent: TextAgent | None = None,
        image_agent: ImageAgent | None = None,
        fusion_agent: FusionAgent | None = None,
        explainability_agent: ExplainabilityAgent | None = None,
        moderation_agent: ModerationAgent | None = None,
    ) -> None:
        self.settings = settings
        self.logger = get_logger(__name__)
        self.repository = AnalysisRepository(session_factory)
        self.router_agent = router_agent or RouterAgent()
        self.text_agent = text_agent or TextAgent()
        self.image_agent = image_agent or ImageAgent()
        self.fusion_agent = fusion_agent or FusionAgent()
        self.explainability_agent = explainability_agent or ExplainabilityAgent()
        self.moderation_agent = moderation_agent or ModerationAgent()
        self.graph = self._build_graph().compile()

    def _build_graph(self) -> StateGraph[MultiShieldWorkflowState]:
        builder: StateGraph[MultiShieldWorkflowState] = StateGraph(MultiShieldWorkflowState)
        builder.add_node("router", self._route)
        builder.add_node("text_analysis", self._text_analysis)
        builder.add_node("image_analysis", self._image_analysis)
        builder.add_node("fusion", self._fusion)
        builder.add_node("explainability", self._explainability)
        builder.add_node("moderation", self._moderation)
        builder.add_node("error", self._error)

        builder.add_edge(START, "router")
        builder.add_conditional_edges("router", self._after_router, {
            "text_analysis": "text_analysis",
            "image_analysis": "image_analysis",
            "error": "error",
        })
        builder.add_conditional_edges("text_analysis", self._after_text_analysis, {
            "image_analysis": "image_analysis",
            "fusion": "fusion",
        })
        builder.add_conditional_edges("image_analysis", self._after_image_analysis, {
            "fusion": "fusion",
        })
        builder.add_edge("fusion", "explainability")
        builder.add_edge("explainability", "moderation")
        builder.add_edge("moderation", END)
        builder.add_edge("error", END)
        return builder

    async def run(self, request: FusionAnalysisRequest) -> WorkflowResponse:
        """Execute the compiled graph and return a normalized response."""

        initial_state: MultiShieldWorkflowState = {
            "workflow_id": str(uuid4()),
            "text": request.text,
            "image_reference": request.image_reference,
            "ocr_text": request.ocr_text,
            "metadata": request.metadata,
            "modality_weights": request.modality_weights,
            "status": "running",
            "trace": ["workflow:started"],
            "errors": [],
            "processed_modalities": [],
        }

        try:
            final_state = await self.graph.ainvoke(initial_state)
        except ValidationError:
            raise
        except Exception as exc:  # pragma: no cover - defensive boundary
            self.logger.exception("MultiShield workflow failed")
            raise ProcessingError("MultiShield workflow execution failed.", {"exception": exc.__class__.__name__}) from exc

        if final_state.get("status") == "failed":
            raise ValidationError(
                "MultiShield workflow could not start because no supported input was provided.",
                {"errors": final_state.get("errors", [])},
            )

        return WorkflowResponse(
            workflow_id=final_state["workflow_id"],
            route=final_state.get("route", "fusion"),
            route_confidence=final_state.get("route_confidence", 0.0),
            text_result=final_state.get("text_result"),
            image_result=final_state.get("image_result"),
            fusion_result=final_state.get("fusion_result"),
            explainability_result=final_state.get("explainability_result"),
            moderation_result=final_state.get("moderation_result"),
            confidence_score=final_state.get("confidence_score", 0.0),
            trace=final_state.get("trace", []),
            errors=final_state.get("errors", []),
            status=final_state.get("status", "completed"),
        )

    async def _route(self, state: MultiShieldWorkflowState) -> MultiShieldWorkflowState:
        decision = await self.router_agent.route(
            {
                "text": state.get("text"),
                "image_reference": state.get("image_reference"),
                "ocr_text": state.get("ocr_text"),
            }
        )
        self.logger.info("router decision", extra={"workflow_id": state["workflow_id"], "route": decision.next_step})
        return {
            "route": decision.next_step,
            "route_confidence": decision.route_confidence,
            "pending_modalities": decision.pending_modalities,
            "trace": [f"router:{decision.next_step}:{decision.reason}"],
        }

    def _after_router(self, state: MultiShieldWorkflowState) -> str:
        return state.get("route", "error")

    async def _text_analysis(self, state: MultiShieldWorkflowState) -> MultiShieldWorkflowState:
        text = state.get("text")
        if not text:
            return {"trace": ["text_analysis:skipped"], "processed_modalities": ["text"]}

        result = await self.text_agent.analyze(
            TextAnalysisRequest(text=text, metadata=state.get("metadata", {}))
        )
        await self.repository.save_analysis(result, {"text": text, "metadata": state.get("metadata", {})})
        return {
            "text_result": result,
            "confidence_score": result.confidence,
            "trace": ["text_analysis:completed"],
            "processed_modalities": ["text"],
        }

    def _after_text_analysis(self, state: MultiShieldWorkflowState) -> str:
        pending = state.get("pending_modalities", [])
        processed = set(state.get("processed_modalities", []))
        if "image" in pending and "image" not in processed:
            return "image_analysis"
        return "fusion"

    async def _image_analysis(self, state: MultiShieldWorkflowState) -> MultiShieldWorkflowState:
        image_reference = state.get("image_reference")
        if not image_reference:
            return {"trace": ["image_analysis:skipped"], "processed_modalities": ["image"]}

        result = await self.image_agent.analyze(
            ImageAnalysisRequest(
                image_reference=image_reference,
                ocr_text=state.get("ocr_text"),
                metadata=state.get("metadata", {}),
            )
        )
        await self.repository.save_analysis(result, {"image_reference": image_reference, "metadata": state.get("metadata", {})})
        return {
            "image_result": result,
            "confidence_score": max(state.get("confidence_score", 0.0), result.confidence),
            "trace": ["image_analysis:completed"],
            "processed_modalities": ["image"],
        }

    def _after_image_analysis(self, state: MultiShieldWorkflowState) -> str:
        return "fusion"

    async def _fusion(self, state: MultiShieldWorkflowState) -> MultiShieldWorkflowState:
        modality_results = [result for result in [state.get("text_result"), state.get("image_result")] if result is not None]
        if not modality_results:
            raise ValidationError("Fusion requires at least one modality result.")

        fused_result = await self.fusion_agent.analyze(modality_results)
        fused_result.metadata = {
            **fused_result.metadata,
            "workflow_id": state["workflow_id"],
            "modality_weights": state.get("modality_weights", {}),
            "source_count": len(modality_results),
        }
        await self.repository.save_analysis(
            fused_result,
            {
                "workflow_id": state["workflow_id"],
                "text": state.get("text"),
                "image_reference": state.get("image_reference"),
                "ocr_text": state.get("ocr_text"),
                "metadata": state.get("metadata", {}),
                "modality_weights": state.get("modality_weights", {}),
            },
        )
        return {
            "fusion_result": fused_result,
            "confidence_score": fused_result.confidence,
            "trace": ["fusion:completed"],
        }

    async def _explainability(self, state: MultiShieldWorkflowState) -> MultiShieldWorkflowState:
        fusion_result = state.get("fusion_result")
        if fusion_result is None:
            raise ValidationError("Explainability requires a fused result.")

        explanation = await self.explainability_agent.explain(fusion_result)
        return {
            "explainability_result": explanation,
            "trace": ["explainability:completed"],
        }

    async def _moderation(self, state: MultiShieldWorkflowState) -> MultiShieldWorkflowState:
        fusion_result = state.get("fusion_result")
        if fusion_result is None:
            raise ValidationError("Moderation requires a fused result.")

        moderation_result = await self.moderation_agent.moderate(fusion_result)
        await self.repository.save_moderation(moderation_result)
        return {
            "moderation_result": moderation_result,
            "status": "completed",
            "trace": ["moderation:completed"],
        }

    async def _error(self, state: MultiShieldWorkflowState) -> MultiShieldWorkflowState:
        message = "No supported modality input was provided."
        self.logger.warning("workflow rejected", extra={"workflow_id": state["workflow_id"], "reason": message})
        return {
            "status": "failed",
            "errors": [message],
            "trace": ["workflow:error"],
        }
