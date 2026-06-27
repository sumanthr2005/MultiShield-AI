"""Application entrypoint for the MultiShield AI backend.

The app is assembled through a composition root so the presentation layer
(`routes`) stays thin and the application service can be swapped or extended
without changing endpoint code.
"""

from __future__ import annotations

from fastapi import FastAPI
from redis.asyncio import Redis
from uuid import uuid4
from time import perf_counter

from backend.database.session import create_session_factory
from backend.routes.api import api_router
from backend.routes.health import router as health_router
from backend.services.analysis_service import AnalysisService
from backend.services.enterprise_service import EnterpriseService
from backend.utils.config import get_settings
from backend.utils.errors import register_exception_handlers
from backend.utils.logger import configure_logging
from prometheus_fastapi_instrumentator import Instrumentator


def create_app() -> FastAPI:
    """Build and configure the FastAPI application.

    The object returned here can be used by Uvicorn, tests, or any ASGI server.
    """

    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs" if settings.enable_docs else None,
        redoc_url="/redoc" if settings.enable_docs else None,
        openapi_url="/openapi.json" if settings.enable_docs else None,
    )

    session_factory = create_session_factory(settings.database_url)
    redis_client = Redis.from_url(settings.redis_url) if settings.redis_url else None
    app.state.settings = settings
    app.state.session_factory = session_factory
    app.state.redis = redis_client
    app.state.analysis_service = AnalysisService(settings=settings, session_factory=session_factory)
    app.state.enterprise_service = EnterpriseService(settings=settings, session_factory=session_factory, redis_client=redis_client)

    register_exception_handlers(app)
    Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

    @app.middleware("http")
    async def capture_usage(request, call_next):
        if request.url.path not in {"/health", "/live", "/ready", "/metrics", "/docs", "/redoc", "/openapi.json"}:
            await app.state.enterprise_service.enforce_rate_limit(request)
        request.state.request_id = str(uuid4())
        start = perf_counter()
        response = await call_next(request)
        duration_ms = int((perf_counter() - start) * 1000)
        if request.url.path not in {"/health", "/live", "/ready", "/metrics", "/docs", "/redoc", "/openapi.json"}:
            await app.state.enterprise_service.record_usage(request, response.status_code, duration_ms)
        return response

    app.include_router(health_router)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.on_event("shutdown")
    async def shutdown_clients() -> None:
        if app.state.redis is not None:
            await app.state.redis.aclose()

    return app


app = create_app()
