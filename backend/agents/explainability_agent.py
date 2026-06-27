"""Explainability agent.

This layer translates machine-readable scores into human-readable reasoning so
moderators, auditors, and downstream systems can understand why a decision was
made.
"""

from __future__ import annotations

from backend.models.schemas import AnalysisResult, ExplainabilityResponse


class ExplainabilityAgent:
    name = "explainability"

    async def explain(self, analysis_result: AnalysisResult) -> ExplainabilityResponse:
        contributing_factors = [
            f"Agent {analysis_result.agent} produced a risk score of {analysis_result.risk_score:.2f}.",
            f"Decision path resolved to {analysis_result.decision} with confidence {analysis_result.confidence:.2f}.",
        ]

        if analysis_result.evidence:
            contributing_factors.append(
                f"Evidence count: {len(analysis_result.evidence)} with the strongest source scored at {max(item.score for item in analysis_result.evidence):.2f}."
            )

        return ExplainabilityResponse(
            analysis_id=analysis_result.analysis_id,
            explanation=analysis_result.explanation,
            contributing_factors=contributing_factors,
            recommended_next_steps=[
                "Send the item to a human moderator if the action is review or block.",
                "Persist the result for auditability and model performance monitoring.",
            ],
            metadata=analysis_result.metadata,
        )
