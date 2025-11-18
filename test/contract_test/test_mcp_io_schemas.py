from typing import Any

import pytest
from pydantic import TypeAdapter

from clickup_mcp.mcp_server.models.inputs.task import (
    TaskCreateInput,
    TaskListInListInput,
)
from clickup_mcp.mcp_server.models.outputs.folder import FolderListResult, FolderResult
from clickup_mcp.mcp_server.models.outputs.list import ListListResult, ListResult
from clickup_mcp.mcp_server.models.outputs.space import SpaceListResult, SpaceResult
from clickup_mcp.mcp_server.models.outputs.task import TaskListResult as TaskListOut
from clickup_mcp.mcp_server.models.outputs.task import TaskResult
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
    # Optional[PriorityInfo] produces anyOf [object,null]
    any_of = priority.get("anyOf") or []
    obj_schema = next((s for s in any_of if s.get("type") == "object"), None)
    # Pydantic may emit a $ref instead of inlining the object
    if obj_schema is None:
        ref_entry = next((s for s in any_of if "$ref" in s), None)
        if ref_entry is not None:
            ref = ref_entry.get("$ref")
            # Resolve $ref like '#/$defs/PriorityInfo'
            if isinstance(ref, str) and ref.startswith("#/"):
                cur = schema
                for part in ref.lstrip("#/").split("/"):
                    cur = cur.get(part, {})
                if cur and isinstance(cur, dict):
                    obj_schema = cur
    if obj_schema is None and priority.get("type") == "object":
        obj_schema = priority
    assert obj_schema is not None, "object schema for priority not found"
    prio_props = obj_schema.get("properties", {})
    assert "value" in prio_props and "label" in prio_props
    # value constraints
    value_schema = prio_props.get("value", {})
    assert value_schema.get("type") == "integer"
    assert value_schema.get("maximum") == 4
    assert value_schema.get("minimum") == 1
    # label type
    label_schema = prio_props.get("label", {})
    assert label_schema.get("type") == "string"
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
