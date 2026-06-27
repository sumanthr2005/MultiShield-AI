"""Image detection endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from backend.models.schemas import AnalysisResult, ImageAnalysisRequest
from backend.services.analysis_service import AnalysisService

router = APIRouter(prefix="/image", tags=["image"])


def get_analysis_service(request: Request) -> AnalysisService:
    return request.app.state.analysis_service


@router.post("/detect", response_model=AnalysisResult)
async def detect_image(payload: ImageAnalysisRequest, service: AnalysisService = Depends(get_analysis_service)) -> AnalysisResult:
    return await service.analyze_image(payload)
