"""
DTOs for ClickUp API requests and responses.

This module exports all DTO classes for interacting with the ClickUp API.
"""

from .folder import FolderCreate, FolderResp, FolderUpdate
from .list import ListCreate, ListResp, ListUpdate
from .space import SpaceCreate, SpaceResp, SpaceUpdate, SpaceFeatures
from .task import TaskCreate, TaskListQuery, TaskResp, TaskUpdate
from .custom_fields import CustomField

__all__ = [
    "SpaceCreate",
    "SpaceResp",
    "SpaceUpdate",
    "FolderCreate",
    "FolderResp",
    "FolderUpdate",
    "ListCreate",
    "ListResp",
    "ListUpdate",
    "TaskCreate",
    "TaskResp",
    "TaskUpdate",
    "TaskListQuery",
    "SpaceFeatures",
    "CustomField",
]
