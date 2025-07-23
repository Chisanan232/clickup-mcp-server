"""
Tests for the CLI --env option functionality.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

from clickup_mcp.entry import parse_args, run_server
from clickup_mcp.models.cli import ServerConfig


class TestCliEnvOption:
    """Tests for the CLI --env option."""

    def test_env_cli_parameter(self):
        """Test parsing the --env CLI parameter."""
        # Create a temporary env file path
        temp_env_path = "/tmp/custom_test.env"

        # Simulate CLI args with --env
        with patch("sys.argv", ["clickup_mcp", "--env", temp_env_path]):
            config = parse_args()
            assert isinstance(config, ServerConfig)
            assert config.env_file == temp_env_path

    def test_env_file_passed_to_create_app(self, monkeypatch):
        """Test that the env file path is correctly passed to create_app."""
        # Create a temp .env file with a test token
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as temp_file:
            temp_file.write("CLICKUP_API_TOKEN=test_token_from_cli_env\n")
            env_path = temp_file.name

        try:
            # Create a config with our temp env file
            config = ServerConfig(env_file=env_path)

            # Ensure environment is clean
            monkeypatch.delenv("CLICKUP_API_TOKEN", raising=False)

            # Mock create_app and uvicorn.run to prevent actual server startup
            with (
                patch("clickup_mcp.entry.create_app") as mock_create_app,
                patch("clickup_mcp.entry.uvicorn.run") as mock_run,
            ):
                # Run the server with our config
                run_server(config)

                # Check that create_app was called with our config containing the env_file path
                mock_create_app.assert_called_once_with(config)

                # Verify the config passed to create_app has the correct env_file
                call_args = mock_create_app.call_args[0][0]
                assert call_args.env_file == env_path

                # Verify uvicorn.run was called
                assert mock_run.called

        finally:
            # Clean up temp file
            Path(env_path).unlink(missing_ok=True)
