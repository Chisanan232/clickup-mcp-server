"""
Data models for ClickUp operations.

This module provides Pydantic models for encapsulating ClickUp API operation parameters
and responses, following PEP 484/585 standards for type hints and domain-driven design.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def snake_to_camel(field: str) -> str:
    """Convert snake_case to camelCase for ClickUp API compatibility."""
    parts = field.split('_')
    return parts[0] + ''.join(p.title() for p in parts[1:])


class ClickUpBaseModel(BaseModel):
    """Base model for all ClickUp data models."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=snake_to_camel,
        from_attributes=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


# Team Models
class TeamRequest(ClickUpBaseModel):
    """Request model for team operations."""
    team_id: str = Field(..., description="The team ID")


class TeamMembersRequest(ClickUpBaseModel):
    """Request model for getting team members."""
    team_id: str = Field(..., description="The team ID")


# Space Models
class SpaceRequest(ClickUpBaseModel):
    """Request model for space operations."""
    space_id: str = Field(..., description="The space ID")


class SpacesRequest(ClickUpBaseModel):
    """Request model for getting spaces in a team."""
    team_id: str = Field(..., description="The team ID")


class CreateSpaceRequest(ClickUpBaseModel):
    """Request model for creating a space."""
    team_id: str = Field(..., description="The team ID")
    name: str = Field(..., description="The space name")
    description: Optional[str] = Field(None, description="The space description")
    multiple_assignees: Optional[bool] = Field(None, description="Allow multiple assignees")
    features: Optional[Dict[str, Any]] = Field(None, description="Space features configuration")
    private: Optional[bool] = Field(None, description="Private space flag")


# Folder Models
class FolderRequest(ClickUpBaseModel):
    """Request model for folder operations."""
    folder_id: str = Field(..., description="The folder ID")


class FoldersRequest(ClickUpBaseModel):
    """Request model for getting folders in a space."""
    space_id: str = Field(..., description="The space ID")


class CreateFolderRequest(ClickUpBaseModel):
    """Request model for creating a folder."""
    space_id: str = Field(..., description="The space ID")
    name: str = Field(..., description="The folder name")


# List Models
class ListRequest(ClickUpBaseModel):
    """Request model for list operations."""
    list_id: str = Field(..., description="The list ID")


class ListsRequest(ClickUpBaseModel):
    """Request model for getting lists."""
    folder_id: Optional[str] = Field(None, description="The folder ID")
    space_id: Optional[str] = Field(None, description="The space ID")
    
    @model_validator(mode='after')
    def validate_ids(self):
        """Ensure either folder_id or space_id is provided."""
        if not self.folder_id and not self.space_id:
            raise ValueError("Either folder_id or space_id must be provided")
        return self
        return v


class CreateListRequest(ClickUpBaseModel):
    """Request model for creating a list."""
    name: str = Field(..., description="The list name")
    folder_id: Optional[str] = Field(None, description="The folder ID")
    space_id: Optional[str] = Field(None, description="The space ID")
    content: Optional[str] = Field(None, description="List description")
    due_date: Optional[int] = Field(None, description="Due date as Unix timestamp")
    due_date_time: Optional[bool] = Field(None, description="Include time in due date")
    priority: Optional[int] = Field(None, description="Priority level")
    assignee: Optional[str] = Field(None, description="Assignee ID")
    status: Optional[str] = Field(None, description="Status")
    
    @model_validator(mode='after')
    def validate_ids(self):
        """Ensure either folder_id or space_id is provided."""
        if not self.folder_id and not self.space_id:
            raise ValueError("Either folder_id or space_id must be provided")
        return self


# Task Models
class TaskRequest(ClickUpBaseModel):
    """Request model for task operations."""
    task_id: str = Field(..., description="The task ID")
    custom_task_ids: Optional[bool] = Field(False, description="Use custom task IDs")
    team_id: Optional[str] = Field(None, description="The team ID")


