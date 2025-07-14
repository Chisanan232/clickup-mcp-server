from __future__ import annotations

# Import for backward compatibility
from typing import Any, Dict, List, Optional, Union, TypeVar

from .client import APIResponse, ClickUpAPIClient, create_clickup_client
from .models import (  # Domain models (preferred approach)
    ClickUpList,
    CustomField,
    Folder,
    Space,
    Task,
    Team,
    User,
)


class TeamAPI:
    """Resource manager for ClickUp Team operations."""

    def __init__(self, client: ClickUpAPIClient):
        """Initialize with an API client instance."""
        self.client = client

    async def get_all(self) -> APIResponse:
        """Get all teams for the authenticated user."""
        return await self.client.get("/team")

    async def get(self, team_id: str | Team) -> APIResponse:
        """Get a specific team by ID."""
        if isinstance(team_id, str):
            team = Team.get_request(team_id)
        else:
            team = team_id
        return await self.client.get(f"/team/{team.team_id}")


class SpaceAPI:
    """Resource manager for ClickUp Space operations."""

    def __init__(self, client: ClickUpAPIClient):
        """Initialize with an API client instance."""
        self.client = client

    async def get_all(self, team_id: str | Team) -> APIResponse:
        """Get all spaces in a team."""
        if isinstance(team_id, str):
            request = Space.list_request(team_id)
        else:
            request = Space.list_request(team_id.team_id)
        return await self.client.get(f"/team/{request.team_id}/space")

    async def get(self, space_id: str | Space) -> APIResponse:
        """Get a specific space by ID."""
        if isinstance(space_id, str):
            request = Space.get_request(space_id)
        else:
            request = space_id
        return await self.client.get(f"/space/{request.space_id}")

    async def create(self, team_id: str, space: Space | str, **kwargs) -> APIResponse:
        """Create a new space in a team."""
        if isinstance(space, str):
            # Legacy support: second parameter is name
            name = space
            # Handle custom fields conversion if present in kwargs
            custom_field_objects: Optional[List[Union[CustomField, Dict[str, Any]]]] = None
            if "custom_fields" in kwargs:
                custom_field_objects = []
                for field in kwargs["custom_fields"]:
                    if isinstance(field, dict):
                        # Convert dicts to CustomField objects
                        field_id = field.get("id", field.get("field_id"))
                        if field_id:
                            custom_field_objects.append(
                                CustomField(
                                    id=field_id,
                                    name=field.get("name", ""),
                                    type=field.get("type", ""),
                                    value=field.get("value", None),
                                )
                            )
                        else:
                            # If we can't convert, keep as dict
                            custom_field_objects.append(field)
                    else:
                        # Already a CustomField
                        custom_field_objects.append(field)

            space = Space.initial(
                team_id=team_id, name=name, custom_fields=custom_field_objects, **kwargs  # Use processed custom fields
            )
        elif not hasattr(space, 'team_id') or not space.team_id:
            # If space object is provided but team_id is missing
            space.team_id = team_id

        data = space.extract_create_data()
        return await self.client.post(f"/team/{space.team_id}/space", data=data)

    async def update(self, space_id: str, data: Dict[str, Any] | Space) -> APIResponse:
        """Update an existing space."""
        if isinstance(data, Space):
            update_data = data.extract_update_data()
        else:
            update_data = data
        return await self.client.put(f"/space/{space_id}", data=update_data)

    async def delete(self, space_id: str) -> APIResponse:
        """Delete a space."""
        return await self.client.delete(f"/space/{space_id}")


