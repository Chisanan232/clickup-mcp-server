"""
Data models for ClickUp operations.

This module provides Pydantic models for encapsulating ClickUp API operation parameters
and responses, following PEP 484/585 standards for type hints and domain-driven design.
"""

from __future__ import annotations

from typing import Any, Dict
from typing import List as ListType
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


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
    def get_request(cls, team_id: str) -> "Team":
        """Create a request for getting a specific team."""
        return cls(team_id=team_id)

    @classmethod
    def get_members_request(cls, team_id: str) -> "Team":
        """Create a request for getting team members."""
        return cls(team_id=team_id)


class Space(ClickUpBaseModel):
    """Domain model for ClickUp Space operations."""

    space_id: Optional[str] = Field(None, description="The space ID")
    team_id: Optional[str] = Field(None, description="The team ID")
    name: Optional[str] = Field(None, description="The space name")
    description: Optional[str] = Field(None, description="The space description")
    multiple_assignees: Optional[bool] = Field(None, description="Allow multiple assignees")
    features: Optional[Dict[str, Any]] = Field(None, description="Space features configuration")
    private: Optional[bool] = Field(None, description="Private space flag")

    @classmethod
    def get_request(cls, space_id: str) -> "Space":
        """Create a request for getting a specific space."""
        return cls(space_id=space_id)

    @classmethod
    def list_request(cls, team_id: str) -> "Space":
        """Create a request for listing spaces in a team."""
        return cls(team_id=team_id)

    @classmethod
    def create_request(cls, team_id: str, name: str, **kwargs) -> "Space":
        """Create a request for creating a new space."""
        return cls(team_id=team_id, name=name, **kwargs)

    @model_validator(mode="after")
    def validate_create_request(self):
        """Validate create request has required fields."""
        if self.name and not self.team_id:
            raise ValueError("team_id is required when creating a space")
        return self

    def extract_create_data(self) -> Dict[str, Any]:
        """Extract data for space creation."""
        data = {"name": self.name}

        if self.description:
            data["description"] = self.description
        if self.multiple_assignees is not None:
            data["multiple_assignees"] = self.multiple_assignees
        if self.features:
            data["features"] = self.features
        if self.private is not None:
            data["private"] = self.private

        return data


class Folder(ClickUpBaseModel):
    """Domain model for ClickUp Folder operations."""

    folder_id: Optional[str] = Field(None, description="The folder ID")
    space_id: Optional[str] = Field(None, description="The space ID")
    name: Optional[str] = Field(None, description="The folder name")

    @classmethod
    def get_request(cls, folder_id: str) -> "Folder":
        """Create a request for getting a specific folder."""
        return cls(folder_id=folder_id)

    @classmethod
    def list_request(cls, space_id: str) -> "Folder":
        """Create a request for listing folders in a space."""
        return cls(space_id=space_id)

    @classmethod
    def create_request(cls, space_id: str, name: str) -> "Folder":
        """Create a request for creating a new folder."""
        return cls(space_id=space_id, name=name)

    @model_validator(mode="after")
    def validate_create_request(self):
        """Validate create request has required fields."""
        if self.name and not self.space_id:
            raise ValueError("space_id is required when creating a folder")
        return self

    def extract_create_data(self) -> Dict[str, Any]:
        """Extract data for folder creation."""
        return {"name": self.name}


