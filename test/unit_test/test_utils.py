"""
Unit tests for ClickUp utilities.
"""

from datetime import datetime, timezone
import pytest

from clickup_mcp.utils import (
    validate_clickup_id,
    format_clickup_date,
    parse_clickup_date,
    build_query_params,
    sanitize_task_name,
    extract_clickup_ids_from_url,
    format_priority,
    format_status,
    chunk_list,
    safe_get,
    filter_none_values,
    ClickUpURLBuilder
)
from clickup_mcp.exceptions import ValidationError


class TestValidateClickUpId:
    """Test cases for validate_clickup_id function."""
    
    def test_valid_ids(self):
        """Test valid ClickUp IDs."""
        valid_ids = [
            "123456789",
            "abc123def456",
            "task-123",
            "list_456",
            "ABC123DEF456",
            "9876543210abcdef"
        ]
        
        for valid_id in valid_ids:
            result = validate_clickup_id(valid_id)
            assert result == valid_id
    
    def test_invalid_ids(self):
        """Test invalid ClickUp IDs."""
        invalid_ids = [
            "",
            None,
            "id with spaces",
            "id@with#symbols",
            "id/with/slashes",
            "id.with.dots"
        ]
        
        for invalid_id in invalid_ids:
            with pytest.raises(ValueError):
                validate_clickup_id(invalid_id)
    
    def test_custom_id_type(self):
        """Test validation with custom ID type for error messages."""
        with pytest.raises(ValueError) as exc_info:
            validate_clickup_id("", "task")
        
        assert "task ID" in str(exc_info.value)


class TestFormatClickUpDate:
    """Test cases for format_clickup_date function."""
    
    def test_none_input(self):
        """Test None input returns None."""
        assert format_clickup_date(None) is None
    
    def test_datetime_input(self):
        """Test datetime input."""
        dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = format_clickup_date(dt)
        expected = int(dt.timestamp() * 1000)
        assert result == expected
    
    def test_unix_timestamp_seconds(self):
        """Test Unix timestamp in seconds."""
        timestamp_seconds = 1672574400  # 2023-01-01 12:00:00 UTC
        result = format_clickup_date(timestamp_seconds)
        assert result == timestamp_seconds * 1000
    
    def test_unix_timestamp_milliseconds(self):
        """Test Unix timestamp in milliseconds."""
        timestamp_ms = 1672574400000  # 2023-01-01 12:00:00 UTC
        result = format_clickup_date(timestamp_ms)
        assert result == timestamp_ms
    
    def test_iso_string_input(self):
        """Test ISO format string input."""
        iso_string = "2023-01-01T12:00:00Z"
        result = format_clickup_date(iso_string)
        assert isinstance(result, int)
        assert result > 0
    
    def test_iso_string_with_timezone(self):
        """Test ISO format string with timezone."""
        iso_string = "2023-01-01T12:00:00+00:00"
        result = format_clickup_date(iso_string)
        assert isinstance(result, int)
        assert result > 0
    
    def test_invalid_string(self):
        """Test invalid string input."""
        with pytest.raises(ValueError):
            format_clickup_date("invalid date string")
    
    def test_invalid_type(self):
        """Test invalid input type."""
        with pytest.raises(ValueError):
            format_clickup_date([1, 2, 3])


class TestParseClickUpDate:
    """Test cases for parse_clickup_date function."""
    
    def test_none_input(self):
        """Test None input returns None."""
        assert parse_clickup_date(None) is None
    
    def test_milliseconds_timestamp(self):
        """Test parsing milliseconds timestamp."""
        timestamp_ms = 1672574400000  # 2023-01-01 12:00:00 UTC
        result = parse_clickup_date(timestamp_ms)
        
        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc
        assert result.year == 2023
        assert result.month == 1
        assert result.day == 1
    
    def test_string_timestamp(self):
        """Test parsing string timestamp."""
        timestamp_str = "1672574400000"
        result = parse_clickup_date(timestamp_str)
        
        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc
    
    def test_invalid_string(self):
        """Test invalid string timestamp."""
        with pytest.raises(ValueError):
            parse_clickup_date("not a number")
    
    def test_invalid_timestamp_value(self):
        """Test invalid timestamp value."""
        with pytest.raises(ValueError):
            parse_clickup_date(-1)


class TestBuildQueryParams:
    """Test cases for build_query_params function."""
    
    def test_basic_params(self):
        """Test basic parameter conversion."""
        params = {
            "page": 1,
            "limit": 50,
            "archived": False
        }
        
        result = build_query_params(params)
        expected = {
            "page": "1",
            "limit": "50",
            "archived": "false"
        }
        
        assert result == expected
    
    def test_list_params(self):
        """Test list parameter handling."""
        params = {
            "statuses": ["open", "in progress"],
            "assignees[]": ["user1", "user2"],
            "tags": []
        }
        
        result = build_query_params(params)
        expected = {
            "statuses[]": ["open", "in progress"],
            "assignees[]": ["user1", "user2"]
        }
        
        assert result == expected
    
    def test_none_values(self):
        """Test None values are filtered out."""
        params = {
            "page": 1,
            "limit": None,
            "archived": False
        }
        
        result = build_query_params(params)
        expected = {
            "page": "1",
            "archived": "false"
        }
        
        assert result == expected
    
    def test_boolean_conversion(self):
        """Test boolean to string conversion."""
        params = {
            "include_closed": True,
            "subtasks": False
        }
        
        result = build_query_params(params)
        expected = {
            "include_closed": "true",
            "subtasks": "false"
        }
        
        assert result == expected


