"""
Utility functions and helpers for ClickUp API operations.

This module provides common utility functions for working with ClickUp API data,
including data transformation, validation, and helper functions.
"""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union


def validate_clickup_id(clickup_id: str, id_type: str = "ID") -> str:
    """
    Validate a ClickUp ID format.

    Args:
        clickup_id: The ID to validate
        id_type: Type of ID for error messages (e.g., "task", "list", "space")

    Returns:
        The validated ID

    Raises:
        ValueError: If the ID format is invalid
    """
    if not clickup_id or not isinstance(clickup_id, str):
        raise ValueError(f"{id_type} ID must be a non-empty string")

    # ClickUp IDs are typically alphanumeric and can contain hyphens
    if not re.match(r"^[a-zA-Z0-9\-_]+$", clickup_id):
        raise ValueError(f"Invalid {id_type} ID format: {clickup_id}")

    return clickup_id


def format_clickup_date(timestamp: int | float | str | datetime | None) -> Optional[int]:
    """
    Convert various date formats to ClickUp timestamp (milliseconds since epoch).

    Args:
        timestamp: Date in various formats (Unix timestamp, ISO string, datetime object)

    Returns:
        Timestamp in milliseconds since epoch, or None if input is None

    Raises:
        ValueError: If the timestamp format is invalid
    """
    if timestamp is None:
        return None

    if isinstance(timestamp, datetime):
        # Convert datetime to milliseconds since epoch
        return int(timestamp.timestamp() * 1000)

    if isinstance(timestamp, (int, float)):
        # Assume it's already a timestamp
        # If it's in seconds, convert to milliseconds
        if timestamp < 10000000000:  # Less than year 2286 in seconds
            return int(timestamp * 1000)
        return int(timestamp)

    if isinstance(timestamp, str):
        try:
            # Try to parse as ISO format
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return int(dt.timestamp() * 1000)
        except ValueError:
            try:
                # Try to parse as Unix timestamp
                ts = float(timestamp)
                return format_clickup_date(ts)
            except ValueError:
                raise ValueError(f"Invalid timestamp format: {timestamp}")

    raise ValueError(f"Unsupported timestamp type: {type(timestamp)}")


def parse_clickup_date(timestamp: int | str | None) -> Optional[datetime]:
    """
    Parse a ClickUp timestamp to a datetime object.

    Args:
        timestamp: ClickUp timestamp (milliseconds since epoch) or string

    Returns:
        datetime object in UTC, or None if input is None

    Raises:
        ValueError: If the timestamp is invalid
    """
    if timestamp is None:
        return None

    if isinstance(timestamp, str):
        try:
            timestamp = int(timestamp)
        except ValueError:
            raise ValueError(f"Invalid timestamp string: {timestamp}")

    if not isinstance(timestamp, int):
        raise ValueError(f"Timestamp must be an integer, got {type(timestamp)}")

    # Check for valid timestamp range
    if timestamp < 0:
        raise ValueError(f"Invalid timestamp value: {timestamp}")

    try:
        # Convert from milliseconds to seconds
        return datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
    except (ValueError, OSError) as e:
        raise ValueError(f"Invalid timestamp value: {timestamp}") from e


def build_query_params(params: Dict[str, Any]) -> Dict[str, str | List[str]]:
    """
    Build query parameters for API requests, handling lists and special values.

    Args:
        params: Dictionary of parameters

    Returns:
        Dictionary with string keys and values suitable for HTTP requests
    """
    query_params: Dict[str, str | List[str]] = {}

    for key, value in params.items():
        if value is None:
            continue

        if isinstance(value, list):
            # Handle list parameters (ClickUp often uses array notation)
            if value:  # Only add if list is not empty
                if key.endswith("[]"):
                    query_params[key] = value
                else:
                    query_params[f"{key}[]"] = value
        elif isinstance(value, bool):
            # Convert boolean to lowercase string
            query_params[key] = str(value).lower()
        else:
            # Convert everything else to string
            query_params[key] = str(value)

    return query_params


def sanitize_task_name(name: str, max_length: int = 255) -> str:
    """
    Sanitize a task name for ClickUp API.

    Args:
        name: The task name to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized task name

    Raises:
        ValueError: If name is empty after sanitization
    """
    if not name or not isinstance(name, str):
        raise ValueError("Task name must be a non-empty string")

    # Remove leading/trailing whitespace and normalize internal whitespace
    sanitized = re.sub(r"\s+", " ", name.strip())

    if not sanitized:
        raise ValueError("Task name cannot be empty after sanitization")

    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip()

    return sanitized


