"""High-level API resource classes.


Design pattern:
    client.messages.channel(channel_id).list()
    client.users.get(user_id)
    client.guilds.channels(guild_id).list()
"""

from __future__ import annotations

import json
from typing import Any, TYPE_CHECKING

import aiohttp

from .models import (
    AuditLogEntry,
    Channel,
    Embed,
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
)

if TYPE_CHECKING:
    from .http import HTTPClient


def _serialize_embeds(embeds: list[Embed | dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert a list of Embed objects (or dicts) to dicts for the API payload."""
    result = []
    for e in embeds:
        if isinstance(e, Embed):
            result.append(e.to_dict())
        elif isinstance(e, dict):
            result.append(e)
        else:
            raise TypeError(f"Expected Embed or dict, got {type(e).__name__}")
    return result


# Users API

class UsersResource:
    """Access user-related endpoints: `/users/*`."""

    def __init__(self, http: HTTPClient):
        self._http = http

    async def me(self) -> User:
        """Get the current bot user. `GET /users/@me`"""
        data = await self._http.get("/users/@me")
        return User(data)

    async def get(self, user_id: int | str) -> User:
        """Get a user by ID. `GET /users/{user_id}`"""
        data = await self._http.get(f"/users/{user_id}")
        return User(data)

    async def edit(self, payload: dict[str, Any] | None = None) -> User:
        """Modify the current bot user. `PATCH /users/@me`"""
        data = await self._http.patch("/users/@me", json=payload)
        return User(data)

    async def dm(self, user_id: int | str) -> Channel:
        """Create a DM channel with a user. `POST /users/@me/channels`"""
        data = await self._http.post(
            "/users/@me/channels",
            json={"recipient_id": int(user_id)},
        )
        return Channel(data)


# Guilds API

class GuildChannelsResource:
    """Manage channels within a specific guild: `/guilds/{guild_id}/channels`."""

    def __init__(self, http: HTTPClient, guild_id: int | str):
        self._http = http
        self._guild_id = int(guild_id)

    async def list(self) -> list[Channel]:
        """Get all channels in the guild. `GET /guilds/{guild_id}/channels`"""
        data = await self._http.get(f"/guilds/{self._guild_id}/channels")
        return [Channel(c) for c in data]

    async def create(self, payload: dict[str, Any]) -> Channel:
        """Create a channel in the guild. `POST /guilds/{guild_id}/channels`"""
        data = await self._http.post(
            f"/guilds/{self._guild_id}/channels",
            json=payload,
        )
        return Channel(data)

    async def reorder(self, payload: list[dict[str, Any]]) -> list[Channel]:
        """Bulk reorder channels. `PATCH /guilds/{guild_id}/channels`"""
        data = await self._http.patch(
            f"/guilds/{self._guild_id}/channels",
            json=payload,
        )
        return [Channel(c) for c in data]


class GuildMembersResource:
    """Manage members within a specific guild: `/guilds/{guild_id}/members`."""

    def __init__(self, http: HTTPClient, guild_id: int | str):
        self._http = http
        self._guild_id = int(guild_id)

    async def list(
        self, *, limit: int = 1, after: int | str | None = None
    ) -> list[Member]:
        """List members. `GET /guilds/{guild_id}/members`"""
        params: dict[str, Any] = {"limit": limit}
        if after is not None:
            params["after"] = int(after)
        data = await self._http.get(
            f"/guilds/{self._guild_id}/members",
            params=params,
        )
        return [Member(m) for m in data]

    async def get(self, user_id: int | str) -> Member:
        """Get a specific member. `GET /guilds/{guild_id}/members/{user_id}`"""
        data = await self._http.get(
            f"/guilds/{self._guild_id}/members/{user_id}"
        )
        return Member(data)

    async def add(
        self,
        user_id: int | str,
        *,
        access_token: str,
        nick: str | None = None,
        roles: list[int] | None = None,
        mute: bool = False,
        deaf: bool = False,
    ) -> Member:
        """Add a member to the guild (requires OAuth2). `PUT /guilds/{guild_id}/members/{user_id}`"""
        payload: dict[str, Any] = {"access_token": access_token}
        if nick is not None:
            payload["nick"] = nick
        if roles is not None:
            payload["roles"] = roles
        payload["mute"] = mute
        payload["deaf"] = deaf
        data = await self._http.put(
            f"/guilds/{self._guild_id}/members/{user_id}",
            json=payload,
        )
        return Member(data)

    async def edit(
        self,
        user_id: int | str,
        *,
        nick: str | None = None,
        roles: list[int] | None = None,
        mute: bool | None = None,
        deaf: bool | None = None,
        channel_id: int | str | None = None,
        communication_disabled_until: str | None = None,
        flags: int | None = None,
    ) -> Member:
        """Edit a member. `PATCH /guilds/{guild_id}/members/{user_id}`"""
        payload: dict[str, Any] = {}
        if nick is not None:
            payload["nick"] = nick
        if roles is not None:
            payload["roles"] = roles
        if mute is not None:
            payload["mute"] = mute
        if deaf is not None:
            payload["deaf"] = deaf
        if channel_id is not None:
            payload["channel_id"] = int(channel_id)
        if communication_disabled_until is not None:
            payload["communication_disabled_until"] = communication_disabled_until
        if flags is not None:
            payload["flags"] = flags
        data = await self._http.patch(
            f"/guilds/{self._guild_id}/members/{user_id}",
            json=payload,
        )
        return Member(data)

    async def remove(self, user_id: int | str) -> None:
        """Remove a member from the guild. `DELETE /guilds/{guild_id}/members/{user_id}`"""
        await self._http.delete(f"/guilds/{self._guild_id}/members/{user_id}")

    async def search(self, query: str, *, limit: int = 1) -> list[Member]:
        """Search members by username prefix. `GET /guilds/{guild_id}/members/search`"""
        data = await self._http.get(
            f"/guilds/{self._guild_id}/members/search",
            params={"query": query, "limit": limit},
        )
        return [Member(m) for m in data]


class GuildRolesResource:
    """Manage roles within a specific guild: `/guilds/{guild_id}/roles`."""

    def __init__(self, http: HTTPClient, guild_id: int | str):
        self._http = http
        self._guild_id = int(guild_id)

    async def list(self) -> list[Role]:
        """List all roles. `GET /guilds/{guild_id}/roles`"""
        data = await self._http.get(f"/guilds/{self._guild_id}/roles")
        return [Role(r) for r in data]

    async def create(self, payload: dict[str, Any]) -> Role:
        """Create a role. `POST /guilds/{guild_id}/roles`"""
        data = await self._http.post(
            f"/guilds/{self._guild_id}/roles",
            json=payload,
        )
        return Role(data)

    async def edit(self, role_id: int | str, payload: dict[str, Any]) -> Role:
        """Edit a role. `PATCH /guilds/{guild_id}/roles/{role_id}`"""
        data = await self._http.patch(
            f"/guilds/{self._guild_id}/roles/{role_id}",
            json=payload,
        )
        return Role(data)

    async def delete(self, role_id: int | str) -> None:
        """Delete a role. `DELETE /guilds/{guild_id}/roles/{role_id}`"""
        await self._http.delete(f"/guilds/{self._guild_id}/roles/{role_id}")

    async def reorder(self, payload: list[dict[str, Any]]) -> list[Role]:
        """Bulk reorder roles. `PATCH /guilds/{guild_id}/roles`"""
        data = await self._http.patch(
            f"/guilds/{self._guild_id}/roles",
            json=payload,
        )
        return [Role(r) for r in data]


class GuildEmojisResource:
    """Manage emojis within a specific guild: `/guilds/{guild_id}/emojis`."""

    def __init__(self, http: HTTPClient, guild_id: int | str):
        self._http = http
        self._guild_id = int(guild_id)

    async def list(self) -> list[Emoji]:
        """List all emojis. `GET /guilds/{guild_id}/emojis`"""
        data = await self._http.get(f"/guilds/{self._guild_id}/emojis")
        return [Emoji(e) for e in data]

    async def get(self, emoji_id: int | str) -> Emoji:
        """Get a specific emoji. `GET /guilds/{guild_id}/emojis/{emoji_id}`"""
        data = await self._http.get(
            f"/guilds/{self._guild_id}/emojis/{emoji_id}"
        )
        return Emoji(data)

    async def create(self, *, name: str, image: str, roles: list[int] | None = None) -> Emoji:
        """Create an emoji. `POST /guilds/{guild_id}/emojis`"""
        payload: dict[str, Any] = {"name": name, "image": image}
        if roles is not None:
            payload["roles"] = roles
        data = await self._http.post(
            f"/guilds/{self._guild_id}/emojis",
            json=payload,
        )
        return Emoji(data)

    async def edit(self, emoji_id: int | str, payload: dict[str, Any]) -> Emoji:
        """Edit an emoji. `PATCH /guilds/{guild_id}/emojis/{emoji_id}`"""
        data = await self._http.patch(
            f"/guilds/{self._guild_id}/emojis/{emoji_id}",
            json=payload,
        )
        return Emoji(data)

    async def delete(self, emoji_id: int | str) -> None:
        """Delete an emoji. `DELETE /guilds/{guild_id}/emojis/{emoji_id}`"""
        await self._http.delete(f"/guilds/{self._guild_id}/emojis/{emoji_id}")


class GuildResource:
    """Access guild-related endpoints.

    Nested sub-resources are accessible as attributes:
        client.guilds.channels(guild_id)
        client.guilds.members(guild_id)
        client.guilds.roles(guild_id)
        client.guilds.emojis(guild_id)
    """

    def __init__(self, http: HTTPClient):
        self._http = http

    # sub-resource factories 

    def channels(self, guild_id: int | str) -> GuildChannelsResource:
        return GuildChannelsResource(self._http, guild_id)

    def members(self, guild_id: int | str) -> GuildMembersResource:
        return GuildMembersResource(self._http, guild_id)

    def roles(self, guild_id: int | str) -> GuildRolesResource:
        return GuildRolesResource(self._http, guild_id)

    def emojis(self, guild_id: int | str) -> GuildEmojisResource:
        return GuildEmojisResource(self._http, guild_id)

    # direct guild endpoints 

    async def list(self, *, limit: int = 200) -> list[Guild]:
        """List the bot's guilds. `GET /users/@me/guilds`"""
        data = await self._http.get(
            "/users/@me/guilds",
            params={"limit": limit},
        )
        return [Guild(g) for g in data]

    async def get(self, guild_id: int | str, *, with_counts: bool = False) -> Guild:
        """Get a guild by ID. `GET /guilds/{guild_id}`"""
        data = await self._http.get(
            f"/guilds/{guild_id}",
            params={"with_counts": str(with_counts).lower()},
        )
        return Guild(data)

    async def preview(self, guild_id: int | str) -> GuildPreview:
        """Get a guild preview. `GET /guilds/{guild_id}/preview`"""
        data = await self._http.get(f"/guilds/{guild_id}/preview")
        return GuildPreview(data)

    async def edit(self, guild_id: int | str, payload: dict[str, Any]) -> Guild:
        """Edit a guild. `PATCH /guilds/{guild_id}`"""
        data = await self._http.patch(f"/guilds/{guild_id}", json=payload)
        return Guild(data)

    async def delete(self, guild_id: int | str) -> None:
        """Delete a guild (must be owner). `DELETE /guilds/{guild_id}`"""
        await self._http.delete(f"/guilds/{guild_id}")

    async def leave(self, guild_id: int | str) -> None:
        """Leave a guild. `DELETE /users/@me/guilds/{guild_id}`"""
        await self._http.delete(f"/users/@me/guilds/{guild_id}")

    async def ban(self, guild_id: int | str, user_id: int | str, **kwargs: Any) -> None:
        """Ban a user from the guild. `PUT /guilds/{guild_id}/bans/{user_id}`"""
        await self._http.put(f"/guilds/{guild_id}/bans/{user_id}", json=kwargs or None)

    async def unban(self, guild_id: int | str, user_id: int | str) -> None:
        """Unban a user. `DELETE /guilds/{guild_id}/bans/{user_id}`"""
        await self._http.delete(f"/guilds/{guild_id}/bans/{user_id}")

    async def bans(self, guild_id: int | str) -> list[dict[str, Any]]:
        """List bans. `GET /guilds/{guild_id}/bans`"""
        data = await self._http.get(f"/guilds/{guild_id}/bans")
        return data  # type: ignore[no-any-return]

    async def audit_logs(
        self,
        guild_id: int | str,
        *,
        limit: int = 50,
        user_id: int | str | None = None,
        action_type: int | None = None,
    ) -> list[AuditLogEntry]:
        """Get the audit log. `GET /guilds/{guild_id}/audit-logs`"""
        params: dict[str, Any] = {"limit": limit}
        if user_id is not None:
            params["user_id"] = int(user_id)
        if action_type is not None:
            params["action_type"] = action_type
        data = await self._http.get(f"/guilds/{guild_id}/audit-logs", params=params)
        entries = data.get("audit_log_entries", [])
        return [AuditLogEntry(e) for e in entries]

    async def integrations(self, guild_id: int | str) -> list[Integration]:
        """List integrations. `GET /guilds/{guild_id}/integrations`"""
        data = await self._http.get(f"/guilds/{guild_id}/integrations")
        return [Integration(i) for i in data]

    async def voice_regions(self) -> list[VoiceRegion]:
        """List available voice regions. `GET /voice/regions`"""
        data = await self._http.get("/voice/regions")
        return [VoiceRegion(r) for r in data]


# Channels API

class ChannelResource:
    """Access channel-related endpoints: `/channels/{channel_id}`."""

    def __init__(self, http: HTTPClient):
        self._http = http

    async def get(self, channel_id: int | str) -> Channel:
        """Get a channel by ID. `GET /channels/{channel_id}`"""
        data = await self._http.get(f"/channels/{channel_id}")
        return Channel(data)

    async def edit(self, channel_id: int | str, payload: dict[str, Any]) -> Channel:
        """Edit a channel. `PATCH /channels/{channel_id}`"""
        data = await self._http.patch(f"/channels/{channel_id}", json=payload)
        return Channel(data)

    async def delete(self, channel_id: int | str) -> None:
        """Delete a channel. `DELETE /channels/{channel_id}`"""
        await self._http.delete(f"/channels/{channel_id}")

    async def typing(self, channel_id: int | str) -> None:
        """Trigger a typing indicator. `POST /channels/{channel_id}/typing`"""
        await self._http.post(f"/channels/{channel_id}/typing")

    async def permissions(
        self, channel_id: int | str, overwrite_id: int | str
    ) -> dict[str, Any]:
        """Get a permission overwrite. `GET /channels/{channel_id}/permissions/{overwrite_id}`"""
        return await self._http.get(f"/channels/{channel_id}/permissions/{overwrite_id}")

    async def set_permissions(
        self,
        channel_id: int | str,
        overwrite_id: int | str,
        *,
        allow: str | None = None,
        deny: str | None = None,
        type: int = 0,
    ) -> None:
        """Set a permission overwrite. `PUT /channels/{channel_id}/permissions/{overwrite_id}`"""
        payload: dict[str, Any] = {"type": type}
        if allow is not None:
            payload["allow"] = allow
        if deny is not None:
            payload["deny"] = deny
        await self._http.put(
            f"/channels/{channel_id}/permissions/{overwrite_id}",
            json=payload,
        )

    async def invites(self, channel_id: int | str) -> list[dict[str, Any]]:
        """List invites for a channel. `GET /channels/{channel_id}/invites`"""
        return await self._http.get(f"/channels/{channel_id}/invites")

    async def follow(self, channel_id: int | str, webhook_channel_id: int | str) -> dict[str, Any]:
        """Follow an announcement channel. `POST /channels/{channel_id}/followers`"""
        return await self._http.post(
            f"/channels/{channel_id}/followers",
            json={"webhook_channel_id": int(webhook_channel_id)},
        )


# Messages API

class MessagesResource:
    """Access message-related endpoints.

    Usage::

        msgs = client.messages
        # List messages in a channel
        messages = await msgs.channel(channel_id).list(limit=10)
        # Send a message
        msg = await msgs.channel(channel_id).send(content="Hello!")
        # Get a specific message
        msg = await msgs.channel(channel_id).get(message_id)
    """

    def __init__(self, http: HTTPClient):
        self._http = http

    def channel(self, channel_id: int | str) -> _ChannelMessages:
        """Get the message helper scoped to a specific channel."""
        return _ChannelMessages(self._http, channel_id)

    # global message operations 

    async def get(
        self, channel_id: int | str, message_id: int | str
    ) -> Message:
        """Get a single message. `GET /channels/{channel_id}/messages/{message_id}`"""
        data = await self._http.get(
            f"/channels/{channel_id}/messages/{message_id}"
        )
        return Message(data)

    async def edit(
        self,
        channel_id: int | str,
        message_id: int | str,
        *,
        content: str | None = None,
        embeds: list[Embed | dict[str, Any]] | None = None,
        flags: int | None = None,
        allowed_mentions: dict[str, Any] | None = None,
        components: list[dict[str, Any]] | None = None,
        attachments: list[dict[str, Any]] | None = None,
        view: Any | None = None,
    ) -> Message:
        """Edit a message. `PATCH /channels/{channel_id}/messages/{message_id}`"""
        from .ui.view import LayoutView

        payload: dict[str, Any] = {}

        if view is not None and isinstance(view, LayoutView):
            view_payload = view.to_payload()
            payload.update(view_payload)
        else:
            if content is not None:
                payload["content"] = content
            if embeds is not None:
                payload["embeds"] = _serialize_embeds(embeds)
            if components is not None:
                payload["components"] = components

        if flags is not None:
            payload["flags"] = flags
        if allowed_mentions is not None:
            payload["allowed_mentions"] = allowed_mentions
        if attachments is not None:
            payload["attachments"] = attachments
        data = await self._http.patch(
            f"/channels/{channel_id}/messages/{message_id}",
            json=payload,
        )
        return Message(data)

    async def delete(
        self, channel_id: int | str, message_id: int | str
    ) -> None:
        """Delete a message. `DELETE /channels/{channel_id}/messages/{message_id}`"""
        await self._http.delete(f"/channels/{channel_id}/messages/{message_id}")

    async def bulk_delete(
        self, channel_id: int | str, message_ids: list[int | str]
    ) -> None:
        """Bulk-delete messages (max 100). `POST /channels/{channel_id}/messages/bulk-delete`"""
        await self._http.post(
            f"/channels/{channel_id}/messages/bulk-delete",
            json={"messages": [int(m) for m in message_ids]},
        )

    async def pin(self, channel_id: int | str, message_id: int | str) -> None:
        """Pin a message. `PUT /channels/{channel_id}/pins/{message_id}`"""
        await self._http.put(f"/channels/{channel_id}/pins/{message_id}")

    async def unpin(self, channel_id: int | str, message_id: int | str) -> None:
        """Unpin a message. `DELETE /channels/{channel_id}/pins/{message_id}`"""
        await self._http.delete(f"/channels/{channel_id}/pins/{message_id}")

    async def pins(self, channel_id: int | str) -> list[Message]:
        """List pinned messages. `GET /channels/{channel_id}/pins`"""
        data = await self._http.get(f"/channels/{channel_id}/pins")
        return [Message(m) for m in data]

    async def crosspost(self, channel_id: int | str, message_id: int | str) -> Message:
        """Crosspost (publish) an announcement. `POST /channels/{channel_id}/messages/{message_id}/crosspost`"""
        data = await self._http.post(
            f"/channels/{channel_id}/messages/{message_id}/crosspost"
        )
        return Message(data)

    async def reactions_add(
        self,
        channel_id: int | str,
        message_id: int | str,
        emoji: str,
        user_id: str = "@me",
    ) -> None:
        """Add a reaction. `PUT /channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me`"""
        await self._http.put(
            f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}"
        )

    async def reactions_remove(
        self,
        channel_id: int | str,
        message_id: int | str,
        emoji: str,
        user_id: str = "@me",
    ) -> None:
        """Remove a reaction. `DELETE /channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}`"""
        await self._http.delete(
            f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}"
        )


