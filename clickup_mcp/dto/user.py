"""
DTOs for ClickUp User API.

This module contains the request and response DTOs for the User API endpoints.
"""

from typing import Dict, List, Optional
from pydantic import Field

from .base import BaseResponseDTO


class UserResponseDTO(BaseResponseDTO):
    """DTO for user response."""
    
    id: int
    username: str
    email: str
    color: str
    profile_picture: Optional[str] = Field(None, alias="profilePicture")
    initials: Optional[str] = None
    timezone: Optional[str] = None
    date_joined: Optional[str] = Field(None, alias="dateJoined")
    date_created: Optional[str] = Field(None, alias="dateCreated")
    role: Optional[int] = None
    last_active: Optional[str] = Field(None, alias="lastActive")
    type: Optional[str] = None