def extract_clickup_ids_from_url(url: str) -> Dict[str, Optional[str]]:
    """
    Extract ClickUp IDs from a ClickUp URL.

    Args:
        url: ClickUp URL

    Returns:
        Dictionary containing extracted IDs (team_id, space_id, folder_id, list_id, task_id)
    """
    ids: Dict[str, Optional[str]] = {
        "team_id": None,
        "space_id": None,
        "folder_id": None,
        "list_id": None,
        "task_id": None,
    }

    # Common ClickUp URL patterns - updated patterns to handle various URL formats
    patterns = {
        "team_id": r"(?:app\.clickup\.com|clickup\.com)(?::\d+)?/(?:team/)?([a-zA-Z0-9\-_]+)(?:/|$)",
        "space_id": r"/space/([a-zA-Z0-9\-_]+)",
        "folder_id": r"/folder/([a-zA-Z0-9\-_]+)",
        "list_id": r"(?:/list/|/v/li/)([a-zA-Z0-9\-_]+)",
        "task_id": r"/[tT]/([a-zA-Z0-9\-_]+)",
    }

    for id_type, pattern in patterns.items():
        match = re.search(pattern, url)
        if match:
            ids[id_type] = match.group(1)

    return ids


def format_priority(priority: int | str | None) -> Optional[int]:
    """
    Format priority value for ClickUp API.

    ClickUp priority values:
    - 1: Urgent
    - 2: High
    - 3: Normal
    - 4: Low

    Args:
        priority: Priority value (int, string name, or None)

    Returns:
        Formatted priority integer or None

    Raises:
        ValueError: If priority value is invalid
    """
    if priority is None:
        return None

    if isinstance(priority, int):
        if priority not in [1, 2, 3, 4]:
            raise ValueError("Priority must be 1 (Urgent), 2 (High), 3 (Normal), or 4 (Low)")
        return priority

    if isinstance(priority, str):
        priority_map = {"urgent": 1, "high": 2, "normal": 3, "low": 4}

        normalized = priority.lower().strip()
        if normalized in priority_map:
            return priority_map[normalized]

        # Try to parse as integer string
        try:
            return format_priority(int(priority))
        except ValueError:
            pass

    raise ValueError(f"Invalid priority value: {priority}")


def format_status(status: str) -> str:
    """
    Format status value for ClickUp API.

    Args:
        status: Status string

    Returns:
        Formatted status string

    Raises:
        ValueError: If status is invalid
    """
    if not status or not isinstance(status, str):
        raise ValueError("Status must be a non-empty string")

    # ClickUp statuses are typically lowercase
    return status.strip().lower()


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.

    Args:
        items: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks

    Raises:
        ValueError: If chunk_size is not positive
    """
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")

    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


def safe_get(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    Safely get nested dictionary values.

    Args:
        data: Dictionary to search in
        *keys: Keys to traverse (nested)
        default: Default value if key path doesn't exist

    Returns:
        Value at the key path or default
    """
    current = data

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default

    return current


def filter_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove keys with None values from a dictionary.

    Args:
        data: Dictionary to filter

    Returns:
        Dictionary with None values removed
    """
    return {k: v for k, v in data.items() if v is not None}


class ClickUpURLBuilder:
    """Utility class for building ClickUp URLs."""

    BASE_URL = "https://app.clickup.com"

    @classmethod
    def build_task_url(cls, task_id: str, team_id: Optional[str] = None) -> str:
        """Build a URL for a ClickUp task."""
        if team_id:
            return f"{cls.BASE_URL}/{team_id}/t/{task_id}"
        return f"{cls.BASE_URL}/t/{task_id}"

    @classmethod
    def build_list_url(cls, list_id: str, team_id: Optional[str] = None) -> str:
        """Build a URL for a ClickUp list."""
        if team_id:
            return f"{cls.BASE_URL}/{team_id}/v/li/{list_id}"
        return f"{cls.BASE_URL}/v/li/{list_id}"

    @classmethod
    def build_space_url(cls, space_id: str, team_id: Optional[str] = None) -> str:
        """Build a URL for a ClickUp space."""
        if team_id:
            return f"{cls.BASE_URL}/{team_id}/v/s/{space_id}"
        return f"{cls.BASE_URL}/v/s/{space_id}"

    @classmethod
    def build_folder_url(cls, folder_id: str, team_id: Optional[str] = None) -> str:
        """Build a URL for a ClickUp folder."""
        if team_id:
            return f"{cls.BASE_URL}/{team_id}/v/f/{folder_id}"
        return f"{cls.BASE_URL}/v/f/{folder_id}"
