from abc import ABCMeta, abstractmethod


class BaseServerFactory[T](metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def create(**kwargs) -> T:
        """
        Create and configure the MCP server with the specified environment file.

        Returns:
            Configured server instance
        """

    @staticmethod
    @abstractmethod
    def get() -> T:
        """
        Get the server instance

        Returns:
            Configured server instance
        """
