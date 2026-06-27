"""Application settings loaded from environment variables.

Keeping configuration in one place makes the application easier to deploy,
test, and reason about in production.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "MultiShield AI"
    app_version: str = "1.0.0"
    environment: str = Field(default="development", validation_alias="APP_ENV")
    debug: bool = False
    enable_docs: bool = True
    api_v1_prefix: str = "/v1"
    log_level: str = "INFO"
    database_url: str = Field(
        default="sqlite+aiosqlite:///./multishield_ai.db",
        validation_alias="DATABASE_URL",
    )
    redis_url: str | None = Field(default=None, validation_alias="REDIS_URL")
    rate_limit_requests_per_minute: int = Field(default=120, validation_alias="RATE_LIMIT_REQUESTS_PER_MINUTE")
    enterprise_dashboard_days: int = Field(default=30, validation_alias="ENTERPRISE_DASHBOARD_DAYS")
    smtp_host: str | None = Field(default=None, validation_alias="SMTP_HOST")
    smtp_port: int = Field(default=587, validation_alias="SMTP_PORT")
    smtp_username: str | None = Field(default=None, validation_alias="SMTP_USERNAME")
    smtp_password: str | None = Field(default=None, validation_alias="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, validation_alias="SMTP_USE_TLS")
    notification_from_email: str | None = Field(default=None, validation_alias="NOTIFICATION_FROM_EMAIL")
    notification_recipients: List[str] = Field(default_factory=list, validation_alias="NOTIFICATION_RECIPIENTS")
    retraining_artifacts_dir: str = Field(default="./workspace/retraining", validation_alias="RETRAINING_ARTIFACTS_DIR")
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])
    request_timeout_seconds: int = 30


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance.

    The settings object is immutable for the life of the process, so caching it
    avoids repeated environment parsing.
    """

    return Settings()
