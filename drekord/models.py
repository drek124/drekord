"""Drekord data models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional


def _parse_snowflake(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)


def _parse_iso(value: Any) -> datetime | None:
    if value is None:
        return None
    # Discord uses ISO-8601 with 'T' separator and 'Z' suffix
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _parse_color(value: int | str) -> int:
    """Parse a color value (``0x5865F2`` or ``'#5865F2'``) into an int :3."""
    if isinstance(value, int):
        return value
    # Strip leading '#' or '0x'
    hex_str = value.lstrip("#").lstrip("0x")
    return int(hex_str, 16)


class _BaseModel:
    """Thin wrapper around a raw payload dict providing attribute access."""

    __slots__ = ("_data",)

    def __init__(self, data: dict[str, Any]):
        object.__setattr__(self, "_data", data)

    # attribute / item access 

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



# Discord Snowflake IDs


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
    """Represents a Discord user."""

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

    def display_name(self) -> str:
        """Return the best available display name."""
        return self.global_name or self.username

    def avatar_url(self, size: int = 128, fmt: str = "png") -> str | None:
        """Build the avatar CDN URL."""
        if self.avatar is None:
            return None
        ext = "gif" if self.avatar.startswith("a_") else fmt
        return f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.{ext}?size={size}"



# Member (Guild member = User + guild-specific data)


class Member(_BaseModel):
    """Represents a guild member (a user within a guild)."""

    __slots__ = ()

    @property
    def user(self) -> User:
        return User(self._data["user"])

    @property
    def nick(self) -> str | None:
        return self._data.get("nick")

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

    def display_name(self) -> str:
        return self.nick or self.user.display_name()



# Guild


class Guild(_BaseModel):
    """Represents a Discord guild (server)."""

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
        return [Role(r) for r in self._data.get("roles", [])]

    @property
    def emojis(self) -> list[Emoji]:
        return [Emoji(e) for e in self._data.get("emojis", [])]

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


class GuildPreview(_BaseModel):
    """Partial guild info from the preview endpoint (no auth required for discovery)."""

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
        return [Emoji(e) for e in self._data.get("emojis", [])]

    @property
    def features(self) -> list[str]:
        return self._data.get("features", [])



# Channel


class Channel(_BaseModel):
    """Represents a Discord channel."""

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
        return [PermissionOverwrite(o) for o in self._data.get("permission_overwrites", [])]

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
        return Emoji(raw) if raw else None

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
            0: "text",
            1: "dm",
            2: "voice",
            3: "group_dm",
            4: "category",
            5: "announcement",
            10: "announcement_thread",
            11: "public_thread",
            12: "private_thread",
            13: "stage",
            15: "forum",
        }
        return _types.get(self.type, "unknown")



# Message


class Message(_BaseModel):
    """Represents a Discord message."""

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
        return User(raw) if raw else None

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
        return [User(u) for u in self._data.get("mentions", [])]

    @property
    def mention_roles(self) -> list[int]:
        return [int(r) for r in self._data.get("mention_roles", [])]

    @property
    def mention_channels(self) -> list[Channel]:
        return [Channel(c) for c in self._data.get("mention_channels", [])]

    @property
    def attachments(self) -> list[Attachment]:
        return [Attachment(a) for a in self._data.get("attachments", [])]

    @property
    def embeds(self) -> list[Embed]:
        return [Embed(e) for e in self._data.get("embeds", [])]

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
        return Channel(raw) if raw else None



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
        return User(raw) if raw else None

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



# Embed (builder for outbound, read-only wrapper for inbound)


class Embed(_BaseModel):
    """Represents a Discord embed.

    Can be used in two ways:

    **1. Builder (for sending):**

        embed = Embed(title="Hello", description="World", color=0x5865F2)
        embed.set_thumbnail(url="https://example.com/thumb.png")
        embed.add_field(name="Field 1", value="Value 1")
        embed.add_field(name="Field 2", value="Value 2", inline=True)
        embed.set_footer(text="Footer text", icon_url="https://example.com/icon.png")
        embed.set_image(url="https://example.com/image.png")
        embed.set_author(name="Author", url="https://example.com", icon_url="https://example.com/icon.png")

        await client.messages.channel(ch).send(embeds=[embed])

    **2. Read-only (from API responses):**

        msg = await client.messages.channel(ch).get(msg_id)
        for embed in msg.embeds:
            print(embed.title)
            print(embed.description)
            for field in embed.fields:
                print(f"  {field.name}: {field.value}")
    """

    __slots__ = ("_fields",)

    def __init__(
        self,
        *,
        title: str | None = None,
        description: str | None = None,
        url: str | None = None,
        color: int | str | None = None,
        timestamp: str | datetime | None = None,
    ):
        data: dict[str, Any] = {}
        if title is not None:
            data["title"] = title
        if description is not None:
            data["description"] = description
        if url is not None:
            data["url"] = url
        if color is not None:
            data["color"] = _parse_color(color)
        if timestamp is not None:
            if isinstance(timestamp, datetime):
                data["timestamp"] = timestamp.isoformat()
            else:
                data["timestamp"] = timestamp
        super().__init__(data)

    #  Read-only properties 

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
        return EmbedFooter(raw) if raw else None

    @property
    def image(self) -> EmbedImage | None:
        raw = self._data.get("image")
        return EmbedImage(raw) if raw else None

    @property
    def thumbnail(self) -> EmbedImage | None:
        raw = self._data.get("thumbnail")
        return EmbedImage(raw) if raw else None

    @property
    def video(self) -> EmbedImage | None:
        raw = self._data.get("video")
        return EmbedImage(raw) if raw else None

    @property
    def provider(self) -> dict[str, Any] | None:
        return self._data.get("provider")

    @property
    def author(self) -> EmbedAuthor | None:
        raw = self._data.get("author")
        return EmbedAuthor(raw) if raw else None

    @property
    def fields(self) -> list[EmbedField]:
        return [EmbedField(f) for f in self._data.get("fields", [])]

    # Class methods

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Embed:
        """Create an Embed from a raw API payload dict (for reading inbound embeds)."""
        instance = cls.__new__(cls)
        object.__setattr__(instance, "_data", dict(data))
        return instance

    # Builder methods (mutate in-place, return self for chaining)

    def set_title(self, title: str) -> Embed:
        """Set the embed title."""
        self._data["title"] = title
        return self

    def set_description(self, description: str) -> Embed:
        """Set the embed description."""
        self._data["description"] = description
        return self

    def set_url(self, url: str) -> Embed:
        """Set the embed URL (makes the title a hyperlink)."""
        self._data["url"] = url
        return self

    def set_color(self, color: int | str) -> Embed:
        """Set the embed color. Accepts an int (``0x5865F2``) or hex string (``'#5865F2'``)."""
        self._data["color"] = _parse_color(color)
        return self

    def set_timestamp(self, timestamp: str | datetime | None = None) -> Embed:
        """Set the embed timestamp. Pass ``None`` to use the current time."""
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
        """Set the embed author."""
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
        """Set the embed footer."""
        footer: dict[str, Any] = {"text": text}
        if icon_url is not None:
            footer["icon_url"] = icon_url
        if proxy_icon_url is not None:
            footer["proxy_icon_url"] = proxy_icon_url
        self._data["footer"] = footer
        return self

    def set_image(self, *, url: str, proxy_url: str | None = None, height: int | None = None, width: int | None = None) -> Embed:
        """Set the embed image."""
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
        """Set the embed thumbnail."""
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
        """Add a field to the embed. Fields are displayed in order."""
        if "fields" not in self._data:
            self._data["fields"] = []
        self._data["fields"].append({
            "name": name,
            "value": value,
            "inline": inline,
        })
        return self

    def remove_field(self, index: int) -> Embed:
        """Remove a field by index."""
        fields = self._data.get("fields", [])
        if 0 <= index < len(fields):
            fields.pop(index)
        return self

    def clear_fields(self) -> Embed:
        """Remove all fields."""
        self._data["fields"] = []
        return self

    def insert_field(self, index: int, *, name: str, value: str, inline: bool = False) -> Embed:
        """Insert a field at a specific index."""
        if "fields" not in self._data:
            self._data["fields"] = []
        self._data["fields"].insert(index, {
            "name": name,
            "value": value,
            "inline": inline,
        })
        return self

    def set_video(self, *, url: str, height: int | None = None, width: int | None = None) -> Embed:
        """Set the embed video."""
        video: dict[str, Any] = {"url": url}
        if height is not None:
            video["height"] = height
        if width is not None:
            video["width"] = width
        self._data["video"] = video
        return self

    # Serialization

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
        return User(raw) if raw else None

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
    """Represents a webhook."""

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
        return User(raw) if raw else None

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
