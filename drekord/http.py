"""Low-level async HTTP client for the Discord REST API.

This module handles:
- Authentication (Bot token / OAuth2 Bearer)
- Rate limit awareness and automatic retry
- JSON serialization/deserialization
- Error mapping to Drekord exceptions

It does **not** expose any high-level API; callers construct URL paths
and pass them to ``request()``.
"""

from __future__ import annotations

import asyncio
import json as _json
import logging
import time
from typing import Any

import aiohttp

from .exceptions import (
    BadRequestError,
    DiscordServerError,
    ForbiddenError,
    HTTPError,
    NotFoundError,
    RateLimitedError,
    UnauthorizedError,
)

__all__ = ["HTTPClient"]

log = logging.getLogger("drekord.http")

DISCORD_API_BASE = "https://discord.com/api/v10"
DISCORD_CDN_BASE = "https://cdn.discordapp.com"


def _maybe_raise_for_status(status: int, body: dict[str, Any] | None) -> None:
    """Map a Discord HTTP status code to a typed exception and raise it."""
    if 200 <= status < 300:
        return

    msg = (body or {}).get("message", f"HTTP {status}")

    if status == 400:
        raise BadRequestError(msg, response_body=body)
    if status == 401:
        raise UnauthorizedError(msg, response_body=body)
    if status == 403:
        raise ForbiddenError(msg, response_body=body)
    if status == 404:
        raise NotFoundError(msg, response_body=body)
    if status == 429:
        retry_after = (body or {}).get("retry_after", 1.0)
        raise RateLimitedError(msg, retry_after=float(retry_after), response_body=body)
    if 500 <= status < 600:
        raise DiscordServerError(msg, status_code=status, response_body=body)

    raise HTTPError(msg, status_code=status, response_body=body)


class HTTPClient:
    """Async HTTP client with builtin rate-limit handling. epic"""

    def __init__(
        self,
        token: str,
        *,
        api_base: str = DISCORD_API_BASE,
        timeout: float = 30.0,
        max_retries: int = 5,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self._token = token
        self._api_base = api_base.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._own_session = session is None
        self._session = session or aiohttp.ClientSession(
            headers=self._default_headers(),
            timeout=aiohttp.ClientTimeout(total=timeout),
        )

        # Global rate-limit state (Discord sends these headers)
        self._global_rate_limit_remaining: float = 0.0
        self._global_rate_limit_reset_at: float = 0.0
        self._lock = asyncio.Lock()

    # Lifecycle

    def _default_headers(self) -> dict[str, str]:
        return {
            "Authorization": self._token,
            "User-Agent": "DiscordBot (https://github.com/drek124/drekord, 0.1.0)",
            "Content-Type": "application/json",
        }

    async def close(self) -> None:
        if self._own_session and self._session and not self._session.closed:
            await self._session.close()

    # Core request method

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        data: Any | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """
        Execute an HTTP request against the Discord API with automatic
        rate-limit retry.

        ### Parameters
        method:
            HTTP verb (``"GET"``, ``"POST"``, ``"PATCH"``, ``"DELETE"``, ``"PUT"``).
        path:
            API path, e.g. ``"/users/@me"`` or ``"/channels/123456/messages"``.
        json:
            JSON-serializable body.
        data:
            Raw body (for multipart uploads).
        params:
            URL query parameters.
        headers:
            Extra headers to merge with the default ones.

        ### Returns
        The parsed JSON response, or `None` for 204 No Content.
        """
        url = f"{self._api_base}{path}"
        attempt = 0

        while attempt < self._max_retries:
            attempt += 1

            # Respect global rate limit
            async with self._lock:
                now = time.monotonic()
                if self._global_rate_limit_reset_at > now:
                    wait = self._global_rate_limit_reset_at - now
                    log.debug("Global rate limit – sleeping %.2fs", wait)
                    await asyncio.sleep(wait)

            merged_headers = dict(self._default_headers())
            if headers:
                merged_headers.update(headers)
            # Remove Content-Type for multipart data (aiohttp sets it)
            if data is not None:
                merged_headers.pop("Content-Type", None)

            try:
                async with self._session.request(
                    method,
                    url,
                    json=json,
                    data=data,
                    params=params,
                    headers=merged_headers,
                ) as resp:
                    status = resp.status

                    # Read response body
                    text = await resp.text()
                    body: dict[str, Any] | None = None
                    if text:
                        try:
                            body = _json.loads(text)
                        except (_json.JSONDecodeError, ValueError):
                            body = {"message": text}

                    # Update global rate-limit state
                    remaining = resp.headers.get("X-RateLimit-Remaining")
                    reset_after = resp.headers.get("X-RateLimit-Reset-After")
                    if remaining is not None:
                        self._global_rate_limit_remaining = float(remaining)
                    if reset_after is not None:
                        self._global_rate_limit_reset_at = time.monotonic() + float(reset_after)

                    # Handle rate limits (retry)
                    if status == 429:
                        retry_after = (body or {}).get("retry_after", 1.0)
                        is_global = (body or {}).get("global", False)
                        if is_global:
                            self._global_rate_limit_reset_at = time.monotonic() + float(retry_after)
                            log.warning("Global rate limit hit – retrying in %.2fs", retry_after)
                        else:
                            log.debug("Rate limited on %s – retrying in %.2fs", path, retry_after)
                        await asyncio.sleep(float(retry_after))
                        continue

                    # Raise immediately for client errors (4xx except 429).
                    # These are never transient, so retrying wont help.
                    if 400 <= status < 500:
                        _maybe_raise_for_status(status, body)

                    # Retry on server errors (5xx)
                    if 500 <= status < 600:
                        if attempt >= self._max_retries:
                            _maybe_raise_for_status(status, body)
                        log.warning(
                            "Server error %d on %s – attempt %d/%d",
                            status, path, attempt, self._max_retries,
                        )
                        await asyncio.sleep(2 ** attempt)
                        continue

                    if status == 204:
                        return None
                    return body

            except aiohttp.ClientError as exc:
                log.warning("Request to %s failed: %s", path, exc)
                if attempt >= self._max_retries:
                    raise HTTPError(
                        f"Request failed after {self._max_retries} attempts: {exc}",
                        status_code=0,
                    ) from exc
                await asyncio.sleep(2 ** attempt)

        raise HTTPError(
            f"Request failed after {self._max_retries} attempts",
            status_code=0,
        )

    # Convenience methods

    async def get(self, path: str, **kwargs: Any) -> Any:
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> Any:
        return await self.request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs: Any) -> Any:
        return await self.request("PUT", path, **kwargs)

    async def patch(self, path: str, **kwargs: Any) -> Any:
        return await self.request("PATCH", path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> Any:
        return await self.request("DELETE", path, **kwargs)
