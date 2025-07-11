"""
Comprehensive unit tests for the ClickUp configuration module.

This module provides full test coverage for the ClickUp configuration classes
and functions, including edge cases, validation, and error handling.
"""

import os
import pytest
from typing import Dict, Any
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

from clickup_mcp.config import ClickUpConfig, load_config_from_env, get_default_config


class TestClickUpConfig:
    """Test class for ClickUpConfig model."""

    def test_valid_config_creation(self):
        """Test creating a valid ClickUpConfig instance."""
        config = ClickUpConfig(api_token="test_token_123")
        
        assert config.api_token == "test_token_123"
        assert config.base_url == "https://api.clickup.com/api/v2"
        assert config.timeout == 30.0
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.rate_limit_requests_per_minute == 100

    def test_config_with_all_parameters(self):
        """Test creating config with all parameters specified."""
        config = ClickUpConfig(
            api_token="custom_token",
            base_url="https://custom.api.com/v1",
            timeout=45.0,
            max_retries=5,
            retry_delay=2.5,
            rate_limit_requests_per_minute=200
        )
        
        assert config.api_token == "custom_token"
        assert config.base_url == "https://custom.api.com/v1"
        assert config.timeout == 45.0
        assert config.max_retries == 5
        assert config.retry_delay == 2.5
        assert config.rate_limit_requests_per_minute == 200

    def test_api_token_validation_empty_string(self):
        """Test API token validation with empty string."""
        with pytest.raises(ValidationError) as exc_info:
            ClickUpConfig(api_token="")
        
        assert "API token cannot be empty" in str(exc_info.value)

    def test_api_token_validation_whitespace_only(self):
        """Test API token validation with whitespace only."""
        with pytest.raises(ValidationError) as exc_info:
            ClickUpConfig(api_token="   ")
        
        assert "API token cannot be empty" in str(exc_info.value)

    def test_api_token_validation_none(self):
        """Test API token validation with None."""
        with pytest.raises(ValidationError) as exc_info:
            ClickUpConfig(api_token=None)
        
        assert "Input should be a valid string" in str(exc_info.value)

    def test_api_token_strips_whitespace(self):
        """Test that API token strips leading/trailing whitespace."""
        config = ClickUpConfig(api_token="  token_with_spaces  ")
        
        assert config.api_token == "token_with_spaces"

    def test_timeout_validation_negative(self):
        """Test timeout validation with negative value."""
        with pytest.raises(ValidationError) as exc_info:
            ClickUpConfig(api_token="test", timeout=-1.0)
        
        assert "Timeout must be positive" in str(exc_info.value)

    def test_timeout_validation_zero(self):
        """Test timeout validation with zero value."""
        with pytest.raises(ValidationError) as exc_info:
            ClickUpConfig(api_token="test", timeout=0.0)
        
        assert "Timeout must be positive" in str(exc_info.value)

    def test_timeout_validation_positive(self):
        """Test timeout validation with positive value."""
        config = ClickUpConfig(api_token="test", timeout=60.5)
        
        assert config.timeout == 60.5

    def test_max_retries_validation_negative(self):
        """Test max_retries validation with negative value."""
        with pytest.raises(ValidationError) as exc_info:
            ClickUpConfig(api_token="test", max_retries=-1)
        
        assert "Max retries cannot be negative" in str(exc_info.value)

    def test_max_retries_validation_zero(self):
        """Test max_retries validation with zero (valid)."""
        config = ClickUpConfig(api_token="test", max_retries=0)
        
        assert config.max_retries == 0

    def test_max_retries_validation_positive(self):
        """Test max_retries validation with positive value."""
        config = ClickUpConfig(api_token="test", max_retries=10)
        
        assert config.max_retries == 10

    def test_retry_delay_validation_negative(self):
        """Test retry_delay validation with negative value."""
        with pytest.raises(ValidationError) as exc_info:
            ClickUpConfig(api_token="test", retry_delay=-0.5)
        
        assert "Retry delay cannot be negative" in str(exc_info.value)

    def test_retry_delay_validation_zero(self):
        """Test retry_delay validation with zero (valid)."""
        config = ClickUpConfig(api_token="test", retry_delay=0.0)
        
        assert config.retry_delay == 0.0

    def test_retry_delay_validation_positive(self):
        """Test retry_delay validation with positive value."""
        config = ClickUpConfig(api_token="test", retry_delay=3.5)
        
        assert config.retry_delay == 3.5

    def test_rate_limit_validation_negative(self):
        """Test rate_limit validation with negative value."""
        with pytest.raises(ValidationError) as exc_info:
            ClickUpConfig(api_token="test", rate_limit_requests_per_minute=-1)
        
        assert "Rate limit must be positive" in str(exc_info.value)

    def test_rate_limit_validation_zero(self):
        """Test rate_limit validation with zero value."""
        with pytest.raises(ValidationError) as exc_info:
            ClickUpConfig(api_token="test", rate_limit_requests_per_minute=0)
        
        assert "Rate limit must be positive" in str(exc_info.value)

    def test_rate_limit_validation_positive(self):
        """Test rate_limit validation with positive value."""
        config = ClickUpConfig(api_token="test", rate_limit_requests_per_minute=500)
        
        assert config.rate_limit_requests_per_minute == 500

    def test_config_forbids_extra_fields(self):
        """Test that config forbids extra fields."""
        with pytest.raises(ValidationError) as exc_info:
            ClickUpConfig(api_token="test", extra_field="should_not_be_allowed")
        
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_config_case_insensitive(self):
        """Test that config is case-insensitive for environment variables."""
        # This test verifies the Config class settings, but direct testing
        # of case insensitivity is done through environment variable loading
        config = ClickUpConfig(api_token="test")
        
        # Verify the Config class has the correct settings
        assert config.model_config.get("env_prefix") == "CLICKUP_"
        assert config.model_config.get("case_sensitive") is False
        assert config.model_config.get("extra") == "forbid"


