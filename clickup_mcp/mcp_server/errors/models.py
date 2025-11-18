"""Envelope and issue models for MCP tool responses (Pydantic v2)."""

from __future__ import annotations

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from .codes import IssueCode


class ToolIssue(BaseModel):
    """Tiny issue object for failures.

    Keep token-lean but actionable. Codes are strict.
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
    """Generic response envelope for MCP tools.

    Success: { ok: true, result }
    Failure: { ok: false, issues: [...] }
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
