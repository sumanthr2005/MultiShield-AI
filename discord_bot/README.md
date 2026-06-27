# MultiShield AI Discord Bot

This bot monitors guild messages, sends text and image payloads to the MultiShield AI FastAPI backend, and deletes or warns based on the moderation decision and guild thresholds.

## Features

- `discord.py` slash commands and message listeners
- Automatic analysis of text messages and image attachments
- Async API integration with `POST /v1/workflow/analyze`
- Per-guild configurable thresholds and mod-log channels
- Moderator explanation embeds with workflow output
- Logging and environment-based configuration

## Setup

1. Copy `.env.example` to `.env` and fill in the Discord token plus the MultiShield API URL.
2. Install dependencies:

```bash
python -m pip install -r discord_bot/requirements.txt
```

3. Start the FastAPI backend first so the Discord bot can reach `POST /v1/workflow/analyze`.
4. Run the bot:

```bash
python -m discord_bot.main
```

## Discord Permissions

Enable the following in the Discord Developer Portal:

- `MESSAGE CONTENT INTENT`
- Server message access
- Manage Messages permission for deletion actions

## Slash Commands

- `/multishield scan message_link:<link>` scans a specific message manually.
- `/multishield config_show` shows the current guild configuration.
- `/multishield config_thresholds warn_threshold:<value> delete_threshold:<value>` updates thresholds.
- `/multishield config_modlog channel:<channel>` sets the moderator log channel.
- `/multishield config_enable enabled:<true|false>` enables or disables moderation for the guild.

## Deployment

### Local

```bash
cd discord_bot
python -m discord_bot.main
```

### Docker

```bash
docker build -t multishield-discord-bot ./discord_bot
docker run --env-file ./discord_bot/.env multishield-discord-bot
```

### Production Notes

- Run the FastAPI backend before the bot.
- Mount a persistent volume for `data/guild_config.json` so admin settings survive restarts.
- Ensure the bot has permission to read messages, delete messages, and send embeds in the mod-log channel.
