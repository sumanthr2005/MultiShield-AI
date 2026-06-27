"""Protected enterprise management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from backend.dependencies.security import enforce_rate_limit, get_enterprise_service, require_roles
from backend.models.schemas import (
    ApiKeyCreateRequest,
    ApiKeyResponse,
    AuditLogResponse,
    FeedbackResponse,
    NotificationResponse,
    PrincipalResponse,
    RetrainingJobCreateRequest,
    RetrainingJobResponse,
    UserCreateRequest,
    UserResponse,
)
from backend.services.enterprise_service import EnterprisePrincipal, EnterpriseService

router = APIRouter(prefix="/enterprise", tags=["enterprise"], dependencies=[Depends(enforce_rate_limit)])


@router.get("/me", response_model=PrincipalResponse)
async def me(principal: EnterprisePrincipal = Depends(require_roles("moderator", "analyst", "auditor", "viewer", "system"))) -> PrincipalResponse:
    return PrincipalResponse(
        user_id=principal.user_id,
        email=principal.email,
        display_name=principal.display_name,
        role=principal.role,
        scopes=principal.scopes,
        api_key_id=principal.api_key_id,
    )


@router.post("/users", response_model=UserResponse)
async def create_user(
    payload: UserCreateRequest,
    request: Request,
    principal: EnterprisePrincipal = Depends(require_roles("admin")),
) -> UserResponse:
    service: EnterpriseService = get_enterprise_service(request)
    return await service.create_user(payload, principal=principal)


@router.get("/users", response_model=list[UserResponse])
async def list_users(request: Request, principal: EnterprisePrincipal = Depends(require_roles("auditor", "admin"))) -> list[UserResponse]:
    service: EnterpriseService = get_enterprise_service(request)
    return await service.list_users()


@router.post("/api-keys", response_model=ApiKeyResponse)
async def create_api_key(
    payload: ApiKeyCreateRequest,
    request: Request,
    principal: EnterprisePrincipal = Depends(require_roles("admin")),
) -> ApiKeyResponse:
    service: EnterpriseService = get_enterprise_service(request)
    return await service.issue_api_key(payload.user_id, payload.name, payload.scopes, principal=principal)


@router.get("/api-keys", response_model=list[ApiKeyResponse])
async def list_api_keys(request: Request, principal: EnterprisePrincipal = Depends(require_roles("auditor", "admin"))) -> list[ApiKeyResponse]:
    service: EnterpriseService = get_enterprise_service(request)
    return await service.list_api_keys()


@router.post("/retraining-jobs", response_model=RetrainingJobResponse)
async def create_retraining_job(
    payload: RetrainingJobCreateRequest,
    request: Request,
    principal: EnterprisePrincipal = Depends(require_roles("analyst", "admin")),
) -> RetrainingJobResponse:
    service: EnterpriseService = get_enterprise_service(request)
    return await service.create_retraining_job(payload, principal=principal)


@router.get("/retraining-jobs", response_model=list[RetrainingJobResponse])
async def list_retraining_jobs(request: Request, principal: EnterprisePrincipal = Depends(require_roles("analyst", "auditor", "admin"))) -> list[RetrainingJobResponse]:
    service: EnterpriseService = get_enterprise_service(request)
    return await service.list_retraining_jobs()


@router.get("/audit-logs", response_model=list[AuditLogResponse])
async def list_audit_logs(request: Request, principal: EnterprisePrincipal = Depends(require_roles("auditor", "admin"))) -> list[AuditLogResponse]:
    service: EnterpriseService = get_enterprise_service(request)
    return await service.list_audit_logs()


@router.get("/notifications", response_model=list[NotificationResponse])
async def list_notifications(request: Request, principal: EnterprisePrincipal = Depends(require_roles("auditor", "admin"))) -> list[NotificationResponse]:
    service: EnterpriseService = get_enterprise_service(request)
    return await service.list_notifications()
