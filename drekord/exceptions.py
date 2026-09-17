"""Drekord exceptions.

All HTTP errors include the full Discord response body for debugging.
The ``__str__`` output is formatted to be immediately useful::

    [401] Unauthorized: Invalid Token (code=50001)

    Response body:
      {"message": "Invalid Token", "code": 50001}

    [403] Forbidden: Missing Permissions (code=50013)

    Response body:
      {"message": "Missing Permissions", "code": 50013, "errors": {...}}

    [400] Bad Request (code=50035)

    Response body:
      {"message": "Invalid Form Body", "code": 50035, "errors": {"content": {"_errors": [...]}}}
"""

from __future__ import annotations

import json


def _format_body(body: dict | None) -> str:
    """Pretty-print a Discord response body for debug output."""
    if not body:
        return "  (empty)"
    try:
        return "  " + json.dumps(body, indent=2, ensure_ascii=False).replace("\n", "\n  ")
    except (TypeError, ValueError):
        return f"  {body}"


class DrekordError(Exception):
    """Base exception for all Drekord errors."""

    def __init__(self, message: str = "", status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


class HTTPError(DrekordError):
    """Raised when an HTTP request to the Discord API fails.

    Attributes:
        status_code:  The HTTP status code (e.g. 400, 401, 404).
        response_body:  The full parsed JSON body from Discord's response.
        discord_code:  The Discord error code if present (e.g. 50013).
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        response_body: dict | None = None,
    ):
        self.status_code = status_code
        self.response_body = response_body or {}
        self.discord_code: int | None = self.response_body.get("code")
        super().__init__(message, status_code=status_code)

    @property
    def message(self) -> str:
        """The human-readable error message from Discord."""
        return super().__str__()

    def __str__(self) -> str:
        msg = super().__str__()

        # Start with a clear header: [STATUS] Message (code=CODE)
        parts = [f"[{self.status_code}] {msg}"]
        if self.discord_code is not None:
            parts[0] += f" (code={self.discord_code})"

        # Then show the full response body for debugging
        body_str = _format_body(self.response_body)
        parts.append(f"\n\nResponse body:\n{body_str}")

        return "\n".join(parts)

    def __repr__(self) -> str:
        return (
            f"<{type(self).__name__} "
            f"status={self.status_code} "
            f"code={self.discord_code} "
            f"message='{self.message}'>"
        )


class BadRequestError(HTTPError):
    """400 Bad Request — The request was malformed or missing required fields."""

    def __init__(self, message: str = "Bad Request", response_body: dict | None = None):
        super().__init__(message, status_code=400, response_body=response_body)


class UnauthorizedError(HTTPError):
    """401 Unauthorized — Invalid or missing authentication token."""

    def __init__(self, message: str = "Unauthorized", response_body: dict | None = None):
        super().__init__(message, status_code=401, response_body=response_body)


class ForbiddenError(HTTPError):
    """403 Forbidden — You lack permission to perform this action."""

    def __init__(self, message: str = "Forbidden", response_body: dict | None = None):
        super().__init__(message, status_code=403, response_body=response_body)


class NotFoundError(HTTPError):
    """404 Not Found — The resource does not exist."""

    def __init__(self, message: str = "Not Found", response_body: dict | None = None):
        super().__init__(message, status_code=404, response_body=response_body)


class RateLimitedError(HTTPError):
    """429 Too Many Requests — You are being rate limited."""

    def __init__(
        self,
        message: str = "Rate Limited",
        retry_after: float = 0.0,
        response_body: dict | None = None,
    ):
        self.retry_after = retry_after
        super().__init__(message, status_code=429, response_body=response_body)

    def __str__(self) -> str:
        base = super().__str__()
        # Append retry_after before the response body section
        parts = base.split("\n\nResponse body:")
        header = parts[0]
        body_section = "\n\nResponse body:" + parts[1] if len(parts) > 1 else ""
        return f"{header}\nRetry after: {self.retry_after}s{body_section}"


class DiscordServerError(HTTPError):
    """5xx — Discord's servers encountered an error."""

    def __init__(
        self,
        message: str = "Discord Server Error",
        status_code: int = 500,
        response_body: dict | None = None,
    ):
        super().__init__(message, status_code=status_code, response_body=response_body)
