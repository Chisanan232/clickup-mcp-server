"""
DTOs for ClickUp API requests and responses.

This module exports all DTO classes for interacting with the ClickUp API.
"""

from .analytics import (
    ListAnalyticsQuery,
    ListAnalyticsResponse,
    SpaceAnalyticsQuery,
    SpaceAnalyticsResponse,
    TaskAnalyticsQuery,
    TaskAnalyticsResponse,
    TeamAnalyticsQuery,
    TeamAnalyticsResponse,
)
from .bottleneck import BottleneckDetectionQuery, BottleneckDetectionResponse
from .custom_fields import CustomField
from .folder import FolderCreate, FolderResp, FolderUpdate
from .insights import InsightsGenerationQuery, InsightsGenerationResponse
from .list import ListCreate, ListResp, ListUpdate
from .space import SpaceCreate, SpaceFeatures, SpaceResp, SpaceUpdate
from .task import TaskCreate, TaskListQuery, TaskResp, TaskUpdate

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
    # Analytics DTOs
    "TaskAnalyticsQuery",
    "TaskAnalyticsResponse",
    "TeamAnalyticsQuery",
    "TeamAnalyticsResponse",
    "ListAnalyticsQuery",
    "ListAnalyticsResponse",
    "SpaceAnalyticsQuery",
    "SpaceAnalyticsResponse",
    # Bottleneck detection DTOs
    "BottleneckDetectionQuery",
    "BottleneckDetectionResponse",
    # Insights generation DTOs
    "InsightsGenerationQuery",
    "InsightsGenerationResponse",
]
