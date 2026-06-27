"""Async client for the MultiShield AI FastAPI backend."""

from __future__ import annotations

from typing import Any

import httpx

from discord_bot.config import BotSettings
from discord_bot.models import WorkflowResponse


class MultiShieldAPIError(RuntimeError):
    """Raised when the FastAPI backend returns an error or an invalid response."""


class MultiShieldAPIClient:
    """Typed wrapper around the MultiShield AI endpoints."""

    def __init__(self, settings: BotSettings) -> None:
        self._settings = settings
        self._client = httpx.AsyncClient(
            base_url=settings.api_base_url.rstrip("/"),
            timeout=settings.api_timeout_seconds,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def analyze_workflow(
        self,
        *,
        text: str | None,
        image_reference: str | None,
        metadata: dict[str, Any],
        ocr_text: str | None = None,
    ) -> WorkflowResponse:
        payload: dict[str, Any] = {"metadata": metadata}
        if text:
            payload["text"] = text
        if image_reference:
            payload["image_reference"] = image_reference
        if ocr_text:
            payload["ocr_text"] = ocr_text

        response = await self._client.post("/v1/workflow/analyze", json=payload)
        if response.status_code >= 400:
            raise MultiShieldAPIError(f"MultiShield API error {response.status_code}: {response.text}")

        try:
            return WorkflowResponse.model_validate(response.json())
        except Exception as exc:  # pragma: no cover - defensive parsing boundary
            raise MultiShieldAPIError("Unable to parse MultiShield workflow response.") from exc