class FolderAPI:
    """Resource manager for ClickUp Folder operations."""

    def __init__(self, client: ClickUpAPIClient):
        """Initialize with an API client instance."""
        self.client = client

    async def get_all(self, space_id: str | Space) -> APIResponse:
        """Get all folders in a space."""
        if isinstance(space_id, str):
            request = Folder.list_request(space_id)
        else:
            request = Folder.list_request(space_id.space_id)
        return await self.client.get(f"/space/{request.space_id}/folder")

    async def get(self, folder_id: str | Folder) -> APIResponse:
        """Get a specific folder by ID."""
        if isinstance(folder_id, str):
            request = Folder.get_request(folder_id)
        else:
            request = folder_id
        return await self.client.get(f"/folder/{request.folder_id}")

    async def create(self, space_id: str, folder: Folder | str, **kwargs) -> APIResponse:
        """Create a new folder in a space."""
        if isinstance(folder, str):
            # Legacy support: second parameter is name
            name = folder
            folder = Folder.initial(name=name, space_id=space_id, **kwargs)
        elif not hasattr(folder, 'space_id') or not folder.space_id:
            # If folder object is provided but space_id is missing
            folder.space_id = space_id

        data = folder.extract_create_data()
        return await self.client.post(f"/space/{folder.space_id}/folder", data=data)

    async def update(self, folder_id: str, data: Dict[str, Any] | Folder) -> APIResponse:
        """Update an existing folder."""
        if isinstance(data, Folder):
            update_data = data.extract_update_data()
        else:
            update_data = data
        return await self.client.put(f"/folder/{folder_id}", data=update_data)

    async def delete(self, folder_id: str) -> APIResponse:
        """Delete a folder."""
        return await self.client.delete(f"/folder/{folder_id}")


class ListAPI:
    """Resource manager for ClickUp List operations."""

    def __init__(self, client: ClickUpAPIClient):
        """Initialize with an API client instance."""
        self.client = client

    async def get_all(self, container_id: str, container_type: str = "folder") -> APIResponse:
        """Get all lists in a container (folder or space).
        
        Args:
            container_id: ID of the container (folder or space)
            container_type: Type of container, either 'folder' or 'space'
            
        Returns:
            API response with lists
        """
        if container_type not in ("folder", "space"):
            raise ValueError("container_type must be either 'folder' or 'space'")
        return await self.client.get(f"/{container_type}/{container_id}/list")

    async def get(self, list_id: str | ClickUpList) -> APIResponse:
        """Get a specific list by ID."""
        if isinstance(list_id, str):
            request = ClickUpList.get_request(list_id)
        else:
            request = list_id
        return await self.client.get(f"/list/{request.list_id}")

    async def create(
        self, 
        container_id: str, 
        list_obj: ClickUpList | str, 
        container_type: str = "folder", 
        **kwargs
    ) -> APIResponse:
        """Create a new list in a container (folder or space).
        
        Args:
            container_id: ID of the container (folder or space)
            list_obj: ClickUpList instance or name string
            container_type: Type of container, either 'folder' or 'space'
            **kwargs: Additional parameters for legacy support
            
        Returns:
            API response with created list
        """
        if container_type not in ("folder", "space"):
            raise ValueError("container_type must be either 'folder' or 'space'")

        if isinstance(list_obj, str):
            # Legacy support: second parameter is name
            name = list_obj
            if container_type == "folder":
                list_obj = ClickUpList.initial(name=name, folder_id=container_id, **kwargs)
            else:
                list_obj = ClickUpList.initial(name=name, space_id=container_id, **kwargs)
        elif container_type == "folder" and (not hasattr(list_obj, 'folder_id') or not list_obj.folder_id):
            # If list object is provided but folder_id is missing
            list_obj.folder_id = container_id
        elif container_type == "space" and (not hasattr(list_obj, 'space_id') or not list_obj.space_id):
            # If list object is provided but space_id is missing
            list_obj.space_id = container_id

        data = list_obj.extract_create_data()
        return await self.client.post(f"/{container_type}/{container_id}/list", data=data)

    async def update(self, list_id: str, data: Dict[str, Any] | ClickUpList) -> APIResponse:
        """Update an existing list."""
        if isinstance(data, ClickUpList):
            update_data = data.extract_update_data()
        else:
            update_data = data
        return await self.client.put(f"/list/{list_id}", data=update_data)

    async def delete(self, list_id: str) -> APIResponse:
        """Delete a list."""
        return await self.client.delete(f"/list/{list_id}")


