"""
Workflow API resource manager.

This module provides a resource manager for interacting with ClickUp Workflow Automations.
It follows the Resource Manager pattern described in the project documentation.

Capabilities:
- Create workflow automations
- Retrieve workflow by ID
- Update workflow automations
- Delete workflow automations
- List workflow automations for a team

Authentication:
- All requests require the ClickUp API token in the `Authorization` header: `Authorization: pk_...`

Quick Examples:
    # Python (async)
    from clickup_mcp.client import ClickUpAPIClient
    from clickup_mcp.models.dto.workflow import WorkflowCreate

    async with ClickUpAPIClient(api_token="pk_...") as client:
        wf_api = client.workflow
        wf = await wf_api.create(
            team_id="team_1",
            workflow_create=WorkflowCreate(
                name="Auto-assign on create",
                trigger_type="task_created",
                trigger_config={"list_id": "456"},
                actions=[{"type": "assign", "user_id": "789"}]
            )
        )

    # curl - Get a workflow
    # GET /workflow/{workflow_id}
    curl -H "Authorization: pk_..." \
         https://api.clickup.com/api/v2/workflow/wf_123

    # wget - List workflows for a team
    # GET /team/{team_id}/workflow
    wget --header="Authorization: pk_..." \
         "https://api.clickup.com/api/v2/team/team_1/workflow"
"""

import logging
from typing import TYPE_CHECKING, Optional

from clickup_mcp.models.dto.workflow import (
    WorkflowCreate,
    WorkflowListResponse,
    WorkflowUpdate,
)

if TYPE_CHECKING:
    from clickup_mcp.client import ClickUpAPIClient

logger = logging.getLogger(__name__)


class WorkflowAPI:
    """
    Workflow Automation API resource manager.

    Provides domain-specific methods to interact with ClickUp Workflow Automations using a shared
    HTTP client. Methods return DTOs (e.g., `WorkflowListResponse`) or booleans for write ops.

    Usage Examples:
        # Python (async) - Initialize
        from clickup_mcp.client import ClickUpAPIClient
        from clickup_mcp.models.dto.workflow import WorkflowCreate

        async with ClickUpAPIClient(api_token="pk_...") as client:
            wf_api = client.workflow
            # Create
            created = await wf_api.create(
                "team_1",
                WorkflowCreate(
                    name="Auto-assign on create",
                    trigger_type="task_created",
                    trigger_config={"list_id": "456"},
                    actions=[{"type": "assign", "user_id": "789"}]
                )
            )
            # Get
            wf = await wf_api.get("wf_123")
            # Update
            updated = await wf_api.update("wf_123", WorkflowUpdate(name="Updated name"))
            # Delete
            deleted = await wf_api.delete("wf_123")
            # List
            wfs = await wf_api.list("team_1")
    """

    def __init__(self, client: "ClickUpAPIClient"):
        """Initialize the WorkflowAPI.

        Args:
            client: The ClickUpAPIClient instance to use for API requests.
        """
        self._client = client

    async def create(self, team_id: str, workflow_create: WorkflowCreate) -> Optional[WorkflowListResponse]:
        """
        Create a workflow automation.

        API:
            POST /team/{team_id}/workflow

        Notes:
            Creates a new workflow automation for the specified team.

        Args:
            team_id: Team/workspace ID
            workflow_create: DTO containing workflow creation data

        Returns:
            WorkflowListResponse: Created workflow data, or None if creation failed

        Examples:
            await wf_api.create(
                "team_1",
                WorkflowCreate(
                    name="Auto-assign on create",
                    trigger_type="task_created",
                    trigger_config={"list_id": "456"},
                    actions=[{"type": "assign", "user_id": "789"}]
                )
            )
        """
        endpoint = f"/team/{team_id}/workflow"
        payload = workflow_create.to_payload()

        logger.info(f"Creating workflow for team {team_id}: {workflow_create.name}")
        response = await self._client.post(endpoint, data=payload)

        if response and "data" in response:
            return WorkflowListResponse.deserialize(response["data"])
        return None

    async def get(self, workflow_id: str) -> Optional[WorkflowListResponse]:
        """
        Get a workflow automation by ID.

        API:
            GET /workflow/{workflow_id}

        Args:
            workflow_id: Workflow automation ID

        Returns:
            WorkflowListResponse: Workflow data, or None if not found

        Examples:
            await wf_api.get("wf_123")
        """
        endpoint = f"/workflow/{workflow_id}"

        logger.info(f"Getting workflow {workflow_id}")
        response = await self._client.get(endpoint)

        if response and "data" in response:
            return WorkflowListResponse.deserialize(response["data"])
        return None

    async def update(self, workflow_id: str, workflow_update: WorkflowUpdate) -> Optional[WorkflowListResponse]:
        """
        Update a workflow automation.

        API:
            PUT /workflow/{workflow_id}

        Args:
            workflow_id: Workflow automation ID
            workflow_update: DTO containing workflow update data

        Returns:
            WorkflowListResponse: Updated workflow data, or None if update failed

        Examples:
            await wf_api.update("wf_123", WorkflowUpdate(name="Updated name", is_active=False))
        """
        endpoint = f"/workflow/{workflow_id}"
        payload = workflow_update.to_payload()

        logger.info(f"Updating workflow {workflow_id}")
        response = await self._client.put(endpoint, data=payload)

        if response and "data" in response:
            return WorkflowListResponse.deserialize(response["data"])
        return None

    async def delete(self, workflow_id: str) -> bool:
        """
        Delete a workflow automation.

        API:
            DELETE /workflow/{workflow_id}

        Args:
            workflow_id: Workflow automation ID

        Returns:
            bool: True if deletion was successful, False otherwise

        Examples:
            await wf_api.delete("wf_123")
        """
        endpoint = f"/workflow/{workflow_id}"

        logger.info(f"Deleting workflow {workflow_id}")
        response = await self._client.delete(endpoint)

        return response is not None

    async def list(
        self, team_id: str, page: int = 0, limit: int = 100, is_active: bool | None = None
    ) -> Optional[WorkflowListResponse]:
        """
        List workflow automations for a team.

        API:
            GET /team/{team_id}/workflow

        Args:
            team_id: Team/workspace ID
            page: Page number (0-indexed)
            limit: Page size (cap 100)
            is_active: Filter by active status

        Returns:
            WorkflowListResponse: List of workflows, or None if request failed

        Examples:
            await wf_api.list("team_1", limit=50, is_active=True)
        """
        endpoint = f"/team/{team_id}/workflow"
        query_params = {
            "page": str(page),
            "limit": str(limit),
        }
        if is_active is not None:
            query_params["is_active"] = str(is_active).lower()

        logger.info(f"Listing workflows for team {team_id} (page={page}, limit={limit})")
        response = await self._client.get(endpoint, params=query_params)

        if response and "data" in response:
            return WorkflowListResponse.deserialize(response["data"])
        return None
