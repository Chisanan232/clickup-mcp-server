"""
Envelope and issue models for MCP tool responses (Pydantic v2).

This module defines the response envelope and error issue models used for all MCP tool
responses. These models ensure consistent, structured error reporting across all tools.

Response Structure:
- **Success**: { ok: true, result: <payload>, issues: [] }
- **Failure**: { ok: false, result: null, issues: [<issue>, ...] }

The ToolResponse envelope wraps all tool results, providing:
- Consistent error handling across all tools
- Structured issue reporting with codes and hints
- Support for rate limiting backoff information
- Type-safe generic result handling

Usage Examples:
    # Python - Create a successful response
    from clickup_mcp.mcp_server.errors.models import ToolResponse

    result = {"id": "task_123", "name": "My Task"}
    response = ToolResponse(ok=True, result=result, issues=[])

    # Python - Create an error response
    from clickup_mcp.mcp_server.errors.models import ToolResponse, ToolIssue
    from clickup_mcp.mcp_server.errors.codes import IssueCode

    issue = ToolIssue(
        code=IssueCode.NOT_FOUND,
        message="Task not found",
        hint="Check the task ID"
    )
    response = ToolResponse(ok=False, issues=[issue])

    # JSON - Serialized response
    {
        "ok": false,
        "result": null,
        "issues": [
            {
                "code": "RATE_LIMIT",
                "message": "Rate limit exceeded",
                "hint": "Back off and retry",
                "retry_after_ms": 1200
            }
        ]
    }
"""

from __future__ import annotations

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from .codes import IssueCode


class ToolIssue(BaseModel):
    """
    Tiny issue object for failures.

    Represents a single error or issue that occurred during tool execution.
    Designed to be token-lean but actionable, with strict canonical codes
    and optional remediation hints.

    Attributes:
        code: Canonical error code from IssueCode enum
        message: End-user readable short message (1-2 sentences)
        hint: Optional one-line remediation hint for the user
        retry_after_ms: Backoff duration in milliseconds (only for RATE_LIMIT)

    Key Design:
    - Keep messages concise and actionable
    - Provide hints for common recovery strategies
    - Include retry_after_ms for rate limiting
    - Codes are strict and standardized

    Usage Examples:
        # Python - Create a validation error issue
        from clickup_mcp.mcp_server.errors.models import ToolIssue
        from clickup_mcp.mcp_server.errors.codes import IssueCode

        issue = ToolIssue(
            code=IssueCode.VALIDATION_ERROR,
            message="Invalid priority value",
            hint="Priority must be 1-4"
        )

        # Python - Create a rate limit issue
        issue = ToolIssue(
            code=IssueCode.RATE_LIMIT,
            message="Rate limit exceeded",
            hint="Back off and retry",
            retry_after_ms=1200
        )

        # JSON - Serialized issue
        {
            "code": "NOT_FOUND",
            "message": "Task not found",
            "hint": "Verify the task ID is correct",
            "retry_after_ms": null
        }
    """

    code: IssueCode = Field(..., description="Canonical error code")
    message: str = Field(..., description="End-user readable short message")
    hint: Optional[str] = Field(None, description="Optional one-line remediation hint")
    retry_after_ms: Optional[int] = Field(None, ge=0, description="Backoff duration in ms (when rate-limited)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code": "RATE_LIMIT",
                    "message": "Rate limit exceeded",
                    "hint": "Back off and retry",
                    "retry_after_ms": 1200,
                }
            ]
        }
    }


T = TypeVar("T")


class ToolResponse(GenericModel, Generic[T]):
    """
    Generic response envelope for MCP tools.

    This is the standard response wrapper for all MCP tool operations. It provides
    a consistent structure for both successful and failed operations, with support
    for structured error reporting and type-safe result handling.

    Response Structure:
    - **Success**: { ok: true, result: <payload>, issues: [] }
    - **Failure**: { ok: false, result: null, issues: [<issue>, ...] }

    The generic type parameter T specifies the result payload type. When ok=false,
    result is null and issues contains one or more ToolIssue objects describing
    what went wrong.

    Attributes:
        ok: True if the operation succeeded, False if it failed
        result: Result payload when ok=true, null when ok=false
        issues: List of ToolIssue objects describing any errors or warnings

    Key Design:
    - Always returns a ToolResponse, never raises exceptions
    - Supports both success and failure cases uniformly
    - Provides structured error information with codes and hints
    - Type-safe generic result handling
    - Serializable to JSON with proper schema generation

    Usage Examples:
        # Python - Successful response
        from clickup_mcp.mcp_server.errors.models import ToolResponse

        result = {"id": "task_123", "name": "My Task"}
        response = ToolResponse[dict](ok=True, result=result, issues=[])

        # Python - Error response
        from clickup_mcp.mcp_server.errors.models import ToolResponse, ToolIssue
        from clickup_mcp.mcp_server.errors.codes import IssueCode

        issue = ToolIssue(
            code=IssueCode.NOT_FOUND,
            message="Task not found",
            hint="Verify the task ID"
        )
        response = ToolResponse(ok=False, issues=[issue])

        # Python - Check response status
        if response.ok:
            print(f"Success: {response.result}")
        else:
            for issue in response.issues:
                print(f"{issue.code}: {issue.message}")
                if issue.hint:
                    print(f"Hint: {issue.hint}")

        # JSON - Serialized success response
        {
            "ok": true,
            "result": {
                "id": "task_123",
                "name": "My Task"
            },
            "issues": []
        }

        # JSON - Serialized error response
        {
            "ok": false,
            "result": null,
            "issues": [
                {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid task ID format",
                    "hint": "Task ID must be alphanumeric",
                    "retry_after_ms": null
                }
            ]
        }
    """

    ok: bool = Field(..., description="True if the operation succeeded")
    result: Optional[T] = Field(None, description="Result payload when ok=true")
    issues: List[ToolIssue] = Field(default_factory=list, description="Business-level issues")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"ok": True, "result": None, "issues": []},
                {
                    "ok": False,
                    "issues": [
                        {
                            "code": "PERMISSION_DENIED",
                            "message": "Missing scope: tasks:write",
                            "hint": "Grant the app the required scope",
                        }
                    ],
                },
            ]
        }
    }
