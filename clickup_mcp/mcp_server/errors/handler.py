"""Decorator to standardize MCP tool error handling and envelope.

MyPy-safe: preserves function signatures with ParamSpec overloads.
Supports both sync and async functions.
"""
from __future__ import annotations

import asyncio
from functools import wraps
from typing import Any, Awaitable, Callable, Optional, ParamSpec, TypeVar, overload

from pydantic import BaseModel

from .models import ToolResponse
from .mapping import map_exception

P = ParamSpec("P")
R = TypeVar("R")
TModel = TypeVar("TModel", bound=BaseModel)


def _wrap_result(value: Any) -> ToolResponse[Any]:
    # If already wrapped, passthrough
    if isinstance(value, ToolResponse):
        return value
    return ToolResponse[Any](ok=True, result=value, issues=[])


@overload
def handle_tool_errors(func: Callable[P, TModel | ToolResponse[TModel] | None]) -> Callable[P, ToolResponse[TModel]]: ...


@overload
def handle_tool_errors(func: Callable[P, Awaitable[TModel | ToolResponse[TModel] | None]]) -> Callable[P, Awaitable[ToolResponse[TModel]]]: ...


def handle_tool_errors(
    func: Callable[P, R] | Callable[P, Awaitable[R]],
) -> Callable[P, R] | Callable[P, Awaitable[R]]:
    """Wrap a tool function to return ToolResponse and map exceptions to ToolIssue.

    - If the tool returns ToolResponse, it's passed through.
    - If it returns a bare result (pydantic model), it's wrapped with ok=True.
    - If it raises, it's converted to ok=False with mapped issues.
    """

    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs):  # type: ignore[misc]
            try:
                value = await func(*args, **kwargs)  # type: ignore[misc]
                return _wrap_result(value)
            except Exception as exc:  # noqa: BLE001
                issue = map_exception(exc)
                return ToolResponse(ok=False, issues=[issue])

        return async_wrapper  # type: ignore[return-value]

    @wraps(func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs):  # type: ignore[misc]
        try:
            value = func(*args, **kwargs)  # type: ignore[misc]
            return _wrap_result(value)
        except Exception as exc:  # noqa: BLE001
            issue = map_exception(exc)
            return ToolResponse(ok=False, issues=[issue])

    return sync_wrapper  # type: ignore[return-value]
