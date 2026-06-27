"""Persistent guild configuration storage."""

from __future__ import annotations

import asyncio
import json

from discord_bot.config import BotSettings, GuildConfig


class GuildConfigStore:
    """File-backed guild settings store.

    The bot only writes this file from admin commands, so a simple JSON store is
    enough and avoids introducing a separate database for runtime configuration.
    """

    def __init__(self, settings: BotSettings) -> None:
        self._settings = settings
        self._path = settings.guild_config_file
        self._lock = asyncio.Lock()
        self._path.parent.mkdir(parents=True, exist_ok=True)

    async def get(self, guild_id: int) -> GuildConfig:
        async with self._lock:
            data = await asyncio.to_thread(self._read_all)
            payload = data.get(str(guild_id))
            if payload is None:
                return GuildConfig(
                    guild_id=guild_id,
                    warn_threshold=self._settings.warn_threshold,
                    delete_threshold=self._settings.delete_threshold,
                    modlog_channel_id=self._settings.default_modlog_channel_id,
                )
            return GuildConfig(**payload)

    async def save(self, config: GuildConfig) -> GuildConfig:
        async with self._lock:
            data = await asyncio.to_thread(self._read_all)
            data[str(config.guild_id)] = config.model_dump()
            await asyncio.to_thread(self._write_all, data)
            return config

    async def update(self, guild_id: int, **updates) -> GuildConfig:
        current = await self.get(guild_id)
        payload = current.model_dump()
        payload.update(updates)
        config = GuildConfig(**payload)
        return await self.save(config)

    def _read_all(self) -> dict[str, dict]:
        if not self._path.exists():
            return {}
        return json.loads(self._path.read_text(encoding="utf-8"))

    def _write_all(self, data: dict[str, dict]) -> None:
        self._path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