class TaskAPI:
    """Resource manager for ClickUp Task operations."""

    def __init__(self, client: ClickUpAPIClient):
        """Initialize with an API client instance."""
        self.client = client

    async def get_all(self, list_id: str, params: Optional[Dict[str, Any] | Task] = None) -> APIResponse:
        """Get all tasks in a list with optional filtering."""
        if isinstance(params, Task):
            query_params = params.extract_list_params()
        elif params is None:
            query_params = {}
        else:
            query_params = params
        return await self.client.get(f"/list/{list_id}/task", params=query_params)

    async def get(
        self, 
        task_id: str | Task, 
        custom_task_ids: bool = False, 
        team_id: Optional[str] = None
    ) -> APIResponse:
        """Get a specific task by ID."""
        if isinstance(task_id, str):
            request = Task.get_request(task_id, custom_task_ids, team_id)
        else:
            request = task_id

        # Build the endpoint based on whether we're using custom task IDs
        if request.custom_task_ids and request.team_id:
            endpoint = f"/task/{request.team_id}/{request.task_id}"
            params = {"custom_task_ids": "true"}
        else:
            endpoint = f"/task/{request.task_id}"
            params = {}

        return await self.client.get(endpoint, params=params)

    async def create(
        self,
        list_id: str,
        task: Task | str,
        **kwargs
    ) -> APIResponse:
        """Create a new task in a list."""
        if isinstance(task, str):
            # Legacy support: second parameter is name
            name = task
            # Handle custom fields conversion if present in kwargs
            custom_field_objects: Optional[List[Union[CustomField, Dict[str, Any]]]] = None
            if "custom_fields" in kwargs:
                custom_field_objects = []
                for field in kwargs.get("custom_fields", []):
                    if isinstance(field, dict):
                        # Convert dicts to CustomField objects
                        field_id = field.get("id", field.get("field_id"))
                        if field_id:
                            custom_field_objects.append(
                                CustomField(
                                    id=field_id,
                                    name=field.get("name", ""),
                                    type=field.get("type", ""),
                                    value=field.get("value", None),
                                )
                            )
                        else:
                            # If we can't convert, keep as dict
                            custom_field_objects.append(field)
                    else:
                        # Already a CustomField
                        custom_field_objects.append(field)

            task = Task.initial(
                list_id=list_id, 
                name=name,
                custom_fields=custom_field_objects,
                **{k: v for k, v in kwargs.items() if k != "custom_fields"}
            )
        elif not hasattr(task, 'list_id') or not task.list_id:
            # If task object is provided but list_id is missing
            task.list_id = list_id

        data = task.extract_create_data()
        return await self.client.post(f"/list/{task.list_id}/task", data=data)

    async def update(
        self,
        task_id: str,
        data: Dict[str, Any] | Task,
        custom_task_ids: bool = False,
        team_id: Optional[str] = None
    ) -> APIResponse:
        """Update an existing task."""
        # Handle both Task objects and raw data dicts
        if isinstance(data, Task):
            update_data = data.extract_update_data()
        else:
            # Special handling for custom fields when provided as dict
            if "custom_fields" in data:
                custom_fields_data = []
                for field in data["custom_fields"]:
                    if isinstance(field, dict):
                        custom_fields_data.append(field)
                    elif hasattr(field, "id") and hasattr(field, "value"):
                        custom_fields_data.append({"field_id": field.id, "value": field.value})
                data["custom_fields"] = custom_fields_data
            update_data = data

        # Build the endpoint based on whether we're using custom task IDs
        if custom_task_ids and team_id:
            endpoint = f"/task/{team_id}/{task_id}"
            params = {"custom_task_ids": "true"}
        else:
            endpoint = f"/task/{task_id}"
            params = {}

        return await self.client.put(endpoint, data=update_data, params=params)

    async def delete(
        self, 
        task_id: str | Task, 
        custom_task_ids: bool = False, 
        team_id: Optional[str] = None
    ) -> APIResponse:
        """Delete a task."""
        if isinstance(task_id, Task):
            request = task_id
            task_id = request.task_id
            custom_task_ids = request.custom_task_ids
            team_id = request.team_id

        # Build the endpoint based on whether we're using custom task IDs
        if custom_task_ids and team_id:
            endpoint = f"/task/{team_id}/{task_id}"
            params = {"custom_task_ids": "true"}
        else:
            endpoint = f"/task/{task_id}"
            params = {}

        return await self.client.delete(endpoint, params=params)
        
    async def add_comment(self, task_id: str, comment: str) -> APIResponse:
        """Add a comment to a task.
        
        Args:
            task_id: ID of the task
            comment: Comment text to add
            
        Returns:
            API response with the created comment
        """
        return await self.client.post(f"/task/{task_id}/comment", data={"comment_text": comment})
        
    async def get_comments(self, task_id: str) -> APIResponse:
        """Get all comments for a task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            API response with task comments
        """
        return await self.client.get(f"/task/{task_id}/comment")
        
    async def update_comment(self, task_id: str, comment_id: str, comment: str) -> APIResponse:
        """Update a comment on a task.
        
        Args:
            task_id: ID of the task
            comment_id: ID of the comment to update
            comment: New comment text
            
        Returns:
            API response with the updated comment
        """
        return await self.client.put(
            f"/task/{task_id}/comment/{comment_id}", 
            data={"comment_text": comment}
        )
        
    async def delete_comment(self, task_id: str, comment_id: str) -> APIResponse:
        """Delete a comment from a task.
        
        Args:
            task_id: ID of the task
            comment_id: ID of the comment to delete
            
        Returns:
            API response confirming deletion
        """
        return await self.client.delete(f"/task/{task_id}/comment/{comment_id}")
        
    async def add_tag(self, task_id: str, tag: str) -> APIResponse:
        """Add a tag to a task.
        
        Args:
            task_id: ID of the task
            tag: Tag name to add
            
        Returns:
            API response with the updated task
        """
        return await self.client.post(f"/task/{task_id}/tag/{tag}")
        
    async def get_tags(self, task_id: str) -> APIResponse:
        """Get all tags for a task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            API response with task tags
        """
        return await self.client.get(f"/task/{task_id}/tag")
        
    async def delete_tag(self, task_id: str, tag: str) -> APIResponse:
        """Delete a tag from a task.
        
        Args:
            task_id: ID of the task
            tag: Tag name to delete
            
        Returns:
            API response confirming deletion
        """
        return await self.client.delete(f"/task/{task_id}/tag/{tag}")