class TestClickUpConfigAdvanced:
    """Advanced test cases for ClickUpConfig."""

    def test_config_with_extreme_values(self):
        """Test config with extreme but valid values."""
        config = ClickUpConfig(
            api_token="a" * 1000,  # Very long token
            timeout=0.001,         # Very small timeout
            max_retries=1000,      # Very high retries
            retry_delay=0.0,       # Zero delay
            rate_limit_requests_per_minute=1  # Very low rate limit
        )
        
        assert len(config.api_token) == 1000
        assert config.timeout == 0.001
        assert config.max_retries == 1000
        assert config.retry_delay == 0.0
        assert config.rate_limit_requests_per_minute == 1

    def test_config_with_float_integers(self):
        """Test config with float values for integer fields."""
        config = ClickUpConfig(
            api_token="test",
            max_retries=5.0,  # Float that converts to int
            rate_limit_requests_per_minute=100.0
        )
        
        assert config.max_retries == 5
        assert config.rate_limit_requests_per_minute == 100

    def test_config_with_string_numbers(self):
        """Test config with string representations of numbers."""
        config = ClickUpConfig(
            api_token="test",
            timeout="45.5",
            max_retries="7",
            retry_delay="2.5",
            rate_limit_requests_per_minute="150"
        )
        
        assert config.timeout == 45.5
        assert config.max_retries == 7
        assert config.retry_delay == 2.5
        assert config.rate_limit_requests_per_minute == 150

    def test_config_validation_order(self):
        """Test that all validations are applied in correct order."""
        # Test multiple validation errors
        with pytest.raises(ValidationError) as exc_info:
            ClickUpConfig(
                api_token="",  # Empty token
                timeout=-1.0,  # Negative timeout
                max_retries=-1,  # Negative retries
                retry_delay=-1.0,  # Negative delay
                rate_limit_requests_per_minute=0  # Zero rate limit
            )
        
        error_messages = str(exc_info.value)
        assert "API token cannot be empty" in error_messages

    def test_config_with_unicode_token(self):
        """Test config with unicode characters in token."""
        unicode_token = "test_token_🚀_日本語"
        config = ClickUpConfig(api_token=unicode_token)
        
        assert config.api_token == unicode_token

    def test_config_with_special_characters_in_base_url(self):
        """Test config with special characters in base URL."""
        special_url = "https://api.example.com/v2?special=true&chars=!@#$%"
        config = ClickUpConfig(
            api_token="test",
            base_url=special_url
        )
        
        assert config.base_url == special_url

    def test_config_field_descriptions(self):
        """Test that config fields have proper descriptions."""
        config = ClickUpConfig(api_token="test")
        
        # Check that field descriptions are present
        fields = ClickUpConfig.model_fields
        assert "ClickUp API token" in fields["api_token"].description
        assert "Base URL for ClickUp API" in fields["base_url"].description
        assert "Request timeout in seconds" in fields["timeout"].description
        assert "Maximum number of retries" in fields["max_retries"].description
        assert "Initial delay between retries" in fields["retry_delay"].description
        assert "Rate limit for API requests" in fields["rate_limit_requests_per_minute"].description