class TasksRequest(ClickUpBaseModel):
    """Request model for getting tasks with filtering options."""
    list_id: str = Field(..., description="The list ID")
    page: Optional[int] = Field(0, description="Page number for pagination")
    order_by: Optional[str] = Field("created", description="Field to order by")
    reverse: Optional[bool] = Field(False, description="Reverse order")
    subtasks: Optional[bool] = Field(False, description="Include subtasks")
    statuses: Optional[List[str]] = Field(None, description="Filter by statuses")
    include_closed: Optional[bool] = Field(False, description="Include closed tasks")
    assignees: Optional[List[str]] = Field(None, description="Filter by assignee IDs")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    due_date_gt: Optional[int] = Field(None, description="Due date greater than (Unix timestamp)")
    due_date_lt: Optional[int] = Field(None, description="Due date less than (Unix timestamp)")
    date_created_gt: Optional[int] = Field(None, description="Created date greater than (Unix timestamp)")
    date_created_lt: Optional[int] = Field(None, description="Created date less than (Unix timestamp)")
    date_updated_gt: Optional[int] = Field(None, description="Updated date greater than (Unix timestamp)")
    date_updated_lt: Optional[int] = Field(None, description="Updated date less than (Unix timestamp)")
    custom_fields: Optional[List[Dict[str, Any]]] = Field(None, description="Custom field filters")


class CustomField(ClickUpBaseModel):
    """Model for custom field configuration."""
    id: str = Field(..., description="Custom field ID")
    name: str = Field(..., description="Custom field name")
    type: str = Field(..., description="Custom field type")
    value: Any = Field(..., description="Custom field value")


class CreateTaskRequest(ClickUpBaseModel):
    """Request model for creating a task."""
    list_id: str = Field(..., description="The list ID")
    name: str = Field(..., description="Task name")
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
    custom_fields: Optional[List[CustomField]] = Field(None, description="Custom field values")
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        """Validate priority is between 0-4."""
        if v is not None and (v < 0 or v > 4):
            raise ValueError("Priority must be between 0 (no priority) and 4 (low)")
        return v


class UpdateTaskRequest(ClickUpBaseModel):
    """Request model for updating a task."""
    task_id: str = Field(..., description="The task ID")
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
    custom_fields: Optional[List[CustomField]] = Field(None, description="Custom field values")
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        """Validate priority is between 0-4."""
        if v is not None and (v < 0 or v > 4):
            raise ValueError("Priority must be between 0 (no priority) and 4 (low)")
        return v


class DeleteTaskRequest(ClickUpBaseModel):
    """Request model for deleting a task."""
    task_id: str = Field(..., description="The task ID")
    custom_task_ids: Optional[bool] = Field(False, description="Use custom task IDs")
    team_id: Optional[str] = Field(None, description="The team ID")


# User Models
class UserRequest(ClickUpBaseModel):
    """Request model for user operations."""
    pass  # No parameters needed for getting authenticated user


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
    members: Optional[List[ClickUpUser]] = Field(None, description="Team members")


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
    statuses: Optional[List[Dict[str, Any]]] = Field(None, description="List statuses")


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
    assignees: Optional[List[ClickUpUser]] = Field(None, description="Task assignees")
    watchers: Optional[List[ClickUpUser]] = Field(None, description="Task watchers")
    checklists: Optional[List[Dict[str, Any]]] = Field(None, description="Task checklists")
    tags: Optional[List[Dict[str, Any]]] = Field(None, description="Task tags")
    parent: Optional[str] = Field(None, description="Parent task ID")
    priority: Optional[Dict[str, Any]] = Field(None, description="Task priority")
    due_date: Optional[int] = Field(None, description="Due date as Unix timestamp")
    start_date: Optional[int] = Field(None, description="Start date as Unix timestamp")
    points: Optional[int] = Field(None, description="Task points")
    time_estimate: Optional[int] = Field(None, description="Time estimate in milliseconds")
    time_spent: Optional[int] = Field(None, description="Time spent in milliseconds")
    custom_fields: Optional[List[CustomField]] = Field(None, description="Custom field values")
    dependencies: Optional[List[Dict[str, Any]]] = Field(None, description="Task dependencies")
    linked_tasks: Optional[List[Dict[str, Any]]] = Field(None, description="Linked tasks")
    team_id: Optional[str] = Field(None, description="Team ID")
    url: Optional[str] = Field(None, description="Task URL")
    permission_level: Optional[str] = Field(None, description="Permission level")
    list: Optional[Dict[str, Any]] = Field(None, description="Parent list")
    project: Optional[Dict[str, Any]] = Field(None, description="Parent project")
    folder: Optional[Dict[str, Any]] = Field(None, description="Parent folder")
    space: Optional[Dict[str, Any]] = Field(None, description="Parent space")


