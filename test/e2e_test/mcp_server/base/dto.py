"""
Data Transfer Objects for MCP client communication.

This module provides the DTOs for MCP function calls and responses,
separating the data representation from business logic.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class FunctionPayloadDto(BaseModel):
    """
    Data transfer object for MCP function calls.
    
    Attributes:
        function: Name of the function to call
        arguments: Dictionary of function arguments
    """
    function: str = Field(..., description="Name of the function to call")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Function arguments")


class FunctionResponseDto(BaseModel):
    """
    Data transfer object for MCP function responses.
    
    Attributes:
        result: Result data from the function call
        error: Optional error message if the call failed
    """
    result: Any = Field(None, description="Result data from the function call")
    error: Optional[str] = Field(None, description="Error message if the call failed")
