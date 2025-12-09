"""
Strict canonical error codes for MCP tools.

This module defines standardized error codes used across all MCP tool responses.
These codes are serialized as string enum values in JSON Schema and responses,
providing a consistent error classification system for clients.

Error Code Categories:
- **Validation Errors**: Input validation failures (VALIDATION_ERROR)
- **Permission Errors**: Authorization/authentication failures (PERMISSION_DENIED)
- **Resource Errors**: Resource not found or conflicts (NOT_FOUND, CONFLICT)
- **Rate Limiting**: API rate limit exceeded (RATE_LIMIT)
- **Transient Errors**: Temporary failures that may succeed on retry (TRANSIENT)
- **Internal Errors**: Server-side errors (INTERNAL)

Usage Examples:
    # Python - Use error codes in exception handling
    from clickup_mcp.mcp_server.errors.codes import IssueCode

    if error_type == "validation":
        code = IssueCode.VALIDATION_ERROR
    elif error_type == "not_found":
        code = IssueCode.NOT_FOUND
    elif error_type == "rate_limit":
        code = IssueCode.RATE_LIMIT

    # Python - Check error code
    if issue.code == IssueCode.RATE_LIMIT:
        print(f"Rate limited, retry after {issue.retry_after_ms}ms")

    # JSON - Serialized in responses
    {
        "code": "VALIDATION_ERROR",
        "message": "Invalid task ID format",
        "hint": "Task ID must be alphanumeric"
    }
"""

from __future__ import annotations

from enum import Enum


class IssueCode(str, Enum):
    """
    Canonical error codes for MCP tool responses.

    These codes provide a standardized way to classify errors across all MCP tools.
    Each code represents a specific category of error that clients can handle
    programmatically.

    Attributes:
        VALIDATION_ERROR: Input validation failed (e.g., invalid format, missing required field)
        PERMISSION_DENIED: User lacks required permissions or authentication
        NOT_FOUND: Requested resource does not exist
        CONFLICT: Operation conflicts with existing state (e.g., duplicate, constraint violation)
        RATE_LIMIT: API rate limit exceeded, client should back off
        TRANSIENT: Temporary failure (network, timeout), client should retry
        INTERNAL: Server-side error, client should report to support

    Usage Examples:
        # Python - Create an issue with error code
        from clickup_mcp.mcp_server.errors.codes import IssueCode
        from clickup_mcp.mcp_server.errors.models import ToolIssue

        issue = ToolIssue(
            code=IssueCode.NOT_FOUND,
            message="Task not found",
            hint="Verify the task ID is correct"
        )

        # Python - Check error code
        if issue.code == IssueCode.RATE_LIMIT:
            # Handle rate limiting with backoff
            pass
        elif issue.code == IssueCode.TRANSIENT:
            # Retry the operation
            pass

        # JSON - Serialized in API responses
        {
            "ok": false,
            "issues": [
                {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid priority value",
                    "hint": "Priority must be 1-4"
                }
            ]
        }
    """

    VALIDATION_ERROR = "VALIDATION_ERROR"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    RATE_LIMIT = "RATE_LIMIT"
    TRANSIENT = "TRANSIENT"
    INTERNAL = "INTERNAL"
