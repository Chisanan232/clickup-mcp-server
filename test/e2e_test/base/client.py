"""
Endpoint client implementations for MCP server communication.

This module provides client classes for both SSE and HTTP streaming
communication with the MCP server endpoints.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any

from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import GetSessionIdCallback, streamablehttp_client
from mcp.shared.message import SessionMessage

from .dto import FunctionPayloadDto

logger = logging.getLogger(__name__)


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

        self._sse_task: asyncio.Task | None = asyncio.create_task(_manager())
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
        logger.debug(f"[SSE] result: {result}")
        if hasattr(result, "model_dump"):
            result_dict = result.model_dump()
            logger.debug(f"[SSE] result_dict: {result_dict}")
            # Check if response has the new structured format
            if (
                isinstance(result_dict, dict)
                and "structuredContent" in result_dict
                and "result" in result_dict["structuredContent"]
            ):
                payload = result_dict["structuredContent"]["result"]
                logger.debug(f"[SSE] structured payload: {payload}")
                if payload is None:
                    return []
                # Unwrap ToolResponse envelope if present
                if isinstance(payload, dict) and "ok" in payload and ("result" in payload or "issues" in payload):
                    value = payload["result"] if payload.get("ok") else []
                    # Normalize list payloads: drop None, convert models to dicts
                    if isinstance(value, list):
                        norm = []
                        for i in value:
                            if i is None:
                                continue
                            if hasattr(i, "model_dump"):
                                try:
                                    norm.append(i.model_dump())
                                except Exception:
                                    norm.append(i)
                            else:
                                norm.append(i)
                        print(f"[DEBUG][SSE] normalized envelope list: {norm}")
                        return norm
                    return value
                # Not an envelope
                if isinstance(payload, list):
                    norm = []
                    for i in payload:
                        if i is None:
                            continue
                        if hasattr(i, "model_dump"):
                            try:
                                norm.append(i.model_dump())
                            except Exception:
                                norm.append(i)
                        else:
                            norm.append(i)
                    print(f"[DEBUG][SSE] normalized list: {norm}")
                    return norm
                return payload
            # Also support returning envelope at top level
            if (
                isinstance(result_dict, dict)
                and "ok" in result_dict
                and ("result" in result_dict or "issues" in result_dict)
            ):
                value = result_dict["result"] if result_dict.get("ok") else []
                if isinstance(value, list):
                    norm = []
                    for i in value:
                        if i is None:
                            continue
                        if hasattr(i, "model_dump"):
                            try:
                                norm.append(i.model_dump())
                            except Exception:
                                norm.append(i)
                        else:
                            norm.append(i)
                    print(f"[DEBUG][SSE] normalized top-level list: {norm}")
                    return norm
                return value
            return result_dict

        # Fallback: if the raw result is a list, filter out None items
        if isinstance(result, list):
            norm = []
            for i in result:
                if i is None:
                    continue
                if hasattr(i, "model_dump"):
                    try:
                        norm.append(i.model_dump())
                    except Exception:
                        norm.append(i)
                else:
                    norm.append(i)
            print(f"[DEBUG][SSE] fallback normalized list: {norm}")
            return norm
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
        self._streams_ready: asyncio.Event = asyncio.Event()
        self._stop_event: asyncio.Event = asyncio.Event()

        async def _manager() -> None:
            async with streamablehttp_client(self.url) as (read_stream, write_stream, _session_id):
                async with ClientSession(read_stream, write_stream) as session:
                    self.read_stream = read_stream
                    self.write_stream = write_stream
                    self.session = session
                    await self.session.initialize()
                    self._streams_ready.set()
                    await self._stop_event.wait()

        self._manager_task: asyncio.Task | None = asyncio.create_task(_manager())
        await self._streams_ready.wait()

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
        print(f"[DEBUG] result: {result}")
        if hasattr(result, "model_dump"):
            result_dict = result.model_dump()
            print(f"[DEBUG] result_dict: {result_dict}")
            # Check if response has the new structured format
            if (
                isinstance(result_dict, dict)
                and "structuredContent" in result_dict
                and "result" in result_dict["structuredContent"]
            ):
                payload = result_dict["structuredContent"]["result"]
                if payload is None:
                    return []
                # Unwrap ToolResponse envelope if present
                if isinstance(payload, dict) and "ok" in payload and ("result" in payload or "issues" in payload):
                    value = payload["result"] if payload.get("ok") else []
                    if isinstance(value, list):
                        return [i for i in value if i is not None]
                    return value
                # Not an envelope
                if isinstance(payload, list):
                    return [i for i in payload if i is not None]
                return payload
            # Also support returning envelope at top level
            if (
                isinstance(result_dict, dict)
                and "ok" in result_dict
                and ("result" in result_dict or "issues" in result_dict)
            ):
                value = result_dict["result"] if result_dict.get("ok") else []
                if isinstance(value, list):
                    return [i for i in value if i is not None]
                return value
            return result_dict

        # Fallback: if the raw result is a list, filter out None items
        if isinstance(result, list):
            return [i for i in result if i is not None]
        return result

    async def close(self) -> None:
        """
        Close the HTTP streaming connection and clean up resources.
        """
        if hasattr(self, "_stop_event"):
            self._stop_event.set()
        if hasattr(self, "_manager_task") and self._manager_task:
            try:
                await self._manager_task
            except Exception:
                pass

        # Clean up references
        self.read_stream = None
        self.write_stream = None
        self.session = None
        self._close_fn = None
        self._manager_task = None
