"""Audio-specific detector.

Audio analysis normally depends on speech-to-text and prosody features. The
contract below lets the platform ingest either a transcript or a reference to
audio that will be processed by an upstream ASR/feature service.
"""

from __future__ import annotations

from uuid import uuid4

from backend.agents.base import DetectionAgent
from backend.models.schemas import AnalysisResult, DetectionEvidence, AudioAnalysisRequest


class AudioAgent(DetectionAgent):
    name = "audio"

    async def analyze(self, payload: AudioAnalysisRequest) -> AnalysisResult:
        if payload.transcript:
            transcript = payload.transcript.lower()
            marker_hits = sum(term in transcript for term in ("abuse", "threat", "dehumanize", "harass"))
            risk_score = min(1.0, 0.22 + marker_hits * 0.22)
            explanation = "The transcript includes patterns that suggest abusive or threatening content." if marker_hits else "The transcript does not contain strong risk patterns."
            confidence = 0.68
        else:
            risk_score = 0.2
            confidence = 0.42
            explanation = "No transcript was supplied, so the audio score is conservative and metadata-driven."

        decision = "block" if risk_score >= 0.75 else "review" if risk_score >= 0.4 else "safe"

        return AnalysisResult(
            analysis_id=str(uuid4()),
            agent=self.name,
            label="audio_hate_risk",
            risk_score=risk_score,
            confidence=confidence,
            decision=decision,
            explanation=explanation,
            evidence=[
                DetectionEvidence(
                    source="audio",
                    snippet=payload.transcript[:240] if payload.transcript else payload.audio_reference,
                    score=risk_score,
                )
            ],
            metadata={"audio_reference": payload.audio_reference, **payload.metadata},
        )
