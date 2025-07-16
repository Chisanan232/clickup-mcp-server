"""
DTOs for ClickUp List API.

This module contains the request and response DTOs for the List API endpoints.
"""

from typing import Any, Dict, List as PyList, Optional, Union
from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO


class ListRequestDTO(BaseRequestDTO):
    """Base DTO for list requests."""
    
    list_id: Optional[str] = None
    folder_id: Optional[str] = None
    space_id: Optional[str] = None


class CreateListRequestDTO(BaseRequestDTO):
    """DTO for creating a list."""
    
    name: str
    folder_id: Optional[str] = None
    space_id: Optional[str] = None
    content: Optional[str] = None
    due_date: Optional[int] = None
    due_date_time: Optional[bool] = None
    priority: Optional[int] = None
    assignee: Optional[Union[str, PyList[str]]] = None
    status: Optional[str] = None


class UpdateListRequestDTO(BaseRequestDTO):
    """DTO for updating a list."""
    
    name: Optional[str] = None
    content: Optional[str] = None
    due_date: Optional[int] = None
    due_date_time: Optional[bool] = None
    priority: Optional[int] = None
    assignee: Optional[Union[str, PyList[str]]] = None
    status: Optional[str] = None
    position: Optional[int] = None


class ListResponseDTO(BaseResponseDTO):
    """DTO for a single list response."""
    
    id: str
    name: str
    orderindex: Optional[int] = None
    status: Optional[Dict[str, Any]] = None
    priority: Optional[Dict[str, Any]] = None
    assignee: Optional[Dict[str, Any]] = None
    task_count: Optional[int] = None
    due_date: Optional[str] = None
    start_date: Optional[str] = None
    folder: Optional[Dict[str, Any]] = None
    space: Optional[Dict[str, Any]] = None
    archived: Optional[bool] = None
    override_statuses: Optional[bool] = None
    permission_level: Optional[str] = None
    content: Optional[str] = None
    statuses: Optional[PyList[Dict[str, Any]]] = None
    due_date_time: Optional[bool] = None
    start_date_time: Optional[bool] = None


class ListsResponseDTO(BaseResponseDTO):
    """DTO for lists response."""
    
    lists: PyList[ListResponseDTO]
