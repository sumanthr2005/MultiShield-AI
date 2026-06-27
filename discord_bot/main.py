"""Discord bot entrypoint for MultiShield AI."""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import discord
from discord.ext import commands

from discord_bot.api_client import MultiShieldAPIClient, MultiShieldAPIError
from discord_bot.commands import multishield
from discord_bot.config import BotSettings, GuildConfig
from discord_bot.models import MessageMetadata, MessageScanOutcome, WorkflowResponse
from discord_bot.policy import EnforcementDecision, ModerationPolicy
from discord_bot.store import GuildConfigStore


logger = logging.getLogger("multishield.discord")

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff")
MESSAGE_LINK_RE = re.compile(r"https://(?:canary\.|ptb\.)?discord(?:app)?\.com/channels/(\d+|@me)/(\d+)/(\d+)")


@dataclass(slots=True)
class ScanContext:
    """Useful metadata about a message scan request."""

    message: discord.Message
    image_urls: list[str]


class MultiShieldBot(commands.Bot):
    """discord.py bot that sends server content to MultiShield AI."""

    def __init__(self, settings: BotSettings) -> None:
        intents = discord.Intents.default()
        intents.guilds = True
        intents.guild_messages = True
        intents.message_content = True
        intents.members = True

        super().__init__(command_prefix=commands.when_mentioned_or(settings.command_prefix), intents=intents)
        self.settings = settings
        self.api_client = MultiShieldAPIClient(settings)
        self.guild_config_store = GuildConfigStore(settings)
        self.policy = ModerationPolicy()

    async def setup_hook(self) -> None:
        self.tree.add_command(multishield)
        await self.tree.sync()
        logger.info("MultiShield slash commands synced")

    async def close(self) -> None:
        await self.api_client.close()
        await super().close()

    async def on_ready(self) -> None:
        logger.info("Logged in as %s (%s)", self.user, self.user.id if self.user else "unknown")

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or message.guild is None:
            return

        config = await self.guild_config_store.get(message.guild.id)
        if not config.enabled:
            return

        outcome = await self.review_message(message, config)
        decision = self.policy.decide(outcome, config)
        await self._enforce(message, decision, outcome, config)

    async def scan_message_link(self, message_link: str) -> MessageScanOutcome:
        match = MESSAGE_LINK_RE.search(message_link)
        if match is None:
            raise ValueError("Invalid Discord message link.")

        guild_id = int(match.group(1))
        channel_id = int(match.group(2))
        message_id = int(match.group(3))

        guild = self.get_guild(guild_id)
        if guild is None:
            raise ValueError("The bot is not in the target guild.")

        channel = guild.get_channel(channel_id)
        if channel is None or not isinstance(channel, discord.TextChannel):
            raise ValueError("The target channel is unavailable or not text-based.")

        message = await channel.fetch_message(message_id)
        config = await self.guild_config_store.get(guild_id)
        return await self.review_message(message, config)

    async def review_message(self, message: discord.Message, config: GuildConfig) -> MessageScanOutcome:
        text = message.content.strip() or None
        attachments = self._extract_image_attachments(message)
        metadata = self._build_metadata(message, attachments)

        if text is None and not attachments:
            return MessageScanOutcome(
                action="allow",
                risk_score=0.0,
                confidence=0.0,
                explanation="No analyzable text or supported image attachment was present.",
                moderator_summary="No analyzable text or supported image attachment was present.",
                workflow_responses=[],
                errors=[],
            )

        responses: list[WorkflowResponse] = []
        errors: list[str] = []

        try:
            if attachments:
                tasks = [
                    self.api_client.analyze_workflow(
                        text=text,
                        image_reference=image_url,
                        metadata={**metadata.model_dump(), "attachment_url": image_url},
                    )
                    for image_url in attachments
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, Exception):
                        errors.append(str(result))
                    else:
                        responses.append(result)
            else:
                responses.append(
                    await self.api_client.analyze_workflow(
                        text=text,
                        image_reference=None,
                        metadata=metadata.model_dump(),
                    )
                )
        except MultiShieldAPIError as exc:
            errors.append(str(exc))

        outcome = self.policy.summarize(responses)
        if errors:
            outcome.errors.extend(errors)
        return outcome

    async def _enforce(
        self,
        message: discord.Message,
        decision: EnforcementDecision,
        outcome: MessageScanOutcome,
        config: GuildConfig,
    ) -> None:
        if decision.action == "allow":
            if outcome.action != "allow":
                logger.info("message flagged but allowed", extra={"message_id": message.id, "guild_id": message.guild.id})
            return

        if decision.action == "delete":
            try:
                await message.delete()
                await self._dm_user(message.author, "Your message was removed by server moderation.", outcome)
            except discord.Forbidden:
                logger.warning("missing permissions to delete message", extra={"message_id": message.id})
                decision = EnforcementDecision(
                    action="warn",
                    reason="Delete failed due to missing permissions.",
                    risk_score=decision.risk_score,
                    confidence=decision.confidence,
                    moderator_summary=decision.moderator_summary,
                )
            except discord.HTTPException as exc:
                logger.exception("message deletion failed")
                await self._log_failure(message, f"Deletion failed: {exc}")
                return

        if decision.action == "warn":
            warning_text = (
                "This message was flagged by MultiShield AI. Please review the server rules and edit or remove the content."
            )
            try:
                await message.reply(warning_text, mention_author=False, allowed_mentions=discord.AllowedMentions.none())
            except discord.HTTPException:
                logger.warning("unable to post warning reply", extra={"message_id": message.id})

        await self._notify_moderators(message, outcome, config, decision)

    async def _notify_moderators(
        self,
        message: discord.Message,
        outcome: MessageScanOutcome,
        config: GuildConfig,
        decision: EnforcementDecision,
    ) -> None:
        channel = None
        if config.modlog_channel_id is not None:
            channel = message.guild.get_channel(config.modlog_channel_id)

        if channel is None and self.settings.default_modlog_channel_id is not None:
            channel = message.guild.get_channel(self.settings.default_modlog_channel_id)

        if channel is None or not isinstance(channel, discord.TextChannel):
            logger.info(
                "moderator notification skipped; no modlog channel configured",
                extra={"guild_id": message.guild.id, "message_id": message.id},
            )
            return

        embed = self._build_moderator_embed(message, outcome, decision)
        await channel.send(embed=embed)

    async def _dm_user(self, user: discord.abc.User, message_text: str, outcome: MessageScanOutcome) -> None:
        try:
            await user.send(f"{message_text}\n\nReason: {outcome.explanation}")
        except discord.HTTPException:
            logger.info("unable to DM user", extra={"user_id": user.id})

    async def _log_failure(self, message: discord.Message, error: str) -> None:
        logger.error("moderation failure: %s", error, extra={"guild_id": message.guild.id, "message_id": message.id})

    def _extract_image_attachments(self, message: discord.Message) -> list[str]:
        image_urls: list[str] = []
        for attachment in message.attachments:
            content_type = (attachment.content_type or "").lower()
            filename = attachment.filename.lower()
            if content_type.startswith("image/") or filename.endswith(IMAGE_EXTENSIONS):
                image_urls.append(attachment.url)
        return image_urls

    def _build_metadata(self, message: discord.Message, attachments: list[str]) -> MessageMetadata:
        return MessageMetadata(
            guild_id=message.guild.id,
            channel_id=message.channel.id,
            message_id=message.id,
            author_id=message.author.id,
            author_name=str(message.author),
            message_link=message.jump_url,
            attachment_urls=attachments,
            attachment_names=[attachment.filename for attachment in message.attachments if attachment.url in attachments],
        )

    def _build_moderator_embed(
        self,
        message: discord.Message,
        outcome: MessageScanOutcome,
        decision: EnforcementDecision,
    ) -> discord.Embed:
        embed = discord.Embed(
            title="MultiShield AI moderation alert",
            description=outcome.moderator_summary,
            color=discord.Color.red() if decision.action == "delete" else discord.Color.orange(),
        )
        embed.add_field(name="Guild", value=f"{message.guild.name} ({message.guild.id})", inline=False)
        embed.add_field(name="Channel", value=f"{message.channel.mention}", inline=True)
        embed.add_field(name="Author", value=f"{message.author} ({message.author.id})", inline=True)
        embed.add_field(name="Action", value=decision.action, inline=True)
        embed.add_field(name="Risk score", value=f"{decision.risk_score:.2f}", inline=True)
        embed.add_field(name="Confidence", value=f"{decision.confidence:.2f}", inline=True)
        embed.add_field(name="Explanation", value=outcome.explanation[:1024], inline=False)

        content_preview = message.content.strip() or "<no text content>"
        embed.add_field(name="Content preview", value=content_preview[:1024], inline=False)
        if message.attachments:
            embed.add_field(
                name="Attachments",
                value="\n".join(attachment.url for attachment in message.attachments)[:1024],
                inline=False,
            )
        embed.add_field(name="Message link", value=message.jump_url, inline=False)
        return embed


async def run() -> None:
    settings = BotSettings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    bot = MultiShieldBot(settings)
    async with bot:
        await bot.start(settings.discord_token)


if __name__ == "__main__":
    asyncio.run(run())