class UserAPI:
    """Resource manager for ClickUp User operations."""

    def __init__(self, client: ClickUpAPIClient):
        """Initialize with an API client instance."""
        self.client = client

    async def get(self) -> APIResponse:
        """Get the authenticated user."""
        return await self.client.get("/user")


class ClickUpResourceClient:
    """
    High-level client for specific ClickUp resources.

    This class provides convenient methods for common ClickUp operations
    through resource-specific managers for teams, spaces, folders, lists, and tasks.
    """

    def __init__(self, api_client: ClickUpAPIClient):
        """Initialize with an API client instance and set up resource managers."""
        self.client = api_client
        
        # Initialize resource-specific API managers
        self.team = TeamAPI(api_client)
        self.space = SpaceAPI(api_client)
        self.folder = FolderAPI(api_client)
        self.list = ListAPI(api_client)
        self.task = TaskAPI(api_client)
        self.user = UserAPI(api_client)

    # Legacy support methods that delegate to the appropriate manager
    # Team operations
    async def get_teams(self) -> APIResponse:
        """Get all teams for the authenticated user."""
        return await self.team.get_all()

    async def get_team(self, request: Team | str) -> APIResponse:
        """Get a specific team by ID."""
        return await self.team.get(request)

    # Space operations
    async def get_spaces(self, request: Space | str) -> APIResponse:
        """Get all spaces in a team."""
        if isinstance(request, str):
            return await self.space.get_all(request)
        return await self.space.get_all(request.team_id)

    async def get_space(self, request: Space | str) -> APIResponse:
        """Get a specific space by ID."""
        return await self.space.get(request)

    async def create_space(self, request: Space | str, name: Optional[str] = None, **kwargs) -> APIResponse:
        """Create a new space in a team."""
        if isinstance(request, str):
            # Legacy support: first parameter is team_id, second is name
            if name is None:
                raise ValueError("name parameter is required when using legacy format")
            return await self.space.create(request, name, **kwargs)
        return await self.space.create(request.team_id, request, **kwargs)

    async def update_space(self, request: Space | str, data: Optional[Dict[str, Any]] = None, **kwargs) -> APIResponse:
        """Update an existing space."""
        if isinstance(request, str):
            # Legacy support: first parameter is space_id, second is data
            space_id = request
            update_data = data or kwargs
            return await self.space.update(space_id, update_data)
        return await self.space.update(request.space_id, request)

    async def delete_space(self, request: Space | str) -> APIResponse:
        """Delete a space."""
        if isinstance(request, str):
            space_id = request
        else:
            space_id = request.space_id
        return await self.space.delete(space_id)

    # Folder operations
    async def get_folders(self, request: Folder | str) -> APIResponse:
        """Get all folders in a space."""
        if isinstance(request, str):
            return await self.folder.get_all(request)
        return await self.folder.get_all(request.space_id)

    async def get_folder(self, request: Folder | str) -> APIResponse:
        """Get a specific folder by ID."""
        return await self.folder.get(request)

    async def create_folder(self, request: Folder | str, name: Optional[str] = None, **kwargs) -> APIResponse:
        """Create a new folder in a space."""
        if isinstance(request, str):
            # Legacy support: first parameter is space_id, second is name
            if name is None:
                raise ValueError("name parameter is required when using legacy format")
            return await self.folder.create(request, name, **kwargs)
        return await self.folder.create(request.space_id, request, **kwargs)

    async def update_folder(self, request: Folder | str, data: Optional[Dict[str, Any]] = None, **kwargs) -> APIResponse:
        """Update an existing folder."""
        if isinstance(request, str):
            # Legacy support: first parameter is folder_id, second is data
            folder_id = request
            update_data = data or kwargs
            return await self.folder.update(folder_id, update_data)
        return await self.folder.update(request.folder_id, request)

    async def delete_folder(self, request: Folder | str) -> APIResponse:
        """Delete a folder."""
        if isinstance(request, str):
            folder_id = request
        else:
            folder_id = request.folder_id
        return await self.folder.delete(folder_id)

    # List operations
    async def get_lists(self, request: Union[Folder, str], container_type: str = "folder") -> APIResponse:
        """Get all lists in a folder or space."""
        if isinstance(request, str):
            container_id = request
        else:
            container_id = request.folder_id if hasattr(request, 'folder_id') and request.folder_id else request.space_id
            container_type = "folder" if hasattr(request, 'folder_id') and request.folder_id else "space"
        return await self.list.get_all(container_id, container_type)

    async def get_list(self, request: ClickUpList | str) -> APIResponse:
        """Get a specific list by ID."""
        return await self.list.get(request)

    async def create_list(
        self, 
        request: Union[ClickUpList, str], 
        name: Optional[str] = None, 
        container_type: str = "folder", 
        **kwargs
    ) -> APIResponse:
        """Create a new list in a folder or space."""
        if isinstance(request, str):
            # Legacy support: first parameter is container_id, second is name
            if name is None:
                raise ValueError("name parameter is required when using legacy format")
            return await self.list.create(request, name, container_type, **kwargs)
        
        # Determine the container type and ID from the request object
        if hasattr(request, 'folder_id') and request.folder_id:
            container_id = request.folder_id
            container_type = "folder"
        elif hasattr(request, 'space_id') and request.space_id:
            container_id = request.space_id
            container_type = "space"
        else:
            raise ValueError("Either folder_id or space_id must be provided in the request object")
            
        return await self.list.create(container_id, request, container_type, **kwargs)

    async def update_list(self, request: ClickUpList | str, data: Optional[Dict[str, Any]] = None, **kwargs) -> APIResponse:
        """Update an existing list."""
        if isinstance(request, str):
            # Legacy support: first parameter is list_id, second is data
            list_id = request
            update_data = data or kwargs
            return await self.list.update(list_id, update_data)
        return await self.list.update(request.list_id, request)

    async def delete_list(self, request: ClickUpList | str) -> APIResponse:
        """Delete a list."""
        if isinstance(request, str):
            list_id = request
        else:
            list_id = request.list_id
        return await self.list.delete(list_id)

    # Task operations
    async def get_tasks(
        self, 
        request: Task | str, 
        params: Optional[Dict[str, Any] | Task] = None, 
        **kwargs
    ) -> APIResponse:
        """Get all tasks in a list with optional filtering."""
        if isinstance(request, str):
            list_id = request
            filter_params = params or kwargs
        else:
            list_id = request.list_id
            filter_params = request
        return await self.task.get_all(list_id, filter_params)

    async def get_task(
        self, 
        request: Task | str, 
        custom_task_ids: bool = False, 
        team_id: Optional[str] = None
    ) -> APIResponse:
        """Get a specific task by ID."""
        if isinstance(request, Task):
            custom_task_ids = request.custom_task_ids
            team_id = request.team_id
        return await self.task.get(request, custom_task_ids, team_id)

    async def create_task(
        self,
        request: Task | str,
        name: Optional[str] = None,
        **kwargs
    ) -> APIResponse:
        """Create a new task in a list."""
        if isinstance(request, str):
            # Legacy support: first parameter is list_id, second is name
            if name is None:
                raise ValueError("name parameter is required when using legacy format")
            return await self.task.create(request, name, **kwargs)
        return await self.task.create(request.list_id, request, **kwargs)

    async def update_task(
        self,
        request: Task | str,
        data: Optional[Dict[str, Any]] = None,
        custom_task_ids: bool = False,
        team_id: Optional[str] = None,
        **kwargs
    ) -> APIResponse:
        """Update an existing task."""
        if isinstance(request, str):
            # Legacy support: first parameter is task_id, second is data
            task_id = request
            update_data = data or kwargs
            return await self.task.update(task_id, update_data, custom_task_ids, team_id)
        return await self.task.update(request.task_id, request, request.custom_task_ids, request.team_id)

    async def delete_task(
        self, 
        request: Task | str, 
        custom_task_ids: bool = False, 
        team_id: Optional[str] = None
    ) -> APIResponse:
        """Delete a task."""
        return await self.task.delete(request, custom_task_ids, team_id)

    async def add_task_comment(
        self, 
        task_id: str, 
        comment: str
    ) -> APIResponse:
        """Add a comment to a task."""
        return await self.task.add_comment(task_id, comment)

    async def get_task_comments(
        self, 
        task_id: str
    ) -> APIResponse:
        """Get comments for a task."""
        return await self.task.get_comments(task_id)

    async def update_task_comment(
        self, 
        task_id: str, 
        comment_id: str, 
        comment: str
    ) -> APIResponse:
        """Update a comment for a task."""
        return await self.task.update_comment(task_id, comment_id, comment)

    async def delete_task_comment(
        self, 
        task_id: str, 
        comment_id: str
    ) -> APIResponse:
        """Delete a comment for a task."""
        return await self.task.delete_comment(task_id, comment_id)

    async def add_task_tag(
        self, 
        task_id: str, 
        tag: str
    ) -> APIResponse:
        """Add a tag to a task."""
        return await self.task.add_tag(task_id, tag)

    async def get_task_tags(
        self, 
        task_id: str
    ) -> APIResponse:
        """Get tags for a task."""
        return await self.task.get_tags(task_id)

    async def delete_task_tag(
        self, 
        task_id: str, 
        tag: str
    ) -> APIResponse:
        """Delete a tag for a task."""
        return await self.task.delete_tag(task_id, tag)

    # User operations
    async def get_user(self) -> APIResponse:
        """Get the authenticated user."""
        return await self.user.get()


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
