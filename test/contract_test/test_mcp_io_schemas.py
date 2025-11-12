from typing import Any

import pytest
from pydantic import TypeAdapter

from clickup_mcp.mcp_server.models.inputs.task import TaskCreateInput, TaskListInListInput
from clickup_mcp.mcp_server.models.outputs.folder import FolderListResult, FolderResult
from clickup_mcp.mcp_server.models.outputs.list import ListListResult, ListResult
from clickup_mcp.mcp_server.models.outputs.task import TaskResult, TaskListResult as TaskListOut
from clickup_mcp.mcp_server.models.outputs.space import SpaceListResult, SpaceResult
from clickup_mcp.mcp_server.models.outputs.workspace import WorkspaceListResult


@pytest.mark.parametrize(
    "model",
    [
        TaskCreateInput,
        TaskListInListInput,
        SpaceResult,
        SpaceListResult,
        FolderResult,
        FolderListResult,
        ListResult,
        ListListResult,
        TaskResult,
        TaskListOut,
        WorkspaceListResult,
    ],
)
def test_json_schema_compiles_and_has_examples(model: Any) -> None:
    schema = TypeAdapter(model).json_schema()
    assert isinstance(schema, dict)
    # Example presence is required by our spec
    assert "examples" in schema, f"examples missing for {model.__name__}"


def test_task_list_in_list_constraints() -> None:
    schema = TypeAdapter(TaskListInListInput).json_schema()
    props = schema.get("properties", {})
    limit = props.get("limit", {})
    assert limit.get("maximum") == 100
    assert limit.get("minimum") == 1
    page = props.get("page", {})
    assert page.get("minimum") == 0


def test_task_result_constraints() -> None:
    schema = TypeAdapter(TaskResult).json_schema()
    props = schema.get("properties", {})
    priority = props.get("priority", {})
    # Optional[int] produces anyOf [int,null]
    any_of = priority.get("anyOf") or []
    int_schema = next((s for s in any_of if s.get("type") == "integer"), None)
    if int_schema is None and priority.get("type") == "integer":
        int_schema = priority
    assert int_schema is not None, "integer schema for priority not found"
    assert int_schema.get("maximum") == 4
    assert int_schema.get("minimum") == 1
    due = props.get("due_date_ms", {})
    # Optional[int] again -> anyOf [int,null]
    any_of_due = due.get("anyOf") or []
    int_due = next((s for s in any_of_due if s.get("type") == "integer"), None)
    if int_due is None and due.get("type") == "integer":
        int_due = due
    assert int_due is not None, "integer schema for due_date_ms not found"
    assert int_due.get("minimum") == 0


def test_task_list_result_shape() -> None:
    schema = TypeAdapter(TaskListOut).json_schema()
    props = schema.get("properties", {})
    assert "items" in props
    assert "next_cursor" in props
    assert "truncated" in props
