"""
# Drekord Discord API Wrapper
Async Discord REST API wrapper.

Drekord is not a bot framework. It is a pure API client designed to be
integrated into any async application that needs to interact with the
Discord REST API — read messages, send messages, manage channels, etc.

v2.0 uses a discord.py-inspired API where you work with live objects::

    import drekord

    async with drekord.Client(token="your_token") as client:
        # Fetch and use channels directly
        channel = await client.fetch_channel(channel_id)
        await channel.send("Hello, world!")

        # Fetch messages and interact with them
        message = await channel.fetch_message(msg_id)
        await message.edit(content="Edited!")
        await message.delete(reason="Cleanup")

        # Work with users
        user = await client.fetch_user(user_id)
        print(user.display_name)

        # Work with guilds
        guild = await client.fetch_guild(guild_id)
        members = await guild.fetch_members(limit=100)
        channels = await guild.fetch_channels()
"""

__version__ = "2.0.0"
__author__ = "drek124"

from .client import Client
from .exceptions import (
    DrekordError,
    HTTPError,
    RateLimitedError,
    ForbiddenError,
    NotFoundError,
    BadRequestError,
    UnauthorizedError,
    DiscordServerError,
)
from .models import (
    User,
    Member,
    Guild,
    Channel,
    Message,
    Role,
    Emoji,
    Attachment,
    Embed,
    EmbedField,
    EmbedFooter,
    EmbedImage,
    EmbedAuthor,
    PermissionOverwrite,
    GuildPreview,
    VoiceRegion,
    Integration,
    AuditLogEntry,
    Webhook,
    Snowflake,
)

__all__ = [
    "Client",
    "DrekordError",
    "HTTPError",
    "RateLimitedError",
    "ForbiddenError",
    "NotFoundError",
    "BadRequestError",
    "UnauthorizedError",
    "DiscordServerError",
    "User",
    "Member",
    "Guild",
    "Channel",
    "Message",
    "Role",
    "Emoji",
    "Attachment",
    "Embed",
    "EmbedField",
    "EmbedFooter",
    "EmbedImage",
    "EmbedAuthor",
    "PermissionOverwrite",
    "GuildPreview",
    "VoiceRegion",
    "Integration",
    "AuditLogEntry",
    "Webhook",
    "Snowflake",
]
