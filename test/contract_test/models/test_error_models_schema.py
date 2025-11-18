from typing import Any, Dict, List

from pydantic import TypeAdapter

from clickup_mcp.mcp_server.errors.codes import IssueCode
from clickup_mcp.mcp_server.errors.models import ToolIssue, ToolResponse


def test_issue_code_enum_schema() -> None:
    schema = TypeAdapter(IssueCode).json_schema()
    assert schema.get("type") == "string"
    # All canonical codes must be included in enum
    enum_vals = set(schema.get("enum", []))
    expected = {c.value for c in IssueCode}
    assert expected.issubset(enum_vals)


def test_tool_issue_schema_contract() -> None:
    schema = TypeAdapter(ToolIssue).json_schema()
    assert isinstance(schema, dict)
    assert "examples" in schema
    props = schema.get("properties", {})
    assert set(["code", "message", "hint", "retry_after_ms"]).issubset(props.keys())
    assert props["code"]["$ref"] or props["code"]["type"] == "string"
    # retry_after_ms must be integer with >= 0 constraint when present
    retry = props.get("retry_after_ms", {})
    if retry.get("type") == "integer":
        assert retry.get("minimum") == 0


def test_tool_response_schema_contract_for_dict_payload() -> None:
    schema = TypeAdapter(ToolResponse[Dict[str, Any]]).json_schema()
    assert isinstance(schema, dict)
    assert "examples" in schema
    props = schema.get("properties", {})
    assert set(["ok", "result", "issues"]).issubset(props.keys())
    assert props["ok"]["type"] == "boolean"
    # result can be object or null
    result_schema = props["result"]
    any_of = result_schema.get("anyOf") or []
    types = {s.get("type") for s in any_of if isinstance(s, dict)} or {result_schema.get("type")}
    assert ("object" in types) or (types == {"null"}) or ("null" in types)
    # issues is array of ToolIssue
    issues_schema = props["issues"]
    assert issues_schema.get("type") == "array"


def test_tool_response_schema_contract_for_list_payload() -> None:
    schema = TypeAdapter(ToolResponse[List[Dict[str, Any]]]).json_schema()
    props = schema.get("properties", {})
    result_schema = props["result"]
    any_of = result_schema.get("anyOf") or []
    has_array = (
        any(s.get("type") == "array" for s in any_of if isinstance(s, dict)) or result_schema.get("type") == "array"
    )
    assert has_array


def test_tool_response_validate_python_success_and_failure() -> None:
    # Success instance
    ok_instance = {
        "ok": True,
        "result": [{"id": "123", "name": "A"}],
        "issues": [],
    }
    parsed_ok = TypeAdapter(ToolResponse[List[Dict[str, Any]]]).validate_python(ok_instance)
    assert parsed_ok.ok is True
    assert isinstance(parsed_ok.result, list) and parsed_ok.issues == []

    # Failure instance
    fail_instance = {
        "ok": False,
        "result": None,
        "issues": [{"code": IssueCode.INTERNAL, "message": "boom"}],
    }
    parsed_fail = TypeAdapter(ToolResponse[List[Dict[str, Any]]]).validate_python(fail_instance)
    assert parsed_fail.ok is False
    assert parsed_fail.result is None
    assert len(parsed_fail.issues) == 1
