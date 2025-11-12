from typing import Any, Dict, List, get_type_hints

import pytest

from clickup_mcp.mcp_server.errors.handler import handle_tool_errors
from clickup_mcp.mcp_server.errors.models import ToolResponse


@handle_tool_errors
async def async_bare_list() -> List[Dict[str, Any]]:
    return [{"k": "v"}]


@handle_tool_errors
def sync_bare_list() -> List[Dict[str, Any]]:
    return [{"k": "v"}]


@pytest.mark.asyncio
async def test_async_wrapper_exposes_toolresponse_annotation() -> None:
    ann = getattr(async_bare_list, "__annotations__", {}).get("return")
    # The wrapper should expose ToolResponse[List[Dict[str, Any]]]
    assert ann is not None and "ToolResponse" in str(ann)
    # And the call should return a ToolResponse instance
    res = await async_bare_list()  # type: ignore[no-untyped-call]
    assert isinstance(res, ToolResponse)
    assert res.ok is True and isinstance(res.result, list)


def test_sync_wrapper_exposes_toolresponse_annotation() -> None:
    ann = getattr(sync_bare_list, "__annotations__", {}).get("return")
    assert ann is not None and "ToolResponse" in str(ann)
    res = sync_bare_list()
    assert isinstance(res, ToolResponse)
    assert res.ok is True and isinstance(res.result, list)
