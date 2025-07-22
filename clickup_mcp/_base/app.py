from abc import ABCMeta, abstractmethod
from typing import Any, Generic, TypeVar

# Define a type variable for the server instance type
T = TypeVar('T')


class BaseServerFactory(Generic[T], metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def create() -> T:
        """
        Create and configure the MCP server with the specified environment file.

        Returns:
            Configured server instance
        """
        pass

    @staticmethod
    @abstractmethod
    def get() -> T:
        """
        Get the server instance

        Returns:
            Configured server instance
        """
        pass
