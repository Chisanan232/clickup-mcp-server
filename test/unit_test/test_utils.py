"""
Unit tests for ClickUp utilities.
"""

from datetime import datetime, timezone

import pytest

from clickup_mcp.utils import (
    ClickUpURLBuilder,
    build_query_params,
    chunk_list,
    extract_clickup_ids_from_url,
    filter_none_values,
    format_clickup_date,
    format_priority,
    format_status,
    parse_clickup_date,
    safe_get,
    sanitize_task_name,
    validate_clickup_id,
)


class TestValidateClickUpId:
    """Test cases for validate_clickup_id function."""

    def test_valid_ids(self):
        """Test valid ClickUp IDs."""
        valid_ids = ["123456789", "abc123def456", "task-123", "list_456", "ABC123DEF456", "9876543210abcdef"]

        for valid_id in valid_ids:
            result = validate_clickup_id(valid_id)
            assert result == valid_id

    def test_invalid_ids(self):
        """Test invalid ClickUp IDs."""
        invalid_ids = ["", None, "id with spaces", "id@with#symbols", "id/with/slashes", "id.with.dots"]

        for invalid_id in invalid_ids:
            with pytest.raises(ValueError):
                validate_clickup_id(invalid_id)

    def test_custom_id_type(self):
        """Test validation with custom ID type for error messages."""
        with pytest.raises(ValueError) as exc_info:
            validate_clickup_id("", "task")

        assert "task ID" in str(exc_info.value)


class TestValidateClickUpIdAdvanced:
    """Advanced test cases for validate_clickup_id function."""

    def test_minimum_length_ids(self):
        """Test minimum length valid IDs."""
        assert validate_clickup_id("1") == "1"
        assert validate_clickup_id("a") == "a"
        assert validate_clickup_id("A") == "A"

    def test_maximum_length_ids(self):
        """Test very long valid IDs."""
        long_id = "a" * 1000  # Very long ID
        assert validate_clickup_id(long_id) == long_id

    def test_mixed_case_ids(self):
        """Test mixed case IDs."""
        mixed_case_ids = ["AbC123", "XyZ789", "mIxEd_CaSe-123"]
        for mixed_id in mixed_case_ids:
            assert validate_clickup_id(mixed_id) == mixed_id

    def test_numeric_only_ids(self):
        """Test purely numeric IDs."""
        numeric_ids = ["123", "000", "999999999"]
        for numeric_id in numeric_ids:
            assert validate_clickup_id(numeric_id) == numeric_id

    def test_alphabetic_only_ids(self):
        """Test purely alphabetic IDs."""
        alpha_ids = ["abc", "XYZ", "AbCdEfGh"]
        for alpha_id in alpha_ids:
            assert validate_clickup_id(alpha_id) == alpha_id

    def test_special_characters_in_ids(self):
        """Test IDs with allowed special characters."""
        special_ids = ["id-with-dashes", "id_with_underscores", "id-123_456"]
        for special_id in special_ids:
            assert validate_clickup_id(special_id) == special_id

    def test_non_string_types(self):
        """Test various non-string types."""
        invalid_types = [123, [], {}, None, True, False, 0.5]
        for invalid_type in invalid_types:
            with pytest.raises(ValueError, match="ID must be a non-empty string"):
                validate_clickup_id(invalid_type)

    def test_empty_string_variations(self):
        """Test various empty string variations."""
        empty_variations = ["", "   ", "\t", "\n", "\r\n"]
        for empty_str in empty_variations:
            with pytest.raises(ValueError):
                validate_clickup_id(empty_str)

    def test_invalid_characters_comprehensive(self):
        """Test comprehensive list of invalid characters."""
        invalid_chars = [
            "@",
            "#",
            "$",
            "%",
            "^",
            "&",
            "*",
            "(",
            ")",
            "+",
            "=",
            "[",
            "]",
            "{",
            "}",
            "|",
            "\\",
            ":",
            ";",
            '"',
            "'",
            "<",
            ">",
            ",",
            ".",
            "?",
            "/",
            "~",
            "`",
        ]

        for char in invalid_chars:
            with pytest.raises(ValueError, match="Invalid.*ID format"):
                validate_clickup_id(f"id{char}test")

    def test_custom_id_types_comprehensive(self):
        """Test various custom ID types for error messages."""
        id_types = ["task", "list", "space", "folder", "team", "user", "project"]
        for id_type in id_types:
            with pytest.raises(ValueError) as exc_info:
                validate_clickup_id("", id_type)
            assert f"{id_type} ID" in str(exc_info.value)

    def test_unicode_characters(self):
        """Test unicode and international characters."""
        unicode_ids = ["café123", "测试123", "🚀rocket", "naïve-id"]
        for unicode_id in unicode_ids:
            with pytest.raises(ValueError):
                validate_clickup_id(unicode_id)


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


