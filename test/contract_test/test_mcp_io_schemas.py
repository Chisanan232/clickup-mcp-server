from typing import Any

import pytest
from pydantic import TypeAdapter

from clickup_mcp.mcp_server.models.outputs.folder import FolderListResult, FolderResult
from clickup_mcp.mcp_server.models.outputs.space import SpaceListResult, SpaceResult
from clickup_mcp.mcp_server.models.outputs.workspace import WorkspaceListResult


@pytest.mark.parametrize(
    "model",
    [
        SpaceResult,
        SpaceListResult,
        FolderResult,
        FolderListResult,
        WorkspaceListResult,
    ],
)
def test_json_schema_compiles_and_has_examples(model: Any) -> None:
    schema = TypeAdapter(model).json_schema()
    assert isinstance(schema, dict)
    # Example presence is required by our spec
    assert "examples" in schema, f"examples missing for {model.__name__}"
