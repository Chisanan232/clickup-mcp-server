"""
Key Result API resource manager.

This module provides a resource manager for interacting with ClickUp Key Results.
It follows the Resource Manager pattern described in the project documentation.

Capabilities:
- Create key results for goals
- Retrieve key result by ID
- Update key results
- Delete key results
- List key results for a goal

Authentication:
- All requests require the ClickUp API token in the `Authorization` header: `Authorization: pk_...`

Quick Examples:
    # Python (async)
    from clickup_mcp.client import ClickUpAPIClient
    from clickup_mcp.models.dto.key_result import KeyResultCreate

    async with ClickUpAPIClient(api_token="pk_...") as client:
        kr_api = client.key_result
        kr = await kr_api.create(
            goal_id="goal_1",
            key_result_create=KeyResultCreate(name="Increase MRR", type="currency", target=1000000)
        )

    # curl - Get a key result
    # GET /key_result/{key_result_id}
    curl -H "Authorization: pk_..." \
         https://api.clickup.com/api/v2/key_result/kr_123

    # wget - List key results for a goal
    # GET /goal/{goal_id}/key_result
    wget --header="Authorization: pk_..." \
         "https://api.clickup.com/api/v2/goal/goal_1/key_result"
"""

import logging
from typing import TYPE_CHECKING, Optional

from clickup_mcp.models.dto.key_result import (
    KeyResultCreate,
    KeyResultListResponse,
    KeyResultUpdate,
)
from clickup_mcp.types import ClickUpGoalID, ClickUpKeyResultID

if TYPE_CHECKING:
    from clickup_mcp.client import ClickUpAPIClient

logger = logging.getLogger(__name__)