class TestParseClickUpDateAdvanced:
    """Advanced test cases for parse_clickup_date function."""

    def test_epoch_timestamp(self):
        """Test Unix epoch timestamp."""
        epoch_ms = 0
        result = parse_clickup_date(epoch_ms)
        expected = datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        assert result == expected

    def test_specific_dates(self):
        """Test specific known dates."""
        # New Year 2023
        new_year_ms = 1672531200000  # 2023-01-01 00:00:00 UTC
        result = parse_clickup_date(new_year_ms)
        expected = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        assert result == expected

    def test_string_timestamp_parsing(self):
        """Test string timestamp parsing."""
        timestamp_str = "1672574400000"
        result = parse_clickup_date(timestamp_str)
        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc

    def test_large_timestamp_values(self):
        """Test very large timestamp values."""
        # Year 2100
        future_ms = 4102444800000
        result = parse_clickup_date(future_ms)
        assert result.year == 2100

    def test_float_string_timestamps(self):
        """Test string timestamps with decimal points."""
        float_str = "1672574400000.0"
        with pytest.raises(ValueError):
            parse_clickup_date(float_str)

    def test_whitespace_string_timestamps(self):
        """Test string timestamps with whitespace."""
        whitespace_strs = [" 1672574400000 ", "\t1672574400000\t", "\n1672574400000\n"]
        for ws_str in whitespace_strs:
            # Should pass because int() can handle whitespace
            result = parse_clickup_date(ws_str)
            assert isinstance(result, datetime)

    def test_invalid_string_formats(self):
        """Test invalid string timestamp formats."""
        invalid_strs = [
            "not-a-number",
            "1672574400000abc",
            "abc1672574400000",
            "1.672574400000e12",  # Scientific notation
            "1,672,574,400,000",  # Comma-separated
            "",
        ]

        for invalid_str in invalid_strs:
            with pytest.raises(ValueError):
                parse_clickup_date(invalid_str)

    def test_negative_timestamps(self):
        """Test negative timestamps (pre-epoch)."""
        negative_ms = -86400000  # One day before epoch
        with pytest.raises(ValueError):
            parse_clickup_date(negative_ms)

    def test_microsecond_precision(self):
        """Test that microsecond precision is handled correctly."""
        # Millisecond precision timestamp
        ms_timestamp = 1672574400123
        result = parse_clickup_date(ms_timestamp)
        assert result.microsecond == 123000  # 123 ms = 123000 microseconds

    def test_boundary_timestamp_values(self):
        """Test boundary timestamp values."""
        # Test with valid positive timestamps
        min_ts = 0  # Epoch
        result = parse_clickup_date(min_ts)
        assert isinstance(result, datetime)

        # Maximum reasonable timestamp
        max_ts = 2147483647000  # Maximum 32-bit signed int * 1000
        result = parse_clickup_date(max_ts)
        assert isinstance(result, datetime)

        # Test negative values should raise errors
        with pytest.raises(ValueError):
            parse_clickup_date(-1)

    def test_timezone_consistency(self):
        """Test that all parsed dates are in UTC timezone."""
        timestamps = [0, 1672574400000, 4102444800000]

        for ts in timestamps:
            result = parse_clickup_date(ts)
            assert result.tzinfo == timezone.utc

    def test_unsupported_input_types(self):
        """Test unsupported input types."""
        unsupported_types = [[], {}, set(), bytes(b"123"), complex(1, 2)]

        for unsupported_type in unsupported_types:
            with pytest.raises(ValueError, match="Timestamp must be an integer"):
                parse_clickup_date(unsupported_type)

        # Test boolean types separately as they are converted to int
        assert parse_clickup_date(True) is not None  # True -> 1
        assert parse_clickup_date(False) is not None  # False -> 0

    def test_extremely_large_values(self):
        """Test extremely large timestamp values that might cause overflow."""
        # Test with a timestamp that's beyond reasonable datetime range
        huge_timestamp = 10**18  # Extremely large value
        with pytest.raises(ValueError):
            parse_clickup_date(huge_timestamp)


class TestBuildQueryParams:
    """Test cases for build_query_params function."""

    def test_basic_params(self):
        """Test basic parameter conversion."""
        params = {"page": 1, "limit": 50, "archived": False}

        result = build_query_params(params)
        expected = {"page": "1", "limit": "50", "archived": "false"}

        assert result == expected

    def test_list_params(self):
        """Test list parameter handling."""
        params = {"statuses": ["open", "in progress"], "assignees[]": ["user1", "user2"], "tags": []}

        result = build_query_params(params)
        expected = {"statuses[]": ["open", "in progress"], "assignees[]": ["user1", "user2"]}

        assert result == expected

    def test_none_values(self):
        """Test None values are filtered out."""
        params = {"page": 1, "limit": None, "archived": False}

        result = build_query_params(params)
        expected = {"page": "1", "archived": "false"}

        assert result == expected

    def test_boolean_conversion(self):
        """Test boolean to string conversion."""
        params = {"include_closed": True, "subtasks": False}

        result = build_query_params(params)
        expected = {"include_closed": "true", "subtasks": "false"}

        assert result == expected


class TestBuildQueryParamsAdvanced:
    """Advanced test cases for build_query_params function."""

    def test_nested_lists(self):
        """Test nested lists in parameters."""
        params = {
            "tags": ["urgent", "backend", "api"],
            "assignees": ["user1", "user2"],
            "statuses": ["open", "in_progress"],
        }

        result = build_query_params(params)
        expected = {
            "tags[]": ["urgent", "backend", "api"],
            "assignees[]": ["user1", "user2"],
            "statuses[]": ["open", "in_progress"],
        }
        assert result == expected

    def test_list_with_array_notation(self):
        """Test list parameters that already have array notation."""
        params = {"tags[]": ["urgent", "backend"], "assignees[]": ["user1", "user2"]}

        result = build_query_params(params)
        expected = {"tags[]": ["urgent", "backend"], "assignees[]": ["user1", "user2"]}
        assert result == expected

    def test_empty_lists(self):
        """Test empty list parameters."""
        params = {"tags": [], "assignees": [], "name": "test"}

        result = build_query_params(params)
        expected = {"name": "test"}  # Empty lists should be excluded
        assert result == expected

    def test_mixed_data_types(self):
        """Test mixed data types in parameters."""
        params = {
            "name": "Test Task",
            "priority": 1,
            "due_date": 1672574400000,
            "archived": True,
            "private": False,
            "tags": ["urgent", "backend"],
            "assignees": None,
            "time_estimate": 3600.5,
        }

        result = build_query_params(params)
        expected = {
            "name": "Test Task",
            "priority": "1",
            "due_date": "1672574400000",
            "archived": "true",
            "private": "false",
            "tags[]": ["urgent", "backend"],
            "time_estimate": "3600.5",
        }
        assert result == expected

    def test_boolean_conversion_edge_cases(self):
        """Test boolean conversion edge cases."""
        params = {"archived": True, "private": False, "include_closed": True, "show_subtasks": False}

        result = build_query_params(params)
        expected = {"archived": "true", "private": "false", "include_closed": "true", "show_subtasks": "false"}
        assert result == expected

    def test_numeric_edge_cases(self):
        """Test numeric edge cases."""
        params = {
            "zero_int": 0,
            "zero_float": 0.0,
            "negative_int": -1,
            "negative_float": -1.5,
            "large_int": 9999999999,
            "scientific": 1e6,
        }

        result = build_query_params(params)
        expected = {
            "zero_int": "0",
            "zero_float": "0.0",
            "negative_int": "-1",
            "negative_float": "-1.5",
            "large_int": "9999999999",
            "scientific": "1000000.0",
        }
        assert result == expected

    def test_special_string_values(self):
        """Test special string values."""
        params = {
            "empty_string": "",
            "whitespace": "   ",
            "special_chars": "!@#$%^&*()",
            "unicode": "café测试🚀",
            "newlines": "line1\nline2\tline3",
        }

        result = build_query_params(params)
        expected = {
            "empty_string": "",
            "whitespace": "   ",
            "special_chars": "!@#$%^&*()",
            "unicode": "café测试🚀",
            "newlines": "line1\nline2\tline3",
        }
        assert result == expected

    def test_list_with_special_values(self):
        """Test lists containing special values."""
        params = {
            "mixed_list": ["string", 123, True, None, 0, ""],
            "numeric_list": [1, 2, 3, 0, -1],
            "boolean_list": [True, False, True],
            "empty_strings": ["", "   ", "valid"],
        }

        result = build_query_params(params)
        expected = {
            "mixed_list[]": ["string", 123, True, None, 0, ""],
            "numeric_list[]": [1, 2, 3, 0, -1],
            "boolean_list[]": [True, False, True],
            "empty_strings[]": ["", "   ", "valid"],
        }
        assert result == expected

    def test_none_values_comprehensive(self):
        """Test comprehensive None value handling."""
        params = {
            "valid_param": "value",
            "none_param": None,
            "another_valid": 123,
            "another_none": None,
            "list_param": ["a", "b"],
        }

        result = build_query_params(params)
        expected = {"valid_param": "value", "another_valid": "123", "list_param[]": ["a", "b"]}
        assert result == expected

    def test_complex_nested_structure(self):
        """Test complex nested parameter structures."""
        params = {
            "simple": "value",
            "complex_list": [
                {"nested": "not_supported"},  # This would become string representation
                "simple_string",
                123,
                True,
            ],
            "multiple_arrays": ["a", "b", "c"],
            "flags": {"flag1": True, "flag2": False},  # This would become string representation
        }

        result = build_query_params(params)

        # Complex objects should be converted to string representation
        assert "simple" in result
        assert "complex_list[]" in result
        assert "multiple_arrays[]" in result
        assert "flags" in result

    def test_empty_params(self):
        """Test empty parameter dictionary."""
        result = build_query_params({})
        assert result == {}

    def test_all_none_params(self):
        """Test parameter dictionary with all None values."""
        params = {"param1": None, "param2": None, "param3": None}

        result = build_query_params(params)
        assert result == {}

    def test_array_notation_preservation(self):
        """Test that existing array notation is preserved."""
        params = {
            "tags[]": ["tag1", "tag2"],
            "users[]": ["user1"],
            "statuses[]": [],  # Empty array should be excluded
            "regular_param": "value",
        }

        result = build_query_params(params)
        expected = {"tags[]": ["tag1", "tag2"], "users[]": ["user1"], "regular_param": "value"}
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


