"""
DTOs for ClickUp Task API.

This module contains the request and response DTOs for the Task API endpoints.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO


class CustomFieldRequestDTO(BaseRequestDTO):
    """DTO for custom field in task requests."""
    
    id: str
    value: Any


class TaskRequestDTO(BaseRequestDTO):
    """Base DTO for task requests."""
    
    task_id: Optional[str] = None
    list_id: Optional[str] = None
    custom_task_ids: Optional[bool] = False
    team_id: Optional[str] = None


class CreateTaskRequestDTO(BaseRequestDTO):
    """DTO for creating a task."""
    
    name: str
    list_id: str
    description: Optional[str] = None
    assignees: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    due_date: Optional[int] = None
    due_date_time: Optional[bool] = None
    time_estimate: Optional[int] = None
    start_date: Optional[int] = None
    start_date_time: Optional[bool] = None
    notify_all: Optional[bool] = None
    parent: Optional[str] = None
    links_to: Optional[str] = None
    check_required_custom_fields: Optional[bool] = None
    custom_fields: Optional[List[CustomFieldRequestDTO]] = None


class UpdateTaskRequestDTO(BaseRequestDTO):
    """DTO for updating a task."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    assignees: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    due_date: Optional[int] = None
    due_date_time: Optional[bool] = None
    time_estimate: Optional[int] = None
    start_date: Optional[int] = None
    start_date_time: Optional[bool] = None
    notify_all: Optional[bool] = None
    parent: Optional[str] = None
    links_to: Optional[str] = None
    custom_fields: Optional[List[CustomFieldRequestDTO]] = None


class TaskStatusResponseDTO(BaseResponseDTO):
    """DTO for task status in response."""
    
    status: str
    color: str
    type: str
    orderindex: int


class TaskCreatorResponseDTO(BaseResponseDTO):
    """DTO for task creator in response."""
    
    id: int
    username: str
    color: str
    email: str
    profilePicture: Optional[str] = None


class TaskAssigneeResponseDTO(BaseResponseDTO):
    """DTO for task assignee in response."""
    
    id: int
    username: str
    color: str
    initials: str
    email: str
    profilePicture: Optional[str] = None


class CustomFieldResponseDTO(BaseResponseDTO):
    """DTO for custom field in task response."""
    
    id: str
    name: str
    type: str
    date_created: str
    hide_from_guests: bool
    value: Any
    type_config: Optional[Dict[str, Any]] = None


class TaskTagResponseDTO(BaseResponseDTO):
    """DTO for task tag in response."""
    
    name: str
    tag_fg: str
    tag_bg: str
    creator: int


class TaskResponseDTO(BaseResponseDTO):
    """DTO for a single task response."""
    
    id: str
    custom_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    status: TaskStatusResponseDTO
    orderindex: str
    date_created: str
    date_updated: str
    date_closed: Optional[str] = None
    archived: bool
    creator: TaskCreatorResponseDTO
    assignees: List[TaskAssigneeResponseDTO]
    watchers: Optional[List[Dict[str, Any]]] = None
    checklists: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[TaskTagResponseDTO]] = None
    parent: Optional[str] = None
    priority: Optional[Dict[str, Any]] = None
    due_date: Optional[str] = None
    start_date: Optional[str] = None
    points: Optional[int] = None
    time_estimate: Optional[int] = None
    time_spent: Optional[int] = None
    custom_fields: Optional[List[CustomFieldResponseDTO]] = None
    dependencies: Optional[List[str]] = None
    linked_tasks: Optional[List[Dict[str, Any]]] = None
    team_id: str
    url: str
    permission_level: str
    list: Dict[str, Any]
    project: Optional[Dict[str, Any]] = None
    folder: Dict[str, Any]
    space: Dict[str, Any]


class TasksResponseDTO(BaseResponseDTO):
    """DTO for tasks response."""
    
    tasks: List[TaskResponseDTO]


class TaskCommentUserResponseDTO(BaseResponseDTO):
    """DTO for user in comment response."""
    
    id: int
    username: str
    email: str
    color: str
    profilePicture: Optional[str] = None


class TaskCommentResponseDTO(BaseResponseDTO):
    """DTO for a single comment response."""
    
    id: str
    comment: List[Dict[str, Any]]  # Rich text format
    user: TaskCommentUserResponseDTO
    resolved: bool
    assigned_by: Optional[TaskCommentUserResponseDTO] = None
    assigned: Optional[bool] = None
    date: int
    text_content: Optional[str] = None


class TaskCommentsResponseDTO(BaseResponseDTO):
    """DTO for comments response."""
    
    comments: List[TaskCommentResponseDTO]


class CreateTaskCommentRequestDTO(BaseRequestDTO):
    """DTO for creating a comment."""
    
    comment_text: str
    assignee: Optional[int] = None
    notify_all: Optional[bool] = None


class UpdateTaskCommentRequestDTO(BaseRequestDTO):
    """DTO for updating a comment."""
    
    comment_text: str
