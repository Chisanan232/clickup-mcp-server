"""
Central exception → ToolIssue mapping.

This module centralizes translation of arbitrary exceptions raised during tool
execution into canonical `ToolIssue` objects with standardized `IssueCode`s.
It ensures that all MCP tools return consistent, actionable error information
without leaking internal details.

Mapping Strategy:
- httpx timeouts → TRANSIENT with retry guidance
- HTTPStatusError → based on status code (429, 401/403, 404, 409, 5xx)
- ClickUp domain errors → mapped to appropriate IssueCode with hints
- Fallback → INTERNAL to avoid leaking internals

Usage Examples:
    # Python - Map httpx timeout
    import httpx
    from clickup_mcp.mcp_server.errors.mapping import map_exception

    try:
        raise httpx.ConnectTimeout("connect timed out")
    except Exception as exc:
        issue = map_exception(exc)
        assert issue.code.value == "TRANSIENT"

    # Python - Map ClickUp validation error
    from clickup_mcp.exceptions import ValidationError

    issue = map_exception(ValidationError("Invalid priority value"))
    assert issue.code.value == "VALIDATION_ERROR"
"""

from __future__ import annotations

from typing import Optional

import httpx

from clickup_mcp.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ClickUpAPIError,
    ClickUpError,
    RateLimitError,
    ResourceNotFoundError,
    ValidationError,
)

from .codes import IssueCode
from .models import ToolIssue


def _retry_after_ms_from_headers(response: Optional[httpx.Response]) -> Optional[int]:
    """
    Extract a retry-after backoff hint (milliseconds) from HTTP response headers.

    This helper inspects common headers to compute a client backoff duration
    when rate limited:
    - "Retry-After": seconds until next attempt (RFC 7231) → converted to ms
    - "X-RateLimit-Reset": epoch seconds until reset (best-effort) → returns 1000 ms

    Args:
        response: Optional httpx.Response from which to read headers

    Returns:
        int | None: Backoff duration in milliseconds, or None if unavailable

    Usage Examples:
        # Python - From Retry-After header
        resp = httpx.Response(429, headers={"Retry-After": "2"})
        assert _retry_after_ms_from_headers(resp) == 2000

        # Python - From X-RateLimit-Reset header (best-effort)
        resp = httpx.Response(429, headers={"X-RateLimit-Reset": "1733635200"})
        assert _retry_after_ms_from_headers(resp) == 1000
    """
    if response is None:
        return None
    # Try Retry-After (seconds)
    ra = response.headers.get("Retry-After")
    if ra and ra.isdigit():
        return int(ra) * 1000
    # ClickUp-specific hints (best-effort)
    # X-RateLimit-Reset is epoch seconds until reset; not exact backoff
    xrlr = response.headers.get("X-RateLimit-Reset")
    if xrlr and xrlr.isdigit():
        # Provide a minimal non-zero backoff if reset in future
        return 1000
    return None


def map_exception(exc: Exception) -> ToolIssue:
    """
    Map any exception to a canonical `ToolIssue` with an `IssueCode` and message.

    Mapping rules prioritize actionable guidance while minimizing internal detail
    leakage. Unknown exceptions are mapped to `INTERNAL`.

    Args:
        exc: Any exception raised by tool code, HTTP client, or domain layer

    Returns:
        ToolIssue: Canonical issue suitable for returning to MCP clients

    Usage Examples:
        # Python - HTTP 429 maps to RATE_LIMIT with retry_after_ms when possible
        resp = httpx.Response(429, headers={"Retry-After": "3"})
        err = httpx.HTTPStatusError("rate limit", request=None, response=resp)
        issue = map_exception(err)
        assert issue.code.value == "RATE_LIMIT"
        assert issue.retry_after_ms == 3000

        # Python - 404 maps to NOT_FOUND
        resp = httpx.Response(404)
        err = httpx.HTTPStatusError("not found", request=None, response=resp)
        assert map_exception(err).code.value == "NOT_FOUND"
    """
    # httpx timeout → TRANSIENT
    if isinstance(exc, (httpx.TimeoutException, httpx.ReadTimeout, httpx.ConnectTimeout)):
        return ToolIssue(code=IssueCode.TRANSIENT, message="Request timed out", hint="Back off and retry")

    # httpx HTTP status error
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code if exc.response is not None else None
        if status == 429:
            return ToolIssue(
                code=IssueCode.RATE_LIMIT,
                message="Rate limit exceeded",
                hint="Back off and retry",
                retry_after_ms=_retry_after_ms_from_headers(exc.response),
            )
        if status in (401, 403):
            return ToolIssue(code=IssueCode.PERMISSION_DENIED, message="Insufficient permissions or invalid token")
        if status == 404:
            return ToolIssue(code=IssueCode.NOT_FOUND, message="Resource not found")
        if status == 409:
            return ToolIssue(code=IssueCode.CONFLICT, message="Conflict")
        if status and 500 <= status < 600:
            return ToolIssue(code=IssueCode.TRANSIENT, message="Upstream service error", hint="Retry later")
        return ToolIssue(code=IssueCode.INTERNAL, message="HTTP error")

    # ClickUp domain exceptions
    if isinstance(exc, RateLimitError):
        assert exc.retry_after
        ms = int(exc.retry_after * 1000) if getattr(exc, "retry_after", None) else None
        return ToolIssue(
            code=IssueCode.RATE_LIMIT, message="Rate limit exceeded", hint="Back off and retry", retry_after_ms=ms
        )
    if isinstance(exc, (AuthenticationError, AuthorizationError)):
        return ToolIssue(code=IssueCode.PERMISSION_DENIED, message="Insufficient permissions or invalid token")
    if isinstance(exc, ResourceNotFoundError):
        return ToolIssue(code=IssueCode.NOT_FOUND, message="Resource not found")
    if isinstance(exc, ValidationError):
        return ToolIssue(code=IssueCode.VALIDATION_ERROR, message=str(exc))
    if isinstance(exc, ClickUpAPIError):
        status = getattr(exc, "status_code", None)
        if isinstance(status, int) and 500 <= status < 600:
            return ToolIssue(code=IssueCode.TRANSIENT, message="Upstream service error", hint="Retry later")
        return ToolIssue(code=IssueCode.INTERNAL, message="API error")
    if isinstance(exc, ClickUpError):
        return ToolIssue(code=IssueCode.INTERNAL, message="Internal error")

    # Default fallback
    return ToolIssue(code=IssueCode.INTERNAL, message="Internal error")
