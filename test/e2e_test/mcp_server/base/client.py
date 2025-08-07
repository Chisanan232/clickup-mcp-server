"""
Endpoint client implementations for MCP server communication.

This module provides client classes for both SSE and HTTP streaming
communication with the MCP server endpoints.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple, AsyncIterator

import aiohttp
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client

from .dto import FunctionPayloadDto, FunctionResponseDto


class EndpointClient(ABC):
    """
    Abstract base class for MCP endpoint clients.
    
    This defines the interface that all endpoint clients must implement
    for connecting to, communicating with, and disconnecting from
    MCP endpoints.
    """

    def __init__(self, url: str):
        """
        Initialize the client with the endpoint URL.
        
        Args:
            url: The URL of the MCP endpoint
        """
        self.url = url
        self.read_stream = None
        self.write_stream = None
        self.session = None
        self._close_fn = None

    @abstractmethod
    async def connect(self) -> None:
        """
        Connect to the MCP endpoint.
        
        This method should establish the connection and initialize
        required streams for communication.
        """
        ...

    @abstractmethod
    async def call_function(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a function on the MCP server.
        
        Args:
            payload: Dictionary containing 'function' name and 'arguments'
            
        Returns:
            Dictionary containing the function result
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
        Connect to the MCP endpoint using SSE.
        
        Sets up the read and write streams and initializes the session.
        """
        # Create SSE client and extract read/write streams
        self._cm = sse_client(self.url)
        self.read_stream, self.write_stream = await self._cm.__aenter__()
        
        # Create and initialize MCP session
        self.session = ClientSession(self.read_stream, self.write_stream)
        await self.session.__aenter__()
        await self.session.initialize()

    async def call_function(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a function on the MCP server using the SSE connection.
        
        Args:
            payload: Dictionary with 'function' name and 'arguments'
            
        Returns:
            Dictionary containing the function result
        
        Raises:
            ValueError: If client is not connected
        """
        if not self.session:
            raise ValueError("Client not connected. Call connect() first.")
            
        # Validate payload using DTO
        validated_payload = FunctionPayloadDto(**payload)
        
        # Call the tool via MCP session
        result = await self.session.call_tool(
            name=validated_payload.function,
            **validated_payload.arguments
        )
        
        # Convert response to dict
        return result.model_dump()

    async def close(self) -> None:
        """
        Close the SSE connection and clean up resources.
        """
        if self.session:
            await self.session.close()
            await self.session.__aexit__(None, None, None)
            
        if hasattr(self, '_cm'):
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
        Connect to the MCP endpoint using HTTP streaming.
        
        Sets up the read and write streams and initializes the session.
        """
        # Create HTTP streaming client and extract read/write streams
        self._cm = streamablehttp_client(self.url)
        self.read_stream, self.write_stream, self._close_fn = await self._cm.__aenter__()
        
        # Create and initialize MCP session
        self.session = ClientSession(self.read_stream, self.write_stream)
        await self.session.__aenter__()
        await self.session.initialize()

    async def call_function(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a function on the MCP server using the HTTP streaming connection.
        
        Args:
            payload: Dictionary with 'function' name and 'arguments'
            
        Returns:
            Dictionary containing the function result
            
        Raises:
            ValueError: If client is not connected
        """
        if not self.session:
            raise ValueError("Client not connected. Call connect() first.")
            
        # Validate payload using DTO
        validated_payload = FunctionPayloadDto(**payload)
        
        # Call the tool via MCP session
        result = await self.session.call_tool(
            name=validated_payload.function,
            **validated_payload.arguments
        )
        
        # Convert response to dict
        return result.model_dump()

    async def close(self) -> None:
        """
        Close the HTTP streaming connection and clean up resources.
        """
        if self.session:
            await self.session.close()
            await self.session.__aexit__(None, None, None)
            
        # Call the explicit close function if available
        if self._close_fn:
            await self._close_fn()
            
        if hasattr(self, '_cm'):
            await self._cm.__aexit__(None, None, None)
            
        # Clean up references
        self.read_stream = None
        self.write_stream = None
        self.session = None
        self._close_fn = None
