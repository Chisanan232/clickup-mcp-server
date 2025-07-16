"""
DTOs for ClickUp Space API.

This module contains the request and response DTOs for the Space API endpoints.
"""

from typing import Any, Dict, List, Optional
from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO


class SpaceRequestDTO(BaseRequestDTO):
    """Base DTO for space requests."""
    
    space_id: Optional[str] = None


class CreateSpaceRequestDTO(BaseRequestDTO):
    """DTO for creating a space."""
    
    name: str
    team_id: str
    multiple_assignees: Optional[bool] = None
    features: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class UpdateSpaceRequestDTO(BaseRequestDTO):
    """DTO for updating a space."""
    
    name: Optional[str] = None
    multiple_assignees: Optional[bool] = None
    features: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class SpaceFeatureResponseDTO(BaseResponseDTO):
    """DTO for space features response."""
    
    due_dates: Optional[Dict[str, Any]] = None
    time_tracking: Optional[Dict[str, Any]] = None
    tags: Optional[Dict[str, Any]] = None
    time_estimates: Optional[Dict[str, Any]] = None
    checklists: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    remap_dependencies: Optional[Dict[str, Any]] = None
    dependency_warning: Optional[Dict[str, Any]] = None
    portfolios: Optional[Dict[str, Any]] = None


class SpaceResponseDTO(BaseResponseDTO):
    """DTO for a single space response."""
    
    id: str
    name: str
    private: Optional[bool] = None
    archived: Optional[bool] = None
    multiple_assignees: Optional[bool] = None
    features: Optional[SpaceFeatureResponseDTO] = None
    avatar: Optional[str] = None
    statuses: Optional[List[Dict[str, Any]]] = None
    members: Optional[List[Dict[str, Any]]] = None
    description: Optional[str] = None


class SpacesResponseDTO(BaseResponseDTO):
    """DTO for spaces response."""
    
    spaces: Optional[List[SpaceResponseDTO]] = Field(default_factory=list)
