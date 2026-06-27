"""Application service that orchestrates the six agent pipeline."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.agents.audio_agent import AudioAgent
from backend.agents.explainability_agent import ExplainabilityAgent
from backend.agents.fusion_agent import FusionAgent
from backend.agents.image_agent import ImageAgent
from backend.agents.moderation_agent import ModerationAgent
from backend.agents.text_agent import TextAgent
from backend.models.schemas import (
    AnalysisResult,
    AudioAnalysisRequest,
    ExplainabilityRequest,
    ExplainabilityResponse,
    FusionAnalysisRequest,
    ImageAnalysisRequest,
    ModerationRequest,
    ModerationResponse,
    TextAnalysisRequest,
    WorkflowResponse,
)
from backend.services.analysis_repository import AnalysisRepository
from backend.utils.config import Settings
from backend.utils.errors import ProcessingError
from backend.workflows.graph import MultiShieldWorkflow


class AnalysisService:
    """Coordinate agent execution, fusion, explainability, moderation, and persistence."""

    def __init__(self, settings: Settings, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.settings = settings
        self.repository = AnalysisRepository(session_factory)
        self.text_agent = TextAgent()
        self.image_agent = ImageAgent()
        self.audio_agent = AudioAgent()
        self.fusion_agent = FusionAgent()
        self.explainability_agent = ExplainabilityAgent()
        self.moderation_agent = ModerationAgent()
        self.workflow = MultiShieldWorkflow(
            settings=settings,
            session_factory=session_factory,
            router_agent=None,
            text_agent=self.text_agent,
            image_agent=self.image_agent,
            fusion_agent=self.fusion_agent,
            explainability_agent=self.explainability_agent,
            moderation_agent=self.moderation_agent,
        )

    async def analyze_text(self, request: TextAnalysisRequest) -> AnalysisResult:
        result = await self.text_agent.analyze(request)
        await self.repository.save_analysis(result, request.model_dump())
        return result

    async def analyze_image(self, request: ImageAnalysisRequest) -> AnalysisResult:
        result = await self.image_agent.analyze(request)
        await self.repository.save_analysis(result, request.model_dump())
        return result

    async def analyze_audio(self, request: AudioAnalysisRequest) -> AnalysisResult:
        result = await self.audio_agent.analyze(request)
        await self.repository.save_analysis(result, request.model_dump())
        return result

    async def analyze_fusion(self, request: FusionAnalysisRequest) -> AnalysisResult:
        workflow_response = await self.workflow.run(request)
        if workflow_response.fusion_result is None:
            raise ProcessingError(
                "Fusion workflow completed without a fused result.",
                {"workflow_id": workflow_response.workflow_id, "route": workflow_response.route},
            )
        return workflow_response.fusion_result

    async def run_workflow(self, request: FusionAnalysisRequest) -> WorkflowResponse:
        return await self.workflow.run(request)

    async def explain(self, request: ExplainabilityRequest) -> ExplainabilityResponse:
        return await self.explainability_agent.explain(request.analysis_result)

    async def moderate(self, request: ModerationRequest) -> ModerationResponse:
        moderation_result = await self.moderation_agent.moderate(request.analysis_result)
        await self.repository.save_moderation(moderation_result)
        return moderation_result
