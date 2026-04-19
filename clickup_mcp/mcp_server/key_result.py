"""MCP tools for ClickUp Key Results.

Tools:
- key_result.create
- key_result.get
- key_result.update
- key_result.delete
- key_result.list
"""

from clickup_mcp.client import ClickUpAPIClientFactory
from clickup_mcp.exceptions import ClickUpAPIError
from clickup_mcp.mcp_server.errors import handle_tool_errors
from clickup_mcp.mcp_server.models.inputs.key_result import (
    KeyResultCreateInput,
    KeyResultDeleteInput,
    KeyResultGetInput,
    KeyResultListInput,
    KeyResultUpdateInput,
)
from clickup_mcp.mcp_server.models.outputs.key_result import (
    KeyResultListResult,
    KeyResultResult,
)
from clickup_mcp.models.mapping.key_result_mapper import KeyResultMapper

from .app import mcp


@mcp.tool(
    title="Create Key Result",
    name="key_result.create",
    description=(
        "Create a key result for a goal with name, type, target, and optional unit. "
        "Time fields are epoch milliseconds. HTTP: POST /goal/{goal_id}/key_result."
    ),
    annotations={
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def key_result_create(input: KeyResultCreateInput) -> KeyResultResult:
    """
    Create a key result for a goal.

    API:
        POST /goal/{goal_id}/key_result

    Args:
        input: KeyResultCreateInput with goal_id, name, type, target, and optional unit, description

    Returns:
        KeyResultResult: The created key result

    Error Handling:
        Decorated with `@handle_tool_errors` and returns a ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., VALIDATION_ERROR, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await key_result_create(KeyResultCreateInput(goal_id="goal_1", name="Increase MRR", type="currency", target=1000000))
        if response.ok:
            print(response.result.id)
    """
    client = ClickUpAPIClientFactory.get()
    domain = KeyResultMapper.from_create_input(input)
    dto = KeyResultMapper.to_create_dto(domain)
    async with client:
        resp = await client.key_result.create(input.goal_id, dto)
    if not resp or not resp.items:
        raise ClickUpAPIError("Create key result failed")
    kr_domain = KeyResultMapper.to_domain(resp.items[0])
    return KeyResultResult(**KeyResultMapper.to_key_result_result_output(kr_domain))


@mcp.tool(
    title="Get Key Result",
    name="key_result.get",
    description=("Get a key result by ID. HTTP: GET /key_result/{key_result_id}."),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def key_result_get(input: KeyResultGetInput) -> KeyResultResult:
    """
    Get a key result by ID.

    API:
        GET /key_result/{key_result_id}

    Args:
        input: KeyResultGetInput with key_result_id

    Returns:
        KeyResultResult: The key result details

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues indicating the error category.

    Examples:
        # Python (async)
        response = await key_result_get(KeyResultGetInput(key_result_id="kr_123"))
        if response.ok:
            print(response.result.name)
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        resp = await client.key_result.get(input.key_result_id)
    if not resp:
        raise ClickUpAPIError("Get key result failed")
    from clickup_mcp.models.dto.key_result import KeyResultResponse

    kr_response = KeyResultResponse(**resp)
    kr_domain = KeyResultMapper.to_domain(kr_response)
    return KeyResultResult(**KeyResultMapper.to_key_result_result_output(kr_domain))


@mcp.tool(
    title="Update Key Result",
    name="key_result.update",
    description=("Update a key result by ID. HTTP: PUT /key_result/{key_result_id}."),
    annotations={
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def key_result_update(input: KeyResultUpdateInput) -> KeyResultResult:
    """
    Update a key result by ID.

    API:
        PUT /key_result/{key_result_id}

    Args:
        input: KeyResultUpdateInput with key_result_id and optional name, target, current, unit, description

    Returns:
        KeyResultResult: The updated key result

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues indicating the error category.

    Examples:
        # Python (async)
        response = await key_result_update(KeyResultUpdateInput(key_result_id="kr_123", target=2000000))
        if response.ok:
            print(response.result.target)
    """
    client = ClickUpAPIClientFactory.get()
    domain = KeyResultMapper.from_update_input(input)
    dto = KeyResultMapper.to_update_dto(domain)
    async with client:
        resp = await client.key_result.update(input.key_result_id, dto)
    if not resp:
        raise ClickUpAPIError("Update key result failed")
    from clickup_mcp.models.dto.key_result import KeyResultResponse

    kr_response = KeyResultResponse(**resp)
    kr_domain = KeyResultMapper.to_domain(kr_response)
    return KeyResultResult(**KeyResultMapper.to_key_result_result_output(kr_domain))


@mcp.tool(
    title="Delete Key Result",
    name="key_result.delete",
    description=("Delete a key result by ID. HTTP: DELETE /key_result/{key_result_id}."),
    annotations={
        "destructiveHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def key_result_delete(input: KeyResultDeleteInput) -> dict:
    """
    Delete a key result by ID.

    API:
        DELETE /key_result/{key_result_id}

    Args:
        input: KeyResultDeleteInput with key_result_id

    Returns:
        dict: Success status

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues indicating the error category.

    Examples:
        # Python (async)
        response = await key_result_delete(KeyResultDeleteInput(key_result_id="kr_123"))
        if response.ok:
            print("Key result deleted successfully")
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        success = await client.key_result.delete(input.key_result_id)
    if not success:
        raise ClickUpAPIError("Delete key result failed")
    return {"success": True, "message": "Key result deleted successfully"}


@mcp.tool(
    title="List Key Results",
    name="key_result.list",
    description=("List key results for a goal. HTTP: GET /goal/{goal_id}/key_result."),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def key_result_list(input: KeyResultListInput) -> KeyResultListResult:
    """
    List key results for a goal.

    API:
        GET /goal/{goal_id}/key_result

    Args:
        input: KeyResultListInput with goal_id

    Returns:
        KeyResultListResult: List of key result list items

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues indicating the error category.

    Examples:
        # Python (async)
        response = await key_result_list(KeyResultListInput(goal_id="goal_1"))
        if response.ok:
            for it in response.result.items:
                print(it.id)
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        resp = await client.key_result.list(input.goal_id)
    if not resp:
        raise ClickUpAPIError("List key results failed")
    items = [KeyResultMapper.to_key_result_result_output(KeyResultMapper.to_domain(entry)) for entry in resp.items]
    return KeyResultListResult(items=items, next_cursor=None, truncated=False)
