"""
Base server factory abstraction.

Design:
- Defines an abstract factory for creating and managing a singleton server instance
  (e.g., a FastAPI app, an HTTP client, or any long-lived service object).
- Uses static abstract methods so downstream factories can remain class-only and
  avoid instantiation overhead.
- Generic over the instance type `T` (PEP 695 style type parameter on Python 3.12+).

Responsibilities:
- `create(**kwargs) -> T`: Build and configure a fresh instance
- `get() -> T`: Return the existing instance or lazily create it
- `reset() -> None`: Drop the cached instance (useful for tests or full reinit)

Lifecycle & scheduling ("cron"):
- This base defines lifecycle hooks (`get`/`reset`); concrete factories may layer
  periodic tasks, background jobs, or health checks using their framework of choice
  (e.g., FastAPI startup events, APScheduler). The scheduling itself is out of scope
  here and must be implemented by subclasses.

Thread-safety:
- Implementations should ensure `get()` and `create()` are safe in concurrent contexts,
  using locks as needed if multiple threads/processes may race on initialization.

Demonstration:
    # Example: FastAPI app factory (singleton)
    from typing import Optional
    from fastapi import FastAPI

    class WebServerFactory(BaseServerFactory[FastAPI]):
        _instance: Optional[FastAPI] = None

        @staticmethod
        def create(**kwargs) -> FastAPI:
            app = FastAPI(title=kwargs.get("title", "ClickUp MCP Server"))
            # mount routers, middleware, startup tasks, etc.
            return app

        @staticmethod
        def get() -> FastAPI:
            if WebServerFactory._instance is None:
                WebServerFactory._instance = WebServerFactory.create()
            return WebServerFactory._instance

        @staticmethod
        def reset() -> None:
            # gracefully shutdown/cleanup if needed, then drop the singleton
            WebServerFactory._instance = None

    # Usage
    app = WebServerFactory.get()      # lazily create once
    WebServerFactory.reset()          # drop for tests, then create again on next get()
"""

from abc import ABCMeta, abstractmethod


class BaseServerFactory[T](metaclass=ABCMeta):
    """
    Abstract singleton factory for server-like objects.

    This base class formalizes a lightweight contract to construct, reuse, and reset
    a single long-lived instance of type `T`. It is intentionally minimal to stay
    framework-agnostic and test-friendly.

    Key ideas:
    - Do not store state here; concrete factories manage their cache/singleton.
    - Keep `create()` idempotent with respect to its arguments or ensure callers
      use `get()` for reuse.
    - Prefer explicit `reset()` in tests to avoid cross-test pollution.

    Examples:
        # Minimal skeleton for a concrete implementation
        class MyFactory(BaseServerFactory[str]):
            _instance: str | None = None

            @staticmethod
            def create(**kwargs) -> str:
                return kwargs.get("value", "default")

            @staticmethod
            def get() -> str:
                if MyFactory._instance is None:
                    MyFactory._instance = MyFactory.create()
                return MyFactory._instance

            @staticmethod
            def reset() -> None:
                MyFactory._instance = None
    """

    @staticmethod
    @abstractmethod
    def create(**kwargs) -> T:
        """
        Create and configure a fresh server instance.

        Design:
        - Should return a fully initialized object of type `T` (e.g., FastAPI app)
        - May accept optional keyword arguments for customization (title, middleware, etc.)
        - Avoid caching here; `get()` is responsible for reuse.

        Args:
            **kwargs: Implementation-defined options used to configure the instance

        Returns:
            T: A new, configured instance (not cached by the base class)

        Examples:
            # Create without caching
            app = WebServerFactory.create(title="My Server")
        """

    @staticmethod
    @abstractmethod
    def get() -> T:
        """
        Get the singleton instance, lazily creating it if needed.

        Behavior:
        - Returns the cached instance when available
        - Otherwise calls `create()` and caches the result
        - Implementations should consider thread-safety if used concurrently

        Returns:
            T: The cached (or newly created) singleton instance

        Examples:
            app = WebServerFactory.get()  # same object on subsequent calls
        """

    @staticmethod
    @abstractmethod
    def reset() -> None:
        """
        Reset the cached singleton instance.

        Notes:
        - Implementations should gracefully shutdown/cleanup resources if required
        - Intended primarily for tests or controlled lifecycle resets

        Examples:
            WebServerFactory.reset()
        """
