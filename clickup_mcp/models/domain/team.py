"""
Team domain models.

This module provides domain models for ClickUp Teams/Workspaces.
"""
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator, model_validator, ConfigDict

from clickup_mcp.models.domain.base import BaseDomainModel


class ClickUpUser(BaseDomainModel):
    """User within a team."""
    
    user_id: Optional[int] = Field(None, alias="id")
    username: Optional[str] = None
    email: Optional[str] = None
    color: Optional[str] = None
    profile_picture: Optional[str] = Field(None, alias="profilePicture")
    initials: Optional[str] = None
    
    # Fields with aliases for backward compatibility
    id: Optional[int] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )

    @property
    def id_value(self) -> Optional[int]:
        """Return user_id for backward compatibility."""
        return self.user_id
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Include 'id' in serialization for backward compatibility."""
        result = super().model_dump(**kwargs)
        if self.user_id is not None and 'id' not in result:
            result['id'] = self.user_id
        return result


class ClickUpTeamMember(BaseDomainModel):
    """Team member with associated user information."""
    
    user: Optional[ClickUpUser] = None


class ClickUpTeam(BaseDomainModel):
    """
    ClickUp Team/Workspace domain model.
    
    This model represents a team/workspace in ClickUp.
    """
    
    team_id: Optional[str] = Field(None, alias="id")
    name: Optional[str] = None
    color: Optional[str] = None
    avatar: Optional[str] = None
    members: Optional[List[ClickUpTeamMember]] = None
    
    # Fields with aliases for backward compatibility
    id: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )

    @property
    def id_value(self) -> Optional[str]:
        """Return team_id for backward compatibility."""
        return self.team_id
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Include 'id' in serialization for backward compatibility."""
        result = super().model_dump(**kwargs)
        if self.team_id is not None and 'id' not in result:
            result['id'] = self.team_id
        return result


# Backward compatibility alias
Team = ClickUpTeam
