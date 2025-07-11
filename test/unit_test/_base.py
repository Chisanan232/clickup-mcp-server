from abc import ABC
from unittest.mock import AsyncMock

import pytest

from clickup_mcp import ClickUpAPIClient


class BaseAPIClientTestSuite(ABC):

    @pytest.fixture
    def api_client(self) -> ClickUpAPIClient:
        """Create a test API client."""
        return ClickUpAPIClient(
            api_token="test_token", timeout=5.0, max_retries=3, retry_delay=0.1, rate_limit_requests_per_minute=5
        )


    @pytest.fixture
    def mock_httpx_client(self) -> AsyncMock:
        """Create a mock httpx client."""
        mock_client = AsyncMock()
        return mock_client
