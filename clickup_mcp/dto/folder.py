"""
DTOs for ClickUp Folder API.

This module contains the request and response DTOs for the Folder API endpoints.
"""

from typing import Any, Dict, List, Optional
from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO


class FolderRequestDTO(BaseRequestDTO):
    """Base DTO for folder requests."""
    
    folder_id: Optional[str] = None
    space_id: Optional[str] = None


class CreateFolderRequestDTO(BaseRequestDTO):
    """DTO for creating a folder."""
    
    name: str
    space_id: str
    hidden: Optional[bool] = None
    position: Optional[int] = None


class UpdateFolderRequestDTO(BaseRequestDTO):
    """DTO for updating a folder."""
    
    name: Optional[str] = None
    hidden: Optional[bool] = None
    position: Optional[int] = None


class FolderResponseDTO(BaseResponseDTO):
    """DTO for a single folder response."""
    
    id: str
    name: str
    orderindex: Optional[int] = None
    override_statuses: Optional[bool] = None
    hidden: Optional[bool] = None
    space: Optional[Dict[str, Any]] = None
    task_count: Optional[str] = None
    archived: Optional[bool] = None
    statuses: Optional[List[Dict[str, Any]]] = None
    lists: Optional[List[Dict[str, Any]]] = None
    permission_level: Optional[str] = None


class FoldersResponseDTO(BaseResponseDTO):
    """DTO for folders response."""
    
    folders: List[FolderResponseDTO]
