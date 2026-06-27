"""Common contract for all agents.

Each agent focuses on one modality or one operational concern so the platform
can evolve independently across text, image, audio, fusion, explainability,
and moderation concerns.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.models.schemas import AnalysisResult


class BaseAgent(ABC):
    """Abstract base for all detection and governance agents."""

    name: str

    @abstractmethod
    async def analyze(self, payload):  # pragma: no cover - interface definition
        """Analyze a payload and return a structured result."""


class DetectionAgent(BaseAgent):
    """Marker class for agents that produce an AnalysisResult."""

    @abstractmethod
    async def analyze(self, payload) -> AnalysisResult:  # pragma: no cover - interface definition
        """Analyze a payload and return a structured result."""
