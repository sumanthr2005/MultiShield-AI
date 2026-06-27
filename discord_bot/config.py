"""Runtime configuration for the Discord bot.

Environment variables are the primary deployment interface, while per-guild
settings are persisted to a local JSON file so administrators can tune the bot
without redeploying it.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Process-level settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    discord_token: str = Field(alias="DISCORD_TOKEN")
    api_base_url: str = Field(default="http://localhost:8000", alias="MULTISHIELD_API_BASE_URL")
    api_timeout_seconds: float = Field(default=60.0, alias="MULTISHIELD_API_TIMEOUT_SECONDS")
    warn_threshold: float = Field(default=0.45, alias="MULTISHIELD_WARN_THRESHOLD")
    delete_threshold: float = Field(default=0.75, alias="MULTISHIELD_DELETE_THRESHOLD")
    command_prefix: str = Field(default="!", alias="MULTISHIELD_COMMAND_PREFIX")
    default_modlog_channel_id: int | None = Field(default=None, alias="MULTISHIELD_MODLOG_CHANNEL_ID")
    data_dir: Path = Field(default=Path("data"), alias="MULTISHIELD_DATA_DIR")
    guild_config_file: Path = Field(default=Path("data/guild_config.json"), alias="MULTISHIELD_GUILD_CONFIG_FILE")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @field_validator("warn_threshold", "delete_threshold")
    @classmethod
    def _validate_threshold(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError("thresholds must be between 0 and 1")
        return value


class GuildConfig(BaseModel):
    """Per-guild moderation settings persisted by the bot."""

    guild_id: int
    enabled: bool = True
    warn_threshold: float = 0.45
    delete_threshold: float = 0.75
    modlog_channel_id: int | None = None
    moderator_role_id: int | None = None
    note: str | None = None
