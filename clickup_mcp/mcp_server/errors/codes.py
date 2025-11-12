"""Strict canonical error codes for MCP tools.

Serialized as string enum values in JSON Schema and responses.
"""
from __future__ import annotations

from enum import Enum


class IssueCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    RATE_LIMIT = "RATE_LIMIT"
    TRANSIENT = "TRANSIENT"
    INTERNAL = "INTERNAL"
