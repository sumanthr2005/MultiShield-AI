"""Text-specific hate speech detector.

This implementation is intentionally lightweight and deterministic so the
service can run without a heavyweight model bundle. In production, the scoring
logic can be replaced with an embedding classifier or a fine-tuned transformer
without changing the API contract.
"""

from __future__ import annotations

from uuid import uuid4

from backend.agents.base import DetectionAgent
from backend.models.schemas import AnalysisResult, DetectionEvidence, TextAnalysisRequest


class TextAgent(DetectionAgent):
    name = "text"

    _risk_markers = ("abuse", "threat", "dehumanize", "harass")

    async def analyze(self, payload: TextAnalysisRequest) -> AnalysisResult:
        normalized_text = payload.text.lower()
        marker_hits = sum(1 for marker in self._risk_markers if marker in normalized_text)
        risk_score = min(1.0, 0.15 + marker_hits * 0.2)
        confidence = min(0.98, 0.55 + len(normalized_text.split()) * 0.01)

        if risk_score >= 0.75:
            decision = "block"
            explanation = "The text contains strong indicators of targeted abuse or harassment."
        elif risk_score >= 0.4:
            decision = "review"
            explanation = "The text contains some potentially harmful language patterns that should be reviewed."
        else:
            decision = "safe"
            explanation = "The text does not contain strong abuse or harassment indicators."

        return AnalysisResult(
            analysis_id=str(uuid4()),
            agent=self.name,
            label="text_hate_risk",
            risk_score=risk_score,
            confidence=confidence,
            decision=decision,
            explanation=explanation,
            evidence=[
                DetectionEvidence(
                    source="text",
                    snippet=payload.text[:240],
                    score=risk_score,
                )
            ],
            metadata={"language": payload.language, **payload.metadata},
        )
