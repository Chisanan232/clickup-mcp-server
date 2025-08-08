"""
Endpoint client implementations for MCP server communication.

This module provides client classes for both SSE and HTTP streaming
communication with the MCP server endpoints.
"""

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
        self.read_stream: MemoryObjectReceiveStream[SessionMessage | Exception] | None = None
        self.write_stream: MemoryObjectSendStream[SessionMessage] | None = None
        self.session: ClientSession | None = None
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
        # Create SSE client and extract read/write streams
        self._cm = sse_client(self.url)
        self.read_stream, self.write_stream = await self._cm.__aenter__()

        # Create session using the streams
        self.session = ClientSession(self.read_stream, self.write_stream)
        await self.session.__aenter__()
        await self.session.initialize()

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
        if self.session:
            await self.session.__aexit__(None, None, None)

        if hasattr(self, "_cm"):
            await self._cm.__aexit__(None, None, None)

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
        # Create HTTP streaming client and extract read/write streams
        self._cm = streamablehttp_client(self.url)
        self.read_stream, self.write_stream, self._close_fn = await self._cm.__aenter__()

        # Create session using the streams
        self.session = ClientSession(self.read_stream, self.write_stream)
        await self.session.__aenter__()
        await self.session.initialize()

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
        if self.session:
            await self.session.__aexit__(None, None, None)

        # Call the explicit close function if available
        if self._close_fn:
            await self._close_fn()

        if hasattr(self, "_cm"):
            await self._cm.__aexit__(None, None, None)

        # Clean up references
        self.read_stream = None
        self.write_stream = None
        self.session = None
        self._close_fn = None