# Helper functions for model conversions
def extract_create_task_data(request: CreateTaskRequest) -> Dict[str, Any]:
    """Extract task creation data from request model."""
    data = {"name": request.name}
    
    if request.description:
        data["description"] = request.description
    if request.assignees:
        data["assignees"] = request.assignees
    if request.tags:
        data["tags"] = request.tags
    if request.status:
        data["status"] = request.status
    if request.priority is not None:
        data["priority"] = request.priority
    if request.due_date:
        data["due_date"] = request.due_date
        if request.due_date_time is not None:
            data["due_date_time"] = request.due_date_time
    if request.time_estimate:
        data["time_estimate"] = request.time_estimate
    if request.start_date:
        data["start_date"] = request.start_date
        if request.start_date_time is not None:
            data["start_date_time"] = request.start_date_time
    if request.notify_all is not None:
        data["notify_all"] = request.notify_all
    if request.parent:
        data["parent"] = request.parent
    if request.links_to:
        data["links_to"] = request.links_to
    if request.check_required_custom_fields is not None:
        data["check_required_custom_fields"] = request.check_required_custom_fields
    if request.custom_fields:
        data["custom_fields"] = [
            {"field_id": field.id, "value": field.value} for field in request.custom_fields
        ]
    
    return data


def extract_update_task_data(request: UpdateTaskRequest) -> Dict[str, Any]:
    """Extract task update data from request model."""
    data = {}
    
    if request.name:
        data["name"] = request.name
    if request.description:
        data["description"] = request.description
    if request.assignees:
        data["assignees"] = request.assignees
    if request.tags:
        data["tags"] = request.tags
    if request.status:
        data["status"] = request.status
    if request.priority is not None:
        data["priority"] = request.priority
    if request.due_date:
        data["due_date"] = request.due_date
    if request.time_estimate:
        data["time_estimate"] = request.time_estimate
    if request.start_date:
        data["start_date"] = request.start_date
    if request.custom_fields:
        data["custom_fields"] = [
            {"field_id": field.id, "value": field.value} for field in request.custom_fields
        ]
    
    return data


def extract_tasks_params(request: TasksRequest) -> Dict[str, Any]:
    """Extract task filtering parameters from request model."""
    params = {
        "page": request.page,
        "order_by": request.order_by,
        "reverse": request.reverse,
        "subtasks": request.subtasks,
        "include_closed": request.include_closed,
    }
    
    # Add optional parameters if provided
    if request.statuses:
        params["statuses[]"] = request.statuses
    if request.assignees:
        params["assignees[]"] = request.assignees
    if request.tags:
        params["tags[]"] = request.tags
    if request.due_date_gt is not None:
        params["due_date_gt"] = request.due_date_gt
    if request.due_date_lt is not None:
        params["due_date_lt"] = request.due_date_lt
    if request.date_created_gt is not None:
        params["date_created_gt"] = request.date_created_gt
    if request.date_created_lt is not None:
        params["date_created_lt"] = request.date_created_lt
    if request.date_updated_gt is not None:
        params["date_updated_gt"] = request.date_updated_gt
    if request.date_updated_lt is not None:
        params["date_updated_lt"] = request.date_updated_lt
    if request.custom_fields:
        params["custom_fields"] = request.custom_fields
    
    return params


def extract_create_space_data(request: CreateSpaceRequest) -> Dict[str, Any]:
    """Extract space creation data from request model."""
    data = {"name": request.name}
    
    if request.description:
        data["description"] = request.description
    if request.multiple_assignees is not None:
        data["multiple_assignees"] = request.multiple_assignees
    if request.features:
        data["features"] = request.features
    if request.private is not None:
        data["private"] = request.private
    
    return data


def extract_create_list_data(request: CreateListRequest) -> Dict[str, Any]:
    """Extract list creation data from request model."""
    data = {"name": request.name}
    
    if request.content:
        data["content"] = request.content
    if request.due_date:
        data["due_date"] = request.due_date
        if request.due_date_time is not None:
            data["due_date_time"] = request.due_date_time
    if request.priority is not None:
        data["priority"] = request.priority
    if request.assignee:
        data["assignee"] = request.assignee
    if request.status:
        data["status"] = request.status
    
    return data
