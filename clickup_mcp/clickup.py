from __future__ import annotations

from typing import Any, Dict, List as ListType, Optional

from .client import APIResponse, ClickUpAPIClient, create_clickup_client
from .models import (
    # Domain models (preferred approach)
    Team,
    Space,
    Folder,
    List,
    Task,
    User,
    CustomField,
    
    # Legacy models (for backward compatibility)
    CreateFolderRequest,
    CreateListRequest,
    CreateSpaceRequest,
    CreateTaskRequest,
    DeleteTaskRequest,
    FolderRequest,
    FoldersRequest,
    ListRequest,
    ListsRequest,
    SpaceRequest,
    SpacesRequest,
    TaskRequest,
    TasksRequest,
    TeamMembersRequest,
    TeamRequest,
    UpdateTaskRequest,
    UserRequest,
    
    # Legacy helper functions (for backward compatibility)
    extract_create_list_data,
    extract_create_space_data,
    extract_create_task_data,
    extract_tasks_params,
    extract_update_task_data,
)


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

    async def get_team(self, request: Team | str) -> APIResponse:
        """Get a specific team by ID."""
        if isinstance(request, str):
            request = Team.get_request(request)
        return await self.client.get(f"/team/{request.team_id}")

    # Space operations
    async def get_spaces(self, request: Space | str) -> APIResponse:
        """Get all spaces in a team."""
        if isinstance(request, str):
            request = Space.list_request(request)
        return await self.client.get(f"/team/{request.team_id}/space")

    async def get_space(self, request: Space | str) -> APIResponse:
        """Get a specific space by ID."""
        if isinstance(request, str):
            request = Space.get_request(request)
        return await self.client.get(f"/space/{request.space_id}")

    async def create_space(self, request: Space | str, name: str = None, **kwargs) -> APIResponse:
        """Create a new space in a team."""
        if isinstance(request, str):
            # Legacy support: first parameter is team_id, second is name
            if name is None:
                raise ValueError("name parameter is required when using legacy format")
            request = Space.create_request(request, name, **kwargs)
        data = request.extract_create_data()
        return await self.client.post(f"/team/{request.team_id}/space", data=data)

    # Folder operations
    async def get_folders(self, request: Folder | str) -> APIResponse:
        """Get all folders in a space."""
        if isinstance(request, str):
            request = Folder.list_request(request)
        return await self.client.get(f"/space/{request.space_id}/folder")

    async def get_folder(self, request: Folder | str) -> APIResponse:
        """Get a specific folder by ID."""
        if isinstance(request, str):
            request = Folder.get_request(request)
        return await self.client.get(f"/folder/{request.folder_id}")

    async def create_folder(self, request: Folder | str, name: str = None) -> APIResponse:
        """Create a new folder in a space."""
        if isinstance(request, str):
            # Legacy support: first parameter is space_id, second is name
            if name is None:
                raise ValueError("name parameter is required when using legacy format")
            request = Folder.create_request(request, name)
        data = request.extract_create_data()
        return await self.client.post(f"/space/{request.space_id}/folder", data=data)

    # List operations
    async def get_lists(self, request: List = None, folder_id: Optional[str] = None, space_id: Optional[str] = None) -> APIResponse:
        """Get lists from a folder or space."""
        if request is None:
            # Legacy support: using keyword arguments
            if folder_id is None and space_id is None:
                raise ValueError("Either folder_id or space_id must be provided")
            request = List.list_request(folder_id=folder_id, space_id=space_id)
        
        if request.folder_id:
            return await self.client.get(f"/folder/{request.folder_id}/list")
        elif request.space_id:
            return await self.client.get(f"/space/{request.space_id}/list")
        else:
            raise ValueError("Either folder_id or space_id must be provided")

    async def get_list(self, request: List | str) -> APIResponse:
        """Get a specific list by ID."""
        if isinstance(request, str):
            request = List.get_request(request)
        return await self.client.get(f"/list/{request.list_id}")

    async def create_list(self, request: List | str, name: str = None, folder_id: Optional[str] = None, space_id: Optional[str] = None, **kwargs) -> APIResponse:
        """Create a new list in a folder or space."""
        if isinstance(request, str):
            # Legacy support: first parameter is name, then folder_id/space_id
            if name is not None:
                # If name is provided, request is actually the name and name is folder_id/space_id
                actual_name = request
                if name == folder_id or name == space_id:
                    # The name parameter is actually an ID, fix the parameters
                    request = List.create_request(name=actual_name, folder_id=folder_id, space_id=space_id, **kwargs)
                else:
                    request = List.create_request(name=actual_name, folder_id=name, space_id=space_id, **kwargs)
            else:
                # Legacy support: request is name, use folder_id/space_id from kwargs
                request = List.create_request(name=request, folder_id=folder_id, space_id=space_id, **kwargs)
        
        data = request.extract_create_data()

        if request.folder_id:
            return await self.client.post(f"/folder/{request.folder_id}/list", data=data)
        elif request.space_id:
            return await self.client.post(f"/space/{request.space_id}/list", data=data)
        else:
            raise ValueError("Either folder_id or space_id must be provided")

    # Task operations
    async def get_tasks(self, request: Task | str, **kwargs) -> APIResponse:
        """Get tasks from a list with optional filtering."""
        if isinstance(request, str):
            # Legacy support: first parameter is list_id, other parameters as kwargs
            request = Task.list_request(request, **kwargs)
        params = request.extract_list_params()
        return await self.client.get(f"/list/{request.list_id}/task", params=params)

    async def get_task(self, request: Task | str, custom_task_ids: Optional[bool] = None, team_id: Optional[str] = None) -> APIResponse:
        """Get a specific task by ID."""
        if isinstance(request, str):
            # Legacy support: first parameter is task_id, other parameters as kwargs
            request = Task.get_request(
                request,
                custom_task_ids=custom_task_ids if custom_task_ids is not None else False,
                team_id=team_id
            )
        params: Dict[str, Any] = {"custom_task_ids": request.custom_task_ids}
        if request.team_id:
            params["team_id"] = request.team_id

        return await self.client.get(f"/task/{request.task_id}", params=params)

    async def create_task(self, request: Task | str, name: str = None, **kwargs) -> APIResponse:
        """Create a new task in a list."""
        if isinstance(request, str):
            # Legacy support: first parameter is list_id, second is name
            if name is None:
                raise ValueError("name parameter is required when using legacy format")
            
            # Convert dict custom_fields to CustomField objects if needed
            custom_fields = kwargs.get("custom_fields")
            if custom_fields:
                custom_field_objects = [
                    CustomField(
                        id=field.get("id", field.get("field_id", "")),
                        name=field.get("name", ""),
                        type=field.get("type", ""),
                        value=field.get("value", None)
                    )
                    for field in custom_fields
                ]
                kwargs["custom_fields"] = custom_field_objects
            
            request = Task.create_request(request, name, **kwargs)
        data = request.extract_create_data()
        return await self.client.post(f"/list/{request.list_id}/task", data=data)

    async def update_task(self, request: Task | str, **kwargs) -> APIResponse:
        """Update a task with the provided fields."""
        if isinstance(request, str):
            # Legacy support: first parameter is task_id, other parameters as kwargs
            # Convert dict custom_fields to CustomField objects if needed
            custom_fields = kwargs.get("custom_fields")
            if custom_fields:
                custom_field_objects = [
                    CustomField(
                        id=field.get("id", field.get("field_id", "")),
                        name=field.get("name", ""),
                        type=field.get("type", ""),
                        value=field.get("value", None)
                    )
                    for field in custom_fields
                ]
                kwargs["custom_fields"] = custom_field_objects
            
            request = Task.update_request(request, **kwargs)
        data = request.extract_update_data()
        return await self.client.put(f"/task/{request.task_id}", data=data)

    async def delete_task(self, request: Task | str, custom_task_ids: Optional[bool] = None, team_id: Optional[str] = None) -> APIResponse:
        """Delete a task by ID."""
        if isinstance(request, str):
            # Legacy support: first parameter is task_id, other parameters as kwargs
            request = Task.delete_request(
                request,
                custom_task_ids=custom_task_ids if custom_task_ids is not None else False,
                team_id=team_id
            )
        params: Dict[str, Any] = {"custom_task_ids": request.custom_task_ids}
        if request.team_id:
            params["team_id"] = request.team_id

        return await self.client.delete(f"/task/{request.task_id}", params=params)

    # User operations
    async def get_user(self, request: User = None) -> APIResponse:
        """Get the authenticated user's information."""
        if request is None:
            request = User.get_request()
        return await self.client.get("/user")

    async def get_team_members(self, request: Team | str) -> APIResponse:
        """Get all members of a team."""
        if isinstance(request, str):
            request = Team.get_members_request(request)
        return await self.client.get(f"/team/{request.team_id}/member")

    # Backward compatibility methods - maintaining existing API
    async def get_team_by_id(self, team_id: str) -> APIResponse:
        """Get a specific team by ID (backward compatibility)."""
        return await self.get_team(Team.get_request(team_id))

    async def get_spaces_by_team_id(self, team_id: str) -> APIResponse:
        """Get all spaces in a team (backward compatibility)."""
        return await self.get_spaces(Space.list_request(team_id))

    async def get_space_by_id(self, space_id: str) -> APIResponse:
        """Get a specific space by ID (backward compatibility)."""
        return await self.get_space(Space.get_request(space_id))

    async def create_space_legacy(self, team_id: str, name: str, **kwargs) -> APIResponse:
        """Create a new space in a team (backward compatibility)."""
        request = Space.create_request(team_id, name, **kwargs)
        return await self.create_space(request)

    async def get_folders_by_space_id(self, space_id: str) -> APIResponse:
        """Get all folders in a space (backward compatibility)."""
        return await self.get_folders(Folder.list_request(space_id))

    async def get_folder_by_id(self, folder_id: str) -> APIResponse:
        """Get a specific folder by ID (backward compatibility)."""
        return await self.get_folder(Folder.get_request(folder_id))

    async def create_folder_legacy(self, space_id: str, name: str) -> APIResponse:
        """Create a new folder in a space (backward compatibility)."""
        request = Folder.create_request(space_id, name)
        return await self.create_folder(request)

    async def get_lists_legacy(self, folder_id: Optional[str] = None, space_id: Optional[str] = None) -> APIResponse:
        """Get lists from a folder or space (backward compatibility)."""
        request = List.list_request(folder_id=folder_id, space_id=space_id)
        return await self.get_lists(request)

    async def get_list_by_id(self, list_id: str) -> APIResponse:
        """Get a specific list by ID (backward compatibility)."""
        return await self.get_list(List.get_request(list_id))

    async def create_list_legacy(
        self, name: str, folder_id: Optional[str] = None, space_id: Optional[str] = None, **kwargs
    ) -> APIResponse:
        """Create a new list in a folder or space (backward compatibility)."""
        request = List.create_request(name=name, folder_id=folder_id, space_id=space_id, **kwargs)
        return await self.create_list(request)

    async def get_tasks_legacy(
        self,
        list_id: str,
        page: int = 0,
        order_by: str = "created",
        reverse: bool = False,
        subtasks: bool = False,
        statuses: Optional[ListType[str]] = None,
        include_closed: bool = False,
        assignees: Optional[ListType[str]] = None,
        tags: Optional[ListType[str]] = None,
        due_date_gt: Optional[int] = None,
        due_date_lt: Optional[int] = None,
        date_created_gt: Optional[int] = None,
        date_created_lt: Optional[int] = None,
        date_updated_gt: Optional[int] = None,
        date_updated_lt: Optional[int] = None,
        custom_fields: Optional[ListType[Dict[str, Any]]] = None,
    ) -> APIResponse:
        """Get tasks from a list with optional filtering (backward compatibility)."""
        request = Task.list_request(
            list_id=list_id,
            page=page,
            order_by=order_by,
            reverse=reverse,
            subtasks=subtasks,
            statuses=statuses,
            include_closed=include_closed,
            assignees=assignees,
            tags=tags,
            due_date_gt=due_date_gt,
            due_date_lt=due_date_lt,
            date_created_gt=date_created_gt,
            date_created_lt=date_created_lt,
            date_updated_gt=date_updated_gt,
            date_updated_lt=date_updated_lt,
            custom_fields=custom_fields,
        )
        return await self.get_tasks(request)

    async def get_task_by_id(self, task_id: str, custom_task_ids: bool = False, team_id: Optional[str] = None) -> APIResponse:
        """Get a specific task by ID (backward compatibility)."""
        request = Task.get_request(task_id=task_id, custom_task_ids=custom_task_ids, team_id=team_id)
        return await self.get_task(request)

    async def create_task_legacy(
        self,
        list_id: str,
        name: str,
        description: Optional[str] = None,
        assignees: Optional[ListType[str]] = None,
        tags: Optional[ListType[str]] = None,
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
        custom_fields: Optional[ListType[Dict[str, Any]]] = None,
    ) -> APIResponse:
        """Create a new task in a list (backward compatibility)."""
        # Convert dict custom_fields to CustomField objects if needed
        custom_field_objects = None
        if custom_fields:
            custom_field_objects = [
                CustomField(
                    id=field.get("id", ""),
                    name=field.get("name", ""),
                    type=field.get("type", ""),
                    value=field.get("value", None)
                )
                for field in custom_fields
            ]

        request = Task.create_request(
            list_id=list_id,
            name=name,
            description=description,
            assignees=assignees,
            tags=tags,
            status=status,
            priority=priority,
            due_date=due_date,
            due_date_time=due_date_time,
            time_estimate=time_estimate,
            start_date=start_date,
            start_date_time=start_date_time,
            notify_all=notify_all,
            parent=parent,
            links_to=links_to,
            check_required_custom_fields=check_required_custom_fields,
            custom_fields=custom_field_objects,
        )
        return await self.create_task(request)

    async def update_task_legacy(self, task_id: str, **kwargs) -> APIResponse:
        """Update a task with the provided fields (backward compatibility)."""
        # Convert dict custom_fields to CustomField objects if needed
        custom_field_objects = None
        if "custom_fields" in kwargs and kwargs["custom_fields"]:
            custom_field_objects = [
                CustomField(
                    id=field.get("id", ""),
                    name=field.get("name", ""),
                    type=field.get("type", ""),
                    value=field.get("value", None)
                )
                for field in kwargs["custom_fields"]
            ]
            kwargs["custom_fields"] = custom_field_objects

        request = Task.update_request(task_id=task_id, **kwargs)
        return await self.update_task(request)

    async def delete_task_by_id(
        self, task_id: str, custom_task_ids: bool = False, team_id: Optional[str] = None
    ) -> APIResponse:
        """Delete a task by ID (backward compatibility)."""
        request = Task.delete_request(task_id=task_id, custom_task_ids=custom_task_ids, team_id=team_id)
        return await self.delete_task(request)

    async def get_user_info(self) -> APIResponse:
        """Get the authenticated user's information (backward compatibility)."""
        return await self.get_user()

    async def get_team_members_by_id(self, team_id: str) -> APIResponse:
        """Get all members of a team (backward compatibility)."""
        request = Team.get_members_request(team_id)
        return await self.get_team_members(request)


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
