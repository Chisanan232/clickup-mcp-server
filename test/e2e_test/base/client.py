"""
Endpoint client implementations for MCP server communication.

This module provides client classes for both SSE and HTTP streaming
communication with the MCP server endpoints.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any

from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import GetSessionIdCallback, streamablehttp_client
from mcp.shared.message import SessionMessage

from .dto import FunctionPayloadDto


class EndpointClient(ABC):
    """
    Abstract base class for MCP endpoint clients.

    This defines the interface that all endpoint clients must implement
    for connecting to, communicating with, and disconnecting from
    MCP endpoints.
    """

    def __init__(self, url: str) -> None:
        """
        Initialize the client with the endpoint URL.

        Args:
            url: The URL of the MCP endpoint
        """
        self.url: str = url
        self.session: ClientSession
        self.read_stream: MemoryObjectReceiveStream[SessionMessage | Exception] | None = None
        self.write_stream: MemoryObjectSendStream[SessionMessage] | None = None
        self._close_fn: GetSessionIdCallback | None = None

    @abstractmethod
    async def connect(self) -> None:
        """
        Connect to the MCP endpoint.

        This method should establish the connection and initialize
        required streams for communication.
        """
        ...

    @abstractmethod
    async def call_function(self, payload: FunctionPayloadDto) -> Any:
        """
        Call a function on the MCP server.

        Args:
            payload: Dictionary containing 'function' name and 'arguments'

        Returns:
            Any: The function result
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """
        Close the connection to the MCP endpoint.

        This method should clean up all resources used by the client.
        """
        ...


class SSEClient(EndpointClient):
    """
    Client for connecting to MCP endpoints using Server-Sent Events (SSE).

    This client uses the sse_client to establish bidirectional
    communication with the server.
    """

    async def connect(self) -> None:
        """
        Connect to the MCP server using SSE transport.
        """
        # Manage the sse_client and session in a background task so that __aexit__
        # runs in the same task and avoids anyio cancel scope issues.
        self._sse_ready: asyncio.Event = asyncio.Event()
        self._sse_stop: asyncio.Event = asyncio.Event()

        async def _manager() -> None:
            async with sse_client(self.url) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    self.read_stream = read_stream
                    self.write_stream = write_stream
                    self.session = session
                    await self.session.initialize()
                    self._sse_ready.set()
                    await self._sse_stop.wait()

        self._sse_task = asyncio.create_task(_manager())
        await self._sse_ready.wait()

    async def call_function(self, payload: FunctionPayloadDto) -> Any:
        """
        Call a function on the MCP server via SSE transport.

        Args:
            payload: The function payload containing function name and arguments

        Returns:
            Any: The function result
        """
        if not self.session:
            raise ValueError("Client not connected")

        # Call the function using the session
        result = await self.session.call_tool(name=payload.function, **payload.arguments)

        # The result is already a structured object, extract it if needed
        if hasattr(result, "model_dump"):
            result_dict = result.model_dump()
            # Check if response has the new structured format
            if (
                isinstance(result_dict, dict)
                and "structuredContent" in result_dict
                and "result" in result_dict["structuredContent"]
            ):
                return result_dict["structuredContent"]["result"]
            return result_dict

        return result

    async def close(self) -> None:
        """
        Close the SSE connection and clean up resources.
        """
        if hasattr(self, "_sse_stop"):
            self._sse_stop.set()
        if hasattr(self, "_sse_task") and self._sse_task:
            try:
                await self._sse_task
            except Exception:
                pass

        # Clean up references
        self.read_stream = None
        self.write_stream = None
        self.session = None


class StreamingHTTPClient(EndpointClient):
    """
    Client for connecting to MCP endpoints using HTTP streaming.

    This client uses the streamablehttp_client to establish bidirectional
    communication with the server over a single HTTP connection.
    """

    async def connect(self) -> None:
        """
        Connect to the MCP server using HTTP streaming transport.
        """
        # Manage the streamable_http context in a dedicated background task so that
        # it can exit in the same task it was entered, avoiding anyio cancel scope errors.
        self._streams_ready: asyncio.Event = asyncio.Event()
        self._stop_event: asyncio.Event = asyncio.Event()

        async def _manager() -> None:
            async with streamablehttp_client(self.url) as (read_stream, write_stream, _session_id):
                # Create session inside the same task that manages the context
                async with ClientSession(read_stream, write_stream) as session:
                    self.read_stream = read_stream
                    self.write_stream = write_stream
                    self.session = session
                    await self.session.initialize()
                    self._streams_ready.set()
                    # Wait until asked to stop (teardown)
                    await self._stop_event.wait()

        self._manager_task = asyncio.create_task(_manager())
        # Wait until streams are ready before creating the session
        await self._streams_ready.wait()

        # Session is already created and initialized inside manager

    async def call_function(self, payload: FunctionPayloadDto) -> Any:
        """
        Call a function on the MCP server via HTTP streaming transport.

        Args:
            payload: The function payload containing function name and arguments

        Returns:
            Any: The function result
        """
        if not self.session:
            raise ValueError("Client not connected")

        # Call the function using the session
        result = await self.session.call_tool(name=payload.function, **payload.arguments)

        # The result is already a structured object, extract it if needed
        if hasattr(result, "model_dump"):
            result_dict = result.model_dump()
            # Check if response has the new structured format
            if (
                isinstance(result_dict, dict)
                and "structuredContent" in result_dict
                and "result" in result_dict["structuredContent"]
            ):
                return result_dict["structuredContent"]["result"]
            return result_dict

        return result

    async def close(self) -> None:
        """
        Close the HTTP streaming connection and clean up resources.
        """
        # Signal the background manager to exit the session and stream context
        # in its own task (must exit in the same task it was created).
        if hasattr(self, "_stop_event"):
            self._stop_event.set()
        if hasattr(self, "_manager_task") and self._manager_task:
            try:
                await self._manager_task
            except Exception:
                # Ensure teardown continues even if background task raises
                pass

        # Clean up references
        self.read_stream = None
        self.write_stream = None
        self.session = None
        self._close_fn = None
        self._manager_task = None
