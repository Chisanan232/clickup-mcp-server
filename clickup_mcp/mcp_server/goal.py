"""MCP tools for ClickUp Goals.

Tools:
- goal.create
- goal.get
- goal.update
- goal.delete
- goal.list
"""

from clickup_mcp.client import ClickUpAPIClientFactory
from clickup_mcp.exceptions import ClickUpAPIError
from clickup_mcp.mcp_server.errors import handle_tool_errors
from clickup_mcp.mcp_server.models.inputs.goal import (
    GoalCreateInput,
    GoalDeleteInput,
    GoalGetInput,
    GoalListInput,
    GoalUpdateInput,
)
from clickup_mcp.mcp_server.models.outputs.goal import GoalListResult, GoalResult
from clickup_mcp.models.dto.goal import GoalListQuery
from clickup_mcp.models.mapping.goal_mapper import GoalMapper

from .app import mcp


@mcp.tool(
    title="Create Goal",
    name="goal.create",
    description=(
        "Create a goal for a team with name, description, and due date. "
        "Time fields are epoch milliseconds. HTTP: POST /team/{team_id}/goal."
    ),
    annotations={
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def goal_create(input: GoalCreateInput) -> GoalResult:
    """
    Create a goal for a team.

    API:
        POST /team/{team_id}/goal

    Args:
        input: GoalCreateInput with team_id, name, description, due_date, and optional key_results, owners

    Returns:
        GoalResult: The created goal

    Error Handling:
        Decorated with `@handle_tool_errors` and returns a ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., VALIDATION_ERROR, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await goal_create(GoalCreateInput(team_id="team_1", name="Q1 Revenue Goal", due_date=1702080000000))
        if response.ok:
            print(response.result.id)
    """
    client = ClickUpAPIClientFactory.get()
    # Input -> Domain -> DTO

    domain = GoalMapper.from_create_input(input)
    dto = GoalMapper.to_create_dto(domain)
    async with client:
        resp = await client.goal.create(input.team_id, dto)
    if not resp or not resp.items:
        raise ClickUpAPIError("Create goal failed")
    goal_domain = GoalMapper.to_domain(resp.items[0])
    return GoalResult(**GoalMapper.to_goal_result_output(goal_domain))


@mcp.tool(
    title="Get Goal",
    name="goal.get",
    description=(
        "Get a goal by ID. HTTP: GET /goal/{goal_id}."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def goal_get(input: GoalGetInput) -> GoalResult:
    """
    Get a goal by ID.

    API:
        GET /goal/{goal_id}

    Args:
        input: GoalGetInput with goal_id

    Returns:
        GoalResult: The goal details

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues indicating the error category.

    Examples:
        # Python (async)
        response = await goal_get(GoalGetInput(goal_id="goal_123"))
        if response.ok:
            print(response.result.name)
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        resp = await client.goal.get(input.goal_id)
    if not resp:
        raise ClickUpAPIError("Get goal failed")
    from clickup_mcp.models.dto.goal import GoalResponse
    goal_response = GoalResponse(**resp)
    goal_domain = GoalMapper.to_domain(goal_response)
    return GoalResult(**GoalMapper.to_goal_result_output(goal_domain))


@mcp.tool(
    title="Update Goal",
    name="goal.update",
    description=(
        "Update a goal by ID. HTTP: PUT /goal/{goal_id}."
    ),
    annotations={
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def goal_update(input: GoalUpdateInput) -> GoalResult:
    """
    Update a goal by ID.

    API:
        PUT /goal/{goal_id}

    Args:
        input: GoalUpdateInput with goal_id and optional name, description, due_date, status

    Returns:
        GoalResult: The updated goal

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues indicating the error category.

    Examples:
        # Python (async)
        response = await goal_update(GoalUpdateInput(goal_id="goal_123", name="Updated Goal Name"))
        if response.ok:
            print(response.result.name)
    """
    client = ClickUpAPIClientFactory.get()
    domain = GoalMapper.from_update_input(input)
    dto = GoalMapper.to_update_dto(domain)
    async with client:
        resp = await client.goal.update(input.goal_id, dto)
    if not resp:
        raise ClickUpAPIError("Update goal failed")
    from clickup_mcp.models.dto.goal import GoalResponse
    goal_response = GoalResponse(**resp)
    goal_domain = GoalMapper.to_domain(goal_response)
    return GoalResult(**GoalMapper.to_goal_result_output(goal_domain))


@mcp.tool(
    title="Delete Goal",
    name="goal.delete",
    description=(
        "Delete a goal by ID. HTTP: DELETE /goal/{goal_id}."
    ),
    annotations={
        "destructiveHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def goal_delete(input: GoalDeleteInput) -> dict:
    """
    Delete a goal by ID.

    API:
        DELETE /goal/{goal_id}

    Args:
        input: GoalDeleteInput with goal_id

    Returns:
        dict: Success status

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues indicating the error category.

    Examples:
        # Python (async)
        response = await goal_delete(GoalDeleteInput(goal_id="goal_123"))
        if response.ok:
            print("Goal deleted successfully")
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        success = await client.goal.delete(input.goal_id)
    if not success:
        raise ClickUpAPIError("Delete goal failed")
    return {"success": True, "message": "Goal deleted successfully"}


@mcp.tool(
    title="List Goals",
    name="goal.list",
    description=(
        "List goals for a team with filters. Constraints: `limit` ≤ 100. "
        "HTTP: GET /team/{team_id}/goal."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def goal_list(input: GoalListInput) -> GoalListResult:
    """
    List goals for a team with filters.

    API:
        GET /team/{team_id}/goal

    Args:
        input: GoalListInput with team_id, optional status, owner, start_date, end_date, page, limit

    Returns:
        GoalListResult: Page of goal list items

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues indicating the error category.

    Examples:
        # Python (async)
        response = await goal_list(GoalListInput(team_id="team_1", status="active", limit=50))
        if response.ok:
            for it in response.result.items:
                print(it.id)
    """
    client = ClickUpAPIClientFactory.get()
    query = GoalListQuery(
        status=input.status,
        owner=input.owner,
        start_date=input.start_date,
        end_date=input.end_date,
        page=input.page,
        limit=input.limit,
    )
    async with client:
        resp = await client.goal.list(input.team_id, query)
    if not resp:
        raise ClickUpAPIError("List goals failed")
    items = [GoalMapper.to_goal_list_item_output(GoalMapper.to_domain(entry)) for entry in resp.items]
    return GoalListResult(items=items, next_cursor=resp.next_page, truncated=False)
