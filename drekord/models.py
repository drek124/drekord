"""Drekord v2.0 data models.

Every model is a "live" object — it holds a reference to the HTTP client
so you can call methods directly on it::

    channel = await client.fetch_channel(channel_id)
    await channel.send("Hello!")

    message = await channel.fetch_message(message_id)
    await message.delete(reason="Cleanup")

    user = await client.fetch_user(user_id)
    print(user.display_name)
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .http import HTTPClient


def _parse_snowflake(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)


def _parse_iso(value: Any) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _parse_color(value: int | str) -> int:
    """Parse a color value (``0x5865F2`` or ``'#5865F2'``) into an int."""
    if isinstance(value, int):
        return value
    hex_str = value.lstrip("#").lstrip("0x")
    return int(hex_str, 16)


class _BaseModel:
    """Thin wrapper around a raw payload dict providing attribute access."""

    __slots__ = ("_data", "_http")

    def __init__(self, data: dict[str, Any], http: HTTPClient | None = None):
        object.__setattr__(self, "_data", data)
        object.__setattr__(self, "_http", http)

    def __getattr__(self, name: str) -> Any:
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            ) from None

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    @property
    def raw(self) -> dict[str, Any]:
        """Return the underlying raw payload dict."""
        return self._data

    def __repr__(self) -> str:
        return f"<{type(self).__name__} id={self.id}>"  # type: ignore[attr-defined]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _BaseModel):
            return self.id == other.id  # type: ignore[attr-defined]
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.id)  # type: ignore[attr-defined]



# Snowflake



class Snowflake:
    """Represents a Discord snowflake ID with helper utilities."""

    __slots__ = ("_value",)

    def __init__(self, value: int | str):
        self._value = int(value)

    @property
    def value(self) -> int:
        return self._value

    @property
    def timestamp(self) -> datetime:
        """Extract the creation timestamp from the snowflake."""
        return datetime.fromtimestamp(((self._value >> 22) + 1420070400000) / 1000)

    def __int__(self) -> int:
        return self._value

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return f"Snowflake({self._value})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (Snowflake, int)):
            other_val = other if isinstance(other, int) else other._value
            return self._value == other_val
        if isinstance(other, str):
            return self._value == int(other)
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)



# User



class User(_BaseModel):
    """Represents a Discord user.

    This is a "live" object — you can call methods on it directly::

        user = await client.fetch_user(user_id)
        dm_channel = await user.create_dm()
        await dm_channel.send("Hello!")
    """

    __slots__ = ()

    @property
    def id(self) -> int:
        return _parse_snowflake(self._data["id"])  # type: ignore[return-value]

    @property
    def username(self) -> str:
        return self._data["username"]

    @property
    def discriminator(self) -> str | None:
        return self._data.get("discriminator")

    @property
    def global_name(self) -> str | None:
        return self._data.get("global_name")

    @property
    def display_name(self) -> str:
        """Return the best available display name."""
        return self.global_name or self.username

    @property
    def avatar(self) -> str | None:
        return self._data.get("avatar")

    @property
    def bot(self) -> bool:
        return self._data.get("bot", False)

    @property
    def system(self) -> bool:
        return self._data.get("system", False)

    @property
    def mfa_enabled(self) -> bool:
        return self._data.get("mfa_enabled", False)

    @property
    def banner(self) -> str | None:
        return self._data.get("banner")

    @property
    def accent_color(self) -> int | None:
        return self._data.get("accent_color")

    @property
    def locale(self) -> str | None:
        return self._data.get("locale")

    @property
    def verified(self) -> bool | None:
        return self._data.get("verified")

    @property
    def email(self) -> str | None:
        return self._data.get("email")

    @property
    def flags(self) -> int | None:
        return self._data.get("flags")

    @property
    def premium_type(self) -> int | None:
        return self._data.get("premium_type")

    @property
    def public_flags(self) -> int | None:
        return self._data.get("public_flags")

    def avatar_url(self, size: int = 128, fmt: str = "png") -> str | None:
        """Build the avatar CDN URL."""
        if self.avatar is None:
            return None
        ext = "gif" if self.avatar.startswith("a_") else fmt
        return f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.{ext}?size={size}"

    #  Live methods 

    async def create_dm(self) -> Channel:
        """Create a DM channel with this user. `POST /users/@me/channels`"""
        if self._http is None:
            raise RuntimeError("User object has no HTTP client — cannot call API methods")
        data = await self._http.post(
            "/users/@me/channels",
            json={"recipient_id": self.id},
        )
        return Channel(data, self._http)

    async def fetch(self) -> User:
        """Re-fetch this user from the API. `GET /users/{id}`"""
        if self._http is None:
            raise RuntimeError("User object has no HTTP client — cannot call API methods")
        data = await self._http.get(f"/users/{self.id}")
        return User(data, self._http)



# Member



class Member(_BaseModel):
    """Represents a guild member (a user within a guild).

    Live methods::

        member = await guild.fetch_member(user_id)
        await member.kick(reason="Rule violation")
        await member.ban(reason="Spam")
    """

    __slots__ = ()

    @property
    def user(self) -> User:
        return User(self._data["user"], self._http)

    @property
    def guild_id(self) -> int | None:
        return _parse_snowflake(self._data.get("guild_id"))

    @property
    def nick(self) -> str | None:
        return self._data.get("nick")

    @property
    def display_name(self) -> str:
        return self.nick or self.user.display_name

    @property
    def avatar(self) -> str | None:
        return self._data.get("avatar")

    @property
    def roles(self) -> list[int]:
        return [int(r) for r in self._data.get("roles", [])]

    @property
    def joined_at(self) -> datetime | None:
        return _parse_iso(self._data.get("joined_at"))

    @property
    def premium_since(self) -> datetime | None:
        return _parse_iso(self._data.get("premium_since"))

    @property
    def deaf(self) -> bool:
        return self._data.get("deaf", False)

    @property
    def mute(self) -> bool:
        return self._data.get("mute", False)

    @property
    def pending(self) -> bool:
        return self._data.get("pending", False)

    @property
    def communication_disabled_until(self) -> datetime | None:
        return _parse_iso(self._data.get("communication_disabled_until"))

    #  Live methods 

    async def kick(self, *, reason: str | None = None) -> None:
        """Kick this member. `DELETE /guilds/{guild_id}/members/{user_id}`"""
        if self._http is None:
            raise RuntimeError("Member object has no HTTP client")
        headers = {}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        guild_id = self.guild_id
        if guild_id is None:
            raise ValueError("Member object has no guild_id")
        await self._http.delete(
            f"/guilds/{guild_id}/members/{self.user.id}",
            headers=headers,
        )

    async def ban(self, *, reason: str | None = None, delete_message_days: int | None = None) -> None:
        """Ban this member. `PUT /guilds/{guild_id}/bans/{user_id}`"""
        if self._http is None:
            raise RuntimeError("Member object has no HTTP client")
        guild_id = self.guild_id
        if guild_id is None:
            raise ValueError("Member object has no guild_id")
        payload: dict[str, Any] = {}
        if reason:
            payload["reason"] = reason
        if delete_message_days is not None:
            payload["delete_message_days"] = delete_message_days
        await self._http.put(
            f"/guilds/{guild_id}/bans/{self.user.id}",
            json=payload or None,
            headers={"X-Audit-Log-Reason": reason} if reason else None,
        )

    async def edit(
        self,
        *,
        nick: str | None = None,
        roles: list[int] | None = None,
        mute: bool | None = None,
        deaf: bool | None = None,
        channel_id: int | str | None = None,
        communication_disabled_until: str | None = None,
        flags: int | None = None,
    ) -> Member:
        """Edit this member. `PATCH /guilds/{guild_id}/members/{user_id}`"""
        if self._http is None:
            raise RuntimeError("Member object has no HTTP client")
        guild_id = self.guild_id
        if guild_id is None:
            raise ValueError("Member object has no guild_id")
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
            f"/guilds/{guild_id}/members/{self.user.id}",
            json=payload,
        )
        return Member(data, self._http)



# Guild



class Guild(_BaseModel):
    """Represents a Discord guild (server).

    Live methods::

        guild = await client.fetch_guild(guild_id)
        channels = await guild.fetch_channels()
        members = await guild.fetch_members(limit=100)
        roles = await guild.fetch_roles()
        await guild.leave()
    """

    __slots__ = ()

    @property
    def id(self) -> int:
        return _parse_snowflake(self._data["id"])  # type: ignore[return-value]

    @property
    def name(self) -> str:
        return self._data["name"]

    @property
    def icon(self) -> str | None:
        return self._data.get("icon")

    @property
    def description(self) -> str | None:
        return self._data.get("description")

    @property
    def owner(self) -> bool | None:
        return self._data.get("owner")

    @property
    def owner_id(self) -> int | None:
        return _parse_snowflake(self._data.get("owner_id"))

    @property
    def permissions(self) -> str | None:
        return self._data.get("permissions")

    @property
    def region(self) -> str | None:
        return self._data.get("region")

    @property
    def afk_channel_id(self) -> int | None:
        return _parse_snowflake(self._data.get("afk_channel_id"))

    @property
    def afk_timeout(self) -> int | None:
        return self._data.get("afk_timeout")

    @property
    def verification_level(self) -> int | None:
        return self._data.get("verification_level")

    @property
    def default_message_notifications(self) -> int | None:
        return self._data.get("default_message_notifications")

    @property
    def explicit_content_filter(self) -> int | None:
        return self._data.get("explicit_content_filter")

    @property
    def roles(self) -> list[Role]:
        return [Role(r, self._http) for r in self._data.get("roles", [])]

    @property
    def emojis(self) -> list[Emoji]:
        return [Emoji(e, self._http) for e in self._data.get("emojis", [])]

    @property
    def features(self) -> list[str]:
        return self._data.get("features", [])

    @property
    def mfa_level(self) -> int | None:
        return self._data.get("mfa_level")

    @property
    def application_id(self) -> int | None:
        return _parse_snowflake(self._data.get("application_id"))

    @property
    def system_channel_id(self) -> int | None:
        return _parse_snowflake(self._data.get("system_channel_id"))

    @property
    def system_channel_flags(self) -> int | None:
        return self._data.get("system_channel_flags")

    @property
    def rules_channel_id(self) -> int | None:
        return _parse_snowflake(self._data.get("rules_channel_id"))

    @property
    def max_presences(self) -> int | None:
        return self._data.get("max_presences")

    @property
    def max_members(self) -> int | None:
        return self._data.get("max_members")

    @property
    def vanity_url_code(self) -> str | None:
        return self._data.get("vanity_url_code")

    @property
    def banner(self) -> str | None:
        return self._data.get("banner")

    @property
    def premium_tier(self) -> int | None:
        return self._data.get("premium_tier")

    @property
    def premium_subscription_count(self) -> int | None:
        return self._data.get("premium_subscription_count")

    @property
    def preferred_locale(self) -> str | None:
        return self._data.get("preferred_locale")

    @property
    def public_updates_channel_id(self) -> int | None:
        return _parse_snowflake(self._data.get("public_updates_channel_id"))

    @property
    def max_video_channel_users(self) -> int | None:
        return self._data.get("max_video_channel_users")

    @property
    def approximate_member_count(self) -> int | None:
        return self._data.get("approximate_member_count")

    @property
    def approximate_presence_count(self) -> int | None:
        return self._data.get("approximate_presence_count")

    @property
    def nsfw_level(self) -> int | None:
        return self._data.get("nsfw_level")

    def icon_url(self, size: int = 128, fmt: str = "png") -> str | None:
        if self.icon is None:
            return None
        ext = "gif" if self.icon.startswith("a_") else fmt
        return f"https://cdn.discordapp.com/icons/{self.id}/{self.icon}.{ext}?size={size}"

    def banner_url(self, size: int = 128, fmt: str = "png") -> str | None:
        if self.banner is None:
            return None
        ext = "gif" if self.banner.startswith("a_") else fmt
        return f"https://cdn.discordapp.com/banners/{self.id}/{self.banner}.{ext}?size={size}"

    #  Live methods 

    async def fetch_channels(self) -> list[Channel]:
        """Get all channels in this guild. `GET /guilds/{id}/channels`"""
        if self._http is None:
            raise RuntimeError("Guild object has no HTTP client")
        data = await self._http.get(f"/guilds/{self.id}/channels")
        return [Channel(c, self._http) for c in data]

    async def create_channel(self, payload: dict[str, Any]) -> Channel:
        """Create a channel in this guild. `POST /guilds/{id}/channels`"""
        if self._http is None:
            raise RuntimeError("Guild object has no HTTP client")
        data = await self._http.post(f"/guilds/{self.id}/channels", json=payload)
        return Channel(data, self._http)

    async def fetch_members(self, *, limit: int = 1, after: int | str | None = None) -> list[Member]:
        """List members in this guild. `GET /guilds/{id}/members`"""
        if self._http is None:
            raise RuntimeError("Guild object has no HTTP client")
        params: dict[str, Any] = {"limit": limit}
        if after is not None:
            params["after"] = int(after)
        data = await self._http.get(f"/guilds/{self.id}/members", params=params)
        return [Member(m, self._http) for m in data]

    async def fetch_member(self, user_id: int | str) -> Member:
        """Get a specific member. `GET /guilds/{id}/members/{user_id}`"""
        if self._http is None:
            raise RuntimeError("Guild object has no HTTP client")
        data = await self._http.get(f"/guilds/{self.id}/members/{user_id}")
        return Member(data, self._http)

    async def search_members(self, query: str, *, limit: int = 1) -> list[Member]:
        """Search members by username prefix. `GET /guilds/{id}/members/search`"""
        if self._http is None:
            raise RuntimeError("Guild object has no HTTP client")
        data = await self._http.get(
            f"/guilds/{self.id}/members/search",
            params={"query": query, "limit": limit},
        )
        return [Member(m, self._http) for m in data]

    async def fetch_roles(self) -> list[Role]:
        """List all roles. `GET /guilds/{id}/roles`"""
        if self._http is None:
            raise RuntimeError("Guild object has no HTTP client")
        data = await self._http.get(f"/guilds/{self.id}/roles")
        return [Role(r, self._http) for r in data]

    async def create_role(self, payload: dict[str, Any]) -> Role:
        """Create a role. `POST /guilds/{id}/roles`"""
        if self._http is None:
            raise RuntimeError("Guild object has no HTTP client")
        data = await self._http.post(f"/guilds/{self.id}/roles", json=payload)
        return Role(data, self._http)

    async def fetch_emojis(self) -> list[Emoji]:
        """List all emojis. `GET /guilds/{id}/emojis`"""
        if self._http is None:
            raise RuntimeError("Guild object has no HTTP client")
        data = await self._http.get(f"/guilds/{self.id}/emojis")
        return [Emoji(e, self._http) for e in data]

    async def fetch_bans(self) -> list[dict[str, Any]]:
        """List bans. `GET /guilds/{id}/bans`"""
        if self._http is None:
            raise RuntimeError("Guild object has no HTTP client")
        return await self._http.get(f"/guilds/{self.id}/bans")

    async def ban_user(self, user_id: int | str, **kwargs: Any) -> None:
        """Ban a user from this guild. `PUT /guilds/{id}/bans/{user_id}`"""
        if self._http is None:
            raise RuntimeError("Guild object has no HTTP client")
        await self._http.put(f"/guilds/{self.id}/bans/{user_id}", json=kwargs or None)

    async def unban_user(self, user_id: int | str) -> None:
        """Unban a user. `DELETE /guilds/{id}/bans/{user_id}`"""
        if self._http is None:
            raise RuntimeError("Guild object has no HTTP client")
        await self._http.delete(f"/guilds/{self.id}/bans/{user_id}")

    async def fetch_audit_logs(
        self, *, limit: int = 50, user_id: int | str | None = None, action_type: int | None = None
    ) -> list[AuditLogEntry]:
        """Get the audit log. `GET /guilds/{id}/audit-logs`"""
        if self._http is None:
            raise RuntimeError("Guild object has no HTTP client")
        params: dict[str, Any] = {"limit": limit}
        if user_id is not None:
            params["user_id"] = int(user_id)
        if action_type is not None:
            params["action_type"] = action_type
        data = await self._http.get(f"/guilds/{self.id}/audit-logs", params=params)
        entries = data.get("audit_log_entries", [])
        return [AuditLogEntry(e, self._http) for e in entries]

    async def edit(self, payload: dict[str, Any]) -> Guild:
        """Edit this guild. `PATCH /guilds/{id}`"""
        if self._http is None:
            raise RuntimeError("Guild object has no HTTP client")
        data = await self._http.patch(f"/guilds/{self.id}", json=payload)
        return Guild(data, self._http)

    async def leave(self) -> None:
        """Leave this guild. `DELETE /users/@me/guilds/{id}`"""
        if self._http is None:
            raise RuntimeError("Guild object has no HTTP client")
        await self._http.delete(f"/users/@me/guilds/{self.id}")

    async def delete(self) -> None:
        """Delete this guild (must be owner). `DELETE /guilds/{id}`"""
        if self._http is None:
            raise RuntimeError("Guild object has no HTTP client")
        await self._http.delete(f"/guilds/{self.id}")


class GuildPreview(_BaseModel):
    """Partial guild info from the preview endpoint."""

    __slots__ = ()

    @property
    def id(self) -> int:
        return _parse_snowflake(self._data["id"])  # type: ignore[return-value]

    @property
    def name(self) -> str:
        return self._data["name"]

    @property
    def icon(self) -> str | None:
        return self._data.get("icon")

    @property
    def description(self) -> str | None:
        return self._data.get("description")

    @property
    def approximate_member_count(self) -> int:
        return self._data["approximate_member_count"]

    @property
    def approximate_presence_count(self) -> int:
        return self._data["approximate_presence_count"]

    @property
    def emojis(self) -> list[Emoji]:
        return [Emoji(e, self._http) for e in self._data.get("emojis", [])]

    @property
    def features(self) -> list[str]:
        return self._data.get("features", [])



# Channel



class Channel(_BaseModel):
    """Represents a Discord channel.

    This is a "live" object — you can call methods directly on it::

        channel = await client.fetch_channel(channel_id)
        await channel.send("Hello!")
        messages = await channel.fetch_messages(limit=10)
        await channel.edit(name="new-name")

    Channel type constants:
        TEXT = 0, DM = 1, VOICE = 2, GROUP_DM = 3, CATEGORY = 4,
        ANNOUNCEMENT = 5, ANNOUNCEMENT_THREAD = 10, PUBLIC_THREAD = 11,
        PRIVATE_THREAD = 12, STAGE = 13, FORUM = 15
    """

    # Channel type constants
    TEXT = 0
    DM = 1
    VOICE = 2
    GROUP_DM = 3
    CATEGORY = 4
    ANNOUNCEMENT = 5
    ANNOUNCEMENT_THREAD = 10
    PUBLIC_THREAD = 11
    PRIVATE_THREAD = 12
    STAGE = 13
    FORUM = 15

    __slots__ = ()

    @property
    def id(self) -> int:
        return _parse_snowflake(self._data["id"])  # type: ignore[return-value]

    @property
    def type(self) -> int:
        return self._data["type"]

    @property
    def guild_id(self) -> int | None:
        return _parse_snowflake(self._data.get("guild_id"))

    @property
    def position(self) -> int | None:
        return self._data.get("position")

    @property
    def name(self) -> str | None:
        return self._data.get("name")

    @property
    def topic(self) -> str | None:
        return self._data.get("topic")

    @property
    def nsfw(self) -> bool:
        return self._data.get("nsfw", False)

    @property
    def last_message_id(self) -> int | None:
        return _parse_snowflake(self._data.get("last_message_id"))

    @property
    def bitrate(self) -> int | None:
        return self._data.get("bitrate")

    @property
    def user_limit(self) -> int | None:
        return self._data.get("user_limit")

    @property
    def parent_id(self) -> int | None:
        return _parse_snowflake(self._data.get("parent_id"))

    @property
    def rate_limit_per_user(self) -> int | None:
        return self._data.get("rate_limit_per_user")

    @property
    def permission_overwrites(self) -> list[PermissionOverwrite]:
        return [PermissionOverwrite(o, self._http) for o in self._data.get("permission_overwrites", [])]

    @property
    def default_auto_archive_duration(self) -> int | None:
        return self._data.get("default_auto_archive_duration")

    @property
    def flags(self) -> int | None:
        return self._data.get("flags")

    @property
    def default_thread_rate_limit_per_user(self) -> int | None:
        return self._data.get("default_thread_rate_limit_per_user")

    @property
    def default_reaction_emoji(self) -> Emoji | None:
        raw = self._data.get("default_reaction_emoji")
        return Emoji(raw, self._http) if raw else None

    @property
    def available_tags(self) -> list[dict[str, Any]]:
        return self._data.get("available_tags", [])

    @property
    def default_sort_order(self) -> int | None:
        return self._data.get("default_sort_order")

    @property
    def default_layout(self) -> int | None:
        return self._data.get("default_layout")

    @property
    def type_name(self) -> str:
        """Human-readable channel type name."""
        _types = {
            0: "text", 1: "dm", 2: "voice", 3: "group_dm",
            4: "category", 5: "announcement", 10: "announcement_thread",
            11: "public_thread", 12: "private_thread", 13: "stage", 15: "forum",
        }
        return _types.get(self.type, "unknown")

    #  Live methods 

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
        """Send a message to this channel.

        Usage::

            channel = await client.fetch_channel(channel_id)
            msg = await channel.send(content="Hello!", tts=False)
            await channel.send(embeds=[embed])
            await channel.send(view=my_layout_view)
        """
        if self._http is None:
            raise RuntimeError("Channel object has no HTTP client")

        from .ui.view import LayoutView

        payload: dict[str, Any] = {}

        # Components V2: view takes precedence
        if view is not None and isinstance(view, LayoutView):
            view_payload = view.to_payload()
            payload.update(view_payload)
        else:
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
            import json
            import aiohttp
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
                f"/channels/{self.id}/messages",
                data=form,
                headers={"Content-Type": None},
            )
        else:
            data = await self._http.post(
                f"/channels/{self.id}/messages",
                json=payload,
            )
        return Message(data, self._http)

    async def fetch_messages(
        self,
        *,
        around: int | str | None = None,
        before: int | str | None = None,
        after: int | str | None = None,
        limit: int = 50,
    ) -> list[Message]:
        """List messages in this channel. `GET /channels/{id}/messages`"""
        if self._http is None:
            raise RuntimeError("Channel object has no HTTP client")
        params: dict[str, Any] = {"limit": limit}
        if around is not None:
            params["around"] = int(around)
        if before is not None:
            params["before"] = int(before)
        if after is not None:
            params["after"] = int(after)
        data = await self._http.get(f"/channels/{self.id}/messages", params=params)
        return [Message(m, self._http) for m in data]

    async def fetch_message(self, message_id: int | str) -> Message:
        """Get a specific message. `GET /channels/{id}/messages/{message_id}`"""
        if self._http is None:
            raise RuntimeError("Channel object has no HTTP client")
        data = await self._http.get(f"/channels/{self.id}/messages/{message_id}")
        return Message(data, self._http)

    async def edit(
        self,
        *,
        name: str | None = None,
        topic: str | None = None,
        position: int | None = None,
        nsfw: bool | None = None,
        bitrate: int | None = None,
        user_limit: int | None = None,
        rate_limit_per_user: int | None = None,
        parent_id: int | str | None = None,
        **kwargs: Any,
    ) -> Channel:
        """Edit this channel. `PATCH /channels/{id}`"""
        if self._http is None:
            raise RuntimeError("Channel object has no HTTP client")
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if topic is not None:
            payload["topic"] = topic
        if position is not None:
            payload["position"] = position
        if nsfw is not None:
            payload["nsfw"] = nsfw
        if bitrate is not None:
            payload["bitrate"] = bitrate
        if user_limit is not None:
            payload["user_limit"] = user_limit
        if rate_limit_per_user is not None:
            payload["rate_limit_per_user"] = rate_limit_per_user
        if parent_id is not None:
            payload["parent_id"] = int(parent_id)
        payload.update(kwargs)
        data = await self._http.patch(f"/channels/{self.id}", json=payload)
        return Channel(data, self._http)

    async def delete(self) -> None:
        """Delete this channel. `DELETE /channels/{id}`"""
        if self._http is None:
            raise RuntimeError("Channel object has no HTTP client")
        await self._http.delete(f"/channels/{self.id}")

    async def typing(self) -> None:
        """Trigger a typing indicator. `POST /channels/{id}/typing`"""
        if self._http is None:
            raise RuntimeError("Channel object has no HTTP client")
        await self._http.post(f"/channels/{self.id}/typing")

    async def fetch_invites(self) -> list[dict[str, Any]]:
        """List invites for this channel. `GET /channels/{id}/invites`"""
        if self._http is None:
            raise RuntimeError("Channel object has no HTTP client")
        return await self._http.get(f"/channels/{self.id}/invites")

    async def set_permissions(
        self,
        overwrite_id: int | str,
        *,
        allow: str | None = None,
        deny: str | None = None,
        type: int = 0,
    ) -> None:
        """Set a permission overwrite. `PUT /channels/{id}/permissions/{overwrite_id}`"""
        if self._http is None:
            raise RuntimeError("Channel object has no HTTP client")
        payload: dict[str, Any] = {"type": type}
        if allow is not None:
            payload["allow"] = allow
        if deny is not None:
            payload["deny"] = deny
        await self._http.put(
            f"/channels/{self.id}/permissions/{overwrite_id}",
            json=payload,
        )

    async def follow(self, webhook_channel_id: int | str) -> dict[str, Any]:
        """Follow an announcement channel. `POST /channels/{id}/followers`"""
        if self._http is None:
            raise RuntimeError("Channel object has no HTTP client")
        return await self._http.post(
            f"/channels/{self.id}/followers",
            json={"webhook_channel_id": int(webhook_channel_id)},
        )



# Message



class Message(_BaseModel):
    """Represents a Discord message.

    This is a "live" object — you can call methods directly on it::

        message = await channel.fetch_message(msg_id)
        await message.edit(content="Edited!")
        await message.delete(reason="Cleanup")
        await message.pin()
    """

    __slots__ = ()

    @property
    def id(self) -> int:
        return _parse_snowflake(self._data["id"])  # type: ignore[return-value]

    @property
    def channel_id(self) -> int:
        return _parse_snowflake(self._data["channel_id"])  # type: ignore[return-value]

    @property
    def guild_id(self) -> int | None:
        return _parse_snowflake(self._data.get("guild_id"))

    @property
    def author(self) -> User | None:
        raw = self._data.get("author")
        return User(raw, self._http) if raw else None

    @property
    def content(self) -> str:
        return self._data.get("content", "")

    @property
    def timestamp(self) -> datetime | None:
        return _parse_iso(self._data.get("timestamp"))

    @property
    def edited_timestamp(self) -> datetime | None:
        return _parse_iso(self._data.get("edited_timestamp"))

    @property
    def tts(self) -> bool:
        return self._data.get("tts", False)

    @property
    def mention_everyone(self) -> bool:
        return self._data.get("mention_everyone", False)

    @property
    def mentions(self) -> list[User]:
        return [User(u, self._http) for u in self._data.get("mentions", [])]

    @property
    def mention_roles(self) -> list[int]:
        return [int(r) for r in self._data.get("mention_roles", [])]

    @property
    def mention_channels(self) -> list[Channel]:
        return [Channel(c, self._http) for c in self._data.get("mention_channels", [])]

    @property
    def attachments(self) -> list[Attachment]:
        return [Attachment(a, self._http) for a in self._data.get("attachments", [])]

    @property
    def embeds(self) -> list[Embed]:
        return [Embed(e, self._http) for e in self._data.get("embeds", [])]

    @property
    def reactions(self) -> list[dict[str, Any]]:
        return self._data.get("reactions", [])

    @property
    def pinned(self) -> bool:
        return self._data.get("pinned", False)

    @property
    def type(self) -> int:
        return self._data.get("type", 0)

    @property
    def flags(self) -> int | None:
        return self._data.get("flags")

    @property
    def message_reference(self) -> dict[str, Any] | None:
        return self._data.get("message_reference")

    @property
    def interaction(self) -> dict[str, Any] | None:
        return self._data.get("interaction")

    @property
    def components(self) -> list[dict[str, Any]]:
        return self._data.get("components", [])

    @property
    def sticker_items(self) -> list[dict[str, Any]]:
        return self._data.get("sticker_items", [])

    @property
    def thread(self) -> Channel | None:
        raw = self._data.get("thread")
        return Channel(raw, self._http) if raw else None

    #  Live methods 

    async def edit(
        self,
        *,
        content: str | None = None,
        embeds: list[Embed | dict[str, Any]] | None = None,
        flags: int | None = None,
        allowed_mentions: dict[str, Any] | None = None,
        components: list[dict[str, Any]] | None = None,
        attachments: list[dict[str, Any]] | None = None,
        view: Any | None = None,
    ) -> Message:
        """Edit this message. `PATCH /channels/{channel_id}/messages/{id}`"""
        if self._http is None:
            raise RuntimeError("Message object has no HTTP client")

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
            f"/channels/{self.channel_id}/messages/{self.id}",
            json=payload,
        )
        return Message(data, self._http)

    async def delete(self, *, reason: str | None = None) -> None:
        """Delete this message. `DELETE /channels/{channel_id}/messages/{id}`"""
        if self._http is None:
            raise RuntimeError("Message object has no HTTP client")
        headers = {}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        await self._http.delete(
            f"/channels/{self.channel_id}/messages/{self.id}",
            headers=headers or None,
        )

    async def pin(self) -> None:
        """Pin this message. `PUT /channels/{channel_id}/pins/{id}`"""
        if self._http is None:
            raise RuntimeError("Message object has no HTTP client")
        await self._http.put(f"/channels/{self.channel_id}/pins/{self.id}")

    async def unpin(self) -> None:
        """Unpin this message. `DELETE /channels/{channel_id}/pins/{id}`"""
        if self._http is None:
            raise RuntimeError("Message object has no HTTP client")
        await self._http.delete(f"/channels/{self.channel_id}/pins/{self.id}")

    async def add_reaction(self, emoji: str) -> None:
        """Add a reaction. `PUT /channels/{channel_id}/messages/{id}/reactions/{emoji}/@me`"""
        if self._http is None:
            raise RuntimeError("Message object has no HTTP client")
        await self._http.put(
            f"/channels/{self.channel_id}/messages/{self.id}/reactions/{emoji}/@me"
        )

    async def remove_reaction(self, emoji: str) -> None:
        """Remove your reaction. `DELETE /channels/{channel_id}/messages/{id}/reactions/{emoji}/@me`"""
        if self._http is None:
            raise RuntimeError("Message object has no HTTP client")
        await self._http.delete(
            f"/channels/{self.channel_id}/messages/{self.id}/reactions/{emoji}/@me"
        )

    async def crosspost(self) -> Message:
        """Crosspost (publish) an announcement. `POST /channels/{channel_id}/messages/{id}/crosspost`"""
        if self._http is None:
            raise RuntimeError("Message object has no HTTP client")
        data = await self._http.post(
            f"/channels/{self.channel_id}/messages/{self.id}/crosspost"
        )
        return Message(data, self._http)



# Role



class Role(_BaseModel):
    """Represents a Discord role."""

    __slots__ = ()

    @property
    def id(self) -> int:
        return _parse_snowflake(self._data["id"])  # type: ignore[return-value]

    @property
    def name(self) -> str:
        return self._data["name"]

    @property
    def color(self) -> int:
        return self._data.get("color", 0)

    @property
    def hoist(self) -> bool:
        return self._data.get("hoist", False)

    @property
    def icon(self) -> str | None:
        return self._data.get("icon")

    @property
    def unicode_emoji(self) -> str | None:
        return self._data.get("unicode_emoji")

    @property
    def position(self) -> int:
        return self._data.get("position", 0)

    @property
    def permissions(self) -> str:
        return str(self._data.get("permissions", "0"))

    @property
    def managed(self) -> bool:
        return self._data.get("managed", False)

    @property
    def mentionable(self) -> bool:
        return self._data.get("mentionable", False)

    @property
    def tags(self) -> dict[str, Any] | None:
        return self._data.get("tags")

    #  Live methods 

    async def edit(self, payload: dict[str, Any]) -> Role:
        """Edit this role. `PATCH /guilds/{guild_id}/roles/{id}`"""
        if self._http is None:
            raise RuntimeError("Role object has no HTTP client")
        guild_id = self._data.get("guild_id")
        if guild_id is None:
            raise ValueError("Role object has no guild_id")
        data = await self._http.patch(f"/guilds/{guild_id}/roles/{self.id}", json=payload)
        return Role(data, self._http)

    async def delete(self) -> None:
        """Delete this role. `DELETE /guilds/{guild_id}/roles/{id}`"""
        if self._http is None:
            raise RuntimeError("Role object has no HTTP client")
        guild_id = self._data.get("guild_id")
        if guild_id is None:
            raise ValueError("Role object has no guild_id")
        await self._http.delete(f"/guilds/{guild_id}/roles/{self.id}")



# Emoji



class Emoji(_BaseModel):
    """Represents a Discord emoji."""

    __slots__ = ()

    @property
    def id(self) -> int | None:
        return _parse_snowflake(self._data.get("id"))

    @property
    def name(self) -> str | None:
        return self._data.get("name")

    @property
    def roles(self) -> list[int]:
        return [int(r) for r in self._data.get("roles", [])]

    @property
    def user(self) -> User | None:
        raw = self._data.get("user")
        return User(raw, self._http) if raw else None

    @property
    def require_colons(self) -> bool:
        return self._data.get("require_colons", False)

    @property
    def managed(self) -> bool:
        return self._data.get("managed", False)

    @property
    def available(self) -> bool:
        return self._data.get("available", True)

    def url(self, size: int = 128) -> str | None:
        if self.id is None:
            return None
        ext = "gif" if self._data.get("animated") else "png"
        return f"https://cdn.discordapp.com/emojis/{self.id}.{ext}?size={size}"

    async def delete(self) -> None:
        """Delete this emoji. `DELETE /guilds/{guild_id}/emojis/{id}`"""
        if self._http is None:
            raise RuntimeError("Emoji object has no HTTP client")
        guild_id = self._data.get("guild_id")
        if guild_id is None:
            raise ValueError("Emoji object has no guild_id")
        await self._http.delete(f"/guilds/{guild_id}/emojis/{self.id}")



# Attachment



class Attachment(_BaseModel):
    """Represents a message attachment."""

    __slots__ = ()

    @property
    def id(self) -> int:
        return _parse_snowflake(self._data["id"])  # type: ignore[return-value]

    @property
    def filename(self) -> str:
        return self._data["filename"]

    @property
    def description(self) -> str | None:
        return self._data.get("description")

    @property
    def content_type(self) -> str | None:
        return self._data.get("content_type")

    @property
    def size(self) -> int:
        return self._data["size"]

    @property
    def url(self) -> str:
        return self._data["url"]

    @property
    def proxy_url(self) -> str:
        return self._data["proxy_url"]

    @property
    def height(self) -> int | None:
        return self._data.get("height")

    @property
    def width(self) -> int | None:
        return self._data.get("width")

    @property
    def ephemeral(self) -> bool:
        return self._data.get("ephemeral", False)

    @property
    def duration_secs(self) -> float | None:
        return self._data.get("duration_secs")

    @property
    def waveform(self) -> str | None:
        return self._data.get("waveform")

    @property
    def flags(self) -> int | None:
        return self._data.get("flags")



# Embed



class Embed(_BaseModel):
    """Represents a Discord embed.

    Can be used in two ways:

    **1. Builder (for sending):**

        embed = Embed(title="Hello", description="World", color=0x5865F2)
        embed.set_thumbnail(url="https://example.com/thumb.png")
        embed.add_field(name="Field 1", value="Value 1")

        await channel.send(embeds=[embed])

    **2. Read-only (from API responses):**

        message = await channel.fetch_message(msg_id)
        for embed in message.embeds:
            print(embed.title)
    """

    __slots__ = ("_fields",)

    def __init__(
        self,
        data: dict[str, Any] | None = None,
        http: HTTPClient | None = None,
        *,
        title: str | None = None,
        description: str | None = None,
        url: str | None = None,
        color: int | str | None = None,
        timestamp: str | datetime | None = None,
    ):
        if data is not None:
            # Reading from API — use provided data
            super().__init__(data, http)
        else:
            # Builder mode — construct from kwargs
            init_data: dict[str, Any] = {}
            if title is not None:
                init_data["title"] = title
            if description is not None:
                init_data["description"] = description
            if url is not None:
                init_data["url"] = url
            if color is not None:
                init_data["color"] = _parse_color(color)
            if timestamp is not None:
                if isinstance(timestamp, datetime):
                    init_data["timestamp"] = timestamp.isoformat()
                else:
                    init_data["timestamp"] = timestamp
            super().__init__(init_data, http)

    # Read-only properties

    @property
    def title(self) -> str | None:
        return self._data.get("title")

    @property
    def type(self) -> str | None:
        return self._data.get("type")

    @property
    def description(self) -> str | None:
        return self._data.get("description")

    @property
    def url(self) -> str | None:
        return self._data.get("url")

    @property
    def timestamp(self) -> datetime | None:
        return _parse_iso(self._data.get("timestamp"))

    @property
    def color(self) -> int | None:
        return self._data.get("color")

    @property
    def footer(self) -> EmbedFooter | None:
        raw = self._data.get("footer")
        return EmbedFooter(raw, self._http) if raw else None

    @property
    def image(self) -> EmbedImage | None:
        raw = self._data.get("image")
        return EmbedImage(raw, self._http) if raw else None

    @property
    def thumbnail(self) -> EmbedImage | None:
        raw = self._data.get("thumbnail")
        return EmbedImage(raw, self._http) if raw else None

    @property
    def video(self) -> EmbedImage | None:
        raw = self._data.get("video")
        return EmbedImage(raw, self._http) if raw else None

    @property
    def provider(self) -> dict[str, Any] | None:
        return self._data.get("provider")

    @property
    def author(self) -> EmbedAuthor | None:
        raw = self._data.get("author")
        return EmbedAuthor(raw, self._http) if raw else None

    @property
    def fields(self) -> list[EmbedField]:
        return [EmbedField(f, self._http) for f in self._data.get("fields", [])]

    # Class methods

    @classmethod
    def from_dict(cls, data: dict[str, Any], http: HTTPClient | None = None) -> Embed:
        """Create an Embed from a raw API payload dict."""
        instance = cls.__new__(cls)
        object.__setattr__(instance, "_data", dict(data))
        object.__setattr__(instance, "_http", http)
        return instance

    # Builder methods (mutate in-place, return self for chaining)

    def set_title(self, title: str) -> Embed:
        self._data["title"] = title
        return self

    def set_description(self, description: str) -> Embed:
        self._data["description"] = description
        return self

    def set_url(self, url: str) -> Embed:
        self._data["url"] = url
        return self

    def set_color(self, color: int | str) -> Embed:
        self._data["color"] = _parse_color(color)
        return self

    def set_timestamp(self, timestamp: str | datetime | None = None) -> Embed:
        if timestamp is None:
            timestamp = datetime.now().astimezone()
        if isinstance(timestamp, datetime):
            self._data["timestamp"] = timestamp.isoformat()
        else:
            self._data["timestamp"] = timestamp
        return self

    def set_author(
        self,
        *,
        name: str,
        url: str | None = None,
        icon_url: str | None = None,
        proxy_icon_url: str | None = None,
    ) -> Embed:
        author: dict[str, Any] = {"name": name}
        if url is not None:
            author["url"] = url
        if icon_url is not None:
            author["icon_url"] = icon_url
        if proxy_icon_url is not None:
            author["proxy_icon_url"] = proxy_icon_url
        self._data["author"] = author
        return self

    def set_footer(
        self,
        *,
        text: str,
        icon_url: str | None = None,
        proxy_icon_url: str | None = None,
    ) -> Embed:
        footer: dict[str, Any] = {"text": text}
        if icon_url is not None:
            footer["icon_url"] = icon_url
        if proxy_icon_url is not None:
            footer["proxy_icon_url"] = proxy_icon_url
        self._data["footer"] = footer
        return self

    def set_image(self, *, url: str, proxy_url: str | None = None, height: int | None = None, width: int | None = None) -> Embed:
        image: dict[str, Any] = {"url": url}
        if proxy_url is not None:
            image["proxy_url"] = proxy_url
        if height is not None:
            image["height"] = height
        if width is not None:
            image["width"] = width
        self._data["image"] = image
        return self

    def set_thumbnail(self, *, url: str, proxy_url: str | None = None, height: int | None = None, width: int | None = None) -> Embed:
        thumb: dict[str, Any] = {"url": url}
        if proxy_url is not None:
            thumb["proxy_url"] = proxy_url
        if height is not None:
            thumb["height"] = height
        if width is not None:
            thumb["width"] = width
        self._data["thumbnail"] = thumb
        return self

    def add_field(self, *, name: str, value: str, inline: bool = False) -> Embed:
        if "fields" not in self._data:
            self._data["fields"] = []
        self._data["fields"].append({"name": name, "value": value, "inline": inline})
        return self

    def remove_field(self, index: int) -> Embed:
        fields = self._data.get("fields", [])
        if 0 <= index < len(fields):
            fields.pop(index)
        return self

    def clear_fields(self) -> Embed:
        self._data["fields"] = []
        return self

    def insert_field(self, index: int, *, name: str, value: str, inline: bool = False) -> Embed:
        if "fields" not in self._data:
            self._data["fields"] = []
        self._data["fields"].insert(index, {"name": name, "value": value, "inline": inline})
        return self

    def set_video(self, *, url: str, height: int | None = None, width: int | None = None) -> Embed:
        video: dict[str, Any] = {"url": url}
        if height is not None:
            video["height"] = height
        if width is not None:
            video["width"] = width
        self._data["video"] = video
        return self

    def to_dict(self) -> dict[str, Any]:
        """Return the payload dict suitable for sending to Discord."""
        return dict(self._data)

    def __repr__(self) -> str:
        title = self.title
        desc = self.description
        if title and desc:
            return f"<Embed title='{title}' description='{desc[:50]}...'>"
        if title:
            return f"<Embed title='{title}'>"
        if desc:
            return f"<Embed description='{desc[:50]}...'>"
        return "<Embed empty>"


class EmbedField(_BaseModel):
    """A single field inside an embed."""

    __slots__ = ()

    @property
    def name(self) -> str:
        return self._data.get("name", "")

    @property
    def value(self) -> str:
        return self._data.get("value", "")

    @property
    def inline(self) -> bool:
        return self._data.get("inline", False)

    def __repr__(self) -> str:
        return f"<EmbedField name='{self.name}' inline={self.inline}>"


class EmbedFooter(_BaseModel):
    """The footer of an embed."""

    __slots__ = ()

    @property
    def text(self) -> str:
        return self._data.get("text", "")

    @property
    def icon_url(self) -> str | None:
        return self._data.get("icon_url")

    @property
    def proxy_icon_url(self) -> str | None:
        return self._data.get("proxy_icon_url")


class EmbedImage(_BaseModel):
    """An image, thumbnail, or video inside an embed."""

    __slots__ = ()

    @property
    def url(self) -> str:
        return self._data.get("url", "")

    @property
    def proxy_url(self) -> str | None:
        return self._data.get("proxy_url")

    @property
    def height(self) -> int | None:
        return self._data.get("height")

    @property
    def width(self) -> int | None:
        return self._data.get("width")


class EmbedAuthor(_BaseModel):
    """The author of an embed."""

    __slots__ = ()

    @property
    def name(self) -> str:
        return self._data.get("name", "")

    @property
    def url(self) -> str | None:
        return self._data.get("url")

    @property
    def icon_url(self) -> str | None:
        return self._data.get("icon_url")

    @property
    def proxy_icon_url(self) -> str | None:
        return self._data.get("proxy_icon_url")



# PermissionOverwrite



class PermissionOverwrite(_BaseModel):
    """Represents a permission overwrite for a channel."""

    __slots__ = ()

    @property
    def id(self) -> int:
        return _parse_snowflake(self._data["id"])  # type: ignore[return-value]

    @property
    def type(self) -> int:
        return self._data["type"]

    @property
    def allow(self) -> str:
        return str(self._data.get("allow", "0"))

    @property
    def deny(self) -> str:
        return str(self._data.get("deny", "0"))



# Voice Region



class VoiceRegion(_BaseModel):
    """Represents a voice region."""

    __slots__ = ()

    @property
    def id(self) -> str:
        return self._data["id"]

    @property
    def name(self) -> str:
        return self._data["name"]

    @property
    def vip(self) -> bool:
        return self._data.get("vip", False)

    @property
    def optimal(self) -> bool:
        return self._data.get("optimal", False)

    @property
    def deprecated(self) -> bool:
        return self._data.get("deprecated", False)

    @property
    def custom(self) -> bool:
        return self._data.get("custom", False)

    @property
    def regions(self) -> str | None:
        return self._data.get("regions")



# Integration



class Integration(_BaseModel):
    """Represents a guild integration."""

    __slots__ = ()

    @property
    def id(self) -> int:
        return _parse_snowflake(self._data["id"])  # type: ignore[return-value]

    @property
    def name(self) -> str:
        return self._data["name"]

    @property
    def type(self) -> str:
        return self._data["type"]

    @property
    def enabled(self) -> bool:
        return self._data.get("enabled", False)

    @property
    def syncing(self) -> bool:
        return self._data.get("syncing", False)

    @property
    def role_id(self) -> int | None:
        return _parse_snowflake(self._data.get("role_id"))

    @property
    def enable_emoticons(self) -> bool | None:
        return self._data.get("enable_emoticons")

    @property
    def expire_behavior(self) -> int | None:
        return self._data.get("expire_behavior")

    @property
    def expire_grace_period(self) -> int | None:
        return self._data.get("expire_grace_period")

    @property
    def user(self) -> User | None:
        raw = self._data.get("user")
        return User(raw, self._http) if raw else None

    @property
    def account(self) -> dict[str, Any]:
        return self._data.get("account", {})

    @property
    def synced_at(self) -> datetime | None:
        return _parse_iso(self._data.get("synced_at"))



# Audit Log



class AuditLogEntry(_BaseModel):
    """Represents an entry in the audit log."""

    __slots__ = ()

    @property
    def id(self) -> int:
        return _parse_snowflake(self._data["id"])  # type: ignore[return-value]

    @property
    def user_id(self) -> int | None:
        return _parse_snowflake(self._data.get("user_id"))

    @property
    def target_id(self) -> int | None:
        return _parse_snowflake(self._data.get("target_id"))

    @property
    def action_type(self) -> int:
        return self._data["action_type"]

    @property
    def options(self) -> dict[str, Any] | None:
        return self._data.get("options")

    @property
    def changes(self) -> list[dict[str, Any]]:
        return self._data.get("changes", [])

    @property
    def reason(self) -> str | None:
        return self._data.get("reason")



# Webhook



class Webhook(_BaseModel):
    """Represents a webhook.

    Live methods::

        webhook = await client.fetch_webhook(webhook_id)
        await webhook.execute(content="Hello!", username="Bot")
        await webhook.edit(name="New Name")
        await webhook.delete()
    """

    __slots__ = ()

    @property
    def id(self) -> int:
        return _parse_snowflake(self._data["id"])  # type: ignore[return-value]

    @property
    def type(self) -> int:
        return self._data["type"]

    @property
    def guild_id(self) -> int | None:
        return _parse_snowflake(self._data.get("guild_id"))

    @property
    def channel_id(self) -> int | None:
        return _parse_snowflake(self._data.get("channel_id"))

    @property
    def user(self) -> User | None:
        raw = self._data.get("user")
        return User(raw, self._http) if raw else None

    @property
    def name(self) -> str | None:
        return self._data.get("name")

    @property
    def avatar(self) -> str | None:
        return self._data.get("avatar")

    @property
    def token(self) -> str | None:
        return self._data.get("token")

    @property
    def application_id(self) -> int | None:
        return _parse_snowflake(self._data.get("application_id"))

    @property
    def url(self) -> str | None:
        return self._data.get("url")

    #  Live methods 

    async def execute(
        self,
        *,
        content: str | None = None,
        embeds: list[Embed | dict[str, Any]] | None = None,
        username: str | None = None,
        avatar_url: str | None = None,
        tts: bool = False,
        wait: bool = False,
        thread_id: int | str | None = None,
        view: Any | None = None,
    ) -> Message | None:
        """Execute (send via) this webhook."""
        if self._http is None:
            raise RuntimeError("Webhook object has no HTTP client")
        if self.token is None:
            raise ValueError("Webhook has no token — cannot execute")

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

        if view is not None and isinstance(view, LayoutView):
            params["with_components"] = "true"

        data = await self._http.post(
            f"/webhooks/{self.id}/{self.token}",
            json=payload,
            params=params,
        )
        if data is None:
            return None
        return Message(data, self._http)

    async def edit(self, payload: dict[str, Any]) -> Webhook:
        """Edit this webhook. `PATCH /webhooks/{id}`"""
        if self._http is None:
            raise RuntimeError("Webhook object has no HTTP client")
        data = await self._http.patch(f"/webhooks/{self.id}", json=payload)
        return Webhook(data, self._http)

    async def delete(self) -> None:
        """Delete this webhook. `DELETE /webhooks/{id}`"""
        if self._http is None:
            raise RuntimeError("Webhook object has no HTTP client")
        await self._http.delete(f"/webhooks/{self.id}")



# Helper: serialize embeds



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