class ClickUpListDomain(ClickUpBaseModel):
    """Domain model for ClickUp List operations."""

    list_id: Optional[str] = Field(None, description="The list ID")
    folder_id: Optional[str] = Field(None, description="The folder ID")
    space_id: Optional[str] = Field(None, description="The space ID")
    name: Optional[str] = Field(None, description="The list name")
    content: Optional[str] = Field(None, description="List description")
    due_date: Optional[int] = Field(None, description="Due date as Unix timestamp")
    due_date_time: Optional[bool] = Field(None, description="Include time in due date")
    priority: Optional[int] = Field(None, description="Priority level")
    assignee: Optional[str] = Field(None, description="Assignee ID")
    status: Optional[str] = Field(None, description="Status")

    @classmethod
    def get_request(cls, list_id: str) -> "ClickUpListDomain":
        """Create a request for getting a specific list."""
        return cls(list_id=list_id)

    @classmethod
    def list_request(cls, folder_id: str = None, space_id: str = None) -> "ClickUpListDomain":
        """Create a request for listing lists in a folder or space."""
        if not folder_id and not space_id:
            raise ValueError("Either folder_id or space_id must be provided")
        return cls(folder_id=folder_id, space_id=space_id)

    @classmethod
    def create_request(cls, name: str, folder_id: str = None, space_id: str = None, **kwargs) -> "ClickUpListDomain":
        """Create a request for creating a new list."""
        if not folder_id and not space_id:
            raise ValueError("Either folder_id or space_id must be provided")
        return cls(name=name, folder_id=folder_id, space_id=space_id, **kwargs)

    @model_validator(mode="after")
    def validate_list_request(self):
        """Validate list request has required fields."""
        if self.name and not self.folder_id and not self.space_id:
            raise ValueError("Either folder_id or space_id must be provided when creating a list")
        return self

    def extract_create_data(self) -> Dict[str, Any]:
        """Extract data for list creation."""
        data = {"name": self.name}

        if self.content:
            data["content"] = self.content
        if self.due_date:
            data["due_date"] = self.due_date
            if self.due_date_time is not None:
                data["due_date_time"] = self.due_date_time
        if self.priority is not None:
            data["priority"] = self.priority
        if self.assignee:
            data["assignee"] = self.assignee
        if self.status:
            data["status"] = self.status

        return data


# Backward compatibility aliases
List = ClickUpListDomain


class CustomField(ClickUpBaseModel):
    """Model for custom field configuration."""

    id: str = Field(..., description="Custom field ID")
    name: str = Field(..., description="Custom field name")
    type: str = Field(..., description="Custom field type")
    value: Any = Field(..., description="Custom field value")