class TestSanitizeTaskNameAdvanced:
    """Advanced test cases for sanitize_task_name function."""

    def test_unicode_characters(self):
        """Test unicode characters in task names."""
        unicode_names = [
            "测试任务",
            "Tâche française",
            "Tareas en español",
            "Задача на русском",
            "タスク日本語",
            "🚀 Rocket Task 🚀",
            "Task with émojis 😊",
        ]

        for name in unicode_names:
            result = sanitize_task_name(name)
            assert result == name  # Should preserve unicode

    def test_multiple_whitespace_types(self):
        """Test different types of whitespace."""
        whitespace_tests = [
            ("Task\t\twith\ttabs", "Task with tabs"),
            ("Task\n\nwith\nnewlines", "Task with newlines"),
            ("Task\r\nwith\r\ncarriage", "Task with carriage"),
            ("Task   with   spaces", "Task with spaces"),
            ("Task\u00a0with\u00a0nbsp", "Task with nbsp"),  # Non-breaking space
            ("Task\u2003with\u2003em", "Task with em"),  # Em space
        ]

        for input_name, expected in whitespace_tests:
            result = sanitize_task_name(input_name)
            assert result == expected

    def test_leading_trailing_whitespace_variations(self):
        """Test various leading and trailing whitespace scenarios."""
        whitespace_variations = [
            ("  Task Name  ", "Task Name"),
            ("\t\tTask Name\t\t", "Task Name"),
            ("\n\nTask Name\n\n", "Task Name"),
            ("   \t\n Task Name \n\t   ", "Task Name"),
            ("Task Name\t\t", "Task Name"),
            ("  \t  Task Name", "Task Name"),
        ]

        for input_name, expected in whitespace_variations:
            result = sanitize_task_name(input_name)
            assert result == expected

    def test_max_length_edge_cases(self):
        """Test maximum length edge cases."""
        # Test exact max length
        exact_max = "a" * 255
        result = sanitize_task_name(exact_max)
        assert result == exact_max
        assert len(result) == 255

        # Test one character over max
        over_max = "a" * 256
        result = sanitize_task_name(over_max)
        assert len(result) == 255
        assert result == "a" * 255

        # Test with trailing whitespace that gets truncated
        over_max_with_spaces = "a" * 250 + "     "
        result = sanitize_task_name(over_max_with_spaces)
        assert len(result) == 250
        assert result == "a" * 250

    def test_custom_max_length(self):
        """Test custom maximum length parameter."""
        test_cases = [
            ("Long task name", 10, "Long task"),
            ("Short", 10, "Short"),
            ("Exact length", 12, "Exact length"),
            ("Over length task", 5, "Over"),
            ("   Padded   ", 6, "Padded"),
        ]

        for input_name, max_len, expected in test_cases:
            result = sanitize_task_name(input_name, max_length=max_len)
            assert result == expected
            assert len(result) <= max_len

    def test_special_characters_preserved(self):
        """Test that special characters are preserved."""
        special_names = [
            "Task #123",
            "Task @mention",
            "Task $price",
            "Task 50% complete",
            "Task (parentheses)",
            "Task [brackets]",
            "Task {braces}",
            "Task <angle>",
            "Task & ampersand",
            "Task | pipe",
            "Task / slash",
            "Task \\ backslash",
            "Task : colon",
            "Task ; semicolon",
            "Task ' apostrophe",
            'Task " quote',
            "Task ? question",
            "Task ! exclamation",
            "Task + plus",
            "Task = equals",
            "Task ~ tilde",
            "Task ` backtick",
        ]

        for name in special_names:
            result = sanitize_task_name(name)
            assert result == name

    def test_only_whitespace_variations(self):
        """Test strings that contain only whitespace."""
        whitespace_only = [
            "   ",
            "\t\t\t",
            "\n\n\n",
            "\r\n\r\n",
            " \t \n \r ",
            "\u00a0\u00a0",  # Non-breaking spaces
            "\u2003\u2003",  # Em spaces
        ]

        for ws in whitespace_only:
            with pytest.raises(ValueError, match="Task name cannot be empty after sanitization"):
                sanitize_task_name(ws)

    def test_invalid_input_types(self):
        """Test invalid input types."""
        invalid_inputs = [None, 123, [], {}, True, False, 0.5, bytes(b"test"), set(), complex(1, 2)]

        for invalid_input in invalid_inputs:
            with pytest.raises(ValueError, match="Task name must be a non-empty string"):
                sanitize_task_name(invalid_input)

    def test_empty_after_truncation(self):
        """Test names that become empty after truncation."""
        # Name that becomes empty after truncation and rstrip
        name_with_trailing_spaces = "   " + " " * 300  # Only spaces
        with pytest.raises(ValueError, match="Task name cannot be empty after sanitization"):
            sanitize_task_name(name_with_trailing_spaces)

    def test_edge_case_truncation_with_words(self):
        """Test truncation that might cut through words."""
        long_name = "This is a very long task name that exceeds the maximum length"
        result = sanitize_task_name(long_name, max_length=20)
        assert len(result) <= 20
        assert result == "This is a very long"  # Should be truncated and rstripped

    def test_mixed_whitespace_normalization(self):
        """Test complex whitespace normalization scenarios."""
        complex_whitespace = "  Task  \t\n  with  \r\n  mixed  \u00a0  whitespace  "
        result = sanitize_task_name(complex_whitespace)
        assert result == "Task with mixed whitespace"

    def test_zero_max_length(self):
        """Test with zero maximum length."""
        # Zero max length should still return empty string (rstrip might result in empty)
        result = sanitize_task_name("Any task name", max_length=0)
        assert result == ""

    def test_negative_max_length(self):
        """Test with negative maximum length."""
        # This should either raise an error or handle gracefully
        try:
            result = sanitize_task_name("Task name", max_length=-1)
            # If it doesn't raise an error, it should handle gracefully
            assert len(result) >= 0
        except ValueError:
            # This is also acceptable behavior
            pass


