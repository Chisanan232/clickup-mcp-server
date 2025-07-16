"""
DTOs for ClickUp Team API.

This module contains the request and response DTOs for the Team API endpoints.
"""

from typing import Any, Dict, List, Optional
from pydantic import Field

from .base import BaseResponseDTO


class TeamResponseDTO(BaseResponseDTO):
    """DTO for a single team/workspace response."""
    
    id: str
    name: str
    color: Optional[str] = None
    avatar: Optional[str] = None
    members: Optional[List[Dict[str, Any]]] = None


class TeamsResponseDTO(BaseResponseDTO):
    """DTO for the teams/workspaces response."""
    
    teams: List[TeamResponseDTO]
