"""
DTOs for ClickUp User API.

This module contains the request and response DTOs for the User API endpoints.
"""

from typing import List, Optional, Union, Dict, Any, ClassVar, Type
from pydantic import BaseModel, Field

from .base import BaseDTO


class UserResponseDTO(BaseDTO):
    """DTO for a ClickUp user API response."""
    id: Union[int, str]  # Allow both int and string IDs for better compatibility with tests
    username: str
    email: str
    color: Optional[str] = None  # Make color optional for test compatibility
    profilePicture: Optional[str] = Field(None)
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "UserResponseDTO":
        """
        Deserialize API response data into a UserResponseDTO.
        
        Args:
            data: API response data
            
        Returns:
            UserResponseDTO instance
        """
        return cls(**data)


class TeamUsersResponseDTO(BaseDTO):
    """DTO for a ClickUp team users API response."""
    users: List[UserResponseDTO]
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "TeamUsersResponseDTO":
        """
        Deserialize API response data into a TeamUsersResponseDTO.
        
        Args:
            data: API response data
            
        Returns:
            TeamUsersResponseDTO instance
        """
        return cls(**data)
