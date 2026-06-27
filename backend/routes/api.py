"""Aggregate all versioned API routers."""

from __future__ import annotations

from fastapi import APIRouter

from backend.routes.analytics import router as analytics_router
from backend.routes.audio import router as audio_router
from backend.routes.enterprise import router as enterprise_router
from backend.routes.explainability import router as explainability_router
from backend.routes.fusion import router as fusion_router
from backend.routes.feedback import router as feedback_router
from backend.routes.image import router as image_router
from backend.routes.moderation import router as moderation_router
from backend.routes.workflow import router as workflow_router
from backend.routes.text import router as text_router

api_router = APIRouter()
api_router.include_router(text_router)
api_router.include_router(image_router)
api_router.include_router(audio_router)
api_router.include_router(fusion_router)
api_router.include_router(explainability_router)
api_router.include_router(moderation_router)
api_router.include_router(workflow_router)
api_router.include_router(feedback_router)
api_router.include_router(analytics_router)
api_router.include_router(enterprise_router)
