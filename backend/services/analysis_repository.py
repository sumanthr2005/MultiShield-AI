"""Persistence layer for analyses and moderation outcomes."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.database.models import AnalysisRecord, AuditLog, ModerationActionRecord
from backend.models.schemas import AnalysisResult, ModerationResponse


class AnalysisRepository:
    """Repository that isolates the ORM from the application service."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def save_analysis(self, analysis_result: AnalysisResult, input_payload: dict) -> AnalysisRecord:
        async with self.session_factory() as session:
            record = AnalysisRecord(
                id=analysis_result.analysis_id,
                agent=analysis_result.agent,
                modality=analysis_result.agent,
                input_payload=input_payload,
                output_payload=analysis_result.model_dump(mode="json"),
                risk_score=analysis_result.risk_score,
                decision=analysis_result.decision,
                explanation=analysis_result.explanation,
            )
            session.add(record)
            session.add(
                AuditLog(
                    event_type="analysis_saved",
                    action="create",
                    resource_type="analysis_record",
                    resource_id=analysis_result.analysis_id,
                    payload={"analysis_id": analysis_result.analysis_id, "agent": analysis_result.agent},
                )
            )
            await session.commit()
            await session.refresh(record)
            return record

    async def save_moderation(self, moderation_response: ModerationResponse) -> ModerationActionRecord:
        async with self.session_factory() as session:
            record = ModerationActionRecord(
                analysis_id=moderation_response.analysis_id,
                action=moderation_response.action,
                rationale=moderation_response.rationale,
                reviewer_group=",".join(moderation_response.recommended_reviewers) if moderation_response.recommended_reviewers else None,
            )
            session.add(record)
            session.add(
                AuditLog(
                    event_type="moderation_saved",
                    action="create",
                    resource_type="moderation_action",
                    resource_id=moderation_response.analysis_id,
                    payload={"analysis_id": moderation_response.analysis_id, "action": moderation_response.action},
                )
            )
            await session.commit()
            await session.refresh(record)
            return record