class TestSanitizeTaskName:
    """Test cases for sanitize_task_name function."""
    
    def test_normal_name(self):
        """Test normal task name."""
        name = "Normal Task Name"
        result = sanitize_task_name(name)
        assert result == "Normal Task Name"
    
    def test_whitespace_normalization(self):
        """Test whitespace normalization."""
        name = "  Task   with    extra   spaces  "
        result = sanitize_task_name(name)
        assert result == "Task with extra spaces"
    
    def test_max_length_truncation(self):
        """Test maximum length truncation."""
        long_name = "A" * 300
        result = sanitize_task_name(long_name, max_length=100)
        assert len(result) == 100
        assert result == "A" * 100
    
    def test_empty_name(self):
        """Test empty name raises error."""
        with pytest.raises(ValueError):
            sanitize_task_name("")
    
    def test_whitespace_only_name(self):
        """Test whitespace-only name raises error."""
        with pytest.raises(ValueError):
            sanitize_task_name("   ")
    
    def test_none_input(self):
        """Test None input raises error."""
        with pytest.raises(ValueError):
            sanitize_task_name(None)


class TestExtractClickUpIdsFromUrl:
    """Test cases for extract_clickup_ids_from_url function."""
    
    def test_task_url(self):
        """Test extracting IDs from task URL."""
        url = "https://app.clickup.com/123456/t/abc123def"
        result = extract_clickup_ids_from_url(url)
        
        expected = {
            'team_id': '123456',
            'space_id': None,
            'folder_id': None,
            'list_id': None,
            'task_id': 'abc123def'
        }
        
        assert result == expected
    
    def test_list_url(self):
        """Test extracting IDs from list URL."""
        url = "https://app.clickup.com/team/123456/space/789/list/456def"
        result = extract_clickup_ids_from_url(url)
        
        assert result['team_id'] == '123456'
        assert result['space_id'] == '789'
        assert result['list_id'] == '456def'
    
    def test_space_url(self):
        """Test extracting IDs from space URL."""
        url = "https://app.clickup.com/team/123456/space/789abc"
        result = extract_clickup_ids_from_url(url)
        
        assert result['team_id'] == '123456'
        assert result['space_id'] == '789abc'
        assert result['list_id'] is None
    
    def test_no_matches(self):
        """Test URL with no matching IDs."""
        url = "https://example.com/some/other/path"
        result = extract_clickup_ids_from_url(url)
        
        expected = {
            'team_id': None,
            'space_id': None,
            'folder_id': None,
            'list_id': None,
            'task_id': None
        }
        
        assert result == expected


class TestFormatPriority:
    """Test cases for format_priority function."""
    
    def test_none_input(self):
        """Test None input returns None."""
        assert format_priority(None) is None
    
    def test_valid_integers(self):
        """Test valid priority integers."""
        for priority in [1, 2, 3, 4]:
            result = format_priority(priority)
            assert result == priority
    
    def test_invalid_integers(self):
        """Test invalid priority integers."""
        for priority in [0, 5, -1, 10]:
            with pytest.raises(ValueError):
                format_priority(priority)
    
    def test_valid_strings(self):
        """Test valid priority strings."""
        string_map = {
            "urgent": 1,
            "high": 2,
            "normal": 3,
            "low": 4,
            "URGENT": 1,
            "High": 2,
            " normal ": 3
        }
        
        for string_priority, expected in string_map.items():
            result = format_priority(string_priority)
            assert result == expected
    
    def test_string_integers(self):
        """Test string representations of integers."""
        for priority_str, expected in [("1", 1), ("2", 2), ("3", 3), ("4", 4)]:
            result = format_priority(priority_str)
            assert result == expected
    
    def test_invalid_strings(self):
        """Test invalid priority strings."""
        invalid_strings = ["medium", "critical", "5", "invalid"]
        
        for invalid_string in invalid_strings:
            with pytest.raises(ValueError):
                format_priority(invalid_string)


class TestFormatStatus:
    """Test cases for format_status function."""
    
    def test_normal_status(self):
        """Test normal status formatting."""
        status = "In Progress"
        result = format_status(status)
        assert result == "in progress"
    
    def test_whitespace_handling(self):
        """Test whitespace handling."""
        status = "  OPEN  "
        result = format_status(status)
        assert result == "open"
    
    def test_empty_status(self):
        """Test empty status raises error."""
        with pytest.raises(ValueError):
            format_status("")
    
    def test_none_status(self):
        """Test None status raises error."""
        with pytest.raises(ValueError):
            format_status(None)


