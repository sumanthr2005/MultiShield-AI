"""Enterprise controls for MultiShield AI.

This module centralizes identity, RBAC, audit logging, usage metrics,
notifications, human feedback, and retraining orchestration so the API layer
remains thin.
"""

from __future__ import annotations

import hashlib
import json
import smtplib
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from email.message import EmailMessage
from pathlib import Path
from secrets import token_urlsafe
from typing import Any

from fastapi import Request
from redis.asyncio import Redis
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.database.models import (
    AnalysisRecord,
    ApiKey,
    AuditLog,
    FeedbackRecord,
    NotificationLog,
    RetrainingJob,
    UsageMetric,
    UserAccount,
)
from backend.models.schemas import (
    AnalyticsSummaryResponse,
    ApiKeyResponse,
    AuditLogResponse,
    FeedbackCreateRequest,
    FeedbackResponse,
    NotificationResponse,
    PrincipalResponse,
    RetrainingJobCreateRequest,
    RetrainingJobResponse,
    UserCreateRequest,
    UserResponse,
)
from backend.utils.config import Settings
from backend.utils.errors import AppError


@dataclass(slots=True)
class EnterprisePrincipal:
    user_id: str
    email: str
    display_name: str
    role: str
    scopes: list[str]
    api_key_id: str


def _hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def _now() -> datetime:
    return datetime.now(tz=UTC)


