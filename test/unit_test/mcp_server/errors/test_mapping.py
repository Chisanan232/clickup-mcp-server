import httpx
import pytest

from clickup_mcp.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ClickUpAPIError,
    ClickUpError,
    RateLimitError,
    ResourceNotFoundError,
    ValidationError,
)
from clickup_mcp.mcp_server.errors.codes import IssueCode
from clickup_mcp.mcp_server.errors.mapping import map_exception
from clickup_mcp.mcp_server.errors.models import ToolIssue


def _http_status_error(status: int, headers: dict | None = None) -> httpx.HTTPStatusError:
    req = httpx.Request("GET", "https://api.example.test/x")
    resp = httpx.Response(status, headers=headers or {}, request=req)
    return httpx.HTTPStatusError("boom", request=req, response=resp)


@pytest.mark.parametrize(
    "exc,expected_code",
    [
        (httpx.TimeoutException("timeout"), IssueCode.TRANSIENT),
        (_http_status_error(401), IssueCode.PERMISSION_DENIED),
        (_http_status_error(403), IssueCode.PERMISSION_DENIED),
        (_http_status_error(404), IssueCode.NOT_FOUND),
        (_http_status_error(409), IssueCode.CONFLICT),
        (_http_status_error(500), IssueCode.TRANSIENT),
        (_http_status_error(429), IssueCode.RATE_LIMIT),
        (AuthenticationError("auth"), IssueCode.PERMISSION_DENIED),
        (AuthorizationError("forbid"), IssueCode.PERMISSION_DENIED),
        (ResourceNotFoundError(), IssueCode.NOT_FOUND),
        (ValidationError("bad"), IssueCode.VALIDATION_ERROR),
        (ClickUpAPIError("api", status_code=503), IssueCode.TRANSIENT),
        (ClickUpAPIError("api"), IssueCode.INTERNAL),
        (ClickUpError("x"), IssueCode.INTERNAL),
        (RuntimeError("y"), IssueCode.INTERNAL),
    ],
)
def test_map_exception_codes(exc: Exception, expected_code: IssueCode) -> None:
    issue = map_exception(exc)
    assert isinstance(issue, ToolIssue)
    assert issue.code == expected_code
    assert isinstance(issue.message, str) and issue.message


def test_rate_limit_retry_after_ms_from_http_headers() -> None:
    # Retry-After seconds header -> converted to ms
    exc = _http_status_error(429, headers={"Retry-After": "2"})
    issue = map_exception(exc)
    assert issue.code == IssueCode.RATE_LIMIT
    assert issue.retry_after_ms == 2000

    # X-RateLimit-Reset present -> best-effort 1000ms
    exc2 = _http_status_error(429, headers={"X-RateLimit-Reset": "173143"})
    issue2 = map_exception(exc2)
    assert issue2.retry_after_ms == 1000


def test_rate_limit_retry_after_ms_from_domain_error() -> None:
    exc = RateLimitError(retry_after=1.5)
    issue = map_exception(exc)
    assert issue.code == IssueCode.RATE_LIMIT
    # 1.5s -> 1500ms
    assert issue.retry_after_ms == 1500
