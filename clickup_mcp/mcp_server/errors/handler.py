"""
Decorator to standardize MCP tool error handling and envelope.

This module provides the @handle_tool_errors decorator that wraps MCP tool functions
to provide consistent error handling and response enveloping. It automatically:

1. Catches all exceptions and converts them to structured ToolIssue objects
2. Wraps bare results in ToolResponse envelopes
3. Preserves function signatures for MyPy type checking
4. Supports both sync and async functions
5. Maintains proper type annotations for IDE support

The decorator uses ParamSpec overloads to preserve function signatures while
ensuring all responses are wrapped in ToolResponse envelopes.

Key Features:
- **Exception Mapping**: Converts exceptions to ToolIssue with appropriate codes
- **Result Wrapping**: Wraps bare results in ToolResponse(ok=True, result=...)
- **Type Safety**: Preserves function signatures for MyPy and IDE support
- **Async Support**: Works with both sync and async functions
- **Schema Compatibility**: Updates return annotations for proper schema generation

Usage Examples:
    # Python - Decorate a tool function
    from clickup_mcp.mcp_server.errors.handler import handle_tool_errors

    @handle_tool_errors
    async def get_task(task_id: str) -> dict:
        # Function returns bare result
        return {"id": task_id, "name": "My Task"}

    # Calling the function
    response = await get_task("task_123")
    # response is ToolResponse[dict] with ok=True

    # Python - Error handling
    @handle_tool_errors
    async def delete_task(task_id: str) -> None:
        if not task_id:
            raise ValueError("Task ID required")
        # ... delete logic ...

    # Calling with error
    response = await delete_task("")
    # response is ToolResponse with ok=False and issues

    # Python - Sync function
    @handle_tool_errors
    def list_tasks() -> list[dict]:
        return [{"id": "1", "name": "Task 1"}]

    response = list_tasks()
    # response is ToolResponse[list[dict]] with ok=True
"""

from __future__ import annotations

import asyncio
from functools import wraps
from typing import (
    Any,
    Awaitable,
    Callable,
    ParamSpec,
    TypeVar,
    get_type_hints,
    overload,
)

from pydantic import BaseModel

from .mapping import map_exception
from .models import ToolResponse

P = ParamSpec("P")
R = TypeVar("R")
TModel = TypeVar("TModel", bound=BaseModel)


def _wrap_result(value: Any) -> ToolResponse[Any]:
    # If already wrapped, passthrough
    if isinstance(value, ToolResponse):
        return value
    return ToolResponse[Any](ok=True, result=value, issues=[])


@overload
def handle_tool_errors(
    func: Callable[P, TModel | ToolResponse[TModel] | None],
) -> Callable[P, ToolResponse[TModel]]: ...


@overload
def handle_tool_errors(
    func: Callable[P, Awaitable[TModel | ToolResponse[TModel] | None]],
) -> Callable[P, Awaitable[ToolResponse[TModel]]]: ...


def handle_tool_errors(  # type: ignore[misc]
    func: Callable[P, R] | Callable[P, Awaitable[R]],
) -> Callable[P, R] | Callable[P, Awaitable[R]]:
    """
    Wrap a tool function to return ToolResponse and map exceptions to ToolIssue.

    This decorator provides automatic error handling and response enveloping for MCP tool
    functions. It ensures all responses follow the standard ToolResponse format, with
    proper error codes and messages.

    Behavior:
    - If the tool returns ToolResponse, it's passed through unchanged
    - If it returns a bare result (pydantic model or other), it's wrapped with ok=True
    - If it raises an exception, it's converted to ok=False with mapped issues
    - Supports both sync and async functions transparently

    Type Safety:
    - Uses ParamSpec to preserve function signatures
    - Updates return annotations to ToolResponse[OriginalReturn]
    - Maintains MyPy compatibility with overloads
    - IDE tooltips show correct parameter and return types

    Exception Mapping:
    - Exceptions are mapped to ToolIssue via map_exception()
    - Each issue has a canonical code (VALIDATION_ERROR, NOT_FOUND, etc.)
    - Messages are end-user readable
    - Hints provide remediation guidance

    Args:
        func: The tool function to wrap (sync or async)

    Returns:
        Wrapped function that returns ToolResponse[T] where T is the original return type

    Usage Examples:
        # Python - Async tool with error handling
        from clickup_mcp.mcp_server.errors.handler import handle_tool_errors

        @handle_tool_errors
        async def get_task(task_id: str) -> dict:
            if not task_id:
                raise ValueError("Task ID required")
            return {"id": task_id, "name": "My Task"}

        # Successful call
        response = await get_task("task_123")
        assert response.ok == True
        assert response.result["id"] == "task_123"

        # Error call
        response = await get_task("")
        assert response.ok == False
        assert len(response.issues) > 0
        assert response.issues[0].code == "VALIDATION_ERROR"

        # Python - Sync tool
        @handle_tool_errors
        def list_tasks() -> list[dict]:
            return [{"id": "1", "name": "Task 1"}]

        response = list_tasks()
        assert response.ok == True
        assert isinstance(response.result, list)

        # Python - Tool that already returns ToolResponse
        from clickup_mcp.mcp_server.errors.models import ToolResponse

        @handle_tool_errors
        async def delete_task(task_id: str) -> ToolResponse[None]:
            if not task_id:
                issue = ToolIssue(code=IssueCode.VALIDATION_ERROR, message="ID required")
                return ToolResponse(ok=False, issues=[issue])
            # ... delete logic ...
            return ToolResponse(ok=True, result=None)

        response = await delete_task("task_123")
        # Response is passed through unchanged
    """

    # Important: bridge bare-return annotations to envelope schemas.
    #
    # Many frameworks (including our @mcp.tool integration) build response schemas
    # from a function's return annotation. We want authors to keep readable, bare
    # payload annotations (e.g., `List[Dict[str, Any]]`) while this decorator
    # always returns a ToolResponse[...] envelope at runtime.
    #
    # To align schema/validation with the actual returned envelope, we patch the
    # ORIGINAL function object's runtime __annotations__['return'] to
    # ToolResponse[OriginalReturn]. This keeps source code readable, but ensures
    # any annotation introspection (even via func.__wrapped__) sees the envelope.
    #
    # Notes:
    # - We only patch when the original annotation isn't already ToolResponse[...].
    # - We use include_extras=True so typing extras (e.g., Annotated) are retained.
    # - On failure, we silently skip (schema may be less specific, but remains valid).
    try:
        hints = get_type_hints(func, globalns=getattr(func, "__globals__", {}), include_extras=True)
    except Exception:
        hints = {}
    orig_ret_for_func = hints.get("return", Any)
    try:
        if "ToolResponse" not in str(orig_ret_for_func):
            func_ann = dict(getattr(func, "__annotations__", {}))
            func_ann["return"] = ToolResponse[orig_ret_for_func]  # type: ignore[valid-type]
            func.__annotations__ = func_ann
    except Exception:
        pass

    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs):
            try:
                value = await func(*args, **kwargs)
                return _wrap_result(value)
            except Exception as exc:  # noqa: BLE001
                issue = map_exception(exc)
                return ToolResponse(ok=False, issues=[issue])

        return async_wrapper

    @wraps(func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs):
        try:
            value = func(*args, **kwargs)
            return _wrap_result(value)
        except Exception as exc:  # noqa: BLE001
            issue = map_exception(exc)
            return ToolResponse(ok=False, issues=[issue])

    return sync_wrapper