class TestExtractClickUpIdsFromUrl:
    """Test cases for extract_clickup_ids_from_url function."""

    def test_task_url(self):
        """Test extracting IDs from task URL."""
        url = "https://app.clickup.com/123456/t/abc123def"
        result = extract_clickup_ids_from_url(url)

        expected = {"team_id": "123456", "space_id": None, "folder_id": None, "list_id": None, "task_id": "abc123def"}

        assert result == expected

    def test_list_url(self):
        """Test extracting IDs from list URL."""
        url = "https://app.clickup.com/team/123456/space/789/list/456def"
        result = extract_clickup_ids_from_url(url)

        assert result["team_id"] == "123456"
        assert result["space_id"] == "789"
        assert result["list_id"] == "456def"

    def test_space_url(self):
        """Test extracting IDs from space URL."""
        url = "https://app.clickup.com/team/123456/space/789abc"
        result = extract_clickup_ids_from_url(url)

        assert result["team_id"] == "123456"
        assert result["space_id"] == "789abc"
        assert result["list_id"] is None

    def test_no_matches(self):
        """Test URL with no matching IDs."""
        url = "https://example.com/some/other/path"
        result = extract_clickup_ids_from_url(url)

        expected = {"team_id": None, "space_id": None, "folder_id": None, "list_id": None, "task_id": None}

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
        string_map = {"urgent": 1, "high": 2, "normal": 3, "low": 4, "URGENT": 1, "High": 2, " normal ": 3}

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


