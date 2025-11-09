"""
ClickUp API Client Module

This module provides a comprehensive HTTP client for interacting with the ClickUp API.
It includes authentication, error handling, rate limiting, and common API operations.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any, Generic, Type, TypeVar

import httpx
from pydantic import BaseModel, Field

from clickup_mcp.models.dto.base import BaseResponseDTO

from ._base import BaseServerFactory
from .api.space import SpaceAPI
from .api.team import TeamAPI
from .exceptions import (
    AuthenticationError,
    ClickUpAPIError,
    RateLimitError,
)

logger = logging.getLogger(__name__)

# Type variable for generic returns
T = TypeVar("T")
D = TypeVar("D", bound=BaseResponseDTO)


class APIResponse(BaseModel, Generic[T]):
    """Standard API response model with support for typed data."""

    status_code: int
    data: dict[str, Any] | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    success: bool = Field(default=True)
    error: str | None = None

    def to_domain_model(self, model_class: Type[T]) -> T:
        """
        Convert raw API response data to a domain model instance.

        Args:
            model_class: The domain model class to instantiate

        Returns:
            An instance of the specified domain model
        """
        if self.data is None:
            raise ValueError("Cannot convert empty response data to domain model")

        # Handle different response formats
        if "data" in self.data:
            # Some API endpoints nest data under a 'data' key
            model_data = self.data["data"]
        else:
            model_data = self.data

        # Create an instance of the domain model
        return model_class(**model_data)

    def to_dto(self, dto_class: Type[D]) -> D:
        """
        Convert raw API response data to a DTO instance.

        Args:
            dto_class: The DTO class to instantiate

        Returns:
            An instance of the specified DTO
        """
        if self.data is None:
            raise ValueError("Cannot convert empty response data to DTO")

        # Use the DTO's deserialize method to create the DTO instance
        return dto_class.deserialize(self.data)

    def extract_list(self, model_class: Type[T], list_key: str = "data") -> list[T]:
        """
        Extract a list of domain models from the API response.

        Args:
            model_class: The domain model class to instantiate for each item
            list_key: The key in the response data containing the list

        Returns:
            A list of domain model instances
        """
        if self.data is None:
            return []

        # Handle different response formats for lists
        if list_key in self.data:
            items = self.data[list_key]
        else:
            # Some endpoints return the list directly
            items = self.data

        if not isinstance(items, list):
            return []

        # Create a list of domain model instances
        return [model_class(**item) for item in items]

    def extract_dto_list(self, dto_class: Type[D], list_key: str = "data") -> list[D]:
        """
        Extract a list of DTOs from the API response.

        Args:
            dto_class: The DTO class to instantiate for each item
            list_key: The key in the response data containing the list

        Returns:
            A list of DTO instances
        """
        if self.data is None:
            return []

        # Handle different response formats for lists
        if list_key in self.data:
            items = self.data[list_key]
        else:
            # Some endpoints return the list directly
            items = self.data

        if not isinstance(items, list):
            return []

        # Create a list of DTO instances
        return [dto_class.deserialize({"data": item} if "id" in item else item) for item in items]


class ClickUpAPIClient:
    """
    A comprehensive HTTP client for the ClickUp API.

    This client handles authentication, rate limiting, error handling,
    and provides common methods for API interactions.
    """

    def __init__(
        self,
        api_token: str,
        base_url: str = "https://api.clickup.com/api/v2",
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        rate_limit_requests_per_minute: int = 100,
    ):
        """
        Initialize the ClickUp API client.

        Args:
            api_token: ClickUp API token for authentication
            base_url: Base URL for the ClickUp API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            retry_delay: Initial delay between retries in seconds
            rate_limit_requests_per_minute: Rate limit for API requests
        """
        self.api_token = api_token
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit = rate_limit_requests_per_minute

        # Calculate seconds between requests based on rate limit
        self._seconds_per_request = 60.0 / rate_limit_requests_per_minute

        # Track request times for rate limiting
        self._request_times: list[float] = []

        # Prepare headers
        self._headers = {
            "Authorization": api_token,
            "Content-Type": "application/json",
            "User-Agent": "ClickUp-MCP-Server/1.0",
        }

        # Create httpx client
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers=self._headers,
        )

        # Initialize API resource managers
        self.space = SpaceAPI(self)
        self.team = TeamAPI(self)

    async def __aenter__(self) -> "ClickUpAPIClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: Any | None) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def _enforce_rate_limit(self) -> None:
        """Enforce rate limiting based on requests per minute."""
        now = asyncio.get_event_loop().time()

        # Remove requests older than 1 minute
        self._request_times = [req_time for req_time in self._request_times if now - req_time < 60]

        # Check if we're at the rate limit
        if len(self._request_times) >= self.rate_limit:
            sleep_time = 60 - (now - self._request_times[0])
            if sleep_time > 0:
                logger.warning(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)

        # Add current request time
        self._request_times.append(now)

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> APIResponse:
        """
        Make an HTTP request with retry logic and error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (relative to base URL)
            params: Query parameters
            data: Request body data
            headers: Additional headers

        Returns:
            APIResponse object containing the response data

        Raises:
            ClickUpAPIError: For API-related errors
            RateLimitError: When rate limit is exceeded
            AuthenticationError: When authentication fails
        """
        await self._enforce_rate_limit()

        # Prepare request
        url = endpoint
        request_headers = self._headers.copy()
        if headers:
            request_headers.update(headers)

        json_data = json.dumps(data) if data else None

        # Retry logic
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"Making {method} request to {url} (attempt {attempt + 1})")

                response = await self._client.request(
                    method=method, url=url, params=params, content=json_data, headers=request_headers
                )

                # Helper function to safely parse JSON
                def safe_json_parse(response_obj: httpx.Response) -> dict[str, Any] | None:
                    try:
                        return response_obj.json() if response_obj.content else None
                    except json.JSONDecodeError:
                        return None

                # Handle different response status codes
                if response.status_code == 200:
                    return APIResponse(
                        status_code=response.status_code,
                        data=safe_json_parse(response),
                        headers=dict(response.headers),
                    )
                elif response.status_code == 401:
                    raise AuthenticationError(
                        "Invalid API token or insufficient permissions",
                        status_code=response.status_code,
                        response_data=safe_json_parse(response),
                    )
                elif response.status_code == 429:
                    raise RateLimitError(
                        "Rate limit exceeded",
                        status_code=response.status_code,
                        response_data=safe_json_parse(response),
                    )
                elif response.status_code >= 400:
                    error_data = safe_json_parse(response)
                    if error_data is None:
                        error_data = {}
                    error_message = error_data.get("err", f"HTTP {response.status_code} error")

                    return APIResponse(
                        status_code=response.status_code,
                        data=error_data,
                        headers=dict(response.headers),
                        success=False,
                        error=error_message,
                    )
                else:
                    return APIResponse(
                        status_code=response.status_code,
                        data=safe_json_parse(response),
                        headers=dict(response.headers),
                    )

            except httpx.HTTPError as e:
                last_exception = e
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")

                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (2**attempt))  # Exponential backoff
                continue

        # If we've exhausted all retries
        raise ClickUpAPIError(f"Request failed after {self.max_retries + 1} attempts: {last_exception}")

    async def get(
        self, endpoint: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None
    ) -> APIResponse:
        """Make a GET request."""
        return await self._make_request("GET", endpoint, params=params, headers=headers)

    async def post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> APIResponse:
        """Make a POST request."""
        return await self._make_request("POST", endpoint, params=params, data=data, headers=headers)

    async def put(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> APIResponse:
        """Make a PUT request."""
        return await self._make_request("PUT", endpoint, params=params, data=data, headers=headers)

    async def delete(
        self, endpoint: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None
    ) -> APIResponse:
        """Make a DELETE request."""
        return await self._make_request("DELETE", endpoint, params=params, headers=headers)

    async def patch(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> APIResponse:
        """Make a PATCH request."""
        return await self._make_request("PATCH", endpoint, params=params, data=data, headers=headers)


def get_api_token(config=None) -> str:
    """
    Get the ClickUp API token from CLI options or environment variables.

    Args:
        config: Optional ServerConfig instance containing CLI options

    Returns:
        The API token if found

    Raises:
        ValueError: If API token cannot be found
    """
    # First check if token is provided directly via CLI option
    if config and config.token:
        return config.token

    # Otherwise get token from environment (env file should be loaded at entry point)
    token = os.environ.get("E2E_TEST_API_TOKEN")

    # Raise error if we don't have a token
    if not token:
        raise ValueError(
            "ClickUp API token not found. Please set the E2E_TEST_API_TOKEN environment variable "
            "in your .env file, or provide it using the --token command line option."
        )

    return token


_CLICKUP_API_CLIENT: ClickUpAPIClient | None = None


class ClickUpAPIClientFactory(BaseServerFactory):
    @staticmethod
    def create(  # type: ignore[override]
        api_token: str,
        base_url: str = "https://api.clickup.com/api/v2",
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        rate_limit_requests_per_minute: int = 100,
    ) -> ClickUpAPIClient:
        """
        Create and configure a ClickUp API client.

        Args:
            api_token: ClickUp API token
            base_url: Base URL for the ClickUp API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            retry_delay: Delay between retries in seconds
            rate_limit_requests_per_minute: Maximum requests per minute

        Returns:
            Configured ClickUpAPIClient instance
        """
        global _CLICKUP_API_CLIENT
        assert _CLICKUP_API_CLIENT is None, "It is not allowed to create more than one instance of ClickUp API client."
        _CLICKUP_API_CLIENT = ClickUpAPIClient(
            api_token=api_token,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            rate_limit_requests_per_minute=rate_limit_requests_per_minute,
        )
        return _CLICKUP_API_CLIENT

    @staticmethod
    def get() -> ClickUpAPIClient:
        """
        Get the MCP server instance

        Returns:
            Configured FastMCP server instance
        """
        assert _CLICKUP_API_CLIENT is not None, "It must be created ClickUp API client first."
        return _CLICKUP_API_CLIENT

    @staticmethod
    def reset() -> None:
        """
        Reset the singleton instance (for testing purposes).
        """
        global _CLICKUP_API_CLIENT
        _CLICKUP_API_CLIENT = None


clickup_api_client_factory = ClickUpAPIClientFactory