class Task(ClickUpBaseModel):
    """Domain model for ClickUp Task operations."""

    task_id: Optional[str] = Field(None, description="The task ID")
    list_id: Optional[str] = Field(None, description="The list ID")
    name: Optional[str] = Field(None, description="Task name")
    description: Optional[str] = Field(None, description="Task description")
    assignees: Optional[ListType[str]] = Field(None, description="List of assignee IDs")
    tags: Optional[ListType[str]] = Field(None, description="List of tags")
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
    custom_fields: Optional[ListType[Union[CustomField, Dict[str, Any]]]] = Field(
        None, description="Custom field values or filters"
    )
    custom_task_ids: Optional[bool] = Field(False, description="Use custom task IDs")
    team_id: Optional[str] = Field(None, description="The team ID")

    # Task list filtering options
    page: Optional[int] = Field(0, description="Page number for pagination")
    order_by: Optional[str] = Field("created", description="Field to order by")
    reverse: Optional[bool] = Field(False, description="Reverse order")
    subtasks: Optional[bool] = Field(False, description="Include subtasks")
    statuses: Optional[ListType[str]] = Field(None, description="Filter by statuses")
    include_closed: Optional[bool] = Field(False, description="Include closed tasks")
    due_date_gt: Optional[int] = Field(None, description="Due date greater than (Unix timestamp)")
    due_date_lt: Optional[int] = Field(None, description="Due date less than (Unix timestamp)")
    date_created_gt: Optional[int] = Field(None, description="Created date greater than (Unix timestamp)")
    date_created_lt: Optional[int] = Field(None, description="Created date less than (Unix timestamp)")
    date_updated_gt: Optional[int] = Field(None, description="Updated date greater than (Unix timestamp)")
    date_updated_lt: Optional[int] = Field(None, description="Updated date less than (Unix timestamp)")

    @classmethod
    def get_request(cls, task_id: str, custom_task_ids: bool = False, team_id: str = None) -> "Task":
        """Create a request for getting a specific task."""
        return cls(task_id=task_id, custom_task_ids=custom_task_ids, team_id=team_id)

    @classmethod
    def list_request(cls, list_id: str, **kwargs) -> "Task":
        """Create a request for listing tasks in a list."""
        return cls(list_id=list_id, **kwargs)

    @classmethod
    def create_request(cls, list_id: str, name: str, **kwargs) -> "Task":
        """Create a request for creating a new task."""
        return cls(list_id=list_id, name=name, **kwargs)

    @classmethod
    def update_request(cls, task_id: str, **kwargs) -> "Task":
        """Create a request for updating a task."""
        return cls(task_id=task_id, **kwargs)

    @classmethod
    def delete_request(cls, task_id: str, custom_task_ids: bool = False, team_id: str = None) -> "Task":
        """Create a request for deleting a task."""
        return cls(task_id=task_id, custom_task_ids=custom_task_ids, team_id=team_id)

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        """Validate priority is between 0-4."""
        if v is not None and (v < 0 or v > 4):
            raise ValueError("Priority must be between 0 (no priority) and 4 (low)")
        return v

    def extract_create_data(self) -> Dict[str, Any]:
        """Extract data for task creation."""
        data = {"name": self.name}

        if self.description:
            data["description"] = self.description
        if self.assignees:
            data["assignees"] = self.assignees
        if self.tags:
            data["tags"] = self.tags
        if self.status:
            data["status"] = self.status
        if self.priority is not None:
            data["priority"] = self.priority
        if self.due_date:
            data["due_date"] = self.due_date
            if self.due_date_time is not None:
                data["due_date_time"] = self.due_date_time
        if self.time_estimate:
            data["time_estimate"] = self.time_estimate
        if self.start_date:
            data["start_date"] = self.start_date
            if self.start_date_time is not None:
                data["start_date_time"] = self.start_date_time
        if self.notify_all is not None:
            data["notify_all"] = self.notify_all
        if self.parent:
            data["parent"] = self.parent
        if self.links_to:
            data["links_to"] = self.links_to
        if self.check_required_custom_fields is not None:
            data["check_required_custom_fields"] = self.check_required_custom_fields
        if self.custom_fields:
            data["custom_fields"] = [
                (
                    {"field_id": field.id, "value": field.value}
                    if isinstance(field, CustomField)
                    else {"field_id": field.get("id", field.get("field_id", "")), "value": field.get("value", None)}
                )
                for field in self.custom_fields
            ]

        return data

    def extract_update_data(self) -> Dict[str, Any]:
        """Extract data for task update."""
        data = {}

        if self.name:
            data["name"] = self.name
        if self.description:
            data["description"] = self.description
        if self.assignees:
            data["assignees"] = self.assignees
        if self.tags:
            data["tags"] = self.tags
        if self.status:
            data["status"] = self.status
        if self.priority is not None:
            data["priority"] = self.priority
        if self.due_date:
            data["due_date"] = self.due_date
        if self.time_estimate:
            data["time_estimate"] = self.time_estimate
        if self.start_date:
            data["start_date"] = self.start_date
        if self.custom_fields:
            data["custom_fields"] = [
                (
                    {"field_id": field.id, "value": field.value}
                    if isinstance(field, CustomField)
                    else {"field_id": field.get("id", field.get("field_id", "")), "value": field.get("value", None)}
                )
                for field in self.custom_fields
            ]

        return data

    def extract_list_params(self) -> Dict[str, Any]:
        """Extract parameters for task listing."""
        params = {
            "page": self.page,
            "order_by": self.order_by,
            "reverse": self.reverse,
            "subtasks": self.subtasks,
            "include_closed": self.include_closed,
        }

        # Add optional parameters if provided
        if self.statuses:
            params["statuses[]"] = self.statuses
        if self.assignees:
            params["assignees[]"] = self.assignees
        if self.tags:
            params["tags[]"] = self.tags
        if self.due_date_gt is not None:
            params["due_date_gt"] = self.due_date_gt
        if self.due_date_lt is not None:
            params["due_date_lt"] = self.due_date_lt
        if self.date_created_gt is not None:
            params["date_created_gt"] = self.date_created_gt
        if self.date_created_lt is not None:
            params["date_created_lt"] = self.date_created_lt
        if self.date_updated_gt is not None:
            params["date_updated_gt"] = self.date_updated_gt
        if self.date_updated_lt is not None:
            params["date_updated_lt"] = self.date_updated_lt
        if self.custom_fields:
            params["custom_fields"] = self.custom_fields

        return params


