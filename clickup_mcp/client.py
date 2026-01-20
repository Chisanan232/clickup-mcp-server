"""
ClickUp API Client Module

This module provides a comprehensive HTTP client for interacting with the ClickUp API.
It includes authentication, error handling, rate limiting, and common API operations.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Generic, Type, TypeVar

import httpx
from pydantic import BaseModel, Field

from ._base import BaseServerFactory
from .api.folder import FolderAPI
from .api.list import ListAPI
from .api.space import SpaceAPI
from .api.task import TaskAPI
from .api.team import TeamAPI
from .config import get_settings
from .exceptions import (
    AuthenticationError,
    ClickUpAPIError,
    RateLimitError,
)
from .models.cli import ServerConfig
from .models.dto.base import BaseResponseDTO
from .types import ClickUpClientProtocol, ClickUpToken

logger = logging.getLogger(__name__)

# Type variable for generic returns
T = TypeVar("T")
D = TypeVar("D", bound=BaseResponseDTO)


class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response model with support for typed data.

    This model encapsulates HTTP responses from the ClickUp API, providing
    a consistent interface for handling both successful and failed requests.
    It supports conversion to domain models and DTOs for type-safe handling.

    Attributes:
        status_code: HTTP status code of the response
        data: Response body data as a dictionary, or None if empty
        headers: Response headers as key-value pairs
        success: Boolean indicating if the request was successful
        error: Error message if the request failed, None otherwise

    Usage Examples:
        # Using with domain models
        response = await client.get("/team/123/space")
        spaces = response.extract_list(ClickUpSpace)

        # Using with DTOs
        response = await client.get("/team/123/space")
        space_dtos = response.extract_dto_list(SpaceResp)

        # Converting to a single domain model
        response = await client.get("/space/456")
        space = response.to_domain_model(ClickUpSpace)
    """

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


