"""MCP tools for ClickUp Workflow Automations.

Tools:
- workflow.create
- workflow.get
- workflow.update
- workflow.delete
- workflow.list
"""

from clickup_mcp.client import ClickUpAPIClientFactory
from clickup_mcp.exceptions import ClickUpAPIError
from clickup_mcp.mcp_server.errors import handle_tool_errors
from clickup_mcp.mcp_server.models.inputs.workflow import (
    WorkflowCreateInput,
    WorkflowDeleteInput,
    WorkflowGetInput,
    WorkflowListInput,
    WorkflowUpdateInput,
)
from clickup_mcp.mcp_server.models.outputs.workflow import (
    WorkflowListResult,
    WorkflowResult,
)
from clickup_mcp.models.mapping.workflow_mapper import WorkflowMapper

from .app import mcp


@mcp.tool(
    title="Create Workflow",
    name="workflow.create",
    description=(
        "Create a workflow automation with name, trigger type, trigger config, and actions. "
        "HTTP: POST /team/{team_id}/workflow."
    ),
    annotations={
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def workflow_create(input: WorkflowCreateInput) -> WorkflowResult:
    """
    Create a workflow automation.

    API:
        POST /team/{team_id}/workflow

    Args:
        input: WorkflowCreateInput with team_id, name, trigger_type, trigger_config, actions, and optional is_active, priority

    Returns:
        WorkflowResult: The created workflow

    Error Handling:
        Decorated with `@handle_tool_errors` and returns a ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., VALIDATION_ERROR, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await workflow_create(WorkflowCreateInput(team_id="team_1", name="Auto-assign", trigger_type="task_created"))
        if response.ok:
            print(response.result.id)
    """
    client = ClickUpAPIClientFactory.get()
    domain = WorkflowMapper.from_create_input(input)
    dto = WorkflowMapper.to_create_dto(domain)
    async with client:
        resp = await client.workflow.create(input.team_id, dto)
    if not resp or not resp.items:
        raise ClickUpAPIError("Create workflow failed")
    wf_domain = WorkflowMapper.to_domain(resp.items[0])
    return WorkflowResult(**WorkflowMapper.to_workflow_result_output(wf_domain))


@mcp.tool(
    title="Get Workflow",
    name="workflow.get",
    description=("Get a workflow automation by ID. HTTP: GET /workflow/{workflow_id}."),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def workflow_get(input: WorkflowGetInput) -> WorkflowResult:
    """
    Get a workflow automation by ID.

    API:
        GET /workflow/{workflow_id}

    Args:
        input: WorkflowGetInput with workflow_id

    Returns:
        WorkflowResult: The workflow details

    Error Handling:
        Decorated with `@handle_tool_errors` and returns a ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., NOT_FOUND, PERMISSION_DENIED).

    Examples:
        # Python (async)
        response = await workflow_get(WorkflowGetInput(workflow_id="wf_123"))
        if response.ok:
            print(response.result.name)
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        resp = await client.workflow.get(input.workflow_id)
    if not resp or not resp.items:
        raise ClickUpAPIError("Get workflow failed")
    wf_domain = WorkflowMapper.to_domain(resp.items[0])
    return WorkflowResult(**WorkflowMapper.to_workflow_result_output(wf_domain))


@mcp.tool(
    title="Update Workflow",
    name="workflow.update",
    description=("Update a workflow automation by ID. HTTP: PUT /workflow/{workflow_id}."),
    annotations={
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def workflow_update(input: WorkflowUpdateInput) -> WorkflowResult:
    """
    Update a workflow automation.

    API:
        PUT /workflow/{workflow_id}

    Args:
        input: WorkflowUpdateInput with workflow_id and optional name, description, trigger_type, trigger_config, actions, is_active, priority

    Returns:
        WorkflowResult: The updated workflow

    Error Handling:
        Decorated with `@handle_tool_errors` and returns a ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., NOT_FOUND, VALIDATION_ERROR, PERMISSION_DENIED).

    Examples:
        # Python (async)
        response = await workflow_update(WorkflowUpdateInput(workflow_id="wf_123", name="Updated name"))
        if response.ok:
            print(response.result.name)
    """
    client = ClickUpAPIClientFactory.get()
    domain = WorkflowMapper.from_update_input(input)
    dto = WorkflowMapper.to_update_dto(domain)
    async with client:
        resp = await client.workflow.update(input.workflow_id, dto)
    if not resp or not resp.items:
        raise ClickUpAPIError("Update workflow failed")
    wf_domain = WorkflowMapper.to_domain(resp.items[0])
    return WorkflowResult(**WorkflowMapper.to_workflow_result_output(wf_domain))


@mcp.tool(
    title="Delete Workflow",
    name="workflow.delete",
    description=("Delete a workflow automation by ID. HTTP: DELETE /workflow/{workflow_id}."),
    annotations={
        "destructiveHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def workflow_delete(input: WorkflowDeleteInput) -> dict:
    """
    Delete a workflow automation.

    API:
        DELETE /workflow/{workflow_id}

    Args:
        input: WorkflowDeleteInput with workflow_id

    Returns:
        dict: Success message

    Error Handling:
        Decorated with `@handle_tool_errors` and returns a ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., NOT_FOUND, PERMISSION_DENIED).

    Examples:
        # Python (async)
        response = await workflow_delete(WorkflowDeleteInput(workflow_id="wf_123"))
        if response.ok:
            print("Workflow deleted")
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        deleted = await client.workflow.delete(input.workflow_id)
    if not deleted:
        raise ClickUpAPIError("Delete workflow failed")
    return {"message": "Workflow deleted successfully"}


@mcp.tool(
    title="List Workflows",
    name="workflow.list",
    description=(
        "List workflow automations for a team with pagination and filters. HTTP: GET /team/{team_id}/workflow."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def workflow_list(input: WorkflowListInput) -> WorkflowListResult:
    """
    List workflow automations for a team.

    API:
        GET /team/{team_id}/workflow

    Args:
        input: WorkflowListInput with team_id, page, limit, and optional is_active

    Returns:
        WorkflowListResult: List of workflows with pagination

    Error Handling:
        Decorated with `@handle_tool_errors` and returns a ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await workflow_list(WorkflowListInput(team_id="team_1", limit=50))
        if response.ok:
            for wf in response.result.items:
                print(wf.name)
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        resp = await client.workflow.list(input.team_id, page=input.page, limit=input.limit, is_active=input.is_active)
    if not resp:
        raise ClickUpAPIError("List workflows failed")
    items = [WorkflowMapper.to_workflow_list_item_output(WorkflowMapper.to_domain(item)) for item in resp.items]
    return WorkflowListResult(items=items, next_cursor=f"page={input.page + 1}" if len(items) == input.limit else None)