class TestChunkList:
    """Test cases for chunk_list function."""
    
    def test_even_chunks(self):
        """Test list that divides evenly into chunks."""
        items = list(range(10))
        chunks = chunk_list(items, 2)
        
        expected = [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]
        assert chunks == expected
    
    def test_uneven_chunks(self):
        """Test list that doesn't divide evenly."""
        items = list(range(10))
        chunks = chunk_list(items, 3)
        
        expected = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
        assert chunks == expected
    
    def test_chunk_size_larger_than_list(self):
        """Test chunk size larger than list."""
        items = [1, 2, 3]
        chunks = chunk_list(items, 5)
        
        expected = [[1, 2, 3]]
        assert chunks == expected
    
    def test_empty_list(self):
        """Test empty list."""
        chunks = chunk_list([], 3)
        assert chunks == []
    
    def test_invalid_chunk_size(self):
        """Test invalid chunk size."""
        with pytest.raises(ValueError):
            chunk_list([1, 2, 3], 0)
        
        with pytest.raises(ValueError):
            chunk_list([1, 2, 3], -1)


class TestSafeGet:
    """Test cases for safe_get function."""
    
    def test_existing_nested_keys(self):
        """Test getting existing nested keys."""
        data = {
            "user": {
                "profile": {
                    "name": "John Doe"
                }
            }
        }
        
        result = safe_get(data, "user", "profile", "name")
        assert result == "John Doe"
    
    def test_missing_key(self):
        """Test missing key returns default."""
        data = {"user": {"profile": {}}}
        
        result = safe_get(data, "user", "profile", "name", default="Unknown")
        assert result == "Unknown"
    
    def test_missing_intermediate_key(self):
        """Test missing intermediate key returns default."""
        data = {"user": {}}
        
        result = safe_get(data, "user", "profile", "name", default="Unknown")
        assert result == "Unknown"
    
    def test_non_dict_intermediate(self):
        """Test non-dict intermediate value returns default."""
        data = {"user": "not a dict"}
        
        result = safe_get(data, "user", "profile", "name", default="Unknown")
        assert result == "Unknown"
    
    def test_single_key(self):
        """Test single key access."""
        data = {"name": "John"}
        
        result = safe_get(data, "name")
        assert result == "John"
    
    def test_default_none(self):
        """Test default None value."""
        data = {}
        
        result = safe_get(data, "missing_key")
        assert result is None


class TestFilterNoneValues:
    """Test cases for filter_none_values function."""
    
    def test_mixed_values(self):
        """Test filtering mixed values."""
        data = {
            "name": "John",
            "age": None,
            "email": "john@example.com",
            "phone": None,
            "active": True
        }
        
        result = filter_none_values(data)
        expected = {
            "name": "John",
            "email": "john@example.com",
            "active": True
        }
        
        assert result == expected
    
    def test_all_none(self):
        """Test all None values."""
        data = {"a": None, "b": None, "c": None}
        result = filter_none_values(data)
        assert result == {}
    
    def test_no_none(self):
        """Test no None values."""
        data = {"a": 1, "b": "text", "c": True}
        result = filter_none_values(data)
        assert result == data
    
    def test_empty_dict(self):
        """Test empty dictionary."""
        result = filter_none_values({})
        assert result == {}


class TestClickUpURLBuilder:
    """Test cases for ClickUpURLBuilder class."""
    
    def test_build_task_url_with_team(self):
        """Test building task URL with team ID."""
        url = ClickUpURLBuilder.build_task_url("task123", team_id="team456")
        expected = "https://app.clickup.com/team456/t/task123"
        assert url == expected
    
    def test_build_task_url_without_team(self):
        """Test building task URL without team ID."""
        url = ClickUpURLBuilder.build_task_url("task123")
        expected = "https://app.clickup.com/t/task123"
        assert url == expected
    
    def test_build_list_url_with_team(self):
        """Test building list URL with team ID."""
        url = ClickUpURLBuilder.build_list_url("list123", team_id="team456")
        expected = "https://app.clickup.com/team456/v/li/list123"
        assert url == expected
    
    def test_build_list_url_without_team(self):
        """Test building list URL without team ID."""
        url = ClickUpURLBuilder.build_list_url("list123")
        expected = "https://app.clickup.com/v/li/list123"
        assert url == expected
    
    def test_build_space_url_with_team(self):
        """Test building space URL with team ID."""
        url = ClickUpURLBuilder.build_space_url("space123", team_id="team456")
        expected = "https://app.clickup.com/team456/v/s/space123"
        assert url == expected
    
    def test_build_folder_url_with_team(self):
        """Test building folder URL with team ID."""
        url = ClickUpURLBuilder.build_folder_url("folder123", team_id="team456")
        expected = "https://app.clickup.com/team456/v/f/folder123"
        assert url == expected
