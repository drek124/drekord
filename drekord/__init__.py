"""
Drekord - A lightweight, async Discord REST API wrapper.

Drekord is not a bot framework. It is a pure API client designed to be
integrated into any async application that needs to interact with the
Discord REST API — read messages, send messages, manage channels, etc.

Usage::

    import drekord

    async with drekord.Client(token="your_token") as client:
        # Basic message
        await client.messages.channel(ch).send(content="Hello!")

        # With an embed
        embed = drekord.Embed(title="Hi", description="World")
        await client.messages.channel(ch).send(embeds=[embed])

        # With Components V2
        view = drekord.ui.LayoutView()
        view.add_item(drekord.ui.Container(
            drekord.ui.TextDisplay("## Hello!"),
            drekord.ui.Separator(),
            accent_color="#5865F2",
        ))
        await client.messages.channel(ch).send(view=view)
"""

__version__ = "0.1.0"
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
