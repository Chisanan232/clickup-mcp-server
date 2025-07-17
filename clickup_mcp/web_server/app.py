"""
FastAPI Web Server for ClickUp MCP.

This module provides a FastAPI web server that mounts the MCP server
for exposing ClickUp functionality through a RESTful API.
"""

from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, Body, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from mcp.server import FastMCP

from clickup_mcp.mcp_server.app import mcp as clickup_mcp


def get_mcp_server() -> FastMCP:
    """
    Get the MCP server instance.
    
    Returns:
        The configured MCP server instance
    """
    return clickup_mcp


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application with MCP server mounted.
    
    Returns:
        Configured FastAPI application
    """
    # Create FastAPI app
    app = FastAPI(
        title="ClickUp MCP Server",
        description="A FastAPI web server that hosts a ClickUp MCP server for interacting with ClickUp API",
        version="0.1.0",
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Root endpoint for health checks
    @app.get("/", response_class=JSONResponse)
    async def root() -> Dict[str, str]:
        """
        Root endpoint providing basic health check.
        
        Returns:
            JSON response with server status
        """
        return {"status": "ok", "server": "ClickUp MCP Server"}
    
    # Mount MCP routes
    mcp_server = get_mcp_server()
    
    # Add MCP endpoints
    @app.get("/mcp/resources", response_class=JSONResponse)
    async def list_resources(request: Request) -> Dict[str, Any]:
        """
        List available MCP resources.
        
        Args:
            request: FastAPI request object
            
        Returns:
            JSON response containing available MCP resources
        """
        resources = mcp_server.list_resources()
        return {"resources": resources}
    
    @app.get("/mcp/tools", response_class=JSONResponse)
    async def get_tools(request: Request) -> Dict[str, Any]:
        """
        Get available MCP tools.
        
        Args:
            request: FastAPI request object
            
        Returns:
            JSON response containing available MCP tools
        """
        tools = mcp_server.list_tools()
        return {"tools": tools}
    
    @app.post("/mcp/execute/{tool_name}", response_class=JSONResponse)
    async def execute_tool(tool_name: str, params: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
        """
        Execute an MCP tool with the provided parameters.
        
        Args:
            tool_name: Name of the MCP tool to execute
            params: Parameters to pass to the tool
            
        Returns:
            JSON response with the result of the tool execution
        """
        # Handle both async and sync execute methods
        execute_method = mcp_server.execute
        
        # Check if the execute method is a coroutine function
        import inspect
        if inspect.iscoroutinefunction(execute_method):
            result = await execute_method(tool_name, **params)
        else:
            result = execute_method(tool_name, **params)
            
        return {"result": result}
    
    return app