class User(ClickUpBaseModel):
    """Domain model for ClickUp User operations."""

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
    members: Optional[ListType[ClickUpUser]] = Field(None, description="Team members")


class ClickUpSpace(ClickUpBaseModel):
    """Model for ClickUp space data."""

    id: str = Field(..., description="Space ID")
    name: str = Field(..., description="Space name")
    color: Optional[str] = Field(None, description="Space color")
    private: Optional[bool] = Field(None, description="Is private space")
    avatar: Optional[str] = Field(None, description="Space avatar URL")
    admin_can_manage: Optional[bool] = Field(None, description="Admin can manage")
    statuses: Optional[ListType[Dict[str, Any]]] = Field(None, description="Space statuses")
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
    lists: Optional[ListType[Dict[str, Any]]] = Field(None, description="Lists in folder")


class ClickUpList(ClickUpBaseModel):
    """Model for ClickUp list data."""

    id: str = Field(..., description="List ID")
    name: str = Field(..., description="List name")
    orderindex: Optional[int] = Field(None, description="Order index")
    content: Optional[str] = Field(None, description="List description")
    status: Optional[Dict[str, Any]] = Field(None, description="List status")
    priority: Optional[Dict[str, Any]] = Field(None, description="List priority")
    assignee: Optional[ClickUpUser] = Field(None, description="List assignee")
    task_count: Optional[int] = Field(None, description="Task count")
    due_date: Optional[int] = Field(None, description="Due date as Unix timestamp")
    due_date_time: Optional[bool] = Field(None, description="Include time in due date")
    start_date: Optional[int] = Field(None, description="Start date as Unix timestamp")
    start_date_time: Optional[bool] = Field(None, description="Include time in start date")
    folder: Optional[Dict[str, Any]] = Field(None, description="Parent folder")
    space: Optional[Dict[str, Any]] = Field(None, description="Parent space")
    archived: Optional[bool] = Field(None, description="Is archived")
    override_statuses: Optional[bool] = Field(None, description="Override statuses")
    statuses: Optional[ListType[Dict[str, Any]]] = Field(None, description="List statuses")


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
    creator: Optional[ClickUpUser] = Field(None, description="Task creator")
    assignees: Optional[ListType[ClickUpUser]] = Field(None, description="Task assignees")
    watchers: Optional[ListType[ClickUpUser]] = Field(None, description="Task watchers")
    checklists: Optional[ListType[Dict[str, Any]]] = Field(None, description="Task checklists")
    tags: Optional[ListType[Dict[str, Any]]] = Field(None, description="Task tags")
    parent: Optional[str] = Field(None, description="Parent task ID")
    priority: Optional[Dict[str, Any]] = Field(None, description="Task priority")
    due_date: Optional[int] = Field(None, description="Due date as Unix timestamp")
    start_date: Optional[int] = Field(None, description="Start date as Unix timestamp")
    points: Optional[int] = Field(None, description="Task points")
    time_estimate: Optional[int] = Field(None, description="Time estimate in milliseconds")
    time_spent: Optional[int] = Field(None, description="Time spent in milliseconds")
    custom_fields: Optional[ListType[CustomField]] = Field(None, description="Custom field values")
    dependencies: Optional[ListType[Dict[str, Any]]] = Field(None, description="Task dependencies")
    linked_tasks: Optional[ListType[Dict[str, Any]]] = Field(None, description="Linked tasks")
    team_id: Optional[str] = Field(None, description="Team ID")
    url: Optional[str] = Field(None, description="Task URL")
    permission_level: Optional[str] = Field(None, description="Permission level")
    list: Optional[Dict[str, Any]] = Field(None, description="Parent list")
    project: Optional[Dict[str, Any]] = Field(None, description="Parent project")
    folder: Optional[Dict[str, Any]] = Field(None, description="Parent folder")
    space: Optional[Dict[str, Any]] = Field(None, description="Parent space")