class KeyResultAPI:
    """
    Key Result API resource manager.

    Provides domain-specific methods to interact with ClickUp Key Results using a shared
    HTTP client. Methods return DTOs (e.g., `KeyResultListResponse`) or booleans for write ops.

    Usage Examples:
        # Python (async) - Initialize
        from clickup_mcp.client import ClickUpAPIClient
        from clickup_mcp.models.dto.key_result import KeyResultCreate

        async with ClickUpAPIClient(api_token="pk_...") as client:
            kr_api = client.key_result
            # Create
            created = await kr_api.create("goal_1", KeyResultCreate(name="Increase MRR", type="currency", target=1000000))
            # Get
            kr = await kr_api.get("kr_123")
            # Update
            updated = await kr_api.update("kr_123", KeyResultUpdate(target=2000000))
            # Delete
            deleted = await kr_api.delete("kr_123")
            # List
            krs = await kr_api.list("goal_1")
    """

    def __init__(self, client: "ClickUpAPIClient"):
        """Initialize the KeyResultAPI.

        Args:
            client: The ClickUpAPIClient instance to use for API requests.
        """
        self._client = client

    async def create(
        self, goal_id: ClickUpGoalID, key_result_create: KeyResultCreate
    ) -> Optional[KeyResultListResponse]:
        """
        Create a key result for a goal.

        API:
            POST /goal/{goal_id}/key_result
            Docs: https://developer.clickup.com/reference/createkeyresult

        Notes:
            - Requires name, type, and target to define the key result
            - Returns a list response containing the created key result

        Args:
            goal_id: The ID of the goal
            key_result_create: KeyResultCreate DTO with key result criteria

        Returns:
            KeyResultListResponse | None: The created key result in a list response, or None if request failed

        Examples:
            # Python (async)
            created = await kr_api.create("goal_1", KeyResultCreate(name="Increase MRR", type="currency", target=1000000))

            # curl
            curl -X POST \
              -H "Authorization: pk_..." \
              -H "Content-Type: application/json" \
              -d '{"name":"Increase MRR","type":"currency","target":1000000}' \
              https://api.clickup.com/api/v2/goal/goal_1/key_result

            # wget
            wget --method=POST \
              --header="Authorization: pk_..." \
              --header="Content-Type: application/json" \
              --body-data='{"name":"Increase MRR","type":"currency","target":1000000}' \
              https://api.clickup.com/api/v2/goal/goal_1/key_result
        """
        response = await self._client.post(f"/goal/{goal_id}/key_result", data=key_result_create.serialize())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return KeyResultListResponse(**response.data)

    async def get(self, key_result_id: ClickUpKeyResultID) -> Optional[dict]:
        """
        Get a key result by ID.

        API:
            GET /key_result/{key_result_id}
            Docs: https://developer.clickup.com/reference/getkeyresult

        Args:
            key_result_id: The ID of the key result

        Returns:
            dict | None: The key result data, or None if request failed

        Examples:
            # Python (async)
            kr = await kr_api.get("kr_123")

            # curl
            curl -H "Authorization: pk_..." \
                 https://api.clickup.com/api/v2/key_result/kr_123

            # wget
            wget --header="Authorization: pk_..." \
                 https://api.clickup.com/api/v2/key_result/kr_123
        """
        response = await self._client.get(f"/key_result/{key_result_id}")

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return response.data

    async def update(self, key_result_id: ClickUpKeyResultID, key_result_update: KeyResultUpdate) -> Optional[dict]:
        """
        Update a key result.

        API:
            PUT /key_result/{key_result_id}
            Docs: https://developer.clickup.com/reference/updatekeyresult

        Notes:
            - Only include fields that need to be updated

        Args:
            key_result_id: The ID of the key result
            key_result_update: KeyResultUpdate DTO with updated fields

        Returns:
            dict | None: The updated key result data, or None if request failed

        Examples:
            # Python (async)
            updated = await kr_api.update("kr_123", KeyResultUpdate(target=2000000))

            # curl
            curl -X PUT \
              -H "Authorization: pk_..." \
              -H "Content-Type: application/json" \
              -d '{"target":2000000}' \
              https://api.clickup.com/api/v2/key_result/kr_123

            # wget
            wget --method=PUT \
              --header="Authorization: pk_..." \
              --header="Content-Type: application/json" \
              --body-data='{"target":2000000}' \
              https://api.clickup.com/api/v2/key_result/kr_123
        """
        response = await self._client.put(f"/key_result/{key_result_id}", data=key_result_update.serialize())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return response.data

    async def delete(self, key_result_id: ClickUpKeyResultID) -> bool:
        """
        Delete a key result.

        API:
            DELETE /key_result/{key_result_id}
            Docs: https://developer.clickup.com/reference/deletekeyresult

        Args:
            key_result_id: The ID of the key result

        Returns:
            bool: True if deletion was successful, False otherwise

        Examples:
            # Python (async)
            deleted = await kr_api.delete("kr_123")

            # curl
            curl -X DELETE \
              -H "Authorization: pk_..." \
              https://api.clickup.com/api/v2/key_result/kr_123

            # wget
            wget --method=DELETE \
              --header="Authorization: pk_..." \
              https://api.clickup.com/api/v2/key_result/kr_123
        """
        response = await self._client.delete(f"/key_result/{key_result_id}")

        return response.success and response.status_code == 200

    async def list(self, goal_id: ClickUpGoalID) -> Optional[KeyResultListResponse]:
        """
        List key results for a goal.

        API:
            GET /goal/{goal_id}/key_result
            Docs: https://developer.clickup.com/reference/getkeyresults

        Args:
            goal_id: The ID of the goal

        Returns:
            KeyResultListResponse | None: The list of key results, or None if request failed

        Examples:
            # Python (async)
            krs = await kr_api.list("goal_1")

            # curl
            curl -H "Authorization: pk_..." \
                 https://api.clickup.com/api/v2/goal/goal_1/key_result

            # wget
            wget --header="Authorization: pk_..." \
                 https://api.clickup.com/api/v2/goal/goal_1/key_result
        """
        response = await self._client.get(f"/goal/{goal_id}/key_result")

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return KeyResultListResponse(**response.data)
