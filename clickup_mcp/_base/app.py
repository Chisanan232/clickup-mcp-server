from abc import ABCMeta, abstractmethod
from typing import Any


class BaseServerFactory(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def create() -> Any:
        """
        Create and configure the MCP server with the specified environment file.

        Returns:
            Configured FastMCP server instance
        """
        pass

    @staticmethod
    @abstractmethod
    def get() -> Any:
        """
        Get the MCP server instance

        Returns:
            Configured FastMCP server instance
        """
        pass
