"""Health check endpoints for orchestration and uptime probes."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from sqlalchemy import text

from backend.models.schemas import HealthResponse, ReadinessResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    settings = request.app.state.settings
    return HealthResponse(
        version=settings.app_version,
        environment=settings.environment,
    )


@router.get("/live", response_model=HealthResponse)
async def live(request: Request) -> HealthResponse:
    settings = request.app.state.settings
    return HealthResponse(
        version=settings.app_version,
        environment=settings.environment,
    )


@router.get("/ready", response_model=ReadinessResponse)
async def ready(request: Request) -> JSONResponse:
    settings = request.app.state.settings
    session_factory = request.app.state.session_factory

    database_status = "ok"
    redis_status = "not_configured"
    overall_status = "ok"
    status_code = 200

    try:
        async with session_factory() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        database_status = "down"
        overall_status = "degraded"
        status_code = 503

    if settings.redis_url:
        try:
            redis_client = Redis.from_url(settings.redis_url)
            await redis_client.ping()
            await redis_client.aclose()
            redis_status = "ok"
        except Exception:
            redis_status = "down"
            overall_status = "degraded"
            status_code = 503

    payload = ReadinessResponse(
        status=overall_status,
        version=settings.app_version,
        environment=settings.environment,
        database=database_status,
        redis=redis_status,
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump(mode="json"))
