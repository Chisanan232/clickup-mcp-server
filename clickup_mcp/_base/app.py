"""
Base server factory classes.

This module provides abstract base classes for server factories
that follow the singleton pattern.
"""

from abc import ABCMeta, abstractmethod


class BaseServerFactory[T](metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def create(**kwargs) -> T:
        """
        Create and configure a server instance.

        Args:
            **kwargs: Additional keyword arguments for server configuration

        Returns:
            Configured server instance
        """

    @staticmethod
    @abstractmethod
    def get() -> T:
        """
        Get the existing server instance or create a new one if none exists.

        Returns:
            Configured server instance
        """

    @staticmethod
    @abstractmethod
    def reset() -> None:
        """
        Reset the singleton instance (primarily for testing).
        """
