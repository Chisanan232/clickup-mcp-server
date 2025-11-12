from typing import Any, Dict, List

import pytest
from pydantic import BaseModel

from clickup_mcp.exceptions import AuthorizationError, ValidationError
from clickup_mcp.mcp_server.errors.codes import IssueCode
from clickup_mcp.mcp_server.errors.handler import handle_tool_errors
from clickup_mcp.mcp_server.errors.models import ToolResponse


class DemoModel(BaseModel):
    x: int


@handle_tool_errors
async def async_ok_list() -> List[Dict[str, Any]]:
    return [{"a": 1}]


@handle_tool_errors
async def async_ok_model() -> DemoModel:
    return DemoModel(x=42)


@handle_tool_errors
async def async_ok_none() -> None:
    return None


@handle_tool_errors
async def async_pass_through(resp: ToolResponse[List[int]]) -> ToolResponse[List[int]]:
    return resp


@handle_tool_errors
async def async_raise_perm() -> List[int]:
    raise AuthorizationError("denied")


@handle_tool_errors
def sync_ok_primitive() -> int:
    return 7


@handle_tool_errors
def sync_raise_validation() -> int:
    raise ValidationError("bad field", field="name", value="!")


@pytest.mark.asyncio
async def test_async_ok_list_wrapped() -> None:
    result = await async_ok_list()  # type: ignore[no-untyped-call]
    assert isinstance(result, ToolResponse)
    assert result.ok is True
    assert result.issues == []
    assert isinstance(result.result, list) and result.result[0]["a"] == 1


@pytest.mark.asyncio
async def test_async_ok_model_wrapped() -> None:
    result = await async_ok_model()
    assert result.ok is True
    # result can be DemoModel or dict depending on envelope consumer; here we just assert non-null
    assert result.result is not None


@pytest.mark.asyncio
async def test_async_ok_none_wrapped() -> None:
    result = await async_ok_none()
    assert result.ok is True
    assert result.result is None


@pytest.mark.asyncio
async def test_async_pass_through_envelope() -> None:
    envelope = ToolResponse[List[int]](ok=True, result=[1, 2, 3], issues=[])
    result = await async_pass_through(envelope)
    assert result is envelope  # passthrough


@pytest.mark.asyncio
async def test_async_raise_permission_maps_issue() -> None:
    result = await async_raise_perm()
    assert result.ok is False
    assert len(result.issues) == 1
    assert result.issues[0].code == IssueCode.PERMISSION_DENIED


def test_sync_ok_primitive_wrapped() -> None:
    result = sync_ok_primitive()
    assert result.ok is True
    assert result.result == 7


def test_sync_raise_validation_maps_issue() -> None:
    result = sync_raise_validation()
    assert result.ok is False
    assert result.issues[0].code == IssueCode.VALIDATION_ERROR
