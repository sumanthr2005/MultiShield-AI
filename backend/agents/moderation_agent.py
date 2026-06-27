"""Moderation agent.

This is the operational policy layer. It transforms the fused model output into
an action that a platform can execute: allow, review, or block. The current
policy is intentionally simple and easy to audit.
"""

from __future__ import annotations

from backend.models.schemas import AnalysisResult, ModerationResponse


class ModerationAgent:
    name = "moderation"

    async def moderate(self, analysis_result: AnalysisResult) -> ModerationResponse:
        if analysis_result.decision == "block":
            return ModerationResponse(
                analysis_id=analysis_result.analysis_id,
                action="block",
                rationale="The fused risk score or a constituent modality crossed the hard block threshold.",
                recommended_reviewers=["trust_and_safety", "policy_ops"],
                metadata=analysis_result.metadata,
            )

        if analysis_result.decision == "review":
            return ModerationResponse(
                analysis_id=analysis_result.analysis_id,
                action="review",
                rationale="The fused result is elevated enough to require a human moderation pass.",
                recommended_reviewers=["human_moderator"],
                metadata=analysis_result.metadata,
            )

        return ModerationResponse(
            analysis_id=analysis_result.analysis_id,
            action="safe",
            rationale="The fused score remains below the intervention threshold.",
            recommended_reviewers=[],
            metadata=analysis_result.metadata,
        )
