"""Human feedback endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from backend.dependencies.security import enforce_rate_limit, get_enterprise_service, get_optional_principal
from backend.models.schemas import FeedbackCreateRequest, FeedbackResponse
from backend.services.enterprise_service import EnterprisePrincipal, EnterpriseService

router = APIRouter(prefix="/feedback", tags=["feedback"], dependencies=[Depends(enforce_rate_limit)])


@router.post("/submit", response_model=FeedbackResponse)
async def submit(
    payload: FeedbackCreateRequest,
    request: Request,
    principal: EnterprisePrincipal | None = Depends(get_optional_principal),
) -> FeedbackResponse:
    service: EnterpriseService = get_enterprise_service(request)
    return await service.submit_feedback(payload, principal=principal)