class TestLoadConfigFromEnv:
    """Test class for load_config_from_env function."""

    def test_load_config_with_all_env_vars(self):
        """Test loading config with all environment variables set."""
        env_vars = {
            "CLICKUP_API_TOKEN": "env_token_123",
            "CLICKUP_BASE_URL": "https://custom.api.com/v3",
            "CLICKUP_TIMEOUT": "60.5",
            "CLICKUP_MAX_RETRIES": "5",
            "CLICKUP_RETRY_DELAY": "2.0",
            "CLICKUP_RATE_LIMIT_REQUESTS_PER_MINUTE": "200"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = load_config_from_env()
            
            assert config.api_token == "env_token_123"
            assert config.base_url == "https://custom.api.com/v3"
            assert config.timeout == 60.5
            assert config.max_retries == 5
            assert config.retry_delay == 2.0
            assert config.rate_limit_requests_per_minute == 200

    def test_load_config_with_minimal_env_vars(self):
        """Test loading config with only required environment variables."""
        env_vars = {
            "CLICKUP_API_TOKEN": "minimal_token"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = load_config_from_env()
            
            assert config.api_token == "minimal_token"
            assert config.base_url == "https://api.clickup.com/api/v2"  # Default
            assert config.timeout == 30.0  # Default
            assert config.max_retries == 3  # Default
            assert config.retry_delay == 1.0  # Default
            assert config.rate_limit_requests_per_minute == 100  # Default

    def test_load_config_missing_api_token(self):
        """Test loading config without API token environment variable."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                load_config_from_env()
            
            assert "CLICKUP_API_TOKEN environment variable is required" in str(exc_info.value)

    def test_load_config_empty_api_token(self):
        """Test loading config with empty API token environment variable."""
        env_vars = {
            "CLICKUP_API_TOKEN": ""
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError) as exc_info:
                load_config_from_env()
            
            assert "CLICKUP_API_TOKEN environment variable is required" in str(exc_info.value)

    def test_load_config_whitespace_api_token(self):
        """Test loading config with whitespace-only API token."""
        env_vars = {
            "CLICKUP_API_TOKEN": "   "
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                load_config_from_env()
            
            assert "API token cannot be empty" in str(exc_info.value)

    def test_load_config_invalid_timeout(self):
        """Test loading config with invalid timeout value."""
        env_vars = {
            "CLICKUP_API_TOKEN": "test_token",
            "CLICKUP_TIMEOUT": "invalid_number"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError) as exc_info:
                load_config_from_env()
            
            assert "could not convert string to float" in str(exc_info.value)

    def test_load_config_invalid_max_retries(self):
        """Test loading config with invalid max_retries value."""
        env_vars = {
            "CLICKUP_API_TOKEN": "test_token",
            "CLICKUP_MAX_RETRIES": "not_a_number"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError) as exc_info:
                load_config_from_env()
            
            assert "invalid literal for int()" in str(exc_info.value)

    def test_load_config_invalid_retry_delay(self):
        """Test loading config with invalid retry_delay value."""
        env_vars = {
            "CLICKUP_API_TOKEN": "test_token",
            "CLICKUP_RETRY_DELAY": "not_a_float"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError) as exc_info:
                load_config_from_env()
            
            assert "could not convert string to float" in str(exc_info.value)

    def test_load_config_invalid_rate_limit(self):
        """Test loading config with invalid rate_limit value."""
        env_vars = {
            "CLICKUP_API_TOKEN": "test_token",
            "CLICKUP_RATE_LIMIT_REQUESTS_PER_MINUTE": "not_an_integer"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError) as exc_info:
                load_config_from_env()
            
            assert "invalid literal for int()" in str(exc_info.value)

    def test_load_config_with_negative_values(self):
        """Test loading config with negative values from environment."""
        env_vars = {
            "CLICKUP_API_TOKEN": "test_token",
            "CLICKUP_TIMEOUT": "-1.0",
            "CLICKUP_MAX_RETRIES": "-1",
            "CLICKUP_RETRY_DELAY": "-1.0",
            "CLICKUP_RATE_LIMIT_REQUESTS_PER_MINUTE": "-1"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                load_config_from_env()
            
            error_message = str(exc_info.value)
            assert "Timeout must be positive" in error_message or \
                   "Max retries cannot be negative" in error_message or \
                   "Retry delay cannot be negative" in error_message or \
                   "Rate limit must be positive" in error_message

    def test_load_config_case_insensitive_env_vars(self):
        """Test loading config with case-insensitive environment variables."""
        # Note: The load_config_from_env function doesn't use Pydantic's env loading
        # It manually reads from os.environ, so it's case-sensitive
        # This test demonstrates the case-sensitive behavior
        env_vars = {
            "CLICKUP_API_TOKEN": "case_test_token",  # Must be uppercase
            "CLICKUP_BASE_URL": "https://mixed.case.com/v2",
            "CLICKUP_TIMEOUT": "45.0",
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = load_config_from_env()
            
            assert config.api_token == "case_test_token"
            assert config.base_url == "https://mixed.case.com/v2"
            assert config.timeout == 45.0

    def test_load_config_with_extra_env_vars(self):
        """Test loading config ignores extra environment variables."""
        env_vars = {
            "CLICKUP_API_TOKEN": "test_token",
            "CLICKUP_EXTRA_FIELD": "should_be_ignored",
            "OTHER_VAR": "also_ignored"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = load_config_from_env()
            
            assert config.api_token == "test_token"
            # Config should only have the defined fields
            assert not hasattr(config, 'extra_field')


class TestLoadConfigFromEnvAdvanced:
    """Advanced test cases for load_config_from_env function."""

    def test_load_config_with_unicode_env_values(self):
        """Test loading config with unicode characters in environment values."""
        env_vars = {
            "CLICKUP_API_TOKEN": "token_🔑_测试",
            "CLICKUP_BASE_URL": "https://api.example.com/v2/🚀"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = load_config_from_env()
            
            assert config.api_token == "token_🔑_测试"
            assert config.base_url == "https://api.example.com/v2/🚀"

    def test_load_config_with_whitespace_env_values(self):
        """Test loading config with whitespace in environment values."""
        env_vars = {
            "CLICKUP_API_TOKEN": "  token_with_spaces  ",
            "CLICKUP_BASE_URL": "  https://api.example.com/v2  "
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = load_config_from_env()
            
            assert config.api_token == "token_with_spaces"  # Should be trimmed
            assert config.base_url == "  https://api.example.com/v2  "  # URL not trimmed

    def test_load_config_with_float_string_values(self):
        """Test loading config with float string values."""
        env_vars = {
            "CLICKUP_API_TOKEN": "test_token",
            "CLICKUP_TIMEOUT": "30.123456",
            "CLICKUP_RETRY_DELAY": "1.999999"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = load_config_from_env()
            
            assert config.timeout == 30.123456
            assert config.retry_delay == 1.999999

    def test_load_config_with_scientific_notation(self):
        """Test loading config with scientific notation values."""
        env_vars = {
            "CLICKUP_API_TOKEN": "test_token",
            "CLICKUP_TIMEOUT": "3e1",  # 30.0
            "CLICKUP_RETRY_DELAY": "1.5e0"  # 1.5
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = load_config_from_env()
            
            assert config.timeout == 30.0
            assert config.retry_delay == 1.5

    def test_load_config_with_zero_values(self):
        """Test loading config with zero values from environment."""
        env_vars = {
            "CLICKUP_API_TOKEN": "test_token",
            "CLICKUP_MAX_RETRIES": "0",
            "CLICKUP_RETRY_DELAY": "0.0"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = load_config_from_env()
            
            assert config.max_retries == 0
            assert config.retry_delay == 0.0


class TestGetDefaultConfig:
    """Test class for get_default_config function."""

    def test_get_default_config_with_token(self):
        """Test getting default config with provided API token."""
        config = get_default_config(api_token="provided_token")
        
        assert config.api_token == "provided_token"
        assert config.base_url == "https://api.clickup.com/api/v2"
        assert config.timeout == 30.0
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.rate_limit_requests_per_minute == 100

    def test_get_default_config_without_token_with_env(self):
        """Test getting default config without token but with environment variable."""
        env_vars = {
            "CLICKUP_API_TOKEN": "env_token_123",
            "CLICKUP_TIMEOUT": "45.0"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = get_default_config()
            
            assert config.api_token == "env_token_123"
            assert config.timeout == 45.0

    def test_get_default_config_without_token_without_env(self):
        """Test getting default config without token and without environment variable."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                get_default_config()
            
            assert "CLICKUP_API_TOKEN environment variable is required" in str(exc_info.value)

    def test_get_default_config_with_empty_token(self):
        """Test getting default config with empty token string."""
        # Empty string is falsy, so it falls back to environment loading
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                get_default_config(api_token="")
            
            assert "CLICKUP_API_TOKEN environment variable is required" in str(exc_info.value)

    def test_get_default_config_with_none_token(self):
        """Test getting default config with None token."""
        env_vars = {
            "CLICKUP_API_TOKEN": "env_fallback_token"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = get_default_config(api_token=None)
            
            assert config.api_token == "env_fallback_token"

    def test_get_default_config_with_whitespace_token(self):
        """Test getting default config with whitespace-only token."""
        with pytest.raises(ValidationError) as exc_info:
            get_default_config(api_token="   ")
        
        assert "API token cannot be empty" in str(exc_info.value)

    def test_get_default_config_precedence(self):
        """Test that provided token takes precedence over environment."""
        env_vars = {
            "CLICKUP_API_TOKEN": "env_token",
            "CLICKUP_TIMEOUT": "60.0"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = get_default_config(api_token="provided_token")
            
            assert config.api_token == "provided_token"
            assert config.timeout == 30.0  # Default, not from env


class TestGetDefaultConfigAdvanced:
    """Advanced test cases for get_default_config function."""

    def test_get_default_config_with_unicode_token(self):
        """Test getting default config with unicode token."""
        unicode_token = "测试_token_🔑"
        config = get_default_config(api_token=unicode_token)
        
        assert config.api_token == unicode_token

    def test_get_default_config_with_long_token(self):
        """Test getting default config with very long token."""
        long_token = "a" * 10000
        config = get_default_config(api_token=long_token)
        
        assert config.api_token == long_token
        assert len(config.api_token) == 10000

    def test_get_default_config_with_special_chars_token(self):
        """Test getting default config with special characters in token."""
        special_token = "token!@#$%^&*()_+-=[]{}|;':\",./<>?"
        config = get_default_config(api_token=special_token)
        
        assert config.api_token == special_token

    def test_get_default_config_token_strips_whitespace(self):
        """Test that provided token strips whitespace."""
        config = get_default_config(api_token="  token_with_spaces  ")
        
        assert config.api_token == "token_with_spaces"

    def test_get_default_config_env_error_handling(self):
        """Test error handling when environment config loading fails."""
        env_vars = {
            "CLICKUP_API_TOKEN": "env_token",
            "CLICKUP_TIMEOUT": "invalid_float"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError) as exc_info:
                get_default_config()
            
            assert "could not convert string to float" in str(exc_info.value)

    def test_get_default_config_env_validation_error(self):
        """Test validation error when environment config is invalid."""
        env_vars = {
            "CLICKUP_API_TOKEN": "env_token",
            "CLICKUP_TIMEOUT": "-1.0"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                get_default_config()
            
            assert "Timeout must be positive" in str(exc_info.value)


class TestConfigIntegration:
    """Integration tests for configuration module."""

    def test_config_creation_and_validation_workflow(self):
        """Test complete workflow of config creation and validation."""
        # Test valid config creation
        config = ClickUpConfig(
            api_token="workflow_token",
            timeout=45.0,
            max_retries=5
        )
        
        assert config.api_token == "workflow_token"
        assert config.timeout == 45.0
        assert config.max_retries == 5
        
        # Test that config can be used in dictionary form
        config_dict = config.model_dump()
        assert config_dict["api_token"] == "workflow_token"
        assert config_dict["timeout"] == 45.0
        assert config_dict["max_retries"] == 5

    def test_env_to_config_to_usage_workflow(self):
        """Test complete workflow from environment to config to usage."""
        env_vars = {
            "CLICKUP_API_TOKEN": "integration_token",
            "CLICKUP_BASE_URL": "https://integration.test.com/v2",
            "CLICKUP_TIMEOUT": "120.0"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            # Load from environment
            config = load_config_from_env()
            
            # Verify config
            assert config.api_token == "integration_token"
            assert config.base_url == "https://integration.test.com/v2"
            assert config.timeout == 120.0
            
            # Test using config in get_default_config
            default_config = get_default_config()
            assert default_config.api_token == "integration_token"
            assert default_config.base_url == "https://integration.test.com/v2"
            assert default_config.timeout == 120.0

    def test_config_serialization_deserialization(self):
        """Test config serialization and deserialization."""
        original_config = ClickUpConfig(
            api_token="serialize_token",
            timeout=99.9,
            max_retries=7,
            retry_delay=2.5,
            rate_limit_requests_per_minute=150
        )
        
        # Serialize to dict
        config_dict = original_config.model_dump()
        
        # Deserialize from dict
        restored_config = ClickUpConfig(**config_dict)
        
        # Verify restoration
        assert restored_config.api_token == original_config.api_token
        assert restored_config.timeout == original_config.timeout
        assert restored_config.max_retries == original_config.max_retries
        assert restored_config.retry_delay == original_config.retry_delay
        assert restored_config.rate_limit_requests_per_minute == original_config.rate_limit_requests_per_minute

    def test_config_with_mock_environment_complex(self):
        """Test config with complex mock environment scenarios."""
        base_env = {
            "CLICKUP_API_TOKEN": "base_token",
            "CLICKUP_TIMEOUT": "30.0"
        }
        
        override_env = {
            "CLICKUP_API_TOKEN": "override_token",
            "CLICKUP_TIMEOUT": "60.0",
            "CLICKUP_MAX_RETRIES": "10"
        }
        
        # Test with base environment
        with patch.dict(os.environ, base_env, clear=True):
            config1 = load_config_from_env()
            assert config1.api_token == "base_token"
            assert config1.timeout == 30.0
            assert config1.max_retries == 3  # Default
        
        # Test with override environment
        with patch.dict(os.environ, override_env, clear=True):
            config2 = load_config_from_env()
            assert config2.api_token == "override_token"
            assert config2.timeout == 60.0
            assert config2.max_retries == 10

    def test_config_error_handling_comprehensive(self):
        """Test comprehensive error handling across all config functions."""
        # Test ClickUpConfig validation errors
        with pytest.raises(ValidationError):
            ClickUpConfig(api_token="")
        
        with pytest.raises(ValidationError):
            ClickUpConfig(api_token="test", timeout=0)
        
        with pytest.raises(ValidationError):
            ClickUpConfig(api_token="test", max_retries=-1)
        
        # Test load_config_from_env errors
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="CLICKUP_API_TOKEN environment variable is required"):
                load_config_from_env()
        
        with patch.dict(os.environ, {"CLICKUP_API_TOKEN": "test", "CLICKUP_TIMEOUT": "invalid"}, clear=True):
            with pytest.raises(ValueError, match="could not convert string to float"):
                load_config_from_env()
        
        # Test get_default_config errors
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="CLICKUP_API_TOKEN environment variable is required"):
                get_default_config()
        
        # Empty string is falsy, so it falls back to environment loading
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="CLICKUP_API_TOKEN environment variable is required"):
                get_default_config(api_token="")
