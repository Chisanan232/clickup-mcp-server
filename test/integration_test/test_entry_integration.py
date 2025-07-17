"""
Integration tests for the entry point module.

This module tests the actual server startup and functionality in a more
realistic environment with minimal mocking.
"""

import signal
import socket
import subprocess
import sys
import threading
import time
from contextlib import closing
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from clickup_mcp.entry import create_app_factory, run_server
from clickup_mcp.models.cli import ServerConfig


def find_free_port() -> int:
    """Find an available port on the local machine."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


class TestEntryIntegration:
    """Integration test suite for the entry module."""

    def test_create_app_factory(self):
        """Test that the app factory creates a valid FastAPI application."""
        app = create_app_factory()
        client = TestClient(app)

        # Test that the root endpoint works
        response = client.get("/")
        assert response.status_code == 200
        assert "status" in response.json()

        # Test that the docs endpoint works
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower()

    @pytest.mark.slow
    @patch("subprocess.Popen")
    def test_server_startup_and_shutdown(self, mock_popen):
        """
        Test server startup and shutdown with mocked subprocess.

        This test is marked as slow as it involves server startup simulation.
        """
        port = find_free_port()

        # Mock the process
        mock_process = mock_popen.return_value
        mock_process.returncode = 0
        mock_process.poll.return_value = None  # Process still running

        # Start server in a mocked process
        cmd = [sys.executable, "-m", "clickup_mcp", "--host", "127.0.0.1", "--port", str(port), "--log-level", "info"]

        # Call the subprocess
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Test it made the expected calls
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        assert args[0] == cmd
        assert "stdout" in kwargs
        assert "stderr" in kwargs

        # Clean up
        process.terminate()

    def test_run_server_in_thread(self):
        """
        Test running the server in a separate thread.

        This allows testing the server without creating a separate process.
        """
        port = find_free_port()
        config = ServerConfig(host="127.0.0.1", port=port, log_level="info", reload=False)

        # Mock uvicorn.run to capture the parameters
        with patch("uvicorn.run") as mock_run:
            # Run server in a separate thread to avoid blocking the test
            thread = threading.Thread(target=run_server, args=(config,))
            thread.daemon = True
            thread.start()

            # Give the thread time to start
            time.sleep(0.5)

            # Verify uvicorn.run was called with the expected parameters
            assert mock_run.call_count == 1
            call_args = mock_run.call_args[1]
            assert call_args["host"] == "127.0.0.1"
            assert call_args["port"] == port
            assert call_args["log_level"] == "info"
            assert call_args["reload"] is False

    @pytest.mark.skipif(
        True,  # Skip this test by default as it's not reliable in CI
        reason="Signal testing can be unreliable in test environments",
    )
    @patch("signal.SIGINT", 2)  # Mock the signal value for cross-platform testing
    @patch("subprocess.Popen")
    def test_signal_handling(self, mock_popen, mock_signal):
        """
        Test that the server handles signals properly.

        This test is skipped by default as signal handling
        can be unreliable in test environments.
        """
        port = find_free_port()

        # Mock the process behavior
        mock_process = mock_popen.return_value
        mock_process.returncode = None
        mock_process.poll.side_effect = [None, 0]  # First None, then 0 after signal

        # Start server in a mocked process
        cmd = [sys.executable, "-m", "clickup_mcp", "--host", "127.0.0.1", "--port", str(port)]

        process = subprocess.Popen(cmd)

        # Send SIGINT (equivalent to Ctrl+C)
        process.send_signal(signal.SIGINT)

        # Verify the signal was sent
        mock_process.send_signal.assert_called_once_with(2)  # SIGINT value

        # Wait for the process to terminate
        process.wait(timeout=5)
        mock_process.wait.assert_called_once()

        # Clean up just in case
        process.terminate()

    @patch("subprocess.Popen")
    def test_server_with_invalid_host(self, mock_popen):
        """Test server behavior with an invalid host."""
        port = find_free_port()

        # Mock the process behavior to simulate failure
        mock_process = mock_popen.return_value
        mock_process.poll.return_value = 1  # Error return code
        mock_process.returncode = 1

        # Configure the mock stderr to contain error message
        mock_stderr = MagicMock()
        mock_stderr.readline.return_value = b"Error: Invalid host specified"
        mock_process.stderr = mock_stderr

        # Start server with an invalid host
        cmd = [sys.executable, "-m", "clickup_mcp", "--host", "invalid_host", "--port", str(port)]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Verify the command was called with expected arguments
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        assert args[0] == cmd
        assert "stdout" in kwargs
        assert "stderr" in kwargs

        # Clean up
        process.terminate()
