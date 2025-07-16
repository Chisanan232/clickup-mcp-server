"""
Data Transfer Objects (DTOs) for ClickUp API.

This module defines the structure of requests and responses for the ClickUp API.
DTOs are separate from domain models to provide a clear boundary between the API layer
and the application's domain logic.
"""

from .base import BaseRequestDTO, BaseResponseDTO
from .team import TeamResponseDTO, TeamsResponseDTO
from .space import (
    SpaceRequestDTO, 
    SpaceResponseDTO, 
    SpacesResponseDTO,
    CreateSpaceRequestDTO,
    UpdateSpaceRequestDTO
)
from .folder import (
    FolderRequestDTO, 
    FolderResponseDTO, 
    FoldersResponseDTO,
    CreateFolderRequestDTO,
    UpdateFolderRequestDTO
)
from .list import (
    ListRequestDTO, 
    ListResponseDTO, 
    ListsResponseDTO,
    CreateListRequestDTO,
    UpdateListRequestDTO
)
from .task import (
    TaskRequestDTO, 
    TaskResponseDTO, 
    TasksResponseDTO,
    CreateTaskRequestDTO,
    UpdateTaskRequestDTO,
    TaskCommentResponseDTO,
    TaskCommentsResponseDTO,
    CreateTaskCommentRequestDTO,
    UpdateTaskCommentRequestDTO
)
from .user import UserResponseDTO, TeamUsersResponseDTO

__all__ = [
    'BaseRequestDTO', 'BaseResponseDTO',
    'TeamResponseDTO', 'TeamsResponseDTO',
    'SpaceRequestDTO', 'SpaceResponseDTO', 'SpacesResponseDTO',
    'CreateSpaceRequestDTO', 'UpdateSpaceRequestDTO',
    'FolderRequestDTO', 'FolderResponseDTO', 'FoldersResponseDTO',
    'CreateFolderRequestDTO', 'UpdateFolderRequestDTO',
    'ListRequestDTO', 'ListResponseDTO', 'ListsResponseDTO',
    'CreateListRequestDTO', 'UpdateListRequestDTO',
    'TaskRequestDTO', 'TaskResponseDTO', 'TasksResponseDTO',
    'CreateTaskRequestDTO', 'UpdateTaskRequestDTO',
    'TaskCommentResponseDTO', 'TaskCommentsResponseDTO',
    'CreateTaskCommentRequestDTO', 'UpdateTaskCommentRequestDTO',
    'UserResponseDTO', 'TeamUsersResponseDTO',
]