class TestFormatPriorityAdvanced:
    """Advanced test cases for format_priority function."""

    def test_case_insensitive_strings(self):
        """Test case-insensitive string priority handling."""
        case_variations = [
            ("urgent", 1),
            ("URGENT", 1),
            ("Urgent", 1),
            ("uRgEnT", 1),
            ("high", 2),
            ("HIGH", 2),
            ("High", 2),
            ("hIgH", 2),
            ("normal", 3),
            ("NORMAL", 3),
            ("Normal", 3),
            ("nOrMaL", 3),
            ("low", 4),
            ("LOW", 4),
            ("Low", 4),
            ("lOw", 4),
        ]

        for input_str, expected in case_variations:
            result = format_priority(input_str)
            assert result == expected

    def test_string_with_whitespace(self):
        """Test string priorities with whitespace."""
        whitespace_variations = [
            (" urgent ", 1),
            ("\turgent\t", 1),
            ("\nurgent\n", 1),
            (" high ", 2),
            ("\thigh\t", 2),
            ("\nhigh\n", 2),
            (" normal ", 3),
            ("\tnormal\t", 3),
            ("\nnormal\n", 3),
            (" low ", 4),
            ("\tlow\t", 4),
            ("\nlow\n", 4),
        ]

        for input_str, expected in whitespace_variations:
            result = format_priority(input_str)
            assert result == expected

    def test_numeric_strings(self):
        """Test numeric string inputs."""
        numeric_strings = [
            ("1", 1),
            ("2", 2),
            ("3", 3),
            ("4", 4),
            (" 1 ", 1),
            ("\t2\t", 2),
            ("\n3\n", 3),
            (" 4 ", 4),
        ]

        for input_str, expected in numeric_strings:
            result = format_priority(input_str)
            assert result == expected

    def test_invalid_numeric_strings(self):
        """Test invalid numeric string inputs."""
        invalid_numerics = ["0", "5", "10", "-1", "1.5", "2.0", "3.14", "999"]

        for invalid_str in invalid_numerics:
            with pytest.raises(ValueError, match="Invalid priority value"):
                format_priority(invalid_str)

    def test_invalid_string_values(self):
        """Test invalid string priority values."""
        invalid_strings = [
            "medium",
            "critical",
            "emergency",
            "none",
            "null",
            "undefined",
            "urgent!",
            "high-priority",
            "low_priority",
            "normal_task",
            "1urgent",
            "2high",
            "urgent1",
            "high2",
            "priority1",
            "p1",
            "",
            "   ",
            "\t\n",
            "priority",
            "level",
            "importance",
        ]

        for invalid_str in invalid_strings:
            with pytest.raises(ValueError, match="Invalid priority value"):
                format_priority(invalid_str)

    def test_boundary_integer_values(self):
        """Test boundary integer values."""
        # Valid boundaries
        valid_boundaries = [1, 2, 3, 4]
        for value in valid_boundaries:
            result = format_priority(value)
            assert result == value

        # Invalid boundaries
        invalid_boundaries = [0, 5, -1, 10, 100, -100]
        for value in invalid_boundaries:
            with pytest.raises(ValueError, match="Priority must be 1"):
                format_priority(value)

    def test_float_inputs(self):
        """Test float inputs (should be invalid)."""
        float_inputs = [1.0, 2.0, 3.0, 4.0, 1.5, 2.5, 3.14, 0.5]

        for float_val in float_inputs:
            with pytest.raises(ValueError, match="Invalid priority value"):
                format_priority(float_val)

    def test_boolean_inputs(self):
        """Test boolean inputs (should be converted to int)."""
        # True -> 1, False -> 0, both should be handled as integers
        assert format_priority(True) == 1  # True is treated as 1
        with pytest.raises(ValueError):  # False is treated as 0, which is invalid
            format_priority(False)

    def test_complex_types(self):
        """Test complex data types."""
        complex_types = [[], {}, set(), tuple(), complex(1, 2), bytes(b"test"), lambda x: x, format_priority, object()]

        for complex_val in complex_types:
            with pytest.raises(ValueError, match="Invalid priority value"):
                format_priority(complex_val)

    def test_numeric_edge_cases(self):
        """Test numeric edge cases."""
        edge_cases = [
            # Large integers
            (1000000, ValueError),
            (-1000000, ValueError),
            # Very large integers
            (2**31, ValueError),
            (2**63, ValueError),
            # Zero and negative
            (0, ValueError),
            (-1, ValueError),
            (-2, ValueError),
        ]

        for value, expected_exception in edge_cases:
            with pytest.raises(expected_exception, match="Priority must be 1"):
                format_priority(value)

    def test_string_representations_of_floats(self):
        """Test string representations of floats."""
        float_strings = ["1.0", "2.0", "3.0", "4.0", "1.5", "2.5", "3.14"]

        for float_str in float_strings:
            with pytest.raises(ValueError, match="Invalid priority value"):
                format_priority(float_str)

    def test_multilingual_priority_strings(self):
        """Test priority strings in different languages (should be invalid)."""
        multilingual_strings = [
            "紧急",
            "高",
            "正常",
            "低",  # Chinese
            "urgent",
            "élevé",
            "normal",
            "faible",  # French
            "urgente",
            "alto",
            "normal",
            "bajo",  # Spanish
            "срочный",
            "высокий",
            "нормальный",
            "низкий",  # Russian
        ]

        for ml_str in multilingual_strings:
            if ml_str not in ["urgent", "normal"]:  # These are valid English
                with pytest.raises(ValueError, match="Invalid priority value"):
                    format_priority(ml_str)

    def test_priority_with_extra_text(self):
        """Test priority strings with extra text."""
        extra_text_strings = [
            "urgent priority",
            "high priority",
            "normal priority",
            "low priority",
            "priority: urgent",
            "priority: high",
            "priority: normal",
            "priority: low",
            "urgentx",
            "xurgent",
            "highx",
            "xhigh",
            "normalx",
            "xnormal",
            "lowx",
            "xlow",
        ]

        for extra_str in extra_text_strings:
            with pytest.raises(ValueError, match="Invalid priority value"):
                format_priority(extra_str)

    def test_none_returns_none(self):
        """Test that None input returns None."""
        assert format_priority(None) is None

    def test_recursive_string_parsing(self):
        """Test that string parsing works recursively through int conversion."""
        # This tests the recursive call to format_priority(int(priority))
        valid_string_ints = ["1", "2", "3", "4"]
        for str_int in valid_string_ints:
            result = format_priority(str_int)
            assert result == int(str_int)

        # Test invalid string ints
        invalid_string_ints = ["0", "5", "-1", "10"]
        for str_int in invalid_string_ints:
            with pytest.raises(ValueError, match="Invalid priority value"):
                format_priority(str_int)


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
        data = {"user": {"profile": {"name": "John Doe"}}}

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


