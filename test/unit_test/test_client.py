"""
Unit tests for ClickUp API client.
"""

import asyncio
import json
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from clickup_mcp.client import APIResponse, ClickUpAPIClient
from clickup_mcp.exceptions import (
    AuthenticationError,
    ClickUpAPIError,
    RateLimitError,
)

from ._base import BaseAPIClientTestSuite


class TestClickUpAPIClient(BaseAPIClientTestSuite):
    """Test cases for ClickUpAPIClient."""

    def test_initialization(self) -> None:
        """Test API client initialization."""
        client = ClickUpAPIClient(
            api_token="test_token", timeout=10.0, max_retries=5, retry_delay=2.0, rate_limit_requests_per_minute=120
        )

        assert client.api_token == "test_token"
        assert client.timeout == 10.0
        assert client.max_retries == 5
        assert client.retry_delay == 2.0
        assert client.rate_limit == 120
        assert "Authorization" in client._headers
        assert client._headers["Authorization"] == "test_token"

    @pytest.mark.asyncio
    async def test_context_manager(self, api_client: ClickUpAPIClient) -> None:
        """Test async context manager functionality."""
        async with api_client as client:
            assert client is api_client

        # Client should be closed after context exit
        # (We can't easily test this without mocking the httpx client)

    @pytest.mark.asyncio
    async def test_rate_limiting(self, api_client: ClickUpAPIClient) -> None:
        """Test rate limiting functionality."""
        # Set a very low rate limit for testing
        api_client.rate_limit = 2

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            # Mock the event loop time to have consistent timing
            with patch("asyncio.get_event_loop") as mock_get_event_loop:
                mock_loop = Mock()
                mock_get_event_loop.return_value = mock_loop

                # Test case 1: No rate limiting needed (old requests that should be cleaned up)
                mock_loop.time.return_value = 100.0
                api_client._request_times = [30.0, 35.0]  # More than 60 seconds old (100-30=70, 100-35=65)

                await api_client._enforce_rate_limit()

                # Should not sleep and should clean up old requests
                mock_sleep.assert_not_called()
                assert len(api_client._request_times) == 1  # Only current request time added
                assert api_client._request_times[0] == 100.0

                # Reset for next test
                mock_sleep.reset_mock()
                api_client._request_times = []

                # Test case 2: Rate limiting triggered (requests within limit but at capacity)
                mock_loop.time.return_value = 200.0
                # Add requests within the last minute that meet the rate limit exactly
                api_client._request_times = [150.0, 160.0]  # 2 requests within 60 seconds (exactly at limit)

                await api_client._enforce_rate_limit()

                # Should sleep for the calculated time
                expected_sleep_time = 60 - (200.0 - 150.0)  # 60 - 50 = 10 seconds
                mock_sleep.assert_called_once_with(expected_sleep_time)
                assert len(api_client._request_times) == 3  # 2 existing + 1 new

                # Reset for next test
                mock_sleep.reset_mock()
                api_client._request_times = []

                # Test case 3: No rate limiting needed (under limit)
                mock_loop.time.return_value = 300.0
                api_client._request_times = [290.0]  # Only 1 request within limit (rate limit is 2)

                await api_client._enforce_rate_limit()

                # Should not sleep because we're under the limit
                mock_sleep.assert_not_called()
                assert len(api_client._request_times) == 2  # 1 existing + 1 new

                # Test case 4: Edge case - sleep time is negative (already expired)
                mock_sleep.reset_mock()
                api_client._request_times = []
                mock_loop.time.return_value = 400.0
                # Add requests where the first one is more than 60 seconds ago
                api_client._request_times = [330.0, 380.0]  # 330 is 70 seconds ago, 380 is 20 seconds ago

                await api_client._enforce_rate_limit()

                # Should not sleep because the first request (330.0) gets cleaned up
                # leaving only [380.0] + new time, so total = 2 (exactly at limit but not over)
                mock_sleep.assert_not_called()
                assert len(api_client._request_times) == 2  # 1 remaining + 1 new

                # Test case 5: Sleep time calculation with edge case
                mock_sleep.reset_mock()
                api_client._request_times = []
                mock_loop.time.return_value = 500.0
                # Add requests that trigger rate limiting
                api_client._request_times = [460.0, 480.0]  # Both within 60 seconds

                await api_client._enforce_rate_limit()

                # Should sleep for remaining time based on oldest request
                expected_sleep_time = 60 - (500.0 - 460.0)  # 60 - 40 = 20 seconds
                mock_sleep.assert_called_once_with(expected_sleep_time)

    @pytest.mark.asyncio
    async def test_successful_request(self, api_client: ClickUpAPIClient) -> None:
        """Test successful API request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"data": "test"}'
        mock_response.json.return_value = {"data": "test"}
        mock_response.headers = {"Content-Type": "application/json"}

        with patch.object(api_client._client, "request", return_value=mock_response) as mock_request:
            response = await api_client._make_request("GET", "/test")

            assert isinstance(response, APIResponse)
            assert response.status_code == 200
            assert response.data == {"data": "test"}
            assert response.success is True
            assert response.error is None

            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_authentication_error(self, api_client: ClickUpAPIClient) -> None:
        """Test authentication error handling."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.content = b'{"err": "Unauthorized"}'
        mock_response.json.return_value = {"err": "Unauthorized"}

        with patch.object(api_client._client, "request", return_value=mock_response):
            with pytest.raises(AuthenticationError) as exc_info:
                await api_client._make_request("GET", "/test")

            assert exc_info.value.status_code == 401
            assert "Invalid API token" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_rate_limit_error(self, api_client: ClickUpAPIClient) -> None:
        """Test rate limit error handling."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.content = b'{"err": "Rate limit exceeded"}'
        mock_response.json.return_value = {"err": "Rate limit exceeded"}

        with patch.object(api_client._client, "request", return_value=mock_response):
            with pytest.raises(RateLimitError) as exc_info:
                await api_client._make_request("GET", "/test")

            assert exc_info.value.status_code == 429

    @pytest.mark.asyncio
    async def test_client_error_response(self, api_client: ClickUpAPIClient) -> None:
        """Test client error response (4xx) handling."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.content = b'{"err": "Bad request"}'
        mock_response.json.return_value = {"err": "Bad request"}
        mock_response.headers = {"Content-Type": "application/json"}

        with patch.object(api_client._client, "request", return_value=mock_response):
            response = await api_client._make_request("GET", "/test")

            assert response.status_code == 400
            assert response.success is False
            assert response.error == "Bad request"
            assert response.data == {"err": "Bad request"}

    @pytest.mark.asyncio
    async def test_retry_logic(self, api_client: ClickUpAPIClient) -> None:
        """Test retry logic for failed requests."""
        # Set up a mock that fails twice then succeeds
        mock_responses = [
            httpx.HTTPError("Connection failed"),
            httpx.HTTPError("Connection failed"),
            Mock(status_code=200, content=b'{"success": true}', json=lambda: {"success": True}, headers={}),
        ]

        call_count = 0

        async def mock_request(*args: Any, **kwargs: Any) -> Any:
            nonlocal call_count
            response = mock_responses[call_count]
            call_count += 1
            if isinstance(response, Exception):
                raise response
            return response

        with patch.object(api_client._client, "request", side_effect=mock_request):
            response = await api_client._make_request("GET", "/test")

            assert response.status_code == 200
            assert call_count == 3  # Two failures + one success

    @pytest.mark.asyncio
    async def test_retry_exhausted(self, api_client: ClickUpAPIClient) -> None:
        """Test behavior when all retries are exhausted."""
        with patch.object(api_client._client, "request", side_effect=httpx.HTTPError("Connection failed")):
            with pytest.raises(ClickUpAPIError) as exc_info:
                await api_client._make_request("GET", "/test")

            assert "Request failed after" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_logs_error_on_client_error_response(
        self, api_client: ClickUpAPIClient, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that a 4xx error logs an error-level message with details."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.content = b'{"err": "Bad request"}'
        mock_response.json.return_value = {"err": "Bad request"}
        mock_response.headers = {"Content-Type": "application/json"}

        with patch.object(api_client._client, "request", return_value=mock_response):
            # Capture error logs
            with caplog.at_level("ERROR"):
                response = await api_client._make_request("GET", "/test")

        assert response.status_code == 400
        assert response.success is False
        # Ensure an error log was produced with expected content
        messages = "\n".join(rec.getMessage() for rec in caplog.records)
        assert "API error GET /test -> 400" in messages
        assert "Bad request" in messages

    @pytest.mark.asyncio
    async def test_logs_error_when_retries_exhausted(
        self, api_client: ClickUpAPIClient, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that exhausting retries logs a final error-level message before raising."""
        with patch.object(api_client._client, "request", side_effect=httpx.HTTPError("Connection failed")):
            with caplog.at_level("ERROR"):
                with pytest.raises(ClickUpAPIError):
                    await api_client._make_request("GET", "/test")

        # Ensure final error log mentions attempts, method, and endpoint
        messages = "\n".join(rec.getMessage() for rec in caplog.records)
        assert "Request failed after" in messages
        assert "GET" in messages
        assert "/test" in messages

    @pytest.mark.asyncio
    async def test_get_request(self, api_client: ClickUpAPIClient) -> None:
        """Test GET request convenience method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"data": "test"}'
        mock_response.json.return_value = {"data": "test"}
        mock_response.headers = {}

        with patch.object(api_client._client, "request", return_value=mock_response) as mock_request:
            response = await api_client.get("/test", params={"key": "value"})

            assert response.status_code == 200
            mock_request.assert_called_once()

            # Check that the request was made with correct parameters
            call_args = mock_request.call_args
            assert call_args[1]["method"] == "GET"
            assert call_args[1]["params"] == {"key": "value"}

    @pytest.mark.asyncio
    async def test_post_request(self, api_client: ClickUpAPIClient) -> None:
        """Test POST request convenience method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"created": true}'
        mock_response.json.return_value = {"created": True}
        mock_response.headers = {}

        with patch.object(api_client._client, "request", return_value=mock_response) as mock_request:
            response = await api_client.post("/test", data={"name": "test"})

            assert response.status_code == 200
            mock_request.assert_called_once()

            # Check that the request was made with correct parameters
            call_args = mock_request.call_args
            assert call_args[1]["method"] == "POST"
            assert call_args[1]["content"] == json.dumps({"name": "test"})

    @pytest.mark.asyncio
    async def test_put_request(self, api_client: ClickUpAPIClient) -> None:
        """Test PUT request convenience method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"updated": true}'
        mock_response.json.return_value = {"updated": True}
        mock_response.headers = {}

        with patch.object(api_client._client, "request", return_value=mock_response) as mock_request:
            response = await api_client.put("/test", data={"name": "updated"})

            assert response.status_code == 200
            assert response.data == {"updated": True}
            mock_request.assert_called_once()

            # Check that the request was made with correct parameters
            call_args = mock_request.call_args
            assert call_args[1]["method"] == "PUT"
            assert call_args[1]["content"] == json.dumps({"name": "updated"})

    @pytest.mark.asyncio
    async def test_delete_request(self, api_client: ClickUpAPIClient) -> None:
        """Test DELETE request convenience method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"deleted": true}'
        mock_response.json.return_value = {"deleted": True}
        mock_response.headers = {}

        with patch.object(api_client._client, "request", return_value=mock_response) as mock_request:
            response = await api_client.delete("/test/123", params={"force": "true"})

            assert response.status_code == 200
            assert response.data == {"deleted": True}
            mock_request.assert_called_once()

            # Check that the request was made with correct parameters
            call_args = mock_request.call_args
            assert call_args[1]["method"] == "DELETE"
            assert call_args[1]["params"] == {"force": "true"}

    @pytest.mark.asyncio
    async def test_patch_request(self, api_client: ClickUpAPIClient) -> None:
        """Test PATCH request convenience method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"patched": true}'
        mock_response.json.return_value = {"patched": True}
        mock_response.headers = {}

        with patch.object(api_client._client, "request", return_value=mock_response) as mock_request:
            response = await api_client.patch("/test/123", data={"field": "value"})

            assert response.status_code == 200
            assert response.data == {"patched": True}
            mock_request.assert_called_once()

            # Check that the request was made with correct parameters
            call_args = mock_request.call_args
            assert call_args[1]["method"] == "PATCH"
            assert call_args[1]["content"] == json.dumps({"field": "value"})

    @pytest.mark.asyncio
    async def test_request_with_custom_headers(self, api_client: ClickUpAPIClient) -> None:
        """Test request with custom headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"success": true}'
        mock_response.json.return_value = {"success": True}
        mock_response.headers = {}

        custom_headers = {"X-Custom-Header": "custom-value", "Accept": "application/json"}

        with patch.object(api_client._client, "request", return_value=mock_response) as mock_request:
            response = await api_client.get("/test", headers=custom_headers)

            assert response.status_code == 200
            mock_request.assert_called_once()

            # Check that custom headers were merged with default headers
            call_args = mock_request.call_args
            headers = call_args[1]["headers"]
            assert headers["X-Custom-Header"] == "custom-value"
            assert headers["Accept"] == "application/json"
            assert headers["Authorization"] == "test_token"  # Default header should still be present

    @pytest.mark.asyncio
    async def test_request_with_params_and_data(self, api_client: ClickUpAPIClient) -> None:
        """Test request with both query parameters and request body."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"success": true}'
        mock_response.json.return_value = {"success": True}
        mock_response.headers = {}

        with patch.object(api_client._client, "request", return_value=mock_response) as mock_request:
            response = await api_client.post(
                "/test", data={"name": "test", "value": 123}, params={"include": "details", "format": "json"}
            )

            assert response.status_code == 200
            mock_request.assert_called_once()

            # Check that both params and data were passed correctly
            call_args = mock_request.call_args
            assert call_args[1]["params"] == {"include": "details", "format": "json"}
            assert call_args[1]["content"] == json.dumps({"name": "test", "value": 123})

    @pytest.mark.asyncio
    async def test_request_with_no_content_response(self, api_client: ClickUpAPIClient) -> None:
        """Test request handling when response has no content."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b""
        mock_response.headers = {}

        with patch.object(api_client._client, "request", return_value=mock_response):
            response = await api_client.get("/test")

            assert response.status_code == 200
            assert response.data is None
            assert response.success is True

    @pytest.mark.asyncio
    async def test_server_error_response(self, api_client: ClickUpAPIClient) -> None:
        """Test server error response (5xx) handling."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.content = b'{"err": "Internal server error"}'
        mock_response.json.return_value = {"err": "Internal server error"}
        mock_response.headers = {"Content-Type": "application/json"}

        with patch.object(api_client._client, "request", return_value=mock_response):
            response = await api_client.get("/test")

            assert response.status_code == 500
            assert response.success is False
            assert response.error == "Internal server error"
            assert response.data == {"err": "Internal server error"}

    @pytest.mark.asyncio
    async def test_response_without_error_field(self, api_client: ClickUpAPIClient) -> None:
        """Test error response without explicit error field."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.content = b'{"message": "Not found"}'
        mock_response.json.return_value = {"message": "Not found"}
        mock_response.headers = {"Content-Type": "application/json"}

        with patch.object(api_client._client, "request", return_value=mock_response):
            response = await api_client.get("/test")

            assert response.status_code == 404
            assert response.success is False
            assert response.error == "HTTP 404 error"  # Default error message
            assert response.data == {"message": "Not found"}

    @pytest.mark.asyncio
    async def test_response_with_empty_json(self, api_client: ClickUpAPIClient) -> None:
        """Test response with empty JSON content."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.content = b"{}"
        mock_response.json.return_value = {}
        mock_response.headers = {}

        with patch.object(api_client._client, "request", return_value=mock_response):
            response = await api_client.get("/test")

            assert response.status_code == 400
            assert response.success is False
            assert response.error == "HTTP 400 error"
            assert response.data == {}

    @pytest.mark.asyncio
    async def test_non_200_success_response(self, api_client: ClickUpAPIClient) -> None:
        """Test non-200 success response (like 201, 202)."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.content = b'{"created": true}'
        mock_response.json.return_value = {"created": True}
        mock_response.headers = {}

        with patch.object(api_client._client, "request", return_value=mock_response):
            response = await api_client.post("/test", data={"name": "test"})

            assert response.status_code == 201
            assert response.success is True  # Default success value
            assert response.data == {"created": True}

    @pytest.mark.asyncio
    async def test_request_timeout_handling(self, api_client: ClickUpAPIClient) -> None:
        """Test request timeout handling."""
        with patch.object(api_client._client, "request", side_effect=httpx.TimeoutException("Request timeout")):
            with pytest.raises(ClickUpAPIError) as exc_info:
                await api_client.get("/test")

            assert "Request failed after" in str(exc_info.value)
            assert "timeout" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_request_connection_error(self, api_client: ClickUpAPIClient) -> None:
        """Test request connection error handling."""
        with patch.object(api_client._client, "request", side_effect=httpx.ConnectError("Connection refused")):
            with pytest.raises(ClickUpAPIError) as exc_info:
                await api_client.get("/test")

            assert "Request failed after" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_exponential_backoff(self, api_client: ClickUpAPIClient) -> None:
        """Test exponential backoff in retry logic."""
        # Set a faster retry delay for testing
        api_client.retry_delay = 0.01

        call_count = 0

        async def mock_request(*args: Any, **kwargs: Any) -> Any:
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise httpx.HTTPError("Connection failed")
            # Success on third attempt
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b'{"success": true}'
            mock_response.json.return_value = {"success": True}
            mock_response.headers = {}
            return mock_response

        with patch.object(api_client._client, "request", side_effect=mock_request):
            # Measure time to verify exponential backoff
            import time

            start_time = time.time()
            response = await api_client.get("/test")
            end_time = time.time()

            assert response.status_code == 200
            assert call_count == 3
            # Should have taken at least some time due to backoff (0.01 + 0.02 = 0.03s minimum)
            assert end_time - start_time >= 0.02

    @pytest.mark.asyncio
    async def test_close_method(self, api_client: ClickUpAPIClient) -> None:
        """Test the close method."""
        mock_client = Mock()
        mock_client.aclose = AsyncMock()
        api_client._client = mock_client

        await api_client.close()

        mock_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_closes_client(self, api_client: ClickUpAPIClient) -> None:
        """Test that context manager properly closes the client."""
        mock_client = Mock()
        mock_client.aclose = AsyncMock()
        api_client._client = mock_client

        async with api_client:
            pass

        mock_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_rate_limit_with_empty_request_times(self, api_client: ClickUpAPIClient) -> None:
        """Test rate limiting when request times list is empty."""
        api_client._request_times = []

        # This should not raise any errors and should add a request time
        await api_client._enforce_rate_limit()

        assert len(api_client._request_times) == 1

    @pytest.mark.asyncio
    async def test_rate_limit_cleanup_old_requests(self, api_client: ClickUpAPIClient) -> None:
        """Test that old request times are cleaned up."""
        # Add some old request times (more than 60 seconds ago)
        current_time = asyncio.get_event_loop().time()
        api_client._request_times = [
            current_time - 120,  # 2 minutes ago
            current_time - 90,  # 1.5 minutes ago
            current_time - 30,  # 30 seconds ago
        ]

        await api_client._enforce_rate_limit()

        # Only the recent request should remain, plus the new one
        assert len(api_client._request_times) == 2
        assert all(current_time - req_time < 60 for req_time in api_client._request_times)

    @pytest.mark.asyncio
    async def test_absolute_url_handling(self, api_client: ClickUpAPIClient) -> None:
        """Test handling of absolute URLs in endpoints."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"success": true}'
        mock_response.json.return_value = {"success": True}
        mock_response.headers = {}

        absolute_url = "https://external-api.example.com/test"

        with patch.object(api_client._client, "request", return_value=mock_response) as mock_request:
            response = await api_client.get(absolute_url)

            assert response.status_code == 200
            mock_request.assert_called_once()

            # Check that the absolute URL was used as-is
            call_args = mock_request.call_args
            assert call_args[1]["url"] == absolute_url

    @pytest.mark.asyncio
    async def test_request_with_none_data(self, api_client: ClickUpAPIClient) -> None:
        """Test request with None data doesn't serialize to JSON."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"success": true}'
        mock_response.json.return_value = {"success": True}
        mock_response.headers = {}

        with patch.object(api_client._client, "request", return_value=mock_response) as mock_request:
            response = await api_client.post("/test", data=None)

            assert response.status_code == 200
            mock_request.assert_called_once()

            # Check that no JSON content was sent
            call_args = mock_request.call_args
            assert call_args[1]["content"] is None

    @pytest.mark.asyncio
    async def test_rate_limit_with_sleep_required(self, api_client: ClickUpAPIClient) -> None:
        """Test rate limiting when sleep is required."""
        # Set a low rate limit for testing
        api_client.rate_limit = 2

        # Set up request times that would trigger rate limiting
        current_time = asyncio.get_event_loop().time()
        # Add two recent requests at the rate limit
        api_client._request_times = [current_time - 5, current_time - 1]

        # Mock asyncio.sleep to verify it's called
        with patch("asyncio.sleep") as mock_sleep:
            await api_client._enforce_rate_limit()

            # Verify sleep was called with a positive value
            mock_sleep.assert_called_once()
            sleep_time = mock_sleep.call_args[0][0]
            assert sleep_time > 0

        # Verify a new request time was added
        assert len(api_client._request_times) == 3

    @pytest.mark.asyncio
    async def test_json_decode_error_handling(self, api_client: ClickUpAPIClient) -> None:
        """Test handling of JSON decode errors in responses."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"invalid": json'  # Invalid JSON
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "doc", 0)
        mock_response.headers = {}

        with patch.object(api_client._client, "request", return_value=mock_response):
            response = await api_client.get("/test")

            assert response.status_code == 200
            assert response.data is None  # Should be None when JSON decode fails
            assert response.success is True

    @pytest.mark.asyncio
    async def test_request_with_list_data(self, api_client: ClickUpAPIClient) -> None:
        """Test request with list data in the body."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"success": true}'
        mock_response.json.return_value = {"success": True}
        mock_response.headers = {}

        list_data = [{"id": 1, "name": "item1"}, {"id": 2, "name": "item2"}]

        with patch.object(api_client._client, "request", return_value=mock_response) as mock_request:
            response = await api_client.post("/test", data=list_data)  # type: ignore[arg-type]

            assert response.status_code == 200
            mock_request.assert_called_once()

            # Check that the list data was serialized to JSON
            call_args = mock_request.call_args
            assert call_args[1]["content"] == json.dumps(list_data)

    @pytest.mark.asyncio
    async def test_request_with_non_json_error_response(self, api_client: ClickUpAPIClient) -> None:
        """Test error response that can't be parsed as JSON."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.content = b"Internal Server Error"  # Plain text, not JSON
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "doc", 0)
        mock_response.headers = {}

        with patch.object(api_client._client, "request", return_value=mock_response):
            response = await api_client.get("/test")

            assert response.status_code == 500
            assert response.success is False
            assert response.error == "HTTP 500 error"  # Default error message
            assert response.data == {}  # Should be empty dict when JSON decode fails

    @pytest.mark.asyncio
    async def test_response_status_codes_edge_cases(self, api_client: ClickUpAPIClient) -> None:
        """Test various edge case status codes."""
        # Test 204 No Content
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.content = b""
        mock_response.headers = {}

        with patch.object(api_client._client, "request", return_value=mock_response):
            response = await api_client.delete("/test")

            assert response.status_code == 204
            assert response.success is True
            assert response.data is None

        # Test 202 Accepted
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.content = b'{"accepted": true}'
        mock_response.json.return_value = {"accepted": True}
        mock_response.headers = {}

        with patch.object(api_client._client, "request", return_value=mock_response):
            response = await api_client.post("/test", data={})

            assert response.status_code == 202
            assert response.success is True
            assert response.data == {"accepted": True}

        # Test 304 Not Modified
        mock_response = Mock()
        mock_response.status_code = 304
        mock_response.content = b""
        mock_response.headers = {}

        with patch.object(api_client._client, "request", return_value=mock_response):
            response = await api_client.get("/test")

            assert response.status_code == 304
            assert response.success is True
            assert response.data is None

    @pytest.mark.asyncio
    async def test_request_url_construction(self, api_client: ClickUpAPIClient) -> None:
        """Test URL construction for different endpoint formats."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"success": true}'
        mock_response.json.return_value = {"success": True}
        mock_response.headers = {}

        # Test relative endpoint
        with patch.object(api_client._client, "request", return_value=mock_response) as mock_request:
            await api_client.get("/teams/123")

            call_args = mock_request.call_args
            assert call_args[1]["url"] == "/teams/123"

        # Test endpoint starting with slash
        with patch.object(api_client._client, "request", return_value=mock_response) as mock_request:
            await api_client.get("teams/456")

            call_args = mock_request.call_args
            assert call_args[1]["url"] == "teams/456"

    @pytest.mark.asyncio
    async def test_client_initialization_with_default_values(self) -> None:
        """Test client initialization with all default values."""
        client = ClickUpAPIClient(api_token="test_token")

        assert client.api_token == "test_token"
        assert client.timeout == 30.0
        assert client.max_retries == 3
        assert client.retry_delay == 1.0
        assert client.rate_limit == 100
        assert client._headers["Authorization"] == "test_token"
        assert client._headers["Content-Type"] == "application/json"
        assert client._headers["User-Agent"] == "ClickUp-MCP-Server/1.0"
        assert str(client._client.base_url) == "https://api.clickup.com/api/v2/"

    @pytest.mark.asyncio
    async def test_make_request_with_all_parameters(self, api_client: ClickUpAPIClient) -> None:
        """Test _make_request with all parameters provided."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"success": true}'
        mock_response.json.return_value = {"success": True}
        mock_response.headers = {}

        custom_headers = {"X-Custom": "value"}
        params = {"filter": "active"}
        data = {"name": "test"}

        with patch.object(api_client._client, "request", return_value=mock_response) as mock_request:
            response = await api_client._make_request(
                method="POST", endpoint="/test", params=params, data=data, headers=custom_headers
            )

            assert response.status_code == 200
            mock_request.assert_called_once()

            # Verify all parameters were passed correctly
            call_args = mock_request.call_args
            assert call_args[1]["method"] == "POST"
            assert call_args[1]["url"] == "/test"
            assert call_args[1]["params"] == params
            assert call_args[1]["content"] == json.dumps(data)

            # Check headers were merged correctly
            headers = call_args[1]["headers"]
            assert headers["X-Custom"] == "value"
            assert headers["Authorization"] == "test_token"
            assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_clickup_api_client_factory(self) -> None:
        """Test the ClickUpAPIClientFactory create and get methods."""
        # Reset the singleton before the test
        import clickup_mcp.client
        from clickup_mcp.client import ClickUpAPIClientFactory

        clickup_mcp.client._CLICKUP_API_CLIENT = None

        # Create a client instance with the factory
        client = ClickUpAPIClientFactory.create(api_token="test_token", timeout=15.0, max_retries=5)

        assert isinstance(client, ClickUpAPIClient)
        assert client.api_token == "test_token"
        assert client.timeout == 15.0
        assert client.max_retries == 5

        # Test the get method returns the same instance
        retrieved_client = ClickUpAPIClientFactory.get()
        assert retrieved_client is client

        # Reset the singleton after the test
        clickup_mcp.client._CLICKUP_API_CLIENT = None


class TestAPIResponse:
    """Test cases for APIResponse model."""

    def test_api_response_creation(self) -> None:
        """Test creating an APIResponse."""
        response: APIResponse = APIResponse(
            status_code=200, data={"test": "data"}, headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 200
        assert response.data == {"test": "data"}
        assert response.headers == {"Content-Type": "application/json"}
        assert response.success is True
        assert response.error is None

    def test_api_response_error(self) -> None:
        """Test creating an error APIResponse."""
        response: APIResponse = APIResponse(
            status_code=400, data={"err": "Bad request"}, success=False, error="Bad request"
        )

        assert response.status_code == 400
        assert response.success is False
        assert response.error == "Bad request"
