"""Authentication, authorization, and rate limit dependencies."""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, Header, Request

from backend.services.enterprise_service import EnterprisePrincipal, EnterpriseService
from backend.utils.errors import AppError


def get_enterprise_service(request: Request) -> EnterpriseService:
    return request.app.state.enterprise_service


async def get_optional_principal(
    request: Request,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> EnterprisePrincipal | None:
    if not x_api_key:
        return None

    service = get_enterprise_service(request)
    principal = await service.authenticate_api_key(x_api_key)
    request.state.principal = principal
    return principal


async def get_current_principal(
    request: Request,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> EnterprisePrincipal:
    if not x_api_key:
        raise AppError("API key required.", status_code=401, code="authentication_required")

    service = get_enterprise_service(request)
    principal = await service.authenticate_api_key(x_api_key)
    request.state.principal = principal
    return principal


def require_roles(*roles: str) -> Callable[..., EnterprisePrincipal]:
    async def _dependency(principal: EnterprisePrincipal = Depends(get_current_principal)) -> EnterprisePrincipal:
        if principal.role not in roles and principal.role != "admin":
            raise AppError("Insufficient permissions.", status_code=403, code="forbidden")
        return principal

    return _dependency


async def enforce_rate_limit(request: Request) -> None:
    service = get_enterprise_service(request)
    await service.enforce_rate_limit(request)