class ClickUpAPIClient(ClickUpClientProtocol):
    """
    A comprehensive HTTP client for the ClickUp API.

    This client handles authentication, rate limiting, error handling,
    and provides common methods for API interactions. It supports async/await
    patterns and includes automatic retry logic with exponential backoff.

    The client is organized into resource managers (space, team, folder, list, task)
    for domain-specific operations, following the Resource Manager pattern.

    Attributes:
        space: SpaceAPI resource manager for space operations
        team: TeamAPI resource manager for team operations
        folder: FolderAPI resource manager for folder operations
        list: ListAPI resource manager for list operations
        task: TaskAPI resource manager for task operations

    Usage Examples:
        # Python - Basic usage with context manager
        async with ClickUpAPIClient(api_token="pk_...") as client:
            response = await client.get("/team/123/space")
            spaces = response.extract_list(ClickUpSpace)

        # Python - Using resource managers
        async with ClickUpAPIClient(api_token="pk_...") as client:
            spaces = await client.space.get_all(team_id="123")
            tasks = await client.task.get_all(list_id="456")

        # Python - Custom configuration
        client = ClickUpAPIClient(
            api_token="pk_...",
            timeout=60.0,
            max_retries=5,
            rate_limit_requests_per_minute=50
        )
    """

    def __init__(
        self,
        api_token: ClickUpToken,
        base_url: str = "https://api.clickup.com/api/v2",
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        rate_limit_requests_per_minute: int = 100,
    ):
        """
        Initialize the ClickUp API client.

        Creates a new ClickUp API client with the specified configuration.
        The client uses httpx for async HTTP requests and implements automatic
        rate limiting and retry logic.

        Args:
            api_token: ClickUp API token for authentication (required)
            base_url: Base URL for the ClickUp API (default: https://api.clickup.com/api/v2)
            timeout: Request timeout in seconds (default: 30.0)
            max_retries: Maximum number of retries for failed requests (default: 3)
            retry_delay: Initial delay between retries in seconds (default: 1.0)
            rate_limit_requests_per_minute: Rate limit for API requests (default: 100)

        Usage Examples:
            # Python - Create with default settings
            client = ClickUpAPIClient(api_token="pk_...")

            # Python - Create with custom configuration
            client = ClickUpAPIClient(
                api_token="pk_...",
                timeout=60.0,
                max_retries=5,
                retry_delay=2.0,
                rate_limit_requests_per_minute=50
            )

            # Python - Use as async context manager
            async with ClickUpAPIClient(api_token="pk_...") as client:
                response = await client.get("/team/123/space")
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
        self.folder = FolderAPI(self)
        self.list = ListAPI(self)
        self.task = TaskAPI(self)

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

                    # Log error details for visibility into API failures
                    logger.error(
                        "API error %s %s -> %s: %s; response=%s",
                        method,
                        url,
                        response.status_code,
                        error_message,
                        error_data,
                    )

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

        # If we've exhausted all retries, log at error level then raise
        logger.error(
            "Request failed after %s attempts for %s %s: %s",
            self.max_retries + 1,
            method,
            url,
            last_exception,
        )
        raise ClickUpAPIError(f"Request failed after {self.max_retries + 1} attempts: {last_exception}")

    async def get(
        self, endpoint: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None
    ) -> APIResponse:
        """
        Make a GET request to the ClickUp API.

        Retrieves data from the specified endpoint with optional query parameters.
        Automatically handles rate limiting, retries, and error handling.

        Args:
            endpoint: API endpoint path (e.g., "/team/123/space")
            params: Query parameters to include in the request
            headers: Additional HTTP headers to include

        Returns:
            APIResponse containing the response data and metadata

        Raises:
            AuthenticationError: If the API token is invalid
            RateLimitError: If the API rate limit is exceeded
            ClickUpAPIError: For other API-related errors

        Usage Examples:
            # Python - Get all spaces in a team
            async with ClickUpAPIClient(api_token="pk_...") as client:
                response = await client.get("/team/123/space")
                spaces = response.extract_list(ClickUpSpace)

            # curl - Get all spaces
            curl -H "Authorization: pk_..." \\
                 https://api.clickup.com/api/v2/team/123/space

            # wget - Get all spaces
            wget --header="Authorization: pk_..." \\
                 https://api.clickup.com/api/v2/team/123/space
        """
        return await self._make_request("GET", endpoint, params=params, headers=headers)

    async def post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> APIResponse:
        """
        Make a POST request to the ClickUp API.

        Creates a new resource at the specified endpoint with the provided data.
        Automatically handles rate limiting, retries, and error handling.

        Args:
            endpoint: API endpoint path (e.g., "/team/123/space")
            data: Request body data as a dictionary
            params: Query parameters to include in the request
            headers: Additional HTTP headers to include

        Returns:
            APIResponse containing the created resource data

        Raises:
            AuthenticationError: If the API token is invalid
            RateLimitError: If the API rate limit is exceeded
            ClickUpAPIError: For other API-related errors

        Usage Examples:
            # Python - Create a new space
            async with ClickUpAPIClient(api_token="pk_...") as client:
                response = await client.post(
                    "/team/123/space",
                    data={"name": "New Space"}
                )
                space = response.to_domain_model(ClickUpSpace)

            # curl - Create a new space
            curl -X POST \\
                 -H "Authorization: pk_..." \\
                 -H "Content-Type: application/json" \\
                 -d '{"name": "New Space"}' \\
                 https://api.clickup.com/api/v2/team/123/space

            # wget - Create a new space
            wget --method=POST \\
                 --header="Authorization: pk_..." \\
                 --header="Content-Type: application/json" \\
                 --body-data='{"name": "New Space"}' \\
                 https://api.clickup.com/api/v2/team/123/space
        """
        return await self._make_request("POST", endpoint, params=params, data=data, headers=headers)

    async def put(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> APIResponse:
        """
        Make a PUT request to the ClickUp API.

        Replaces an entire resource at the specified endpoint with the provided data.
        Automatically handles rate limiting, retries, and error handling.

        Args:
            endpoint: API endpoint path (e.g., "/space/456")
            data: Request body data as a dictionary (replaces entire resource)
            params: Query parameters to include in the request
            headers: Additional HTTP headers to include

        Returns:
            APIResponse containing the updated resource data

        Raises:
            AuthenticationError: If the API token is invalid
            RateLimitError: If the API rate limit is exceeded
            ClickUpAPIError: For other API-related errors

        Usage Examples:
            # Python - Update a space (full replacement)
            async with ClickUpAPIClient(api_token="pk_...") as client:
                response = await client.put(
                    "/space/456",
                    data={"name": "Updated Space", "color": "#FF0000"}
                )
                space = response.to_domain_model(ClickUpSpace)

            # curl - Update a space
            curl -X PUT \\
                 -H "Authorization: pk_..." \\
                 -H "Content-Type: application/json" \\
                 -d '{"name": "Updated Space", "color": "#FF0000"}' \\
                 https://api.clickup.com/api/v2/space/456

            # wget - Update a space
            wget --method=PUT \\
                 --header="Authorization: pk_..." \\
                 --header="Content-Type: application/json" \\
                 --body-data='{"name": "Updated Space"}' \\
                 https://api.clickup.com/api/v2/space/456
        """
        return await self._make_request("PUT", endpoint, params=params, data=data, headers=headers)

    async def delete(
        self, endpoint: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None
    ) -> APIResponse:
        """
        Make a DELETE request to the ClickUp API.

        Deletes a resource at the specified endpoint.
        Automatically handles rate limiting, retries, and error handling.

        Args:
            endpoint: API endpoint path (e.g., "/space/456")
            params: Query parameters to include in the request
            headers: Additional HTTP headers to include

        Returns:
            APIResponse with deletion confirmation

        Raises:
            AuthenticationError: If the API token is invalid
            RateLimitError: If the API rate limit is exceeded
            ClickUpAPIError: For other API-related errors

        Usage Examples:
            # Python - Delete a space
            async with ClickUpAPIClient(api_token="pk_...") as client:
                response = await client.delete("/space/456")
                if response.success:
                    print("Space deleted successfully")

            # curl - Delete a space
            curl -X DELETE \\
                 -H "Authorization: pk_..." \\
                 https://api.clickup.com/api/v2/space/456

            # wget - Delete a space
            wget --method=DELETE \\
                 --header="Authorization: pk_..." \\
                 https://api.clickup.com/api/v2/space/456
        """
        return await self._make_request("DELETE", endpoint, params=params, headers=headers)

    async def patch(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> APIResponse:
        """
        Make a PATCH request to the ClickUp API.

        Partially updates a resource at the specified endpoint.
        Only the provided fields are updated; other fields remain unchanged.
        Automatically handles rate limiting, retries, and error handling.

        Args:
            endpoint: API endpoint path (e.g., "/space/456")
            data: Request body data with fields to update
            params: Query parameters to include in the request
            headers: Additional HTTP headers to include

        Returns:
            APIResponse containing the updated resource data

        Raises:
            AuthenticationError: If the API token is invalid
            RateLimitError: If the API rate limit is exceeded
            ClickUpAPIError: For other API-related errors

        Usage Examples:
            # Python - Partially update a space (only name)
            async with ClickUpAPIClient(api_token="pk_...") as client:
                response = await client.patch(
                    "/space/456",
                    data={"name": "New Name"}
                )
                space = response.to_domain_model(ClickUpSpace)

            # curl - Partially update a space
            curl -X PATCH \\
                 -H "Authorization: pk_..." \\
                 -H "Content-Type: application/json" \\
                 -d '{"name": "New Name"}' \\
                 https://api.clickup.com/api/v2/space/456

            # wget - Partially update a space
            wget --method=PATCH \\
                 --header="Authorization: pk_..." \\
                 --header="Content-Type: application/json" \\
                 --body-data='{"name": "New Name"}' \\
                 https://api.clickup.com/api/v2/space/456
        """
        return await self._make_request("PATCH", endpoint, params=params, data=data, headers=headers)


def get_api_token(config: ServerConfig | None = None) -> str:
    """
    Get the ClickUp API token from CLI options or environment variables.

    This function implements a precedence-based token resolution strategy:
    1. CLI token (if provided via --token option)
    2. Environment variable CLICKUP_API_TOKEN (via BaseSettings)
    3. Fallback environment variable E2E_TEST_API_TOKEN (for testing)

    The function uses pydantic-settings for robust environment configuration.

    Args:
        config: Optional ServerConfig instance containing CLI options and env_file path

    Returns:
        The ClickUp API token string

    Raises:
        ValueError: If API token cannot be found in any location

    Usage Examples:
        # Python - Get token from environment
        token = get_api_token()

        # Python - Get token from CLI config
        config = ServerConfig(token="pk_...", env_file=".env")
        token = get_api_token(config)

        # Environment setup
        export CLICKUP_API_TOKEN="pk_your_token_here"

        # Or in .env file
        CLICKUP_API_TOKEN=pk_your_token_here
    """
    # 1. CLI token overrides everything if provided
    if config and config.token:
        return config.token

    # 2. Get settings (handles .env file loading if configured)
    env_file = config.env_file if config else None
    settings = get_settings(env_file)

    # 3. Try primary token
    if settings.clickup_api_token:
        return settings.clickup_api_token.get_secret_value()

    # Raise error if we don't have a token
    raise ValueError(
        "ClickUp API token not found. Set CLICKUP_API_TOKEN in your .env/environment, "
        "or provide it using the --token option."
    )


_CLICKUP_API_CLIENT: ClickUpAPIClient | None = None


class ClickUpAPIClientFactory(BaseServerFactory):
    """
    Factory for creating and managing ClickUp API client instances.

    This factory implements the singleton pattern to ensure only one
    ClickUpAPIClient instance exists throughout the application lifecycle.
    It provides methods for creating, retrieving, and resetting the client.

    Usage Examples:
        # Python - Create and use the client
        from clickup_mcp import ClickUpAPIClientFactory

        client = ClickUpAPIClientFactory.create(api_token="pk_...")
        response = await client.get("/team/123/space")

        # Get existing client
        client = ClickUpAPIClientFactory.get()

        # Reset for testing
        ClickUpAPIClientFactory.reset()
    """

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
        Create and configure a ClickUp API client singleton instance.

        This method creates a new ClickUpAPIClient with the specified configuration.
        Subsequent calls will raise an assertion error to prevent multiple instances.
        Use reset() to clear the singleton before creating a new instance.

        Args:
            api_token: ClickUp API token for authentication (required)
            base_url: Base URL for the ClickUp API (default: https://api.clickup.com/api/v2)
            timeout: Request timeout in seconds (default: 30.0)
            max_retries: Maximum number of retries for failed requests (default: 3)
            retry_delay: Initial delay between retries in seconds (default: 1.0)
            rate_limit_requests_per_minute: Maximum requests per minute (default: 100)

        Returns:
            Configured ClickUpAPIClient instance

        Raises:
            AssertionError: If a client instance already exists

        Usage Examples:
            # Python - Create with default settings
            client = ClickUpAPIClientFactory.create(api_token="pk_...")

            # Python - Create with custom timeout and retries
            client = ClickUpAPIClientFactory.create(
                api_token="pk_...",
                timeout=60.0,
                max_retries=5,
                rate_limit_requests_per_minute=50
            )
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
        Get the existing ClickUp API client singleton instance.

        Returns the previously created client instance. Raises an assertion
        error if no client has been created yet. Use create() to initialize
        the client before calling this method.

        Returns:
            Configured ClickUpAPIClient instance

        Raises:
            AssertionError: If the client has not been created yet

        Usage Examples:
            # Python - Get existing client
            client = ClickUpAPIClientFactory.get()
            response = await client.get("/team/123/space")
        """
        assert _CLICKUP_API_CLIENT is not None, "It must be created ClickUp API client first."
        return _CLICKUP_API_CLIENT

    @staticmethod
    def reset() -> None:
        """
        Reset the singleton instance to None.

        This method clears the cached client instance, allowing a new one
        to be created. Primarily used for testing and in scenarios where
        you need to reinitialize the client with different configuration.

        Usage Examples:
            # Python - Reset for testing
            ClickUpAPIClientFactory.reset()
            client = ClickUpAPIClientFactory.create(api_token="pk_new_token")
        """
        global _CLICKUP_API_CLIENT
        _CLICKUP_API_CLIENT = None


clickup_api_client_factory = ClickUpAPIClientFactory