class EnterpriseService:
    """Coordinate enterprise features on top of the core application data."""

    def __init__(self, settings: Settings, session_factory: async_sessionmaker[AsyncSession], redis_client: Redis | None = None) -> None:
        self.settings = settings
        self.session_factory = session_factory
        self.redis_client = redis_client
        self._fallback_rate_limits: dict[str, tuple[int, float]] = {}

    async def authenticate_api_key(self, api_key: str) -> EnterprisePrincipal:
        key_hash = _hash_api_key(api_key.strip())

        async with self.session_factory() as session:
            statement = (
                select(ApiKey, UserAccount)
                .join(UserAccount, UserAccount.id == ApiKey.user_id)
                .where(ApiKey.key_hash == key_hash)
                .where(ApiKey.is_active.is_(True))
                .where(UserAccount.is_active.is_(True))
            )
            result = await session.execute(statement)
            row = result.first()
            if row is None:
                raise AppError("Invalid API key.", status_code=401, code="authentication_failed")

            api_key_row, user_row = row
            if api_key_row.expires_at and api_key_row.expires_at < _now():
                raise AppError("API key has expired.", status_code=401, code="authentication_failed")

            api_key_row.last_used_at = _now()
            await self.record_audit(
                session,
                event_type="authentication",
                action="authenticate",
                actor_id=user_row.id,
                actor_role=user_row.role,
                resource_type="api_key",
                resource_id=api_key_row.id,
                payload={"email": user_row.email, "scopes": api_key_row.scopes},
            )
            await session.commit()

            return EnterprisePrincipal(
                user_id=user_row.id,
                email=user_row.email,
                display_name=user_row.display_name,
                role=user_row.role,
                scopes=list(api_key_row.scopes or []),
                api_key_id=api_key_row.id,
            )

    async def ensure_user(self, session: AsyncSession, payload: UserCreateRequest) -> UserAccount:
        existing = await session.execute(select(UserAccount).where(UserAccount.email == payload.email))
        user = existing.scalar_one_or_none()
        if user is not None:
            raise AppError("User already exists.", status_code=409, code="conflict")

        user = UserAccount(email=payload.email, display_name=payload.display_name, role=payload.role)
        session.add(user)
        await session.flush()
        return user

    async def create_user(self, payload: UserCreateRequest, principal: EnterprisePrincipal | None = None) -> UserResponse:
        async with self.session_factory() as session:
            user = await self.ensure_user(session, payload)
            await self.record_audit(
                session,
                event_type="user_created",
                action="create",
                actor_id=principal.user_id if principal else None,
                actor_role=principal.role if principal else None,
                resource_type="user_account",
                resource_id=user.id,
                payload={"email": user.email, "role": user.role},
            )
            await session.commit()
            return self._user_to_response(user)

    async def list_users(self) -> list[UserResponse]:
        async with self.session_factory() as session:
            result = await session.execute(select(UserAccount).order_by(UserAccount.created_at.desc()))
            return [self._user_to_response(user) for user in result.scalars().all()]

    async def issue_api_key(self, user_id: str, name: str, scopes: list[str], principal: EnterprisePrincipal | None = None) -> ApiKeyResponse:
        plaintext_key = f"msk_{token_urlsafe(6)}_{token_urlsafe(32)}"
        key_hash = _hash_api_key(plaintext_key)
        key_prefix = plaintext_key[:12]

        async with self.session_factory() as session:
            user = await session.get(UserAccount, user_id)
            if user is None:
                raise AppError("User not found.", status_code=404, code="not_found")

            api_key = ApiKey(
                user_id=user_id,
                name=name,
                key_prefix=key_prefix,
                key_hash=key_hash,
                scopes=scopes,
            )
            session.add(api_key)
            await session.flush()
            await self.record_audit(
                session,
                event_type="api_key_issued",
                action="create",
                actor_id=principal.user_id if principal else None,
                actor_role=principal.role if principal else None,
                resource_type="api_key",
                resource_id=api_key.id,
                payload={"user_id": user_id, "name": name, "scopes": scopes},
            )
            await session.commit()
            await session.refresh(api_key)
            return self._api_key_to_response(api_key, plaintext_key)

    async def list_api_keys(self) -> list[ApiKeyResponse]:
        async with self.session_factory() as session:
            result = await session.execute(select(ApiKey).order_by(ApiKey.created_at.desc()))
            return [self._api_key_to_response(api_key) for api_key in result.scalars().all()]

    async def submit_feedback(self, payload: FeedbackCreateRequest, principal: EnterprisePrincipal | None = None) -> FeedbackResponse:
        active_learning_bucket = self._bucket_feedback(payload)
        async with self.session_factory() as session:
            feedback = FeedbackRecord(
                analysis_id=payload.analysis_id,
                submitted_by_user_id=principal.user_id if principal else None,
                label=payload.label,
                comment=payload.comment,
                confidence_rating=payload.confidence_rating,
                is_actionable=payload.is_actionable,
                status=payload.status,
                active_learning_bucket=active_learning_bucket,
            )
            session.add(feedback)
            await self.record_audit(
                session,
                event_type="feedback_submitted",
                action="create",
                actor_id=principal.user_id if principal else None,
                actor_role=principal.role if principal else None,
                resource_type="feedback_record",
                resource_id=feedback.id,
                payload=payload.model_dump(),
            )
            await self._emit_notifications(
                session,
                subject=f"New feedback received for analysis {payload.analysis_id}",
                body=json.dumps(payload.model_dump(), default=str, indent=2),
                details={"analysis_id": payload.analysis_id, "status": payload.status},
            )
            await session.commit()
            await session.refresh(feedback)
            return self._feedback_to_response(feedback)

    async def list_feedback(self) -> list[FeedbackResponse]:
        async with self.session_factory() as session:
            result = await session.execute(select(FeedbackRecord).order_by(FeedbackRecord.created_at.desc()))
            return [self._feedback_to_response(item) for item in result.scalars().all()]

    async def create_retraining_job(self, payload: RetrainingJobCreateRequest, principal: EnterprisePrincipal | None = None) -> RetrainingJobResponse:
        window_start = _now() - timedelta(days=payload.source_window_days)
        async with self.session_factory() as session:
            feedback_result = await session.execute(
                select(FeedbackRecord)
                .where(FeedbackRecord.created_at >= window_start)
                .where(FeedbackRecord.is_actionable.is_(True))
                .order_by(FeedbackRecord.created_at.desc())
            )
            feedback_items = feedback_result.scalars().all()

            job = RetrainingJob(
                name=payload.name,
                status="completed",
                triggered_by_user_id=principal.user_id if principal else None,
                source_window_days=payload.source_window_days,
                source_snapshot={"feedback_count": len(feedback_items), "window_start": window_start.isoformat()},
                notes=payload.notes,
                model_version=f"candidate-{_now().strftime('%Y%m%d%H%M%S')}",
            )
            session.add(job)
            await session.flush()

            artifacts_dir = Path(self.settings.retraining_artifacts_dir)
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            dataset_path = artifacts_dir / f"{job.id}.jsonl"
            dataset_rows = [
                {
                    "analysis_id": item.analysis_id,
                    "label": item.label,
                    "comment": item.comment,
                    "confidence_rating": item.confidence_rating,
                    "is_actionable": item.is_actionable,
                    "status": item.status,
                    "created_at": item.created_at.isoformat() if item.created_at else None,
                }
                for item in feedback_items
            ]
            dataset_path.write_text("\n".join(json.dumps(row, default=str) for row in dataset_rows), encoding="utf-8")

            job.dataset_path = str(dataset_path)
            job.metrics = {"exported_examples": len(dataset_rows)}

            await self.record_audit(
                session,
                event_type="retraining_job_created",
                action="create",
                actor_id=principal.user_id if principal else None,
                actor_role=principal.role if principal else None,
                resource_type="retraining_job",
                resource_id=job.id,
                payload={"name": payload.name, "window_days": payload.source_window_days, "exported_examples": len(dataset_rows)},
            )
            await self._emit_notifications(
                session,
                subject=f"Retraining job prepared: {payload.name}",
                body=json.dumps({"job_id": job.id, "exported_examples": len(dataset_rows)}, indent=2),
                details={"job_id": job.id, "dataset_path": str(dataset_path)},
            )
            await session.commit()
            await session.refresh(job)
            return self._retraining_job_to_response(job)

    async def list_retraining_jobs(self) -> list[RetrainingJobResponse]:
        async with self.session_factory() as session:
            result = await session.execute(select(RetrainingJob).order_by(RetrainingJob.created_at.desc()))
            return [self._retraining_job_to_response(item) for item in result.scalars().all()]

    async def list_audit_logs(self) -> list[AuditLogResponse]:
        async with self.session_factory() as session:
            result = await session.execute(select(AuditLog).order_by(AuditLog.created_at.desc()))
            return [self._audit_to_response(item) for item in result.scalars().all()]

    async def list_notifications(self) -> list[NotificationResponse]:
        async with self.session_factory() as session:
            result = await session.execute(select(NotificationLog).order_by(NotificationLog.created_at.desc()))
            return [self._notification_to_response(item) for item in result.scalars().all()]

    async def analytics_summary(self, window_days: int | None = None) -> AnalyticsSummaryResponse:
        window_days = window_days or self.settings.enterprise_dashboard_days
        cutoff = _now() - timedelta(days=window_days)

        async with self.session_factory() as session:
            total_analyses = await session.scalar(select(func.count()).select_from(AnalysisRecord).where(AnalysisRecord.created_at >= cutoff)) or 0
            total_feedback = await session.scalar(select(func.count()).select_from(FeedbackRecord).where(FeedbackRecord.created_at >= cutoff)) or 0
            active_feedback = await session.scalar(
                select(func.count()).select_from(FeedbackRecord).where(FeedbackRecord.created_at >= cutoff).where(FeedbackRecord.is_actionable.is_(True))
            ) or 0
            total_users = await session.scalar(select(func.count()).select_from(UserAccount)) or 0
            total_api_keys = await session.scalar(select(func.count()).select_from(ApiKey)) or 0
            total_retraining_jobs = await session.scalar(select(func.count()).select_from(RetrainingJob).where(RetrainingJob.created_at >= cutoff)) or 0
            open_retraining_jobs = await session.scalar(
                select(func.count()).select_from(RetrainingJob).where(RetrainingJob.created_at >= cutoff).where(RetrainingJob.status != "completed")
            ) or 0

            decision_rows = await session.execute(
                select(AnalysisRecord.decision, func.count()).where(AnalysisRecord.created_at >= cutoff).group_by(AnalysisRecord.decision)
            )
            role_rows = await session.execute(select(UserAccount.role, func.count()).group_by(UserAccount.role))
            feedback_rows = await session.execute(select(FeedbackRecord.status, func.count()).where(FeedbackRecord.created_at >= cutoff).group_by(FeedbackRecord.status))
            usage_rows = await session.execute(
                select(UsageMetric.route, func.count())
                .where(UsageMetric.created_at >= cutoff)
                .group_by(UsageMetric.route)
                .order_by(desc(func.count()))
            )

            return AnalyticsSummaryResponse(
                window_days=window_days,
                total_analyses=int(total_analyses),
                total_feedback=int(total_feedback),
                active_feedback=int(active_feedback),
                total_users=int(total_users),
                total_api_keys=int(total_api_keys),
                total_retraining_jobs=int(total_retraining_jobs),
                open_retraining_jobs=int(open_retraining_jobs),
                decision_breakdown={decision: int(count) for decision, count in decision_rows.all()},
                role_breakdown={role: int(count) for role, count in role_rows.all()},
                feedback_breakdown={status: int(count) for status, count in feedback_rows.all()},
                usage_by_route={route: int(count) for route, count in usage_rows.all()},
            )

    async def record_usage(self, request: Request, status_code: int, duration_ms: int) -> None:
        request_id = getattr(request.state, "request_id", token_urlsafe(16))
        principal: EnterprisePrincipal | None = getattr(request.state, "principal", None)
        route = request.url.path
        metric = UsageMetric(
            request_id=request_id,
            principal_id=principal.user_id if principal else None,
            principal_role=principal.role if principal else None,
            route=route,
            method=request.method,
            status_code=status_code,
            duration_ms=duration_ms,
        )

        async with self.session_factory() as session:
            session.add(metric)
            await session.commit()

    async def enforce_rate_limit(self, request: Request) -> None:
        route = request.url.path
        identity = request.headers.get("X-API-Key") or (request.client.host if request.client else "anonymous")
        window = int(time.time() // 60)
        key = f"rate:{identity}:{route}:{window}"

        if self.redis_client is not None:
            count = await self.redis_client.incr(key)
            if count == 1:
                await self.redis_client.expire(key, 70)
        else:
            count, expiry = self._fallback_rate_limits.get(key, (0, time.time() + 70))
            if expiry < time.time():
                count = 0
                expiry = time.time() + 70
            count += 1
            self._fallback_rate_limits[key] = (count, expiry)

        if count > self.settings.rate_limit_requests_per_minute:
            raise AppError("Rate limit exceeded.", status_code=429, code="rate_limited")

    async def record_audit(
        self,
        session: AsyncSession,
        *,
        event_type: str,
        payload: dict[str, Any],
        action: str | None = None,
        actor_id: str | None = None,
        actor_role: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        request_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        session.add(
            AuditLog(
                event_type=event_type,
                action=action,
                actor_id=actor_id,
                actor_role=actor_role,
                resource_type=resource_type,
                resource_id=resource_id,
                request_id=request_id,
                ip_address=ip_address,
                user_agent=user_agent,
                payload=payload,
            )
        )

    async def _emit_notifications(self, session: AsyncSession, subject: str, body: str, details: dict[str, Any]) -> None:
        recipients = self.settings.notification_recipients
        if not recipients and not self.settings.smtp_host:
            session.add(
                NotificationLog(
                    recipient=None,
                    channel="email",
                    subject=subject,
                    body=body,
                    delivery_status="queued",
                    details=details,
                )
            )
            return

        for recipient in recipients or [self.settings.notification_from_email or "ops@example.com"]:
            notification = NotificationLog(
                recipient=recipient,
                channel="email",
                subject=subject,
                body=body,
                delivery_status="queued",
                details=details,
            )
            session.add(notification)
            await session.flush()

            if not self.settings.smtp_host:
                continue

            try:
                await self._send_email(recipient, subject, body)
                notification.delivery_status = "sent"
                notification.sent_at = _now()
            except Exception as exc:  # pragma: no cover - best effort notification delivery
                notification.delivery_status = "failed"
                notification.delivery_error = str(exc)

    async def _send_email(self, recipient: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.settings.notification_from_email or self.settings.smtp_username or "noreply@localhost"
        message["To"] = recipient
        message.set_content(body)

        def _send() -> None:
            with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=10) as smtp:
                if self.settings.smtp_use_tls:
                    smtp.starttls()
                if self.settings.smtp_username and self.settings.smtp_password:
                    smtp.login(self.settings.smtp_username, self.settings.smtp_password)
                smtp.send_message(message)

        import asyncio

        await asyncio.to_thread(_send)

    @staticmethod
    def _bucket_feedback(payload: FeedbackCreateRequest) -> str:
        if payload.confidence_rating is None:
            return "unknown"
        if payload.confidence_rating < 0.4:
            return "low_confidence"
        if payload.confidence_rating < 0.75:
            return "medium_confidence"
        return "high_confidence"

    @staticmethod
    def _user_to_response(user: UserAccount) -> UserResponse:
        return UserResponse(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            role=user.role,
            is_active=bool(user.is_active),
            created_at=user.created_at,
        )

    @staticmethod
    def _api_key_to_response(api_key: ApiKey, plaintext_key: str | None = None) -> ApiKeyResponse:
        return ApiKeyResponse(
            id=api_key.id,
            user_id=api_key.user_id,
            name=api_key.name,
            key_prefix=api_key.key_prefix,
            scopes=list(api_key.scopes or []),
            is_active=bool(api_key.is_active),
            expires_at=api_key.expires_at,
            created_at=api_key.created_at,
            plaintext_key=plaintext_key,
        )

    @staticmethod
    def _feedback_to_response(item: FeedbackRecord) -> FeedbackResponse:
        return FeedbackResponse(
            id=item.id,
            analysis_id=item.analysis_id,
            label=item.label,
            comment=item.comment,
            confidence_rating=item.confidence_rating,
            is_actionable=bool(item.is_actionable),
            status=item.status,
            created_at=item.created_at,
        )

    @staticmethod
    def _retraining_job_to_response(job: RetrainingJob) -> RetrainingJobResponse:
        return RetrainingJobResponse(
            id=job.id,
            name=job.name,
            status=job.status,
            dataset_path=job.dataset_path,
            model_version=job.model_version,
            notes=job.notes,
            created_at=job.created_at,
            completed_at=job.completed_at,
        )

    @staticmethod
    def _notification_to_response(item: NotificationLog) -> NotificationResponse:
        return NotificationResponse(
            id=item.id,
            recipient=item.recipient,
            channel=item.channel,
            subject=item.subject,
            delivery_status=item.delivery_status,
            created_at=item.created_at,
        )

    @staticmethod
    def _audit_to_response(item: AuditLog) -> AuditLogResponse:
        return AuditLogResponse(
            id=item.id,
            event_type=item.event_type,
            action=item.action,
            actor_id=item.actor_id,
            actor_role=item.actor_role,
            resource_type=item.resource_type,
            resource_id=item.resource_id,
            request_id=item.request_id,
            ip_address=item.ip_address,
            payload=item.payload,
            created_at=item.created_at,
        )
