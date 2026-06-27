"""Moderation endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from backend.models.schemas import ModerationRequest, ModerationResponse
from backend.services.analysis_service import AnalysisService

router = APIRouter(prefix="/moderation", tags=["moderation"])


def get_analysis_service(request: Request) -> AnalysisService:
    return request.app.state.analysis_service


@router.post("/moderate", response_model=ModerationResponse)
async def moderate(payload: ModerationRequest, service: AnalysisService = Depends(get_analysis_service)) -> ModerationResponse:
    return await service.moderate(payload)
