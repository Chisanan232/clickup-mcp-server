"""Central exception → ToolIssue mapping."""
from __future__ import annotations

import httpx
from typing import Optional

from .codes import IssueCode
from .models import ToolIssue
from clickup_mcp.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ClickUpAPIError,
    ClickUpError,
    RateLimitError,
    ResourceNotFoundError,
    ValidationError,
)


def _retry_after_ms_from_headers(response: Optional[httpx.Response]) -> Optional[int]:
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
    """Map arbitrary exception to a canonical ToolIssue.

    Keep messages short; avoid leaking internals.
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
        ms = int(float(exc.retry_after) * 1000) if getattr(exc, "retry_after", None) else None
        return ToolIssue(code=IssueCode.RATE_LIMIT, message="Rate limit exceeded", hint="Back off and retry", retry_after_ms=ms)
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
