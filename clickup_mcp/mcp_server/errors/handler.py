"""Decorator to standardize MCP tool error handling and envelope.

MyPy-safe: preserves function signatures with ParamSpec overloads.
Supports both sync and async functions.
"""

from __future__ import annotations

import asyncio
from functools import wraps
from typing import Any, Awaitable, Callable, ParamSpec, TypeVar, get_type_hints, overload

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
    """Wrap a tool function to return ToolResponse and map exceptions to ToolIssue.

    - If the tool returns ToolResponse, it's passed through.
    - If it returns a bare result (pydantic model), it's wrapped with ok=True.
    - If it raises, it's converted to ok=False with mapped issues.
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