class TestSafeGetAdvanced:
    """Advanced test cases for safe_get function."""

    def test_deeply_nested_dictionaries(self):
        """Test deeply nested dictionary access."""
        deep_dict = {"level1": {"level2": {"level3": {"level4": {"level5": "deep_value"}}}}}

        assert safe_get(deep_dict, "level1", "level2", "level3", "level4", "level5") == "deep_value"
        assert safe_get(deep_dict, "level1", "level2", "level3", "level4", "level5", "nonexistent") is None

    def test_mixed_data_types_in_nested_structure(self):
        """Test nested structures with mixed data types."""
        mixed_dict = {
            "string_key": "string_value",
            "int_key": 42,
            "float_key": 3.14,
            "bool_key": True,
            "none_key": None,
            "list_key": [1, 2, 3],
            "nested": {
                "inner_string": "inner_value",
                "inner_int": 100,
                "inner_list": ["a", "b", "c"],
                "inner_dict": {"deep": "value"},
            },
        }

        assert safe_get(mixed_dict, "string_key") == "string_value"
        assert safe_get(mixed_dict, "int_key") == 42
        assert safe_get(mixed_dict, "float_key") == 3.14
        assert safe_get(mixed_dict, "bool_key") is True
        assert safe_get(mixed_dict, "none_key") is None
        assert safe_get(mixed_dict, "list_key") == [1, 2, 3]
        assert safe_get(mixed_dict, "nested", "inner_string") == "inner_value"
        assert safe_get(mixed_dict, "nested", "inner_dict", "deep") == "value"

    def test_non_dict_intermediate_values(self):
        """Test when intermediate values are not dictionaries."""
        non_dict_structure = {
            "string_val": "I'm a string",
            "int_val": 42,
            "list_val": [1, 2, 3],
            "none_val": None,
            "bool_val": True,
            "nested": {"valid": "value"},
        }

        # These should return default because intermediate values aren't dicts
        assert safe_get(non_dict_structure, "string_val", "nonexistent") is None
        assert safe_get(non_dict_structure, "int_val", "nonexistent") is None
        assert safe_get(non_dict_structure, "list_val", "nonexistent") is None
        assert safe_get(non_dict_structure, "none_val", "nonexistent") is None
        assert safe_get(non_dict_structure, "bool_val", "nonexistent") is None

        # This should work
        assert safe_get(non_dict_structure, "nested", "valid") == "value"

    def test_custom_default_values(self):
        """Test custom default values."""
        data = {"exists": "value"}

        # Test various default types
        assert safe_get(data, "missing", default="custom_default") == "custom_default"
        assert safe_get(data, "missing", default=42) == 42
        assert safe_get(data, "missing", default=[]) == []
        assert safe_get(data, "missing", default={}) == {}
        assert safe_get(data, "missing", default=False) is False
        assert safe_get(data, "missing", default=0) == 0
        assert safe_get(data, "missing", default="") == ""

    def test_empty_key_sequence(self):
        """Test behavior with empty key sequence."""
        data = {"key": "value"}

        # No keys should return the original data
        assert safe_get(data) == data

    def test_single_key_access(self):
        """Test single key access scenarios."""
        data = {
            "simple": "value",
            "": "empty_key_value",
            " ": "space_key_value",
            "0": "zero_string_key",
            0: "zero_int_key",
            None: "none_key_value",
            1: "one_int_key",
            2: "two_int_key",
        }

        assert safe_get(data, "simple") == "value"
        assert safe_get(data, "") == "empty_key_value"
        assert safe_get(data, " ") == "space_key_value"
        assert safe_get(data, "0") == "zero_string_key"
        assert safe_get(data, 0) == "zero_int_key"
        assert safe_get(data, None) == "none_key_value"
        assert safe_get(data, 1) == "one_int_key"
        assert safe_get(data, 2) == "two_int_key"

        # Test boolean keys (they map to int keys in Python)
        assert safe_get(data, True) == "one_int_key"  # True == 1
        assert safe_get(data, False) == "zero_int_key"  # False == 0

    def test_key_types_consistency(self):
        """Test different key types in nested access."""
        data = {"string_key": {0: {True: {None: "nested_value"}}}}

        assert safe_get(data, "string_key", 0, True, None) == "nested_value"
        assert safe_get(data, "string_key", 0, True, "None") is None  # String "None" vs None

    def test_special_string_keys(self):
        """Test special string keys."""
        data = {
            "": "empty",
            " ": "space",
            "\t": "tab",
            "\n": "newline",
            "\r\n": "crlf",
            "   ": "multiple_spaces",
            "key with spaces": "spaced_key",
            "key-with-dashes": "dashed_key",
            "key_with_underscores": "underscore_key",
            "key.with.dots": "dotted_key",
            "key/with/slashes": "slashed_key",
            "key\\with\\backslashes": "backslash_key",
            "key:with:colons": "colon_key",
            "key@with@symbols": "symbol_key",
        }

        for key, expected_value in data.items():
            assert safe_get(data, key) == expected_value

    def test_unicode_keys(self):
        """Test unicode keys."""
        data = {
            "café": "coffee",
            "测试": "test",
            "🚀": "rocket",
            "naïve": "naive",
            "résumé": "resume",
            "北京": "beijing",
            "東京": "tokyo",
            "🌟⭐": "stars",
        }

        for key, expected_value in data.items():
            assert safe_get(data, key) == expected_value

    def test_large_nested_structure(self):
        """Test with large nested structure."""
        # Create a large nested structure
        large_dict = {}
        current = large_dict
        keys = []

        for i in range(100):
            key = f"level_{i}"
            keys.append(key)
            current[key] = {}
            current = current[key]

        # Set final value
        current["final"] = "deep_value"
        keys.append("final")

        # Test access
        assert safe_get(large_dict, *keys) == "deep_value"

        # Test partial access
        partial_keys = keys[:50]
        result = safe_get(large_dict, *partial_keys)
        assert isinstance(result, dict)

    def test_circular_reference_safety(self):
        """Test safety with circular references."""
        data = {"a": {}}
        data["a"]["b"] = data  # Create circular reference

        # Should not cause infinite recursion
        assert safe_get(data, "a", "b", "a", "b") == data
        assert safe_get(data, "a", "b", "a", "nonexistent") is None

    def test_none_values_in_path(self):
        """Test when values in the path are None."""
        data = {"level1": {"level2": None, "level3": {"level4": "value"}}}

        assert safe_get(data, "level1", "level2") is None
        assert safe_get(data, "level1", "level2", "anything") is None
        assert safe_get(data, "level1", "level3", "level4") == "value"

    def test_default_value_with_none_in_path(self):
        """Test default values when None is encountered in path."""
        data = {"level1": {"level2": None}}

        assert safe_get(data, "level1", "level2", "anything", default="default") == "default"

    def test_empty_nested_dicts(self):
        """Test with empty nested dictionaries."""
        data = {"empty": {}, "nested_empty": {"empty": {}}}

        assert safe_get(data, "empty") == {}
        assert safe_get(data, "empty", "anything") is None
        assert safe_get(data, "nested_empty", "empty") == {}
        assert safe_get(data, "nested_empty", "empty", "anything") is None

    def test_boolean_and_numeric_values(self):
        """Test with boolean and numeric values in structure."""
        data = {
            "zero": 0,
            "false": False,
            "empty_string": "",
            "empty_list": [],
            "empty_dict": {},
            "nested": {"zero": 0, "false": False, "empty_string": "", "none": None},
        }

        assert safe_get(data, "zero") == 0
        assert safe_get(data, "false") is False
        assert safe_get(data, "empty_string") == ""
        assert safe_get(data, "empty_list") == []
        assert safe_get(data, "empty_dict") == {}
        assert safe_get(data, "nested", "zero") == 0
        assert safe_get(data, "nested", "false") is False
        assert safe_get(data, "nested", "empty_string") == ""
        assert safe_get(data, "nested", "none") is None

    def test_key_error_scenarios(self):
        """Test various key error scenarios."""
        data = {"exists": {"nested": "value"}}

        # Missing keys at different levels
        assert safe_get(data, "missing") is None
        assert safe_get(data, "exists", "missing") is None
        assert safe_get(data, "missing", "nested") is None


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


