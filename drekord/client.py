"""Drekord v2.0 client — the entry point for all API interactions.

Usage::

    import asyncio
    import drekord

    async def main():
        async with drekord.Client(token="your_token") as client:
            # Get bot info
            me = await client.me()
            print(f"Logged in as {me.username}")

            # Fetch and send
            channel = await client.fetch_channel(CHANNEL_ID)
            await channel.send("Hello!")

            # Interact with objects
            user = await client.fetch_user(USER_ID)
            await user.create_dm()
            print(user.display_name)

    asyncio.run(main())
"""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .http import HTTPClient
from .models import (
    Channel,
    Emoji,
    Guild,
    GuildPreview,
    Integration,
    Member,
    Message,
    Role,
    User,
    VoiceRegion,
    Webhook,
    AuditLogEntry,
)

__all__ = ["Client"]

log = logging.getLogger("drekord")


class Client:
    """The main Drekord client — a clean, discord.py-inspired API.

    ### Parameters
    token:
        Your bot token (``Bot MTIz...``) or OAuth2 bearer token (``Bearer MTIz...``).
        If neither prefix is present, ``Bot`` is assumed automatically.
    timeout:
        Default HTTP request timeout in seconds (default 30).
    max_retries:
        Maximum number of retries on transient failures (default 5).
    session:
        An optional pre-existing ``aiohttp.ClientSession`` to reuse.
        If ``None`` (default), the client creates and manages its own session.

    ### Usage::

        async with drekord.Client(token="YOUR_TOKEN") as client:
            # Fetch objects
            channel = await client.fetch_channel(channel_id)
            user = await client.fetch_user(user_id)
            guild = await client.fetch_guild(guild_id)

            # Use them naturally
            await channel.send("Hello!")
            print(user.display_name)
            members = await guild.fetch_members(limit=10)
    """

    def __init__(
        self,
        token: str,
        *,
        timeout: float = 30.0,
        max_retries: int = 5,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        if not token.startswith(("Bot ", "Bearer ")):
            token = f"Bot {token}"

        self._http = HTTPClient(
            token,
            timeout=timeout,
            max_retries=max_retries,
            session=session,
        )

    #  Lifecycle 

    async def __aenter__(self) -> Client:
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP session."""
        await self._http.close()

    @property
    def http(self) -> HTTPClient:
        """Access the low-level HTTP client directly."""
        return self._http

    # ======================================================================
    # Top-level fetch methods (discord.py style)
    # ======================================================================

    #  Users 

    async def me(self) -> User:
        """Get the current bot user. `GET /users/@me`

        Usage::

            me = await client.me()
            print(f"Logged in as {me.username}")
        """
        data = await self._http.get("/users/@me")
        return User(data, self._http)

    async def fetch_user(self, user_id: int | str) -> User:
        """Get a user by ID. `GET /users/{user_id}`

        Usage::

            user = await client.fetch_user(123456)
            print(user.display_name)
            dm_channel = await user.create_dm()
        """
        data = await self._http.get(f"/users/{user_id}")
        return User(data, self._http)

    async def edit_me(self, payload: dict[str, Any] | None = None) -> User:
        """Modify the current bot user. `PATCH /users/@me`"""
        data = await self._http.patch("/users/@me", json=payload)
        return User(data, self._http)

    #  Channels 

    async def fetch_channel(self, channel_id: int | str) -> Channel:
        """Get a channel by ID. `GET /channels/{channel_id}`

        Usage::

            channel = await client.fetch_channel(channel_id)
            await channel.send("Hello!")
            messages = await channel.fetch_messages(limit=10)
            await channel.edit(name="new-name")
        """
        data = await self._http.get(f"/channels/{channel_id}")
        return Channel(data, self._http)

    #  Messages 

    async def fetch_message(self, channel_id: int | str, message_id: int | str) -> Message:
        """Get a single message. `GET /channels/{channel_id}/messages/{message_id}`

        Usage::

            message = await client.fetch_message(channel_id, message_id)
            print(message.content)
            await message.edit(content="Edited!")
            await message.delete()
        """
        data = await self._http.get(f"/channels/{channel_id}/messages/{message_id}")
        return Message(data, self._http)

    async def bulk_delete_messages(
        self, channel_id: int | str, message_ids: list[int | str]
    ) -> None:
        """Bulk-delete messages (max 100). `POST /channels/{channel_id}/messages/bulk-delete`"""
        await self._http.post(
            f"/channels/{channel_id}/messages/bulk-delete",
            json={"messages": [int(m) for m in message_ids]},
        )

    #  Guilds 

    async def fetch_guilds(self, *, limit: int = 200) -> list[Guild]:
        """List the bot's guilds. `GET /users/@me/guilds`

        Usage::

            guilds = await client.fetch_guilds()
            for guild in guilds:
                print(guild.name)
        """
        data = await self._http.get("/users/@me/guilds", params={"limit": limit})
        return [Guild(g, self._http) for g in data]

    async def fetch_guild(self, guild_id: int | str, *, with_counts: bool = False) -> Guild:
        """Get a guild by ID. `GET /guilds/{guild_id}`

        Usage::

            guild = await client.fetch_guild(guild_id)
            channels = await guild.fetch_channels()
            members = await guild.fetch_members(limit=100)
            await guild.leave()
        """
        data = await self._http.get(
            f"/guilds/{guild_id}",
            params={"with_counts": str(with_counts).lower()},
        )
        return Guild(data, self._http)

    async def fetch_guild_preview(self, guild_id: int | str) -> GuildPreview:
        """Get a guild preview. `GET /guilds/{guild_id}/preview`"""
        data = await self._http.get(f"/guilds/{guild_id}/preview")
        return GuildPreview(data, self._http)

    #  Members 

    async def fetch_member(self, guild_id: int | str, user_id: int | str) -> Member:
        """Get a specific guild member. `GET /guilds/{guild_id}/members/{user_id}`

        Usage::

            member = await client.fetch_member(guild_id, user_id)
            print(member.display_name)
            await member.kick(reason="Rule violation")
        """
        data = await self._http.get(f"/guilds/{guild_id}/members/{user_id}")
        return Member(data, self._http)

    async def fetch_members(
        self, guild_id: int | str, *, limit: int = 1, after: int | str | None = None
    ) -> list[Member]:
        """List members in a guild. `GET /guilds/{guild_id}/members`"""
        params: dict[str, Any] = {"limit": limit}
        if after is not None:
            params["after"] = int(after)
        data = await self._http.get(f"/guilds/{guild_id}/members", params=params)
        return [Member(m, self._http) for m in data]

    #  Roles 

    async def fetch_roles(self, guild_id: int | str) -> list[Role]:
        """List all roles in a guild. `GET /guilds/{guild_id}/roles`"""
        data = await self._http.get(f"/guilds/{guild_id}/roles")
        return [Role(r, self._http) for r in data]

    async def create_role(self, guild_id: int | str, payload: dict[str, Any]) -> Role:
        """Create a role. `POST /guilds/{guild_id}/roles`"""
        data = await self._http.post(f"/guilds/{guild_id}/roles", json=payload)
        return Role(data, self._http)

    #  Webhooks 

    async def fetch_webhook(self, webhook_id: int | str) -> Webhook:
        """Get a webhook by ID. `GET /webhooks/{webhook_id}`

        Usage::

            webhook = await client.fetch_webhook(webhook_id)
            await webhook.execute(content="Hello!")
            await webhook.edit(name="New Name")
            await webhook.delete()
        """
        data = await self._http.get(f"/webhooks/{webhook_id}")
        return Webhook(data, self._http)

    async def fetch_webhooks(self, channel_id: int | str) -> list[Webhook]:
        """List webhooks in a channel. `GET /channels/{channel_id}/webhooks`"""
        data = await self._http.get(f"/channels/{channel_id}/webhooks")
        return [Webhook(w, self._http) for w in data]

    async def create_webhook(
        self, channel_id: int | str, *, name: str, avatar: str | None = None
    ) -> Webhook:
        """Create a webhook. `POST /channels/{channel_id}/webhooks`"""
        payload: dict[str, Any] = {"name": name}
        if avatar is not None:
            payload["avatar"] = avatar
        data = await self._http.post(f"/channels/{channel_id}/webhooks", json=payload)
        return Webhook(data, self._http)

    #  Invites 

    async def fetch_channel_invites(self, channel_id: int | str) -> list[dict[str, Any]]:
        """List invites for a channel. `GET /channels/{channel_id}/invites`"""
        return await self._http.get(f"/channels/{channel_id}/invites")

    async def fetch_guild_invites(self, guild_id: int | str) -> list[dict[str, Any]]:
        """List invites for a guild. `GET /guilds/{guild_id}/invites`"""
        return await self._http.get(f"/guilds/{guild_id}/invites")

    async def fetch_invite(self, invite_code: str) -> dict[str, Any]:
        """Get an invite. `GET /invites/{invite_code}`"""
        return await self._http.get(f"/invites/{invite_code}")

    async def delete_invite(self, invite_code: str) -> None:
        """Delete an invite. `DELETE /invites/{invite_code}`"""
        await self._http.delete(f"/invites/{invite_code}")

    #  Voice Regions 

    async def fetch_voice_regions(self) -> list[VoiceRegion]:
        """List available voice regions. `GET /voice/regions`"""
        data = await self._http.get("/voice/regions")
        return [VoiceRegion(r, self._http) for r in data]

    #  Emojis 

    async def fetch_emojis(self, guild_id: int | str) -> list[Emoji]:
        """List all emojis in a guild. `GET /guilds/{guild_id}/emojis`"""
        data = await self._http.get(f"/guilds/{guild_id}/emojis")
        return [Emoji(e, self._http) for e in data]

    #  Raw request (escape hatch) 

    async def request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Send a raw HTTP request to the Discord API.

        This is an escape hatch for endpoints not yet covered.
        Use it sparingly::

            data = await client.request("GET", "/gateway")
            data = await client.request("POST", "/channels/123/threads", json={...})
        """
        return await self._http.request(method, path, **kwargs)

    def __repr__(self) -> str:
        return "<drekord.Client>"
