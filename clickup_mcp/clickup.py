from typing import Optional, List, Dict, Any

from .client import ClickUpAPIClient, APIResponse, create_clickup_client


class ClickUpResourceClient:
    """
    High-level client for specific ClickUp resources.

    This class provides convenient methods for common ClickUp operations
    like managing teams, spaces, folders, lists, and tasks.
    """

    def __init__(self, api_client: ClickUpAPIClient):
        """Initialize with an API client instance."""
        self.client = api_client

    # Team operations
    async def get_teams(self) -> APIResponse:
        """Get all teams for the authenticated user."""
        return await self.client.get("/team")

    async def get_team(self, team_id: str) -> APIResponse:
        """Get a specific team by ID."""
        return await self.client.get(f"/team/{team_id}")

    # Space operations
    async def get_spaces(self, team_id: str) -> APIResponse:
        """Get all spaces in a team."""
        return await self.client.get(f"/team/{team_id}/space")

    async def get_space(self, space_id: str) -> APIResponse:
        """Get a specific space by ID."""
        return await self.client.get(f"/space/{space_id}")

    async def create_space(self, team_id: str, name: str, **kwargs) -> APIResponse:
        """Create a new space in a team."""
        data = {"name": name, **kwargs}
        return await self.client.post(f"/team/{team_id}/space", data=data)

    # Folder operations
    async def get_folders(self, space_id: str) -> APIResponse:
        """Get all folders in a space."""
        return await self.client.get(f"/space/{space_id}/folder")

    async def get_folder(self, folder_id: str) -> APIResponse:
        """Get a specific folder by ID."""
        return await self.client.get(f"/folder/{folder_id}")

    async def create_folder(self, space_id: str, name: str) -> APIResponse:
        """Create a new folder in a space."""
        data = {"name": name}
        return await self.client.post(f"/space/{space_id}/folder", data=data)

    # List operations
    async def get_lists(self, folder_id: Optional[str] = None, space_id: Optional[str] = None) -> APIResponse:
        """Get lists from a folder or space."""
        if folder_id:
            return await self.client.get(f"/folder/{folder_id}/list")
        elif space_id:
            return await self.client.get(f"/space/{space_id}/list")
        else:
            raise ValueError("Either folder_id or space_id must be provided")

    async def get_list(self, list_id: str) -> APIResponse:
        """Get a specific list by ID."""
        return await self.client.get(f"/list/{list_id}")

    async def create_list(
        self, name: str, folder_id: Optional[str] = None, space_id: Optional[str] = None, **kwargs
    ) -> APIResponse:
        """Create a new list in a folder or space."""
        data = {"name": name, **kwargs}

        if folder_id:
            return await self.client.post(f"/folder/{folder_id}/list", data=data)
        elif space_id:
            return await self.client.post(f"/space/{space_id}/list", data=data)
        else:
            raise ValueError("Either folder_id or space_id must be provided")

    # Task operations
    async def get_tasks(
        self,
        list_id: str,
        page: int = 0,
        order_by: str = "created",
        reverse: bool = False,
        subtasks: bool = False,
        statuses: Optional[List[str]] = None,
        include_closed: bool = False,
        assignees: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        due_date_gt: Optional[int] = None,
        due_date_lt: Optional[int] = None,
        date_created_gt: Optional[int] = None,
        date_created_lt: Optional[int] = None,
        date_updated_gt: Optional[int] = None,
        date_updated_lt: Optional[int] = None,
        custom_fields: Optional[List[Dict]] = None,
    ) -> APIResponse:
        """Get tasks from a list with optional filtering."""
        params: Dict[str, Any] = {
            "page": page,
            "order_by": order_by,
            "reverse": reverse,
            "subtasks": subtasks,
            "include_closed": include_closed,
        }

        # Add optional parameters if provided
        if statuses:
            params["statuses[]"] = statuses
        if assignees:
            params["assignees[]"] = assignees
        if tags:
            params["tags[]"] = tags
        if due_date_gt is not None:
            params["due_date_gt"] = due_date_gt
        if due_date_lt is not None:
            params["due_date_lt"] = due_date_lt
        if date_created_gt is not None:
            params["date_created_gt"] = date_created_gt
        if date_created_lt is not None:
            params["date_created_lt"] = date_created_lt
        if date_updated_gt is not None:
            params["date_updated_gt"] = date_updated_gt
        if date_updated_lt is not None:
            params["date_updated_lt"] = date_updated_lt
        if custom_fields:
            params["custom_fields"] = custom_fields

        return await self.client.get(f"/list/{list_id}/task", params=params)

    async def get_task(self, task_id: str, custom_task_ids: bool = False, team_id: Optional[str] = None) -> APIResponse:
        """Get a specific task by ID."""
        params: Dict[str, Any] = {"custom_task_ids": custom_task_ids}
        if team_id:
            params["team_id"] = team_id

        return await self.client.get(f"/task/{task_id}", params=params)

    async def create_task(
        self,
        list_id: str,
        name: str,
        description: Optional[str] = None,
        assignees: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        status: Optional[str] = None,
        priority: Optional[int] = None,
        due_date: Optional[int] = None,
        due_date_time: Optional[bool] = False,
        time_estimate: Optional[int] = None,
        start_date: Optional[int] = None,
        start_date_time: Optional[bool] = False,
        notify_all: Optional[bool] = True,
        parent: Optional[str] = None,
        links_to: Optional[str] = None,
        check_required_custom_fields: Optional[bool] = True,
        custom_fields: Optional[List[Dict]] = None,
    ) -> APIResponse:
        """Create a new task in a list."""
        data: Dict[str, Any] = {
            "name": name,
            "notify_all": notify_all,
            "check_required_custom_fields": check_required_custom_fields,
        }

        # Add optional fields if provided
        if description:
            data["description"] = description
        if assignees:
            data["assignees"] = assignees
        if tags:
            data["tags"] = tags
        if status:
            data["status"] = status
        if priority is not None:
            data["priority"] = priority
        if due_date:
            data["due_date"] = due_date
            data["due_date_time"] = due_date_time
        if time_estimate:
            data["time_estimate"] = time_estimate
        if start_date:
            data["start_date"] = start_date
            data["start_date_time"] = start_date_time
        if parent:
            data["parent"] = parent
        if links_to:
            data["links_to"] = links_to
        if custom_fields:
            data["custom_fields"] = custom_fields

        return await self.client.post(f"/list/{list_id}/task", data=data)

    async def update_task(self, task_id: str, **kwargs) -> APIResponse:
        """Update a task with the provided fields."""
        return await self.client.put(f"/task/{task_id}", data=kwargs)

    async def delete_task(
        self, task_id: str, custom_task_ids: bool = False, team_id: Optional[str] = None
    ) -> APIResponse:
        """Delete a task by ID."""
        params: Dict[str, Any] = {"custom_task_ids": custom_task_ids}
        if team_id:
            params["team_id"] = team_id

        return await self.client.delete(f"/task/{task_id}", params=params)

    # User operations
    async def get_user(self) -> APIResponse:
        """Get the authenticated user's information."""
        return await self.client.get("/user")

    async def get_team_members(self, team_id: str) -> APIResponse:
        """Get all members of a team."""
        return await self.client.get(f"/team/{team_id}/member")


# Convenience function to create a resource client
def create_resource_client(api_token: str, **kwargs) -> ClickUpResourceClient:
    """
    Create a ClickUp resource client with the provided token and optional configuration.

    Args:
        api_token: ClickUp API token
        **kwargs: Additional configuration options for the underlying API client

    Returns:
        Configured ClickUpResourceClient instance
    """
    api_client = create_clickup_client(api_token, **kwargs)
    return ClickUpResourceClient(api_client)