class TestClickUpURLBuilderAdvanced:
    """Advanced test cases for ClickUpURLBuilder class."""

    def test_space_url_variations(self):
        """Test space URL building variations."""
        # With team
        url = ClickUpURLBuilder.build_space_url("space123", "team456")
        assert url == "https://app.clickup.com/team456/v/s/space123"

        # Without team
        url = ClickUpURLBuilder.build_space_url("space123")
        assert url == "https://app.clickup.com/v/s/space123"

        # With None team (should be same as without)
        url = ClickUpURLBuilder.build_space_url("space123", None)
        assert url == "https://app.clickup.com/v/s/space123"

        # With empty string team (should be same as without)
        url = ClickUpURLBuilder.build_space_url("space123", "")
        assert url == "https://app.clickup.com/v/s/space123"

    def test_folder_url_variations(self):
        """Test folder URL building variations."""
        # With team
        url = ClickUpURLBuilder.build_folder_url("folder123", "team456")
        assert url == "https://app.clickup.com/team456/v/f/folder123"

        # Without team
        url = ClickUpURLBuilder.build_folder_url("folder123")
        assert url == "https://app.clickup.com/v/f/folder123"

        # With None team (should be same as without)
        url = ClickUpURLBuilder.build_folder_url("folder123", None)
        assert url == "https://app.clickup.com/v/f/folder123"

        # With empty string team (should be same as without)
        url = ClickUpURLBuilder.build_folder_url("folder123", "")
        assert url == "https://app.clickup.com/v/f/folder123"

    def test_special_ids(self):
        """Test URL building with special characters in IDs."""
        # Task with special characters
        url = ClickUpURLBuilder.build_task_url("task-123_456", "team-789")
        assert url == "https://app.clickup.com/team-789/t/task-123_456"

        # List with special characters
        url = ClickUpURLBuilder.build_list_url("list_123-456", "team_789")
        assert url == "https://app.clickup.com/team_789/v/li/list_123-456"

        # Space with special characters
        url = ClickUpURLBuilder.build_space_url("space-123_456", "team-789_012")
        assert url == "https://app.clickup.com/team-789_012/v/s/space-123_456"

        # Folder with special characters
        url = ClickUpURLBuilder.build_folder_url("folder_123-456", "team-789")
        assert url == "https://app.clickup.com/team-789/v/f/folder_123-456"

    def test_numeric_string_ids(self):
        """Test URL building with numeric string IDs."""
        # All numeric IDs
        url = ClickUpURLBuilder.build_task_url("123456789", "987654321")
        assert url == "https://app.clickup.com/987654321/t/123456789"

        url = ClickUpURLBuilder.build_list_url("123456", "789012")
        assert url == "https://app.clickup.com/789012/v/li/123456"

        url = ClickUpURLBuilder.build_space_url("345678", "901234")
        assert url == "https://app.clickup.com/901234/v/s/345678"

        url = ClickUpURLBuilder.build_folder_url("567890", "123456")
        assert url == "https://app.clickup.com/123456/v/f/567890"

    def test_mixed_case_ids(self):
        """Test URL building with mixed case IDs."""
        # Mixed case IDs
        url = ClickUpURLBuilder.build_task_url("TaSk123", "TeAm456")
        assert url == "https://app.clickup.com/TeAm456/t/TaSk123"

        url = ClickUpURLBuilder.build_list_url("LiSt123", "TeAm456")
        assert url == "https://app.clickup.com/TeAm456/v/li/LiSt123"

        url = ClickUpURLBuilder.build_space_url("SpAcE123", "TeAm456")
        assert url == "https://app.clickup.com/TeAm456/v/s/SpAcE123"

        url = ClickUpURLBuilder.build_folder_url("FoLdEr123", "TeAm456")
        assert url == "https://app.clickup.com/TeAm456/v/f/FoLdEr123"

    def test_base_url_consistency(self):
        """Test that all methods use the same base URL."""
        base_url = "https://app.clickup.com"

        # Test all methods use the same base URL
        task_url = ClickUpURLBuilder.build_task_url("task123")
        list_url = ClickUpURLBuilder.build_list_url("list123")
        space_url = ClickUpURLBuilder.build_space_url("space123")
        folder_url = ClickUpURLBuilder.build_folder_url("folder123")

        assert task_url.startswith(base_url)
        assert list_url.startswith(base_url)
        assert space_url.startswith(base_url)
        assert folder_url.startswith(base_url)

    def test_url_patterns(self):
        """Test specific URL patterns for each method."""
        # Task URL pattern
        url = ClickUpURLBuilder.build_task_url("task123", "team456")
        assert "/t/" in url

        # List URL pattern
        url = ClickUpURLBuilder.build_list_url("list123", "team456")
        assert "/v/li/" in url

        # Space URL pattern
        url = ClickUpURLBuilder.build_space_url("space123", "team456")
        assert "/v/s/" in url

        # Folder URL pattern
        url = ClickUpURLBuilder.build_folder_url("folder123", "team456")
        assert "/v/f/" in url


class TestUtilsIntegration:
    """Integration tests for utility functions working together."""

    def test_id_validation_with_url_extraction(self):
        """Test that extracted IDs pass validation."""
        test_urls = [
            "https://app.clickup.com/team123/t/task456",
            "https://app.clickup.com/team123/v/li/list456",
            "https://app.clickup.com/team123/space/space456",
            "https://app.clickup.com/team123/folder/folder456",
        ]

        for url in test_urls:
            extracted_ids = extract_clickup_ids_from_url(url)
            for id_type, id_value in extracted_ids.items():
                if id_value is not None:
                    # Should not raise an exception
                    validated_id = validate_clickup_id(id_value, id_type)
                    assert validated_id == id_value

    def test_url_builder_with_extracted_ids(self):
        """Test that extracted IDs can be used to build URLs."""
        original_url = "https://app.clickup.com/team123/t/task456"
        extracted_ids = extract_clickup_ids_from_url(original_url)

        # Rebuild URL using extracted IDs
        rebuilt_url = ClickUpURLBuilder.build_task_url(extracted_ids["task_id"], extracted_ids["team_id"])

        # URLs should be equivalent (though not necessarily identical due to format differences)
        assert extracted_ids["task_id"] in rebuilt_url
        assert extracted_ids["team_id"] in rebuilt_url

    def test_date_formatting_round_trip(self):
        """Test that date formatting and parsing work together."""
        from datetime import datetime, timezone

        # Test with current datetime
        original_dt = datetime(2023, 6, 15, 14, 30, 0, tzinfo=timezone.utc)

        # Format to ClickUp timestamp
        formatted_ts = format_clickup_date(original_dt)
        assert formatted_ts is not None

        # Parse back to datetime
        parsed_dt = parse_clickup_date(formatted_ts)
        assert parsed_dt is not None

        # Should be the same (allowing for millisecond precision)
        assert abs((parsed_dt - original_dt).total_seconds()) < 0.001

    def test_task_name_sanitization_with_params(self):
        """Test task name sanitization with query parameters."""
        # Create a task with sanitized name
        task_name = "  My Task With    Multiple   Spaces  "
        sanitized_name = sanitize_task_name(task_name)

        # Use in query parameters
        params = {
            "name": sanitized_name,
            "priority": format_priority("high"),
            "status": format_status("Open"),
            "tags": ["urgent", "backend"],
        }

        query_params = build_query_params(params)

        # Verify all components work together
        assert query_params["name"] == "My Task With Multiple Spaces"
        assert query_params["priority"] == "2"
        assert query_params["status"] == "open"
        assert query_params["tags[]"] == ["urgent", "backend"]


