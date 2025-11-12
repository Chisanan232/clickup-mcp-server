import pytest
from pydantic import TypeAdapter

from clickup_mcp.mcp_server.errors.models import ToolIssue, ToolResponse
from clickup_mcp.mcp_server.errors.codes import IssueCode


def test_tool_issue_minimal_and_optional_fields() -> None:
    issue = ToolIssue(code=IssueCode.VALIDATION_ERROR, message="Bad input")
    assert issue.code == IssueCode.VALIDATION_ERROR
    assert issue.message == "Bad input"
    assert issue.hint is None
    assert issue.retry_after_ms is None

    issue2 = ToolIssue(
        code=IssueCode.RATE_LIMIT,
        message="Rate limit exceeded",
        hint="Back off and retry",
        retry_after_ms=1200,
    )
    assert issue2.hint == "Back off and retry"
    assert issue2.retry_after_ms == 1200


def test_tool_response_success_and_failure_variants() -> None:
    # Success with arbitrary payload types (list/dict/primitive)
    ok_list = ToolResponse(ok=True, result=[{"x": 1}], issues=[])
    assert ok_list.ok is True
    assert ok_list.issues == []
    assert isinstance(ok_list.result, list)

    ok_dict = ToolResponse[dict](ok=True, result={"a": 1}, issues=[])
    assert ok_dict.result == {"a": 1}

    ok_none = ToolResponse(ok=True, result=None, issues=[])
    assert ok_none.result is None

    # Failure variant
    fail = ToolResponse(ok=False, issues=[ToolIssue(code=IssueCode.INTERNAL, message="boom")])
    assert fail.ok is False
    assert fail.result is None
    assert len(fail.issues) == 1


def test_error_models_json_schema_has_examples() -> None:
    issue_schema = TypeAdapter(ToolIssue).json_schema()
    assert "examples" in issue_schema

    # Use a concrete parameterization for ToolResponse schema extraction
    resp_schema = TypeAdapter(ToolResponse[dict]).json_schema()
    assert "examples" in resp_schema
    props = resp_schema.get("properties", {})
    assert set(["ok", "result", "issues"]).issubset(props.keys())
