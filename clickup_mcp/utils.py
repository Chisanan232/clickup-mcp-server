"""
Utility functions for the ClickUp MCP server.
"""
import logging
from pathlib import Path
from typing import Optional


def load_environment_from_file(env_file: Optional[str] = None) -> bool:
    """
    Load environment variables from a .env file if provided.

    Args:
        env_file: Path to the environment file

    Returns:
        True if environment was loaded successfully, False otherwise
    """
    if not env_file:
        return False
    
    from dotenv import load_dotenv

    env_path = Path(env_file)
    if env_path.exists():
        logging.info(f"Loading environment variables from {env_file}")
        load_dotenv(env_path)
        return True
    else:
        logging.warning(f"Environment file {env_file} not found")
        return False
