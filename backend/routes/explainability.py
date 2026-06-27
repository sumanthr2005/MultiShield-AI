"""Explainability endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from backend.models.schemas import ExplainabilityRequest, ExplainabilityResponse
from backend.services.analysis_service import AnalysisService

router = APIRouter(prefix="/explainability", tags=["explainability"])


def get_analysis_service(request: Request) -> AnalysisService:
    return request.app.state.analysis_service


@router.post("/explain", response_model=ExplainabilityResponse)
async def explain(payload: ExplainabilityRequest, service: AnalysisService = Depends(get_analysis_service)) -> ExplainabilityResponse:
    return await service.explain(payload)
