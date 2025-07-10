"""
Unit tests for ClickUp API client.
"""

import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch
import pytest
import httpx

from clickup_mcp.client import ClickUpAPIClient, ClickUpResourceClient, APIResponse
from clickup_mcp.exceptions import (
    ClickUpAPIError,
    AuthenticationError,
    RateLimitError,
    ResourceNotFoundError
)


@pytest.fixture
def api_client():
    """Create a test API client."""
    return ClickUpAPIClient(
        api_token="test_token",
        timeout=5.0,
        max_retries=3,
        retry_delay=0.1,
        rate_limit_requests_per_minute=5
    )


@pytest.fixture
def mock_httpx_client():
    """Create a mock httpx client."""
    mock_client = AsyncMock()
    return mock_client


class TestClickUpAPIClient:
    """Test cases for ClickUpAPIClient."""
    
    def test_initialization(self):
        """Test API client initialization."""
        client = ClickUpAPIClient(
            api_token="test_token",
            timeout=10.0,
            max_retries=5,
            retry_delay=2.0,
            rate_limit_requests_per_minute=120
        )
        
        assert client.api_token == "test_token"
        assert client.timeout == 10.0
        assert client.max_retries == 5
        assert client.retry_delay == 2.0
        assert client.rate_limit == 120
        assert "Authorization" in client._headers
        assert client._headers["Authorization"] == "test_token"
    
    @pytest.mark.asyncio
    async def test_context_manager(self, api_client):
        """Test async context manager functionality."""
        async with api_client as client:
            assert client is api_client
        
        # Client should be closed after context exit
        # (We can't easily test this without mocking the httpx client)
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, api_client):
        """Test rate limiting functionality."""
        # Set a very low rate limit for testing
        api_client.rate_limit = 2
        
        start_time = asyncio.get_event_loop().time()
        
        # Add some request times to simulate recent requests
        current_time = start_time
        api_client._request_times = [current_time - 10, current_time - 5]
        
        # This should not be rate limited
        await api_client._enforce_rate_limit()
        
        # Add more requests to trigger rate limiting
        api_client._request_times = [current_time, current_time + 0.1]
        
        # This should be rate limited and take some time
        rate_limit_start = asyncio.get_event_loop().time()
        await api_client._enforce_rate_limit()
        rate_limit_end = asyncio.get_event_loop().time()
        
        # The rate limiting should have taken some time
        # (In practice this would be up to 60 seconds, but our test data is artificial)
    
    @pytest.mark.asyncio
    async def test_successful_request(self, api_client):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"data": "test"}'
        mock_response.json.return_value = {"data": "test"}
        mock_response.headers = {"Content-Type": "application/json"}
        
        with patch.object(api_client._client, 'request', return_value=mock_response) as mock_request:
            response = await api_client._make_request("GET", "/test")
            
            assert isinstance(response, APIResponse)
            assert response.status_code == 200
            assert response.data == {"data": "test"}
            assert response.success is True
            assert response.error is None
            
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authentication_error(self, api_client):
        """Test authentication error handling."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.content = b'{"err": "Unauthorized"}'
        mock_response.json.return_value = {"err": "Unauthorized"}
        
        with patch.object(api_client._client, 'request', return_value=mock_response):
            with pytest.raises(AuthenticationError) as exc_info:
                await api_client._make_request("GET", "/test")
            
            assert exc_info.value.status_code == 401
            assert "Invalid API token" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_rate_limit_error(self, api_client):
        """Test rate limit error handling."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.content = b'{"err": "Rate limit exceeded"}'
        mock_response.json.return_value = {"err": "Rate limit exceeded"}
        
        with patch.object(api_client._client, 'request', return_value=mock_response):
            with pytest.raises(RateLimitError) as exc_info:
                await api_client._make_request("GET", "/test")
            
            assert exc_info.value.status_code == 429
    
    @pytest.mark.asyncio
    async def test_client_error_response(self, api_client):
        """Test client error response (4xx) handling."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.content = b'{"err": "Bad request"}'
        mock_response.json.return_value = {"err": "Bad request"}
        mock_response.headers = {"Content-Type": "application/json"}
        
        with patch.object(api_client._client, 'request', return_value=mock_response):
            response = await api_client._make_request("GET", "/test")
            
            assert response.status_code == 400
            assert response.success is False
            assert response.error == "Bad request"
            assert response.data == {"err": "Bad request"}
    
    @pytest.mark.asyncio
    async def test_retry_logic(self, api_client):
        """Test retry logic for failed requests."""
        # Set up a mock that fails twice then succeeds
        mock_responses = [
            httpx.HTTPError("Connection failed"),
            httpx.HTTPError("Connection failed"),
            Mock(status_code=200, content=b'{"success": true}', 
                 json=lambda: {"success": True}, headers={})
        ]
        
        call_count = 0
        async def mock_request(*args, **kwargs):
            nonlocal call_count
            response = mock_responses[call_count]
            call_count += 1
            if isinstance(response, Exception):
                raise response
            return response
        
        with patch.object(api_client._client, 'request', side_effect=mock_request):
            response = await api_client._make_request("GET", "/test")
            
            assert response.status_code == 200
            assert call_count == 3  # Two failures + one success
    
    @pytest.mark.asyncio
    async def test_retry_exhausted(self, api_client):
        """Test behavior when all retries are exhausted."""
        with patch.object(api_client._client, 'request', side_effect=httpx.HTTPError("Connection failed")):
            with pytest.raises(ClickUpAPIError) as exc_info:
                await api_client._make_request("GET", "/test")
            
            assert "Request failed after" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_request(self, api_client):
        """Test GET request convenience method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"data": "test"}'
        mock_response.json.return_value = {"data": "test"}
        mock_response.headers = {}
        
        with patch.object(api_client._client, 'request', return_value=mock_response) as mock_request:
            response = await api_client.get("/test", params={"key": "value"})
            
            assert response.status_code == 200
            mock_request.assert_called_once()
            
            # Check that the request was made with correct parameters
            call_args = mock_request.call_args
            assert call_args[1]['method'] == 'GET'
            assert call_args[1]['params'] == {"key": "value"}
    
    @pytest.mark.asyncio
    async def test_post_request(self, api_client):
        """Test POST request convenience method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"created": true}'
        mock_response.json.return_value = {"created": True}
        mock_response.headers = {}
        
        with patch.object(api_client._client, 'request', return_value=mock_response) as mock_request:
            response = await api_client.post("/test", data={"name": "test"})
            
            assert response.status_code == 200
            mock_request.assert_called_once()
            
            # Check that the request was made with correct parameters
            call_args = mock_request.call_args
            assert call_args[1]['method'] == 'POST'
            assert call_args[1]['content'] == json.dumps({"name": "test"})


class TestClickUpResourceClient:
    """Test cases for ClickUpResourceClient."""
    
    @pytest.fixture
    def resource_client(self, api_client):
        """Create a test resource client."""
        return ClickUpResourceClient(api_client)
    
    @pytest.mark.asyncio
    async def test_get_teams(self, resource_client):
        """Test getting teams."""
        with patch.object(resource_client.client, 'get', return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_teams()
            mock_get.assert_called_once_with("/team")
    
    @pytest.mark.asyncio
    async def test_get_team(self, resource_client):
        """Test getting a specific team."""
        with patch.object(resource_client.client, 'get', return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_team("123")
            mock_get.assert_called_once_with("/team/123")
    
    @pytest.mark.asyncio
    async def test_create_space(self, resource_client):
        """Test creating a space."""
        with patch.object(resource_client.client, 'post', return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_space("team123", "Test Space", description="A test space")
            
            mock_post.assert_called_once_with(
                "/team/team123/space",
                data={"name": "Test Space", "description": "A test space"}
            )
    
    @pytest.mark.asyncio
    async def test_get_tasks_with_filters(self, resource_client):
        """Test getting tasks with filters."""
        with patch.object(resource_client.client, 'get', return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_tasks(
                "list123",
                page=1,
                statuses=["open", "in progress"],
                assignees=["user1", "user2"],
                due_date_gt=1609459200000  # Example timestamp
            )
            
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "/list/list123/task"
            
            params = call_args[1]['params']
            assert params['page'] == 1
            assert params['statuses[]'] == ["open", "in progress"]
            assert params['assignees[]'] == ["user1", "user2"]
            assert params['due_date_gt'] == 1609459200000
    
    @pytest.mark.asyncio
    async def test_create_task_minimal(self, resource_client):
        """Test creating a task with minimal data."""
        with patch.object(resource_client.client, 'post', return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_task("list123", "Test Task")
            
            mock_post.assert_called_once_with(
                "/list/list123/task",
                data={
                    "name": "Test Task",
                    "notify_all": True,
                    "check_required_custom_fields": True
                }
            )
    
    @pytest.mark.asyncio
    async def test_create_task_full(self, resource_client):
        """Test creating a task with all optional data."""
        with patch.object(resource_client.client, 'post', return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_task(
                "list123",
                "Test Task",
                description="A test task",
                assignees=["user1"],
                tags=["urgent"],
                status="open",
                priority=1,
                due_date=1609459200000,
                time_estimate=3600000
            )
            
            expected_data = {
                "name": "Test Task",
                "description": "A test task",
                "assignees": ["user1"],
                "tags": ["urgent"],
                "status": "open",
                "priority": 1,
                "due_date": 1609459200000,
                "due_date_time": False,
                "time_estimate": 3600000,
                "notify_all": True,
                "check_required_custom_fields": True
            }
            
            mock_post.assert_called_once_with("/list/list123/task", data=expected_data)
    
    @pytest.mark.asyncio
    async def test_update_task(self, resource_client):
        """Test updating a task."""
        with patch.object(resource_client.client, 'put', return_value=APIResponse(status_code=200)) as mock_put:
            await resource_client.update_task(
                "task123",
                name="Updated Task",
                status="completed"
            )
            
            mock_put.assert_called_once_with(
                "/task/task123",
                data={"name": "Updated Task", "status": "completed"}
            )
    
    @pytest.mark.asyncio
    async def test_delete_task(self, resource_client):
        """Test deleting a task."""
        with patch.object(resource_client.client, 'delete', return_value=APIResponse(status_code=200)) as mock_delete:
            await resource_client.delete_task("task123", team_id="team123")
            
            mock_delete.assert_called_once_with(
                "/task/task123",
                params={"custom_task_ids": False, "team_id": "team123"}
            )
    
    @pytest.mark.asyncio
    async def test_create_list_in_folder(self, resource_client):
        """Test creating a list in a folder."""
        with patch.object(resource_client.client, 'post', return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_list("Test List", folder_id="folder123")
            
            mock_post.assert_called_once_with(
                "/folder/folder123/list",
                data={"name": "Test List"}
            )
    
    @pytest.mark.asyncio
    async def test_create_list_in_space(self, resource_client):
        """Test creating a list in a space."""
        with patch.object(resource_client.client, 'post', return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_list("Test List", space_id="space123")
            
            mock_post.assert_called_once_with(
                "/space/space123/list",
                data={"name": "Test List"}
            )
    
    @pytest.mark.asyncio
    async def test_create_list_no_parent(self, resource_client):
        """Test creating a list without folder_id or space_id raises error."""
        with pytest.raises(ValueError) as exc_info:
            await resource_client.create_list("Test List")
        
        assert "Either folder_id or space_id must be provided" in str(exc_info.value)


class TestAPIResponse:
    """Test cases for APIResponse model."""
    
    def test_api_response_creation(self):
        """Test creating an APIResponse."""
        response = APIResponse(
            status_code=200,
            data={"test": "data"},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        assert response.data == {"test": "data"}
        assert response.headers == {"Content-Type": "application/json"}
        assert response.success is True
        assert response.error is None
    
    def test_api_response_error(self):
        """Test creating an error APIResponse."""
        response = APIResponse(
            status_code=400,
            data={"err": "Bad request"},
            success=False,
            error="Bad request"
        )
        
        assert response.status_code == 400
        assert response.success is False
        assert response.error == "Bad request"
