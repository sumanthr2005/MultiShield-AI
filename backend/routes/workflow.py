"""LangGraph workflow endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from backend.models.schemas import FusionAnalysisRequest, WorkflowResponse
from backend.services.analysis_service import AnalysisService

router = APIRouter(prefix="/workflow", tags=["workflow"])


def get_analysis_service(request: Request) -> AnalysisService:
    return request.app.state.analysis_service


@router.post("/analyze", response_model=WorkflowResponse)
async def analyze_workflow(payload: FusionAnalysisRequest, service: AnalysisService = Depends(get_analysis_service)) -> WorkflowResponse:
    return await service.run_workflow(payload)
