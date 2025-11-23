"""
Utility functions for the ClickUp MCP server.
"""

import logging
from pathlib import Path


def load_environment_from_file(env_file: str | None = None) -> bool:
    """
    Load environment variables from a .env file if provided.

    Args:
        env_file: Path to the environment file

    Returns:
        True if environment was loaded successfully, False otherwise
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
