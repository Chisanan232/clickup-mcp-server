"""
Pytest configuration and shared fixtures for the test suite.

This module provides common fixtures and configuration used across all test modules,
including the TestSettings fixture for accessing test configuration.
"""

import pytest

from test.config import TestSettings, get_test_settings


@pytest.fixture
def test_settings() -> TestSettings:
	"""
	Pytest fixture that provides a TestSettings instance.

	This fixture loads test configuration from environment variables and .env files.
	It's available to all test modules and can be used by injecting it as a parameter
	in test functions or class methods.

	Returns:
		TestSettings instance with loaded configuration.

	Example:
		>>> def test_something(test_settings):
		...     api_token = test_settings.e2e_test_api_token
		...     team_id = test_settings.clickup_test_team_id
	"""
	return get_test_settings()
