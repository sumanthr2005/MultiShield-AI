"""Fusion agent that combines modality-specific signals.

The fusion stage is the policy layer that turns individual modality scores into
a single platform decision. It is intentionally conservative: a single strong
signal can elevate the final action to review or block.
"""

from __future__ import annotations

from uuid import uuid4

from backend.agents.base import DetectionAgent
from backend.models.schemas import AnalysisResult, DetectionEvidence


class FusionAgent(DetectionAgent):
    name = "fusion"

    async def analyze(self, payload: list[AnalysisResult]) -> AnalysisResult:
        if not payload:
            return AnalysisResult(
                analysis_id=str(uuid4()),
                agent=self.name,
                label="fusion_hate_risk",
                risk_score=0.0,
                confidence=0.0,
                decision="safe",
                explanation="No modality results were supplied to the fusion stage.",
            )

        total_weight = 0.0
        weighted_score = 0.0
        confidence_total = 0.0
        evidence: list[DetectionEvidence] = []
        modality_labels: list[str] = []

        for result in payload:
            weight = max(result.confidence, 0.1)
            total_weight += weight
            weighted_score += result.risk_score * weight
            confidence_total += result.confidence
            modality_labels.append(result.agent)
            evidence.extend(result.evidence)

        fused_score = weighted_score / total_weight if total_weight else 0.0
        fused_confidence = min(0.99, confidence_total / len(payload))

        if any(result.decision == "block" for result in payload) or fused_score >= 0.75:
            decision = "block"
            explanation = "At least one modality exceeded the high-risk threshold, so the fused decision is block."
        elif fused_score >= 0.4:
            decision = "review"
            explanation = "The combined modality signals are elevated enough to warrant human review."
        else:
            decision = "safe"
            explanation = "The combined modality signals remain below the review threshold."

        return AnalysisResult(
            analysis_id=str(uuid4()),
            agent=self.name,
            label="fusion_hate_risk",
            risk_score=fused_score,
            confidence=fused_confidence,
            decision=decision,
            explanation=explanation,
            evidence=evidence,
            metadata={"fused_modalities": modality_labels},
        )
