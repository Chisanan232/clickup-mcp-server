"""
ClickUp API Client Module

This module provides a comprehensive HTTP client for interacting with the ClickUp API.
It includes authentication, error handling, rate limiting, and common API operations.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class ClickUpAPIError(Exception):
    """Base exception for ClickUp API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class RateLimitError(ClickUpAPIError):
    """Exception raised when API rate limit is exceeded."""
    pass


class AuthenticationError(ClickUpAPIError):
    """Exception raised when authentication fails."""
    pass


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
        rate_limit_requests_per_minute: int = 100
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
            "User-Agent": "ClickUp-MCP-Server/1.0"
        }
        
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=self._headers,
            timeout=self.timeout
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
    
    async def _enforce_rate_limit(self):
        """Enforce rate limiting based on requests per minute."""
        async with self._rate_limit_lock:
            now = asyncio.get_event_loop().time()
            
            # Remove requests older than 1 minute
            self._request_times = [
                req_time for req_time in self._request_times 
                if now - req_time < 60
            ]
            
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
        headers: Optional[Dict[str, str]] = None
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
        url = endpoint if endpoint.startswith('http') else endpoint
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
                    method=method,
                    url=url,
                    params=params,
                    content=json_data,
                    headers=request_headers
                )
                
                # Handle different response status codes
                if response.status_code == 200:
                    return APIResponse(
                        status_code=response.status_code,
                        data=response.json() if response.content else None,
                        headers=dict(response.headers)
                    )
                elif response.status_code == 401:
                    raise AuthenticationError(
                        "Invalid API token or insufficient permissions",
                        status_code=response.status_code,
                        response_data=response.json() if response.content else None
                    )
                elif response.status_code == 429:
                    raise RateLimitError(
                        "Rate limit exceeded",
                        status_code=response.status_code,
                        response_data=response.json() if response.content else None
                    )
                elif response.status_code >= 400:
                    error_data = response.json() if response.content else {}
                    error_message = error_data.get('err', f'HTTP {response.status_code} error')
                    
                    return APIResponse(
                        status_code=response.status_code,
                        data=error_data,
                        headers=dict(response.headers),
                        success=False,
                        error=error_message
                    )
                else:
                    return APIResponse(
                        status_code=response.status_code,
                        data=response.json() if response.content else None,
                        headers=dict(response.headers)
                    )
                    
            except httpx.HTTPError as e:
                last_exception = e
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                continue
        
        # If we've exhausted all retries
        raise ClickUpAPIError(f"Request failed after {self.max_retries + 1} attempts: {last_exception}")
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """Make a GET request."""
        return await self._make_request("GET", endpoint, params=params, headers=headers)
    
    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """Make a POST request."""
        return await self._make_request("POST", endpoint, params=params, data=data, headers=headers)
    
    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """Make a PUT request."""
        return await self._make_request("PUT", endpoint, params=params, data=data, headers=headers)
    
    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """Make a DELETE request."""
        return await self._make_request("DELETE", endpoint, params=params, headers=headers)
    
    async def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """Make a PATCH request."""
        return await self._make_request("PATCH", endpoint, params=params, data=data, headers=headers)


