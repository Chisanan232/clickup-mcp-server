"""
Data models for ClickUp operations.

This module provides Pydantic models for encapsulating ClickUp API operation parameters
and responses, following PEP 484/585 standards for type hints and domain-driven design.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator, validator


def snake_to_camel(field: str) -> str:
    """Convert snake_case to camelCase for ClickUp API compatibility."""
    parts = field.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


class ClickUpBaseModel(BaseModel):
    """Base model for all ClickUp data models."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=snake_to_camel,
        from_attributes=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


# Domain Models with Converged Logic


class Team(ClickUpBaseModel):
    """Domain model for ClickUp Team operations."""

    team_id: str = Field(..., description="The team ID")

    @classmethod
    def initial(cls, team_id: str) -> "Team":
        """Create a new Team instance with required fields.
        
        Args:
            team_id: The team ID
            
        Returns:
            Initialized Team instance
        """
        return cls(team_id=team_id)

    @classmethod
    def get_request(cls, team_id: str) -> "Team":
        """Create a request for getting a specific team."""
        return cls(team_id=team_id)

    @classmethod
    def get_members_request(cls, team_id: str) -> "Team":
        """Create a request for getting team members."""
        return cls(team_id=team_id)


class Space(ClickUpBaseModel):
    """Domain model for ClickUp Space operations."""

    model_config = ConfigDict(
        extra="allow",  # Allow extra fields
    )

    space_id: Optional[str] = Field(None, description="The space ID")
    team_id: Optional[str] = Field(None, description="The team ID")
    name: Optional[str] = Field(None, description="The space name")
    description: Optional[str] = Field(None, description="Space description")
    multiple_assignees: Optional[bool] = Field(None, description="Allow multiple assignees")
    features: Optional[Dict[str, Any]] = Field(None, description="Features configuration")
    private: Optional[bool] = Field(None, description="Private space")

    @classmethod
    def initial(
        cls, 
        name: str, 
        team_id: str, 
        description: Optional[str] = None, 
        multiple_assignees: Optional[bool] = None, 
        features: Optional[Dict[str, Any]] = None,
        private: Optional[bool] = None,
        **kwargs
    ) -> "Space":
        """Create a new Space instance with required fields.
        
        Args:
            name: The space name
            team_id: The team ID
            description: Space description
            multiple_assignees: Allow multiple assignees
            features: Features configuration
            private: Whether space is private
            **kwargs: Additional attributes
            
        Returns:
            Initialized Space instance
        """
        return cls(
            name=name, 
            team_id=team_id,
            description=description,
            multiple_assignees=multiple_assignees,
            features=features,
            private=private,
            **kwargs
        )

    @classmethod
    def update_data(
        cls,
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        multiple_assignees: Optional[bool] = None, 
        features: Optional[Dict[str, Any]] = None,
        private: Optional[bool] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create update data dictionary for a space.
        
        Args:
            name: The space name
            description: Space description
            multiple_assignees: Allow multiple assignees
            features: Features configuration
            private: Whether space is private
            **kwargs: Additional attributes to update
            
        Returns:
            Dictionary with update data
        """
        data: Dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if multiple_assignees is not None:
            data["multiple_assignees"] = multiple_assignees
        if features is not None:
            data["features"] = features
        if private is not None:
            data["private"] = private
        # Add any additional kwargs
        data.update({k: v for k, v in kwargs.items() if v is not None})
        return data

    @classmethod
    def get_request(cls, space_id: str) -> "Space":
        """Create a request for getting a specific space."""
        return cls(
            space_id=space_id,
            team_id=None,
            name=None,
            description=None,
            multiple_assignees=None,
            features=None,
            private=None,
        )

    @classmethod
    def list_request(cls, team_id: str) -> "Space":
        """Create a request for listing spaces in a team."""
        return cls(
            team_id=team_id,
            space_id=None,
            name=None,
            description=None,
            multiple_assignees=None,
            features=None,
            private=None,
        )

    @classmethod
    def create_request(cls, team_id: str, name: str, **kwargs) -> "Space":
        """Create a new request object for space creation."""
        return cls(team_id=team_id, name=name, **kwargs)

    @model_validator(mode="after")
    def validate_create_request(self):
        """Validate create request has required fields."""
        if self.name and not self.team_id:
            raise ValueError("team_id is required when creating a space")
        return self

    def extract_create_data(self) -> Dict[str, Any]:
        """Extract data for space creation."""
        data: Dict[str, Any] = {"name": self.name}
        if self.description:
            data["description"] = self.description
        # Only include these fields if explicitly set AND not None
        if self.multiple_assignees is not None and "multiple_assignees" in self.__fields_set__:
            data["multiple_assignees"] = self.multiple_assignees
        if self.private is not None and "private" in self.__fields_set__:
            data["private"] = self.private
        if self.features:
            data["features"] = self.features

        return data


class Folder(ClickUpBaseModel):
    """Domain model for ClickUp Folder operations."""

    model_config = ConfigDict(
        extra="allow",  # Allow extra fields
    )

    folder_id: Optional[str] = Field(None, description="The folder ID")
    space_id: Optional[str] = Field(None, description="The space ID")
    name: Optional[str] = Field(None, description="The folder name")

    @classmethod
    def initial(cls, name: str, space_id: Optional[str] = None, **kwargs) -> "Folder":
        """Create a new Folder instance with required fields.
        
        Args:
            name: The folder name
            space_id: The space ID
            **kwargs: Additional attributes
            
        Returns:
            Initialized Folder instance
        """
        return cls(name=name, space_id=space_id, **kwargs)

    @classmethod
    def update_data(cls, name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Create update data dictionary for a folder.
        
        Args:
            name: The folder name
            **kwargs: Additional attributes to update
            
        Returns:
            Dictionary with update data
        """
        data: Dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        # Add any additional kwargs
        data.update({k: v for k, v in kwargs.items() if v is not None})
        return data

    @classmethod
    def get_request(cls, folder_id: str) -> "Folder":
        """Create a request for getting a specific folder."""
        return cls(folder_id=folder_id, space_id=None, name=None)

    @classmethod
    def list_request(cls, space_id: str) -> "Folder":
        """Create a request for listing folders in a space."""
        return cls(space_id=space_id, folder_id=None, name=None)

    @classmethod
    def create_request(cls, space_id: str, name: str) -> "Folder":
        """Create a request for creating a new folder."""
        return cls(space_id=space_id, name=name, folder_id=None)

    @model_validator(mode="after")
    def validate_create_request(self):
        """Validate create request has required fields."""
        if self.name and not self.space_id:
            raise ValueError("space_id is required when creating a folder")
        return self

    def extract_create_data(self) -> Dict[str, Any]:
        """Extract data for folder creation."""
        return {"name": self.name}


class ClickUpList(ClickUpBaseModel):
    """Domain model for ClickUp List operations.

    Note: Formerly known as ClickUpListDomain to avoid conflict with typing.List.
    """

    list_id: Optional[str] = Field(None, description="List ID")
    folder_id: Optional[str] = Field(None, description="Folder ID")
    space_id: Optional[str] = Field(None, description="Space ID")
    name: Optional[str] = Field(None, description="List name")
    content: Optional[str] = Field(None, description="List description")
    due_date: Optional[int] = Field(None, description="Due date as Unix timestamp")
    due_date_time: Optional[bool] = Field(None, description="Include time in due date")
    start_date: Optional[int] = Field(None, description="Start date as Unix timestamp")
    start_date_time: Optional[bool] = Field(None, description="Include time in start date")
    priority: Optional[int] = Field(None, description="Priority (1-4)")
    assignee: Optional[str] = Field(None, description="User ID to assign")
    status: Optional[str] = Field(None, description="Custom status")

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @classmethod
    def initial(
        cls,
        name: str,
        folder_id: Optional[str] = None,
        space_id: Optional[str] = None,
        content: Optional[str] = None,
        due_date: Optional[int] = None,
        due_date_time: Optional[bool] = None,
        start_date: Optional[int] = None,
        start_date_time: Optional[bool] = None,
        priority: Optional[int] = None,
        assignee: Optional[str] = None,
        status: Optional[str] = None,
        **kwargs
    ) -> "ClickUpList":
        """Create a new ClickUpList instance with required fields.
        
        Args:
            name: The list name
            folder_id: The folder ID
            space_id: The space ID
            content: List description
            due_date: Due date as Unix timestamp
            due_date_time: Include time in due date
            start_date: Start date as Unix timestamp
            start_date_time: Include time in start date
            priority: Priority (1-4)
            assignee: User ID to assign
            status: Custom status
            **kwargs: Additional attributes
            
        Returns:
            Initialized ClickUpList instance
        """
        if not folder_id and not space_id:
            raise ValueError("Either folder_id or space_id must be provided")
            
        return cls(
            name=name,
            folder_id=folder_id,
            space_id=space_id,
            content=content,
            due_date=due_date,
            due_date_time=due_date_time,
            start_date=start_date,
            start_date_time=start_date_time,
            priority=priority,
            assignee=assignee,
            status=status,
            **kwargs
        )

    @classmethod
    def update_data(
        cls,
        name: Optional[str] = None,
        content: Optional[str] = None,
        due_date: Optional[int] = None,
        due_date_time: Optional[bool] = None,
        start_date: Optional[int] = None,
        start_date_time: Optional[bool] = None,
        priority: Optional[int] = None,
        assignee: Optional[str] = None,
        status: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create update data dictionary for a list.
        
        Args:
            name: The list name
            content: List description
            due_date: Due date as Unix timestamp
            due_date_time: Include time in due date
            start_date: Start date as Unix timestamp
            start_date_time: Include time in start date
            priority: Priority (1-4)
            assignee: User ID to assign
            status: Custom status
            **kwargs: Additional attributes to update
            
        Returns:
            Dictionary with update data
        """
        data: Dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if content is not None:
            data["content"] = content
        if due_date is not None:
            data["due_date"] = due_date
        if due_date_time is not None:
            data["due_date_time"] = due_date_time
        if start_date is not None:
            data["start_date"] = start_date
        if start_date_time is not None:
            data["start_date_time"] = start_date_time
        if priority is not None:
            data["priority"] = priority
        if assignee is not None:
            data["assignee"] = assignee
        if status is not None:
            data["status"] = status
        # Add any additional kwargs
        data.update({k: v for k, v in kwargs.items() if v is not None})
        return data

    @classmethod
    def get_request(cls, list_id: str) -> "ClickUpList":
        """Create a request for getting a specific list."""
        return cls(
            list_id=list_id,
            folder_id=None,
            space_id=None,
            name=None,
            content=None,
            due_date=None,
            due_date_time=None,
            start_date=None,
            start_date_time=None,
            priority=None,
            assignee=None,
            status=None,
        )

    @classmethod
    def list_request(cls, folder_id: Optional[str] = None, space_id: Optional[str] = None) -> "ClickUpList":
        """Create a request for listing all lists in a folder or space."""
        if not folder_id and not space_id:
            raise ValueError("Either folder_id or space_id must be provided")

        return cls(
            list_id=None,
            folder_id=folder_id,
            space_id=space_id,
            name=None,
            content=None,
            due_date=None,
            due_date_time=None,
            start_date=None,
            start_date_time=None,
            priority=None,
            assignee=None,
            status=None,
        )

    @classmethod
    def create_request(
        cls, name: str, folder_id: Optional[str] = None, space_id: Optional[str] = None, **kwargs
    ) -> "ClickUpList":
        """Create a request for creating a new list."""
        if not folder_id and not space_id:
            raise ValueError("Either folder_id or space_id must be provided when creating a list")

        return cls(name=name, folder_id=folder_id, space_id=space_id, list_id=None, **kwargs)

    @model_validator(mode="after")
    def validate_create_request(self):
        """Validate create request has required fields."""
        if self.name and not (self.folder_id or self.space_id):
            raise ValueError("Either folder_id or space_id must be provided when creating a list")
        return self

    def extract_create_data(self) -> Dict[str, Any]:
        """Extract data for list creation."""
        data: Dict[str, Any] = {"name": self.name}

        # Only include fields that were explicitly set
        if self.content and "content" in self.__fields_set__:
            data["content"] = self.content
        if self.due_date and "due_date" in self.__fields_set__:
            data["due_date"] = self.due_date
        if self.due_date_time is not None and "due_date_time" in self.__fields_set__:
            data["due_date_time"] = self.due_date_time
        if self.priority and "priority" in self.__fields_set__:
            data["priority"] = self.priority
        if self.assignee and "assignee" in self.__fields_set__:
            data["assignee"] = self.assignee
        if self.status and "status" in self.__fields_set__:
            data["status"] = self.status

        return data

    def validate_list_request(self):
        """Validate list request has required fields.

        Used by tests to verify validation behavior.
        """
        # Skip validation for get requests (when list_id is set)
        if self.list_id:
            return self

        # For other operations, require folder_id or space_id
        if not (self.folder_id or self.space_id):
            raise ValueError("Either folder_id or space_id must be provided when creating a list")
        return self


# Add backward compatibility alias to ensure tests continue to work
ClickUpListDomain = ClickUpList  # For backward compatibility with existing code


class Task(ClickUpBaseModel):
    """Domain model for ClickUp Task operations."""

    model_config = ConfigDict(
        extra="allow",  # Allow extra fields
    )

    task_id: Optional[str] = Field(None, description="The task ID")
    list_id: Optional[str] = Field(None, description="The list ID")
    name: Optional[str] = Field(None, description="Task name")
    description: Optional[str] = Field(None, description="Task description")
    assignees: Optional[List[str]] = Field(None, description="List of assignee IDs")
    tags: Optional[List[str]] = Field(None, description="List of tags")
    status: Optional[str] = Field(None, description="Task status")
    priority: Optional[int] = Field(None, description="Priority level (1-4)")
    due_date: Optional[int] = Field(None, description="Due date as Unix timestamp")
    due_date_time: Optional[bool] = Field(False, description="Include time in due date")
    time_estimate: Optional[int] = Field(None, description="Time estimate in milliseconds")
    start_date: Optional[int] = Field(None, description="Start date as Unix timestamp")
    start_date_time: Optional[bool] = Field(False, description="Include time in start date")
    notify_all: Optional[bool] = Field(True, description="Notify all team members")
    parent: Optional[str] = Field(None, description="Parent task ID for subtasks")
    links_to: Optional[str] = Field(None, description="Link to another task")
    check_required_custom_fields: Optional[bool] = Field(True, description="Check required custom fields")
    custom_fields: Optional[List["CustomField" | Dict[str, Any]]] = Field(
        None, description="Custom field values or filters"
    )
    custom_task_ids: Optional[bool] = Field(False, description="Use custom task IDs")
    team_id: Optional[str] = Field(None, description="The team ID")

    # List tasks parameters
    page: int = Field(0, description="Page number for pagination")
    order_by: str = Field("created", description="Field to order by")
    reverse: bool = Field(False, description="Reverse the order")
    subtasks: bool = Field(False, description="Include subtasks")
    include_closed: bool = Field(False, description="Include closed tasks")
    statuses: Optional[List[str]] = Field(None, description="Filter by statuses")
    due_date_gt: Optional[int] = Field(None, description="Due date greater than")
    due_date_lt: Optional[int] = Field(None, description="Due date less than")
    date_created_gt: Optional[int] = Field(None, description="Date created greater than")
    date_created_lt: Optional[int] = Field(None, description="Date created less than")
    date_updated_gt: Optional[int] = Field(None, description="Date updated greater than")
    date_updated_lt: Optional[int] = Field(None, description="Date updated less than")

    @validator("priority")
    def validate_priority(cls, v):
        """Validate priority is between 1 and 4."""
        if v is not None and v not in [0, 1, 2, 3, 4]:
            raise ValueError("Priority must be between 0 (no priority) and 4 (low)")
        return v

    @classmethod
    def extract_task_from_response(cls, response_data: Dict[str, Any]) -> "Task":
        """Extract task data from API response."""
        # Extract and convert custom fields to CustomField objects if present
        custom_fields_list: Optional[List["CustomField" | Dict[str, Any]]] = None
        if "custom_fields" in response_data:
            custom_fields_list = []
            for field in response_data.get("custom_fields", []):
                if isinstance(field, dict) and field.get("id"):
                    custom_fields_list.append(
                        CustomField(
                            id=str(field.get("id", "")),
                            name=str(field.get("name", "")),
                            type=str(field.get("type", "")),
                            value=field.get("value", None),
                        )
                    )

        # Safely extract assignee IDs
        assignees_list: List[str] = []
        for assignee in response_data.get("assignees", []):
            if isinstance(assignee, dict) and assignee.get("id"):
                assignees_list.append(str(assignee.get("id", "")))

        # Extract status from response
        status = None
        if isinstance(response_data.get("status"), dict):
            status = str(response_data.get("status", {}).get("status", ""))

        # Extract list ID from response
        list_id = None
        if isinstance(response_data.get("list"), dict):
            list_id = str(response_data.get("list", {}).get("id", ""))

        return cls(
            task_id=str(response_data.get("id", "")),
            name=response_data.get("name"),
            description=response_data.get("description"),
            status=status,
            list_id=list_id,
            assignees=assignees_list,
            tags=response_data.get("tags", []),
            priority=response_data.get("priority"),
            due_date=response_data.get("due_date"),
            due_date_time=response_data.get("due_date_time"),
            time_estimate=response_data.get("time_estimate"),
            start_date=response_data.get("start_date"),
            start_date_time=response_data.get("start_date_time"),
            custom_fields=custom_fields_list,
            # Add all other fields with default values to satisfy mypy
            notify_all=True,
            parent=None,
            links_to=None,
            check_required_custom_fields=True,
            custom_task_ids=False,
            team_id=None,
            page=0,
            order_by="created",
            reverse=False,
            subtasks=False,
            include_closed=False,
            statuses=None,
            due_date_gt=None,
            due_date_lt=None,
            date_created_gt=None,
            date_created_lt=None,
            date_updated_gt=None,
            date_updated_lt=None,
        )

    @classmethod
    def extract_list_tasks_response(cls, response_data: Dict[str, Any]) -> List["Task"]:
        """Extract list of tasks from API response."""
        tasks: List["Task"] = []
        for task_data in response_data.get("tasks", []):
            tasks.append(cls.extract_task_from_response(task_data))
        return tasks

    @classmethod
    def initial(
        cls,
        name: str,
        list_id: Optional[str] = None,
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
        custom_fields: Optional[List["CustomField" | Dict[str, Any]]] = None,
        **kwargs
    ) -> "Task":
        """Create a new Task instance with required fields.
        
        Args:
            name: The task name
            list_id: The list ID
            description: Task description
            assignees: List of assignee IDs
            tags: List of tags
            status: Task status
            priority: Priority level (1-4)
            due_date: Due date as Unix timestamp
            due_date_time: Include time in due date
            time_estimate: Time estimate in milliseconds
            start_date: Start date as Unix timestamp
            start_date_time: Include time in start date
            notify_all: Notify all team members
            parent: Parent task ID for subtasks
            links_to: Link to another task
            check_required_custom_fields: Check required custom fields
            custom_fields: Custom field values
            **kwargs: Additional attributes
            
        Returns:
            Initialized Task instance
        """
        return cls(
            name=name,
            list_id=list_id,
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
            custom_fields=custom_fields,
            **kwargs
        )

    @classmethod
    def update_data(
        cls,
        name: Optional[str] = None,
        description: Optional[str] = None,
        assignees: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        status: Optional[str] = None,
        priority: Optional[int] = None,
        due_date: Optional[int] = None,
        due_date_time: Optional[bool] = None,
        time_estimate: Optional[int] = None,
        start_date: Optional[int] = None,
        start_date_time: Optional[bool] = None,
        notify_all: Optional[bool] = None,
        custom_fields: Optional[List["CustomField" | Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create update data dictionary for a task.
        
        Args:
            name: The task name
            description: Task description
            assignees: List of assignee IDs
            tags: List of tags
            status: Task status
            priority: Priority level (1-4)
            due_date: Due date as Unix timestamp
            due_date_time: Include time in due date
            time_estimate: Time estimate in milliseconds
            start_date: Start date as Unix timestamp
            start_date_time: Include time in start date
            notify_all: Notify all team members
            custom_fields: Custom field values
            **kwargs: Additional attributes to update
            
        Returns:
            Dictionary with update data
        """
        data: Dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if assignees is not None:
            data["assignees"] = assignees
        if tags is not None:
            data["tags"] = tags
        if status is not None:
            data["status"] = status
        if priority is not None:
            data["priority"] = priority
        if due_date is not None:
            data["due_date"] = due_date
        if due_date_time is not None:
            data["due_date_time"] = due_date_time
        if time_estimate is not None:
            data["time_estimate"] = time_estimate
        if start_date is not None:
            data["start_date"] = start_date
        if start_date_time is not None:
            data["start_date_time"] = start_date_time
        if notify_all is not None:
            data["notify_all"] = notify_all
            
        # Handle custom fields specially
        if custom_fields is not None:
            custom_fields_data = []
            for field in custom_fields:
                if isinstance(field, dict):
                    custom_fields_data.append(field)
                elif hasattr(field, "id") and hasattr(field, "value"):
                    custom_fields_data.append({"field_id": field.id, "value": field.value})
            data["custom_fields"] = custom_fields_data
            
        # Add any additional kwargs
        data.update({k: v for k, v in kwargs.items() if v is not None})
        return data

    @classmethod
    def get_request(cls, task_id: str, custom_task_ids: bool = False, team_id: Optional[str] = None) -> "Task":
        """Create a request for getting a specific task."""
        return cls(
            task_id=task_id,
            custom_task_ids=custom_task_ids,
            team_id=team_id,
            list_id=None,
            name=None,
            description=None,
            assignees=None,
            tags=None,
            status=None,
            priority=None,
            due_date=None,
            due_date_time=False,
            time_estimate=None,
            start_date=None,
            start_date_time=False,
            notify_all=True,
            parent=None,
            links_to=None,
            check_required_custom_fields=True,
            custom_fields=None,
            page=0,
            order_by="created",
            reverse=False,
            subtasks=False,
            include_closed=False,
            statuses=None,
            due_date_gt=None,
            due_date_lt=None,
            date_created_gt=None,
            date_created_lt=None,
            date_updated_gt=None,
            date_updated_lt=None,
        )

    @classmethod
    def list_request(
        cls,
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
        custom_fields: Optional[List["CustomField" | Dict[str, Any]]] = None,
    ) -> "Task":
        """Create a request for listing tasks."""
        return cls(
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
            task_id=None,
            name=None,
            description=None,
            status=None,
            priority=None,
            due_date=None,
            due_date_time=False,
            time_estimate=None,
            start_date=None,
            start_date_time=False,
            notify_all=True,
            parent=None,
            links_to=None,
            check_required_custom_fields=True,
            custom_task_ids=False,
            team_id=None,
        )

    @classmethod
    def create_request(
        cls,
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
        custom_fields: Optional[List["CustomField" | Dict[str, Any]]] = None,
    ) -> "Task":
        """Create a request for task creation."""
        return cls(
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
            custom_fields=custom_fields,
            custom_task_ids=False,
            task_id=None,
            team_id=None,
            page=0,
            order_by="created",
            reverse=False,
            subtasks=False,
            include_closed=False,
            statuses=None,
            due_date_gt=None,
            due_date_lt=None,
            date_created_gt=None,
            date_created_lt=None,
            date_updated_gt=None,
            date_updated_lt=None,
        )

    @classmethod
    def update_request(
        cls,
        task_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        assignees: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        status: Optional[str] = None,
        priority: Optional[int] = None,
        due_date: Optional[int] = None,
        due_date_time: Optional[bool] = None,
        time_estimate: Optional[int] = None,
        start_date: Optional[int] = None,
        start_date_time: Optional[bool] = None,
        notify_all: Optional[bool] = None,
        custom_fields: Optional[List["CustomField" | Dict[str, Any]]] = None,
    ) -> "Task":
        """Create a request for task update."""
        return cls(
            task_id=task_id,
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
            custom_fields=custom_fields,
            list_id=None,
            parent=None,
            links_to=None,
            check_required_custom_fields=True,
            custom_task_ids=False,
            team_id=None,
            page=0,
            order_by="created",
            reverse=False,
            subtasks=False,
            include_closed=False,
            statuses=None,
            due_date_gt=None,
            due_date_lt=None,
            date_created_gt=None,
            date_created_lt=None,
            date_updated_gt=None,
            date_updated_lt=None,
        )

    @classmethod
    def delete_request(cls, task_id: str, custom_task_ids: bool = False, team_id: Optional[str] = None) -> "Task":
        """Create a request for deleting a task."""
        return cls(
            task_id=task_id,
            custom_task_ids=custom_task_ids,
            team_id=team_id,
            list_id=None,
            name=None,
            description=None,
            assignees=None,
            tags=None,
            status=None,
            priority=None,
            due_date=None,
            due_date_time=False,
            time_estimate=None,
            start_date=None,
            start_date_time=False,
            notify_all=True,
            parent=None,
            links_to=None,
            check_required_custom_fields=True,
            custom_fields=None,
            page=0,
            order_by="created",
            reverse=False,
            subtasks=False,
            include_closed=False,
            statuses=None,
            due_date_gt=None,
            due_date_lt=None,
            date_created_gt=None,
            date_created_lt=None,
            date_updated_gt=None,
            date_updated_lt=None,
        )


class User(ClickUpBaseModel):
    """Domain model for ClickUp User operations."""
    
    @classmethod
    def initial(cls) -> "User":
        """Create a new User instance.
        
        Returns:
            Initialized User instance
        """
        return cls()

    @classmethod
    def get_request(cls) -> "User":
        """Create a request for getting the authenticated user."""
        return cls()


# Response Models
class ClickUpUser(ClickUpBaseModel):
    """Model for ClickUp user data."""

    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    color: Optional[str] = Field(None, description="User color")
    profile_picture: Optional[str] = Field(None, description="Profile picture URL")
    initials: Optional[str] = Field(None, description="User initials")
    week_start_day: Optional[int] = Field(None, description="Week start day")
    global_font_support: Optional[bool] = Field(None, description="Global font support")
    timezone: Optional[str] = Field(None, description="User timezone")


class ClickUpTeam(ClickUpBaseModel):
    """Model for ClickUp team data."""

    id: str = Field(..., description="Team ID")
    name: str = Field(..., description="Team name")
    color: Optional[str] = Field(None, description="Team color")
    avatar: Optional[str] = Field(None, description="Team avatar URL")
    members: Optional[List["ClickUpUser"]] = Field(None, description="Team members")


class ClickUpSpace(ClickUpBaseModel):
    """Model for ClickUp space data."""

    id: str = Field(..., description="Space ID")
    name: str = Field(..., description="Space name")
    color: Optional[str] = Field(None, description="Space color")
    private: Optional[bool] = Field(None, description="Is private space")
    avatar: Optional[str] = Field(None, description="Space avatar URL")
    admin_can_manage: Optional[bool] = Field(None, description="Admin can manage")
    statuses: Optional[List[Dict[str, Any]]] = Field(None, description="Space statuses")
    multiple_assignees: Optional[bool] = Field(None, description="Allow multiple assignees")
    features: Optional[Dict[str, Any]] = Field(None, description="Space features")


class ClickUpFolder(ClickUpBaseModel):
    """Model for ClickUp folder data."""

    id: str = Field(..., description="Folder ID")
    name: str = Field(..., description="Folder name")
    orderindex: Optional[int] = Field(None, description="Order index")
    override_statuses: Optional[bool] = Field(None, description="Override statuses")
    hidden: Optional[bool] = Field(None, description="Is hidden")
    space: Optional[Dict[str, Any]] = Field(None, description="Parent space")
    task_count: Optional[int] = Field(None, description="Task count")
    lists: Optional[List[Dict[str, Any]]] = Field(None, description="Lists in folder")


class ClickUpListResponse(ClickUpBaseModel):
    """Model for ClickUp list data."""

    id: str = Field(..., description="List ID")
    name: str = Field(..., description="List name")
    orderindex: Optional[int] = Field(None, description="Order index")
    content: Optional[str] = Field(None, description="List description")
    status: Optional[Dict[str, Any]] = Field(None, description="List status")
    priority: Optional[Dict[str, Any]] = Field(None, description="List priority")
    assignee: Optional[Dict[str, Any]] = Field(None, description="List assignee")
    task_count: Optional[int] = Field(None, description="Task count")
    due_date: Optional[int] = Field(None, description="Due date as Unix timestamp")
    start_date: Optional[int] = Field(None, description="Start date as Unix timestamp")
    folder: Optional[Dict[str, Any]] = Field(None, description="Parent folder")
    space: Optional[Dict[str, Any]] = Field(None, description="Parent space")
    archived: Optional[bool] = Field(None, description="Is archived")
    override_statuses: Optional[bool] = Field(None, description="Override statuses")
    permission_level: Optional[str] = Field(None, description="Permission level")


class ClickUpTask(ClickUpBaseModel):
    """Model for ClickUp task data."""

    id: str = Field(..., description="Task ID")
    custom_id: Optional[str] = Field(None, description="Custom task ID")
    name: str = Field(..., description="Task name")
    text_content: Optional[str] = Field(None, description="Task text content")
    description: Optional[str] = Field(None, description="Task description")
    status: Optional[Dict[str, Any]] = Field(None, description="Task status")
    orderindex: Optional[str] = Field(None, description="Order index")
    date_created: Optional[int] = Field(None, description="Date created as Unix timestamp")
    date_updated: Optional[int] = Field(None, description="Date updated as Unix timestamp")
    date_closed: Optional[int] = Field(None, description="Date closed as Unix timestamp")
    date_done: Optional[int] = Field(None, description="Date done as Unix timestamp")
    archived: Optional[bool] = Field(None, description="Is archived")
    creator: Optional["ClickUpUser"] = Field(None, description="Task creator")
    assignees: Optional[List["ClickUpUser"]] = Field(None, description="Task assignees")
    watchers: Optional[List["ClickUpUser"]] = Field(None, description="Task watchers")
    checklists: Optional[List[Dict[str, Any]]] = Field(None, description="Task checklists")
    tags: Optional[List[Dict[str, Any]]] = Field(None, description="Task tags")
    parent: Optional[str] = Field(None, description="Parent task ID")
    priority: Optional[Dict[str, Any]] = Field(None, description="Task priority")
    due_date: Optional[int] = Field(None, description="Due date as Unix timestamp")
    start_date: Optional[int] = Field(None, description="Start date as Unix timestamp")
    points: Optional[int] = Field(None, description="Task points")
    time_estimate: Optional[int] = Field(None, description="Time estimate in milliseconds")
    time_spent: Optional[int] = Field(None, description="Time spent in milliseconds")
    custom_fields: Optional[List["CustomField"]] = Field(None, description="Custom field values")
    dependencies: Optional[List[Dict[str, Any]]] = Field(None, description="Task dependencies")
    linked_tasks: Optional[List[Dict[str, Any]]] = Field(None, description="Linked tasks")
    team_id: Optional[str] = Field(None, description="Team ID")
    url: Optional[str] = Field(None, description="Task URL")
    permission_level: Optional[str] = Field(None, description="Permission level")
    list: Optional[Dict[str, Any]] = Field(None, description="Parent list")
    project: Optional[Dict[str, Any]] = Field(None, description="Parent project")
    folder: Optional[Dict[str, Any]] = Field(None, description="Parent folder")
    space: Optional[Dict[str, Any]] = Field(None, description="Parent space")


class CustomField(ClickUpBaseModel):
    """Model for custom field configuration."""

    id: str = Field(..., description="Custom field ID")
    name: str = Field(..., description="Custom field name")
    type: str = Field(..., description="Custom field type")
    value: Any = Field(..., description="Custom field value")


# Backward compatibility aliases
