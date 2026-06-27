"""Image-specific detector.

The production architecture expects an image model or OCR/vision service here.
This implementation keeps the contract stable and uses image metadata plus any
OCR text supplied by the caller so the backend remains runnable during early
integration work.
"""

from __future__ import annotations

from uuid import uuid4

from backend.agents.base import DetectionAgent
from backend.models.schemas import AnalysisResult, DetectionEvidence, ImageAnalysisRequest


class ImageAgent(DetectionAgent):
    name = "image"

    async def analyze(self, payload: ImageAnalysisRequest) -> AnalysisResult:
        if payload.ocr_text:
            ocr_signal = payload.ocr_text.lower()
            marker_hits = sum(term in ocr_signal for term in ("abuse", "threat", "dehumanize", "harass"))
            risk_score = min(1.0, 0.2 + marker_hits * 0.2)
            explanation = "OCR text from the image contains potentially harmful language patterns." if marker_hits else "OCR text does not show strong risk patterns."
            confidence = 0.66
        else:
            risk_score = 0.18
            confidence = 0.45
            explanation = "No OCR text was provided, so the image score is conservative and metadata-driven."

        decision = "block" if risk_score >= 0.75 else "review" if risk_score >= 0.4 else "safe"

        return AnalysisResult(
            analysis_id=str(uuid4()),
            agent=self.name,
            label="image_hate_risk",
            risk_score=risk_score,
            confidence=confidence,
            decision=decision,
            explanation=explanation,
            evidence=[
                DetectionEvidence(
                    source="image",
                    snippet=payload.ocr_text[:240] if payload.ocr_text else payload.image_reference,
                    score=risk_score,
                )
            ],
            metadata={"image_reference": payload.image_reference, **payload.metadata},
        )