class _ChannelMessages:
    """Scoped helper for message operations on a specific channel."""

    def __init__(self, http: HTTPClient, channel_id: int | str):
        self._http = http
        self._channel_id = int(channel_id)

    @property
    def channel_id(self) -> int:
        return self._channel_id

    async def list(
        self,
        *,
        around: int | str | None = None,
        before: int | str | None = None,
        after: int | str | None = None,
        limit: int = 50,
    ) -> list[Message]:
        """List messages in this channel. `GET /channels/{channel_id}/messages`"""
        params: dict[str, Any] = {"limit": limit}
        if around is not None:
            params["around"] = int(around)
        if before is not None:
            params["before"] = int(before)
        if after is not None:
            params["after"] = int(after)
        data = await self._http.get(
            f"/channels/{self._channel_id}/messages",
            params=params,
        )
        return [Message(m) for m in data]

    async def send(
        self,
        *,
        content: str | None = None,
        embeds: list[Embed | dict[str, Any]] | None = None,
        tts: bool = False,
        flags: int | None = None,
        allowed_mentions: dict[str, Any] | None = None,
        message_reference: dict[str, Any] | None = None,
        components: list[dict[str, Any]] | None = None,
        sticker_ids: list[int | str] | None = None,
        nonce: str | int | None = None,
        enforce_nonce: bool = False,
        files: list[tuple[str, Any, str]] | None = None,
        view: Any | None = None,
    ) -> Message:
        """Send a message to this channel. `POST /channels/{channel_id}/messages`

        ### Parameters
        view:
            A `drekord.ui.LayoutView` for Components V2 messages.
            When provided, `content`, `embeds`, `stickers`, and `poll`
            are ignored, all content must be expressed as components.
            The `IS_COMPONENTS_V2` flag is set automatically.
        """
        from .ui.view import LayoutView

        payload: dict[str, Any] = {}

        # Components V2: view takes precedence
        if view is not None and isinstance(view, LayoutView):
            view_payload = view.to_payload()
            payload.update(view_payload)
        else:
            # Legacy components
            if content is not None:
                payload["content"] = content
            if embeds is not None:
                payload["embeds"] = _serialize_embeds(embeds)
            if tts:
                payload["tts"] = True
            if components is not None:
                payload["components"] = components
            if sticker_ids is not None:
                payload["sticker_ids"] = [int(s) for s in sticker_ids]

        if flags is not None:
            payload["flags"] = flags
        if allowed_mentions is not None:
            payload["allowed_mentions"] = allowed_mentions
        if message_reference is not None:
            payload["message_reference"] = message_reference
        if nonce is not None:
            payload["nonce"] = nonce
        if enforce_nonce:
            payload["enforce_nonce"] = True

        # File uploads (multipart)
        if files:
            form = aiohttp.FormData()
            if payload:
                form.add_field(
                    "payload_json",
                    json.dumps(payload),
                    content_type="application/json",
                )
            for i, (filename, fileobj, content_type) in enumerate(files):
                form.add_field(
                    f"files[{i}]",
                    fileobj,
                    filename=filename,
                    content_type=content_type,
                )
            data = await self._http.post(
                f"/channels/{self._channel_id}/messages",
                data=form,
                headers={"Content-Type": None},  # let aiohttp handle it
            )
        else:
            data = await self._http.post(
                f"/channels/{self._channel_id}/messages",
                json=payload,
            )
        return Message(data)

    async def get(self, message_id: int | str) -> Message:
        """Get a specific message. `GET /channels/{channel_id}/messages/{message_id}`"""
        data = await self._http.get(
            f"/channels/{self._channel_id}/messages/{message_id}"
        )
        return Message(data)

    async def edit(self, message_id: int | str, **kwargs: Any) -> Message:
        """Edit a message (convenience wrapper)."""
        msgs = MessagesResource(self._http)
        return await msgs.edit(self._channel_id, message_id, **kwargs)

    async def delete(self, message_id: int | str) -> None:
        """Delete a message (convenience wrapper)."""
        msgs = MessagesResource(self._http)
        await msgs.delete(self._channel_id, message_id)

    async def pin(self, message_id: int | str) -> None:
        """Pin a message."""
        await self._http.put(f"/channels/{self._channel_id}/pins/{message_id}")

    async def unpin(self, message_id: int | str) -> None:
        """Unpin a message."""
        await self._http.delete(f"/channels/{self._channel_id}/pins/{message_id}")

    async def typing(self) -> None:
        """Trigger a typing indicator."""
        await self._http.post(f"/channels/{self._channel_id}/typing")



