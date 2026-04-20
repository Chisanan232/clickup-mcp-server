"""
Workflow Context API resource manager.

This module provides a resource manager for interacting with ClickUp Workflow Contexts.
It follows the Resource Manager pattern described in the project documentation.

Capabilities:
- Create workflow contexts
- Retrieve workflow context by ID
- Update workflow contexts
- Delete workflow contexts
- List workflow contexts for a workflow

Authentication:
- All requests require the ClickUp API token in the `Authorization` header: `Authorization: pk_...`

Quick Examples:
    # Python (async)
    from clickup_mcp.client import ClickUpAPIClient
    from clickup_mcp.models.dto.workflow_context import WorkflowContextCreate

    async with ClickUpAPIClient(api_token="pk_...") as client:
        ctx_api = client.workflow_context
        ctx = await ctx_api.create(
            workflow_id="wf_1",
            context_create=WorkflowContextCreate(
                name="Production Context",
                variables={"priority": "high", "assignee": "user_789"}
            )
        )

    # curl - Get a context
    # GET /workflow/{workflow_id}/context/{context_id}
    curl -H "Authorization: pk_..." \
         https://api.clickup.com/api/v2/workflow/wf_1/context/ctx_123

    # wget - List contexts for a workflow
    # GET /workflow/{workflow_id}/context
    wget --header="Authorization: pk_..." \
         "https://api.clickup.com/api/v2/workflow/wf_1/context"
"""

import logging
from typing import TYPE_CHECKING, Optional

from clickup_mcp.models.dto.workflow_context import (
    WorkflowContextCreate,
    WorkflowContextListResponse,
    WorkflowContextUpdate,
)

if TYPE_CHECKING:
    from clickup_mcp.client import ClickUpAPIClient

logger = logging.getLogger(__name__)


class WorkflowContextAPI:
    """
    Workflow Context API resource manager.

    Provides domain-specific methods to interact with ClickUp Workflow Contexts using a shared
    HTTP client. Methods return DTOs (e.g., `WorkflowContextListResponse`) or booleans for write ops.

    Usage Examples:
        # Python (async) - Initialize
        from clickup_mcp.client import ClickUpAPIClient
        from clickup_mcp.models.dto.workflow_context import WorkflowContextCreate

        async with ClickUpAPIClient(api_token="pk_...") as client:
            ctx_api = client.workflow_context
            # Create
            created = await ctx_api.create(
                "wf_1",
                WorkflowContextCreate(name="Production Context", variables={"priority": "high"})
            )
            # Get
            ctx = await ctx_api.get("wf_1", "ctx_123")
            # Update
            updated = await ctx_api.update("wf_1", "ctx_123", WorkflowContextUpdate(name="Updated Context"))
            # Delete
            deleted = await ctx_api.delete("wf_1", "ctx_123")
            # List
            ctxs = await ctx_api.list("wf_1")
    """

    def __init__(self, client: "ClickUpAPIClient"):
        """Initialize the WorkflowContextAPI.

        Args:
            client: The ClickUpAPIClient instance to use for API requests.
        """
        self._client = client

    async def create(
        self, workflow_id: str, context_create: WorkflowContextCreate
    ) -> Optional[WorkflowContextListResponse]:
        """
        Create a workflow context.

        API:
            POST /workflow/{workflow_id}/context

        Notes:
            Creates a new workflow context for the specified workflow.

        Args:
            workflow_id: Workflow ID
            context_create: DTO containing context creation data

        Returns:
            WorkflowContextListResponse: Created context data, or None if creation failed

        Examples:
            await ctx_api.create(
                "wf_1",
                WorkflowContextCreate(name="Production Context", variables={"priority": "high"})
            )
        """
        endpoint = f"/workflow/{workflow_id}/context"
        payload = context_create.to_payload()

        logger.info(f"Creating context for workflow {workflow_id}: {context_create.name}")
        response = await self._client.post(endpoint, json=payload)

        if response and "data" in response:
            return WorkflowContextListResponse.deserialize(response["data"])
        return None

    async def get(self, workflow_id: str, context_id: str) -> Optional[WorkflowContextListResponse]:
        """
        Get a workflow context by ID.

        API:
            GET /workflow/{workflow_id}/context/{context_id}

        Args:
            workflow_id: Workflow ID
            context_id: Context ID

        Returns:
            WorkflowContextListResponse: Context data, or None if not found

        Examples:
            await ctx_api.get("wf_1", "ctx_123")
        """
        endpoint = f"/workflow/{workflow_id}/context/{context_id}"

        logger.info(f"Getting context {context_id} for workflow {workflow_id}")
        response = await self._client.get(endpoint)

        if response and "data" in response:
            return WorkflowContextListResponse.deserialize(response["data"])
        return None

    async def update(
        self, workflow_id: str, context_id: str, context_update: WorkflowContextUpdate
    ) -> Optional[WorkflowContextListResponse]:
        """
        Update a workflow context.

        API:
            PUT /workflow/{workflow_id}/context/{context_id}

        Args:
            workflow_id: Workflow ID
            context_id: Context ID
            context_update: DTO containing context update data

        Returns:
            WorkflowContextListResponse: Updated context data, or None if update failed

        Examples:
            await ctx_api.update("wf_1", "ctx_123", WorkflowContextUpdate(name="Updated Context"))
        """
        endpoint = f"/workflow/{workflow_id}/context/{context_id}"
        payload = context_update.to_payload()

        logger.info(f"Updating context {context_id} for workflow {workflow_id}")
        response = await self._client.put(endpoint, json=payload)

        if response and "data" in response:
            return WorkflowContextListResponse.deserialize(response["data"])
        return None

    async def delete(self, workflow_id: str, context_id: str) -> bool:
        """
        Delete a workflow context.

        API:
            DELETE /workflow/{workflow_id}/context/{context_id}

        Args:
            workflow_id: Workflow ID
            context_id: Context ID

        Returns:
            bool: True if deletion was successful, False otherwise

        Examples:
            await ctx_api.delete("wf_1", "ctx_123")
        """
        endpoint = f"/workflow/{workflow_id}/context/{context_id}"

        logger.info(f"Deleting context {context_id} for workflow {workflow_id}")
        response = await self._client.delete(endpoint)

        return response is not None

    async def list(self, workflow_id: str, page: int = 0, limit: int = 100) -> Optional[WorkflowContextListResponse]:
        """
        List workflow contexts for a workflow.

        API:
            GET /workflow/{workflow_id}/context

        Args:
            workflow_id: Workflow ID
            page: Page number (0-indexed)
            limit: Page size (cap 100)

        Returns:
            WorkflowContextListResponse: List of contexts, or None if request failed

        Examples:
            await ctx_api.list("wf_1", limit=50)
        """
        endpoint = f"/workflow/{workflow_id}/context"
        query_params = {
            "page": str(page),
            "limit": str(limit),
        }

        logger.info(f"Listing contexts for workflow {workflow_id} (page={page}, limit={limit})")
        response = await self._client.get(endpoint, params=query_params)

        if response and "data" in response:
            return WorkflowContextListResponse.deserialize(response["data"])
        return None
