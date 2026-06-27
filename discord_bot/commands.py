"""Slash commands for moderator and administrator workflows."""

from __future__ import annotations

import discord
from discord import app_commands

from discord_bot.config import GuildConfig


multishield = app_commands.Group(name="multishield", description="MultiShield AI administration and moderation commands")


def _guild_config_summary(config: GuildConfig) -> str:
    return (
        f"Enabled: {config.enabled}\n"
        f"Warn threshold: {config.warn_threshold:.2f}\n"
        f"Delete threshold: {config.delete_threshold:.2f}\n"
        f"Mod log channel: {config.modlog_channel_id or 'unset'}\n"
        f"Moderator role: {config.moderator_role_id or 'unset'}"
    )


@multishield.command(name="scan", description="Scan a Discord message by link with MultiShield AI.")
@app_commands.describe(message_link="A Discord message link to scan")
async def scan_message(interaction: discord.Interaction, message_link: str) -> None:
    bot = interaction.client
    await interaction.response.defer(ephemeral=True, thinking=True)
    if not hasattr(bot, "scan_message_link"):
        await interaction.followup.send("The bot is not ready to scan messages.", ephemeral=True)
        return

    outcome = await bot.scan_message_link(message_link)
    await interaction.followup.send(outcome.moderator_summary, ephemeral=True)


@multishield.command(name="config_show", description="Show the current MultiShield AI configuration for this server.")
async def config_show(interaction: discord.Interaction) -> None:
    if interaction.guild is None:
        await interaction.response.send_message("This command only works in a server.", ephemeral=True)
        return

    bot = interaction.client
    config = await bot.guild_config_store.get(interaction.guild.id)
    embed = discord.Embed(title="MultiShield AI Configuration", description=_guild_config_summary(config), color=discord.Color.blue())
    await interaction.response.send_message(embed=embed, ephemeral=True)


@multishield.command(name="config_thresholds", description="Set the warning and delete thresholds for this server.")
@app_commands.checks.has_permissions(manage_guild=True)
async def config_thresholds(interaction: discord.Interaction, warn_threshold: float, delete_threshold: float) -> None:
    if interaction.guild is None:
        await interaction.response.send_message("This command only works in a server.", ephemeral=True)
        return

    if not 0.0 <= warn_threshold <= 1.0 or not 0.0 <= delete_threshold <= 1.0:
        await interaction.response.send_message("Thresholds must be between 0 and 1.", ephemeral=True)
        return

    if warn_threshold >= delete_threshold:
        await interaction.response.send_message("Warning threshold must be lower than delete threshold.", ephemeral=True)
        return

    bot = interaction.client
    config = await bot.guild_config_store.update(
        interaction.guild.id,
        warn_threshold=warn_threshold,
        delete_threshold=delete_threshold,
    )
    await interaction.response.send_message(
        f"Thresholds updated. Warn={config.warn_threshold:.2f}, Delete={config.delete_threshold:.2f}",
        ephemeral=True,
    )


@multishield.command(name="config_modlog", description="Set the moderator log channel for this server.")
@app_commands.checks.has_permissions(manage_guild=True)
async def config_modlog(interaction: discord.Interaction, channel: discord.TextChannel) -> None:
    if interaction.guild is None:
        await interaction.response.send_message("This command only works in a server.", ephemeral=True)
        return

    bot = interaction.client
    config = await bot.guild_config_store.update(interaction.guild.id, modlog_channel_id=channel.id)
    await interaction.response.send_message(
        f"Moderator log channel set to {channel.mention}.",
        ephemeral=True,
    )


@multishield.command(name="config_enable", description="Enable or disable moderation for this server.")
@app_commands.checks.has_permissions(manage_guild=True)
async def config_enable(interaction: discord.Interaction, enabled: bool) -> None:
    if interaction.guild is None:
        await interaction.response.send_message("This command only works in a server.", ephemeral=True)
        return

    bot = interaction.client
    config = await bot.guild_config_store.update(interaction.guild.id, enabled=enabled)
    await interaction.response.send_message(
        f"Moderation has been {'enabled' if config.enabled else 'disabled'} for this server.",
        ephemeral=True,
    )
