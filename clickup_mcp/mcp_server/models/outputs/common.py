"""Common result models for MCP tools."""

from pydantic import BaseModel, Field


class OperationResult(BaseModel):
    """Generic OK/Fail response for mutating operations."""

    ok: bool = Field(..., description="True if the operation succeeded")

    model_config = {"json_schema_extra": {"examples": [{"ok": True}]}}


class DeletionResult(BaseModel):
    """Deletion result for delete operations."""

    deleted: bool = Field(..., description="True if the resource was deleted")

    model_config = {"json_schema_extra": {"examples": [{"deleted": True}]}}