# ======================================================================
# Webhooks API
# ======================================================================

class WebhooksResource:
    """Access webhook-related endpoints: `/webhooks/*` and channel webhooks."""

    def __init__(self, http: HTTPClient):
        self._http = http

    async def channel_webhooks(self, channel_id: int | str) -> list[Webhook]:
        """List webhooks in a channel. `GET /channels/{channel_id}/webhooks`"""
        data = await self._http.get(f"/channels/{channel_id}/webhooks")
        return [Webhook(w) for w in data]

    async def guild_webhooks(self, guild_id: int | str) -> list[Webhook]:
        """List webhooks in a guild. `GET /guilds/{guild_id}/webhooks`"""
        data = await self._http.get(f"/guilds/{guild_id}/webhooks")
        return [Webhook(w) for w in data]

    async def get(self, webhook_id: int | str) -> Webhook:
        """Get a webhook by ID. `GET /webhooks/{webhook_id}`"""
        data = await self._http.get(f"/webhooks/{webhook_id}")
        return Webhook(data)

    async def create(
        self, channel_id: int | str, *, name: str, avatar: str | None = None
    ) -> Webhook:
        """Create a webhook. `POST /channels/{channel_id}/webhooks`"""
        payload: dict[str, Any] = {"name": name}
        if avatar is not None:
            payload["avatar"] = avatar
        data = await self._http.post(
            f"/channels/{channel_id}/webhooks",
            json=payload,
        )
        return Webhook(data)

    async def edit(
        self, webhook_id: int | str, payload: dict[str, Any]
    ) -> Webhook:
        """Edit a webhook. `PATCH /webhooks/{webhook_id}`"""
        data = await self._http.patch(f"/webhooks/{webhook_id}", json=payload)
        return Webhook(data)

    async def delete(self, webhook_id: int | str) -> None:
        """Delete a webhook. `DELETE /webhooks/{webhook_id}`"""
        await self._http.delete(f"/webhooks/{webhook_id}")

    async def execute(
        self,
        webhook_id: int | str,
        *,
        token: str,
        content: str | None = None,
        embeds: list[Embed | dict[str, Any]] | None = None,
        username: str | None = None,
        avatar_url: str | None = None,
        tts: bool = False,
        wait: bool = False,
        thread_id: int | str | None = None,
        view: Any | None = None,
    ) -> Message | None:
        """Execute (send via) a webhook. `POST /webhooks/{webhook_id}/{token}`"""
        from .ui.view import LayoutView

        payload: dict[str, Any] = {}

        if view is not None and isinstance(view, LayoutView):
            view_payload = view.to_payload()
            payload.update(view_payload)
        else:
            if content is not None:
                payload["content"] = content
            if embeds is not None:
                payload["embeds"] = _serialize_embeds(embeds)

        if username is not None:
            payload["username"] = username
        if avatar_url is not None:
            payload["avatar_url"] = avatar_url
        if tts:
            payload["tts"] = True

        params: dict[str, Any] = {"wait": str(wait).lower()}
        if thread_id is not None:
            params["thread_id"] = int(thread_id)

        # Webhooks need this query param for components v2
        if view is not None and isinstance(view, LayoutView):
            params["with_components"] = "true"

        data = await self._http.post(
            f"/webhooks/{webhook_id}/{token}",
            json=payload,
            params=params,
        )
        if data is None:
            return None
        return Message(data)