class ClickUpResourceClient:
    """
    High-level client for specific ClickUp resources.
    
    This class provides convenient methods for common ClickUp operations
    like managing teams, spaces, folders, lists, and tasks.
    """
    
    def __init__(self, api_client: ClickUpAPIClient):
        """Initialize with an API client instance."""
        self.client = api_client
    
    # Team operations
    async def get_teams(self) -> APIResponse:
        """Get all teams for the authenticated user."""
        return await self.client.get("/team")
    
    async def get_team(self, team_id: str) -> APIResponse:
        """Get a specific team by ID."""
        return await self.client.get(f"/team/{team_id}")
    
    # Space operations
    async def get_spaces(self, team_id: str) -> APIResponse:
        """Get all spaces in a team."""
        return await self.client.get(f"/team/{team_id}/space")
    
    async def get_space(self, space_id: str) -> APIResponse:
        """Get a specific space by ID."""
        return await self.client.get(f"/space/{space_id}")
    
    async def create_space(self, team_id: str, name: str, **kwargs) -> APIResponse:
        """Create a new space in a team."""
        data = {"name": name, **kwargs}
        return await self.client.post(f"/team/{team_id}/space", data=data)
    
    # Folder operations
    async def get_folders(self, space_id: str) -> APIResponse:
        """Get all folders in a space."""
        return await self.client.get(f"/space/{space_id}/folder")
    
    async def get_folder(self, folder_id: str) -> APIResponse:
        """Get a specific folder by ID."""
        return await self.client.get(f"/folder/{folder_id}")
    
    async def create_folder(self, space_id: str, name: str) -> APIResponse:
        """Create a new folder in a space."""
        data = {"name": name}
        return await self.client.post(f"/space/{space_id}/folder", data=data)
    
    # List operations
    async def get_lists(self, folder_id: Optional[str] = None, space_id: Optional[str] = None) -> APIResponse:
        """Get lists from a folder or space."""
        if folder_id:
            return await self.client.get(f"/folder/{folder_id}/list")
        elif space_id:
            return await self.client.get(f"/space/{space_id}/list")
        else:
            raise ValueError("Either folder_id or space_id must be provided")
    
    async def get_list(self, list_id: str) -> APIResponse:
        """Get a specific list by ID."""
        return await self.client.get(f"/list/{list_id}")
    
    async def create_list(
        self,
        name: str,
        folder_id: Optional[str] = None,
        space_id: Optional[str] = None,
        **kwargs
    ) -> APIResponse:
        """Create a new list in a folder or space."""
        data = {"name": name, **kwargs}
        
        if folder_id:
            return await self.client.post(f"/folder/{folder_id}/list", data=data)
        elif space_id:
            return await self.client.post(f"/space/{space_id}/list", data=data)
        else:
            raise ValueError("Either folder_id or space_id must be provided")
    
    # Task operations
    async def get_tasks(
        self,
        list_id: str,
        page: int = 0,
        order_by: str = "created",
        reverse: bool = False,
        subtasks: bool = False,
        statuses: Optional[List[str]] = None,
        include_closed: bool = False,
        assignees: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        due_date_gt: Optional[int] = None,
        due_date_lt: Optional[int] = None,
        date_created_gt: Optional[int] = None,
        date_created_lt: Optional[int] = None,
        date_updated_gt: Optional[int] = None,
        date_updated_lt: Optional[int] = None,
        custom_fields: Optional[List[Dict]] = None
    ) -> APIResponse:
        """Get tasks from a list with optional filtering."""
        params = {
            "page": page,
            "order_by": order_by,
            "reverse": reverse,
            "subtasks": subtasks,
            "include_closed": include_closed
        }
        
        # Add optional parameters if provided
        if statuses:
            params["statuses[]"] = statuses
        if assignees:
            params["assignees[]"] = assignees
        if tags:
            params["tags[]"] = tags
        if due_date_gt is not None:
            params["due_date_gt"] = due_date_gt
        if due_date_lt is not None:
            params["due_date_lt"] = due_date_lt
        if date_created_gt is not None:
            params["date_created_gt"] = date_created_gt
        if date_created_lt is not None:
            params["date_created_lt"] = date_created_lt
        if date_updated_gt is not None:
            params["date_updated_gt"] = date_updated_gt
        if date_updated_lt is not None:
            params["date_updated_lt"] = date_updated_lt
        if custom_fields:
            params["custom_fields"] = custom_fields
        
        return await self.client.get(f"/list/{list_id}/task", params=params)
    
    async def get_task(self, task_id: str, custom_task_ids: bool = False, team_id: Optional[str] = None) -> APIResponse:
        """Get a specific task by ID."""
        params = {"custom_task_ids": custom_task_ids}
        if team_id:
            params["team_id"] = team_id
        
        return await self.client.get(f"/task/{task_id}", params=params)
    
    async def create_task(
        self,
        list_id: str,
        name: str,
        description: Optional[str] = None,
        assignees: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        status: Optional[str] = None,
        priority: Optional[int] = None,
        due_date: Optional[int] = None,
        due_date_time: Optional[bool] = False,
        time_estimate: Optional[int] = None,
        start_date: Optional[int] = None,
        start_date_time: Optional[bool] = False,
        notify_all: Optional[bool] = True,
        parent: Optional[str] = None,
        links_to: Optional[str] = None,
        check_required_custom_fields: Optional[bool] = True,
        custom_fields: Optional[List[Dict]] = None
    ) -> APIResponse:
        """Create a new task in a list."""
        data = {
            "name": name,
            "notify_all": notify_all,
            "check_required_custom_fields": check_required_custom_fields
        }
        
        # Add optional fields if provided
        if description:
            data["description"] = description
        if assignees:
            data["assignees"] = assignees
        if tags:
            data["tags"] = tags
        if status:
            data["status"] = status
        if priority is not None:
            data["priority"] = priority
        if due_date:
            data["due_date"] = due_date
            data["due_date_time"] = due_date_time
        if time_estimate:
            data["time_estimate"] = time_estimate
        if start_date:
            data["start_date"] = start_date
            data["start_date_time"] = start_date_time
        if parent:
            data["parent"] = parent
        if links_to:
            data["links_to"] = links_to
        if custom_fields:
            data["custom_fields"] = custom_fields
        
        return await self.client.post(f"/list/{list_id}/task", data=data)
    
    async def update_task(self, task_id: str, **kwargs) -> APIResponse:
        """Update a task with the provided fields."""
        return await self.client.put(f"/task/{task_id}", data=kwargs)
    
    async def delete_task(self, task_id: str, custom_task_ids: bool = False, team_id: Optional[str] = None) -> APIResponse:
        """Delete a task by ID."""
        params = {"custom_task_ids": custom_task_ids}
        if team_id:
            params["team_id"] = team_id
        
        return await self.client.delete(f"/task/{task_id}", params=params)
    
    # User operations
    async def get_user(self) -> APIResponse:
        """Get the authenticated user's information."""
        return await self.client.get("/user")
    
    async def get_team_members(self, team_id: str) -> APIResponse:
        """Get all members of a team."""
        return await self.client.get(f"/team/{team_id}/member")


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


# Convenience function to create a resource client
def create_resource_client(api_token: str, **kwargs) -> ClickUpResourceClient:
    """
    Create a ClickUp resource client with the provided token and optional configuration.
    
    Args:
        api_token: ClickUp API token
        **kwargs: Additional configuration options for the underlying API client
        
    Returns:
        Configured ClickUpResourceClient instance
    """
    api_client = create_clickup_client(api_token, **kwargs)
    return ClickUpResourceClient(api_client)
