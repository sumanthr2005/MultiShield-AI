"""Analytics summary endpoint used by the dashboard."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from backend.dependencies.security import enforce_rate_limit, get_enterprise_service
from backend.models.schemas import AnalyticsSummaryResponse
from backend.services.enterprise_service import EnterpriseService

router = APIRouter(prefix="/analytics", tags=["analytics"], dependencies=[Depends(enforce_rate_limit)])


@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def summary(request: Request) -> AnalyticsSummaryResponse:
    service: EnterpriseService = get_enterprise_service(request)
    return await service.analytics_summary()
