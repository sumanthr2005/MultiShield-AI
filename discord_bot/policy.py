"""Moderation policy and enforcement helpers."""

from __future__ import annotations

from dataclasses import dataclass

from discord_bot.config import GuildConfig
from discord_bot.models import EnforcementAction, MessageScanOutcome, WorkflowResponse


@dataclass(slots=True)
class EnforcementDecision:
    action: EnforcementAction
    reason: str
    risk_score: float
    confidence: float
    moderator_summary: str


class ModerationPolicy:
    """Map MultiShield decisions and guild thresholds to bot actions."""

    def decide(self, outcome: MessageScanOutcome, config: GuildConfig) -> EnforcementDecision:
        if outcome.errors:
            return EnforcementDecision(
                action="allow",
                reason="Analysis failed, so the bot fell back to allow and logged the error.",
                risk_score=0.0,
                confidence=0.0,
                moderator_summary=outcome.moderator_summary,
            )

        risk_score = outcome.risk_score
        confidence = outcome.confidence

        if risk_score >= config.delete_threshold or outcome.action == "delete":
            return EnforcementDecision(
                action="delete",
                reason="Risk exceeded the delete threshold.",
                risk_score=risk_score,
                confidence=confidence,
                moderator_summary=outcome.moderator_summary,
            )

        if risk_score >= config.warn_threshold or outcome.action == "warn":
            return EnforcementDecision(
                action="warn",
                reason="Risk exceeded the warning threshold.",
                risk_score=risk_score,
                confidence=confidence,
                moderator_summary=outcome.moderator_summary,
            )

        return EnforcementDecision(
            action="allow",
            reason="Risk remained below the warning threshold.",
            risk_score=risk_score,
            confidence=confidence,
            moderator_summary=outcome.moderator_summary,
        )

    def summarize(self, responses: list[WorkflowResponse]) -> MessageScanOutcome:
        if not responses:
            return MessageScanOutcome(
                action="allow",
                risk_score=0.0,
                confidence=0.0,
                explanation="No analyzable content was found.",
                moderator_summary="No text or supported image attachments were detected.",
                workflow_responses=[],
                errors=[],
            )

        fused = [response.fusion_result for response in responses if response.fusion_result is not None]
        moderation = [response.moderation_result for response in responses if response.moderation_result is not None]
        highest_risk = max((item.risk_score for item in fused), default=0.0)
        highest_confidence = max((item.confidence for item in fused), default=0.0)

        if any(item and item.action == "block" for item in moderation):
            action = "delete"
        elif any(item and item.action == "review" for item in moderation):
            action = "warn"
        else:
            action = "allow"

        explanation = fused[0].explanation if fused else "Content was analyzed by MultiShield AI."
        moderator_summary = "\n".join(
            [
                f"Workflow runs: {len(responses)}",
                f"Highest risk score: {highest_risk:.2f}",
                f"Highest confidence: {highest_confidence:.2f}",
                f"Decision: {action}",
            ]
        )

        return MessageScanOutcome(
            action=action,
            risk_score=highest_risk,
            confidence=highest_confidence,
            explanation=explanation,
            moderator_summary=moderator_summary,
            workflow_responses=responses,
            errors=[],
        )
