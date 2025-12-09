"""
Utility functions for the ClickUp MCP server.
"""

import logging
from pathlib import Path


def load_environment_from_file(env_file: str | None = None) -> bool:
    """
    Load environment variables from a .env file if provided.

    This function provides flexible environment variable loading with automatic
    discovery. If no path is provided, it attempts to find a .env file in the
    current working directory or parent directories. If a specific path is provided,
    it first checks if that file exists, and if not, attempts to discover it using
    the provided filename.

    Args:
        env_file: Path to the environment file. If None, attempts auto-discovery.

    Returns:
        True if environment was loaded successfully, False otherwise

    Usage Examples:
        # Python - Load from default .env file
        load_environment_from_file()

        # Python - Load from specific file
        load_environment_from_file(".env.production")

        # Python - Load from custom path
        load_environment_from_file("/etc/clickup/.env")

        # Environment file format (.env)
        CLICKUP_API_TOKEN=pk_your_token_here
        LOG_LEVEL=info
        DATABASE_URL=postgresql://user:pass@localhost/db
    """
    from dotenv import find_dotenv, load_dotenv

    # If no path provided, try to auto-discover a .env file from CWD upward
    if not env_file:
        discovered = find_dotenv(usecwd=True)
        if discovered:
            logging.info(f"Loading environment variables from {discovered}")
            load_dotenv(discovered)
            return True
        return False

    env_path = Path(env_file)
    if env_path.exists():
        logging.info(f"Loading environment variables from {env_file}")
        load_dotenv(env_path)
        return True

    # If the explicit path doesn't exist, attempt discovery using the provided filename
    discovered = find_dotenv(filename=str(env_file), usecwd=True)
    if discovered:
        logging.info(f"Loading environment variables from {discovered}")
        load_dotenv(discovered)
        return True

    logging.warning(f"Environment file {env_file} not found")
    return False
