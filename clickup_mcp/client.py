"""
ClickUp API Client Module

This module provides a comprehensive HTTP client for interacting with the ClickUp API.
It includes authentication, error handling, rate limiting, and common API operations.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field

from .exceptions import (
    AuthenticationError,
    ClickUpAPIError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class APIResponse(BaseModel):
    """Standard API response model."""

    status_code: int
    data: Optional[Dict[str, Any]] = None
    headers: Dict[str, str] = Field(default_factory=dict)
    success: bool = Field(default=True)
    error: Optional[str] = None


class ClickUpAPIClient:
    """
    A comprehensive HTTP client for the ClickUp API.

    This client handles authentication, rate limiting, error handling,
    and provides common methods for API interactions.
    """

    BASE_URL = "https://api.clickup.com/api/v2"

    def __init__(
        self,
        api_token: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        rate_limit_requests_per_minute: int = 100,
    ):
        """
        Initialize the ClickUp API client.

        Args:
            api_token: ClickUp API token for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            retry_delay: Delay between retries in seconds
            rate_limit_requests_per_minute: Rate limit for API requests
        """
        self.api_token = api_token
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit = rate_limit_requests_per_minute

        # Rate limiting
        self._request_times: List[float] = []
        self._rate_limit_lock = asyncio.Lock()

        # HTTP client configuration
        self._headers = {
            "Authorization": api_token,
            "Content-Type": "application/json",
            "User-Agent": "ClickUp-MCP-Server/1.0",
        }

        self._client = httpx.AsyncClient(base_url=self.BASE_URL, headers=self._headers, timeout=self.timeout)

    async def __aenter__(self) -> "ClickUpAPIClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()

    async def _enforce_rate_limit(self) -> None:
        """Enforce rate limiting based on requests per minute."""
        async with self._rate_limit_lock:
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
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
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
        url = endpoint if endpoint.startswith("http") else endpoint
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
                def safe_json_parse(response_obj):
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
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """Make a GET request."""
        return await self._make_request("GET", endpoint, params=params, headers=headers)

    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> APIResponse:
        """Make a POST request."""
        return await self._make_request("POST", endpoint, params=params, data=data, headers=headers)

    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> APIResponse:
        """Make a PUT request."""
        return await self._make_request("PUT", endpoint, params=params, data=data, headers=headers)

    async def delete(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """Make a DELETE request."""
        return await self._make_request("DELETE", endpoint, params=params, headers=headers)

    async def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> APIResponse:
        """Make a PATCH request."""
        return await self._make_request("PATCH", endpoint, params=params, data=data, headers=headers)


# Convenience function to create a configured client
def create_clickup_client(api_token: str, **kwargs) -> ClickUpAPIClient:
    """
    Create a ClickUp API client with the provided token and optional configuration.

    Args:
        api_token: ClickUp API token
        **kwargs: Additional configuration options for the client

    Returns:
        Configured ClickUpAPIClient instance
    """
    return ClickUpAPIClient(api_token=api_token, **kwargs)