# ======================================================================
# Invites API
# ======================================================================

class InvitesResource:
    """Access invite-related endpoints."""

    def __init__(self, http: HTTPClient):
        self._http = http

    async def channel_invites(self, channel_id: int | str) -> list[dict[str, Any]]:
        """List invites for a channel. `GET /channels/{channel_id}/invites`"""
        return await self._http.get(f"/channels/{channel_id}/invites")

    async def guild_invites(self, guild_id: int | str) -> list[dict[str, Any]]:
        """List invites for a guild. `GET /guilds/{guild_id}/invites`"""
        return await self._http.get(f"/guilds/{guild_id}/invites")

    async def get(self, invite_code: str) -> dict[str, Any]:
        """Get an invite. `GET /invites/{invite_code}`"""
        return await self._http.get(f"/invites/{invite_code}")

    async def delete(self, invite_code: str) -> None:
        """Delete an invite. `DELETE /invites/{invite_code}`"""
        await self._http.delete(f"/invites/{invite_code}")


# ======================================================================
# Emoji (global) API
# ======================================================================

class EmojiResource:
    """Access global emoji endpoints."""

    def __init__(self, http: HTTPClient):
        self._http = http

    async def list(self, *, limit: int = 250) -> list[Emoji]:
        """List all emojis. `GET /emojis`"""
        data = await self._http.get("/emojis", params={"limit": limit})
        emojis = data.get("items", data) if isinstance(data, dict) else data
        return [Emoji(e) for e in emojis]
