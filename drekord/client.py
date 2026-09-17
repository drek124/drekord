"""Drekord client: The entry point for all API interactions.

Usage::

    import asyncio
    import drekord

    async def main():
        async with drekord.Client(token="your_token_lol") as client:
            # Get client user
            me = await client.users.me()
            print(f"Logged in as {me.username}")

            # Send a message
            msg = await client.messages.channel(channel_id).send(content="Hello, drek!")
            print(f"Sent message {msg.id}")

    asyncio.run(main())

More stuff:

    client.users          # UsersResource
    client.guilds         # GuildResource
    client.messages       # MessagesResource
    client.channels       # ChannelResource
    client.webhooks       # WebhooksResource
    client.invites        # InvitesResource
    client.emojis         # EmojiResource
"""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .api import (
    ChannelResource,
    EmojiResource,
    GuildResource,
    InvitesResource,
    MessagesResource,
    UsersResource,
    WebhooksResource,
)
from .http import HTTPClient

__all__ = ["Client"]

log = logging.getLogger("drekord")


class Client:
    """The main Drekord client.

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
    """

    def __init__(
        self,
        token: str,
        *,
        timeout: float = 30.0,
        max_retries: int = 5,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        # Normalize the token prefix
        if not token.startswith(("Bot ", "Bearer ")):
            token = f"Bot {token}"

        self._http = HTTPClient(
            token,
            timeout=timeout,
            max_retries=max_retries,
            session=session,
        )

        # Public resource accessors
        self.users = UsersResource(self._http)
        self.guilds = GuildResource(self._http)
        self.messages = MessagesResource(self._http)
        self.channels = ChannelResource(self._http)
        self.webhooks = WebhooksResource(self._http)
        self.invites = InvitesResource(self._http)
        self.emojis = EmojiResource(self._http)

    
    # Lifecycle
    

    async def __aenter__(self) -> Client:
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP session."""
        await self._http.close()

    
    # Raw request (escape hatch)
    

    async def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        """Send a raw HTTP request to the Discord API.

        This is an escape hatch for endpoints not yet covered by the
        resource classes. Use it sparingly.

        Examples::

            data = await client.request("GET", "/gateway")
            data = await client.request("POST", "/channels/123/threads", json={...})
        """
        return await self._http.request(method, path, **kwargs)

    
    # Convenience shortcuts
    

    @property
    def http(self) -> HTTPClient:
        """Access the low-level HTTP client directly."""
        return self._http

    def __repr__(self) -> str:
        return "<drekord.Client>"