class TestFilterNoneValues:
    """Test cases for filter_none_values function."""

    def test_basic_filtering(self):
        """Test basic None value filtering."""
        data = {"a": 1, "b": None, "c": "test", "d": None, "e": 0}
        result = filter_none_values(data)
        expected = {"a": 1, "c": "test", "e": 0}
        assert result == expected

    def test_empty_dict(self):
        """Test filtering empty dictionary."""
        result = filter_none_values({})
        assert result == {}

    def test_all_none_values(self):
        """Test dictionary with all None values."""
        data = {"a": None, "b": None, "c": None}
        result = filter_none_values(data)
        assert result == {}

    def test_no_none_values(self):
        """Test dictionary with no None values."""
        data = {"a": 1, "b": "test", "c": [], "d": {}}
        result = filter_none_values(data)
        assert result == data

    def test_mixed_data_types(self):
        """Test filtering with mixed data types."""
        data = {
            "string": "value",
            "number": 42,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "none1": None,
            "none2": None,
            "false": False,
            "zero": 0,
            "empty_string": "",
            "empty_list": [],
            "empty_dict": {},
        }
        result = filter_none_values(data)
        expected = {
            "string": "value",
            "number": 42,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "false": False,
            "zero": 0,
            "empty_string": "",
            "empty_list": [],
            "empty_dict": {},
        }
        assert result == expected

    def test_special_keys(self):
        """Test filtering with special key types."""
        # Test with non-colliding keys to avoid 0/False and 1/True collisions
        data = {
            "": "empty_key",
            " ": "space_key",
            "normal": "value",
            "none_value": None,
            2: "two_key",
            3: None,
            "True": "true_string_key",
            "False": None,
        }
        result = filter_none_values(data)
        expected = {"": "empty_key", " ": "space_key", "normal": "value", 2: "two_key", "True": "true_string_key"}
        assert result == expected


class TestClickUpURLBuilderExtended:
    """Extended test cases for ClickUpURLBuilder class."""

    def test_space_url_variations(self):
        """Test space URL building variations."""
        # With team
        url = ClickUpURLBuilder.build_space_url("space123", "team456")
        assert url == "https://app.clickup.com/team456/v/s/space123"

        # Without team
        url = ClickUpURLBuilder.build_space_url("space123")
        assert url == "https://app.clickup.com/v/s/space123"

        # With None team (should be same as without)
        url = ClickUpURLBuilder.build_space_url("space123", None)
        assert url == "https://app.clickup.com/v/s/space123"

        # With empty string team (should be same as without)
        url = ClickUpURLBuilder.build_space_url("space123", "")
        assert url == "https://app.clickup.com/v/s/space123"

    def test_folder_url_variations(self):
        """Test folder URL building variations."""
        # With team
        url = ClickUpURLBuilder.build_folder_url("folder123", "team456")
        assert url == "https://app.clickup.com/team456/v/f/folder123"

        # Without team
        url = ClickUpURLBuilder.build_folder_url("folder123")
        assert url == "https://app.clickup.com/v/f/folder123"

        # With None team (should be same as without)
        url = ClickUpURLBuilder.build_folder_url("folder123", None)
        assert url == "https://app.clickup.com/v/f/folder123"

        # With empty string team (should be same as without)
        url = ClickUpURLBuilder.build_folder_url("folder123", "")
        assert url == "https://app.clickup.com/v/f/folder123"

    def test_special_ids(self):
        """Test URL building with special characters in IDs."""
        # Task with special characters
        url = ClickUpURLBuilder.build_task_url("task-123_456", "team-789")
        assert url == "https://app.clickup.com/team-789/t/task-123_456"

        # List with special characters
        url = ClickUpURLBuilder.build_list_url("list_123-456", "team_789")
        assert url == "https://app.clickup.com/team_789/v/li/list_123-456"

        # Space with special characters
        url = ClickUpURLBuilder.build_space_url("space-123_456", "team-789_012")
        assert url == "https://app.clickup.com/team-789_012/v/s/space-123_456"

        # Folder with special characters
        url = ClickUpURLBuilder.build_folder_url("folder_123-456", "team-789")
        assert url == "https://app.clickup.com/team-789/v/f/folder_123-456"

    def test_numeric_string_ids(self):
        """Test URL building with numeric string IDs."""
        # All numeric IDs
        url = ClickUpURLBuilder.build_task_url("123456789", "987654321")
        assert url == "https://app.clickup.com/987654321/t/123456789"

        url = ClickUpURLBuilder.build_list_url("123456", "789012")
        assert url == "https://app.clickup.com/789012/v/li/123456"

        url = ClickUpURLBuilder.build_space_url("345678", "901234")
        assert url == "https://app.clickup.com/901234/v/s/345678"

        url = ClickUpURLBuilder.build_folder_url("567890", "123456")
        assert url == "https://app.clickup.com/123456/v/f/567890"

    def test_mixed_case_ids(self):
        """Test URL building with mixed case IDs."""
        # Mixed case IDs
        url = ClickUpURLBuilder.build_task_url("TaSk123", "TeAm456")
        assert url == "https://app.clickup.com/TeAm456/t/TaSk123"

        url = ClickUpURLBuilder.build_list_url("LiSt123", "TeAm456")
        assert url == "https://app.clickup.com/TeAm456/v/li/LiSt123"

        url = ClickUpURLBuilder.build_space_url("SpAcE123", "TeAm456")
        assert url == "https://app.clickup.com/TeAm456/v/s/SpAcE123"

        url = ClickUpURLBuilder.build_folder_url("FoLdEr123", "TeAm456")
        assert url == "https://app.clickup.com/TeAm456/v/f/FoLdEr123"

    def test_base_url_consistency(self):
        """Test that all methods use the same base URL."""
        base_url = "https://app.clickup.com"

        # Test all methods use the same base URL
        task_url = ClickUpURLBuilder.build_task_url("task123")
        list_url = ClickUpURLBuilder.build_list_url("list123")
        space_url = ClickUpURLBuilder.build_space_url("space123")
        folder_url = ClickUpURLBuilder.build_folder_url("folder123")

        assert task_url.startswith(base_url)
        assert list_url.startswith(base_url)
        assert space_url.startswith(base_url)
        assert folder_url.startswith(base_url)

    def test_url_patterns(self):
        """Test specific URL patterns for each method."""
        # Task URL pattern
        url = ClickUpURLBuilder.build_task_url("task123", "team456")
        assert "/t/" in url

        # List URL pattern
        url = ClickUpURLBuilder.build_list_url("list123", "team456")
        assert "/v/li/" in url

        # Space URL pattern
        url = ClickUpURLBuilder.build_space_url("space123", "team456")
        assert "/v/s/" in url

        # Folder URL pattern
        url = ClickUpURLBuilder.build_folder_url("folder123", "team456")
        assert "/v/f/" in url
