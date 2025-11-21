import inspect
from typing import Awaitable, Callable, Protocol

from clickup_mcp.web_server.event.models import (
    ClickUpWebhookEvent,
    ClickUpWebhookEventType,
)

from .registry import get_registry

# Type aliases for clarity (human-friendly)
EventReturn = object
SyncHandler = Callable[[ClickUpWebhookEvent], EventReturn]
AsyncHandler = Callable[[ClickUpWebhookEvent], Awaitable[EventReturn]]
Handler = Callable[[ClickUpWebhookEvent], EventReturn | Awaitable[EventReturn]]


class _HandlerFn(Protocol):
    def __call__(self, event: ClickUpWebhookEvent, /) -> EventReturn | Awaitable[EventReturn]: ...


def ensure_async(fn: _HandlerFn) -> AsyncHandler:
    if inspect.iscoroutinefunction(fn):
        return fn  # type: ignore[return-value]

    async def wrapper(event: ClickUpWebhookEvent) -> None:
        fn(event)

    return wrapper


class ClickUpEventDecorator:
    def __call__(self, event_type: ClickUpWebhookEventType):
        """
        Enum-based usage:

            @clickup_event(ClickUpWebhookEventType.TASK_STATUS_UPDATED)
            async def handler(event: ClickUpWebhookEvent) -> None:
                ...
        """

        def decorator(func: Handler):  # type: ignore[override]
            async_fn = ensure_async(func)
            get_registry().register(event_type, async_fn)
            # Return original function to preserve user function identity
            return func

        return decorator

    # ----- Explicit attribute-style decorators (one per enum member) -----
    # Task events
    def task_created(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'taskCreated' webhook events."""
        return self(ClickUpWebhookEventType.TASK_CREATED)(fn)

    def task_updated(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'taskUpdated' webhook events."""
        return self(ClickUpWebhookEventType.TASK_UPDATED)(fn)

    def task_deleted(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'taskDeleted' webhook events."""
        return self(ClickUpWebhookEventType.TASK_DELETED)(fn)

    def task_status_updated(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'taskStatusUpdated' webhook events."""
        return self(ClickUpWebhookEventType.TASK_STATUS_UPDATED)(fn)

    def task_assignee_updated(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'taskAssigneeUpdated' webhook events."""
        return self(ClickUpWebhookEventType.TASK_ASSIGNEE_UPDATED)(fn)

    def task_due_date_updated(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'taskDueDateUpdated' webhook events."""
        return self(ClickUpWebhookEventType.TASK_DUE_DATE_UPDATED)(fn)

    def task_tag_updated(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'taskTagUpdated' webhook events."""
        return self(ClickUpWebhookEventType.TASK_TAG_UPDATED)(fn)

    def task_moved(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'taskMoved' webhook events."""
        return self(ClickUpWebhookEventType.TASK_MOVED)(fn)

    def task_comment_posted(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'taskCommentPosted' webhook events."""
        return self(ClickUpWebhookEventType.TASK_COMMENT_POSTED)(fn)

    def task_comment_updated(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'taskCommentUpdated' webhook events."""
        return self(ClickUpWebhookEventType.TASK_COMMENT_UPDATED)(fn)

    def task_time_estimate_updated(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'taskTimeEstimateUpdated' webhook events."""
        return self(ClickUpWebhookEventType.TASK_TIME_ESTIMATE_UPDATED)(fn)

    def task_time_tracked_updated(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'taskTimeTrackedUpdated' webhook events."""
        return self(ClickUpWebhookEventType.TASK_TIME_TRACKED_UPDATED)(fn)

    def task_priority_updated(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'taskPriorityUpdated' webhook events."""
        return self(ClickUpWebhookEventType.TASK_PRIORITY_UPDATED)(fn)

    # List events
    def list_created(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'listCreated' webhook events."""
        return self(ClickUpWebhookEventType.LIST_CREATED)(fn)

    def list_updated(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'listUpdated' webhook events."""
        return self(ClickUpWebhookEventType.LIST_UPDATED)(fn)

    def list_deleted(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'listDeleted' webhook events."""
        return self(ClickUpWebhookEventType.LIST_DELETED)(fn)

    # Folder events
    def folder_created(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'folderCreated' webhook events."""
        return self(ClickUpWebhookEventType.FOLDER_CREATED)(fn)

    def folder_updated(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'folderUpdated' webhook events."""
        return self(ClickUpWebhookEventType.FOLDER_UPDATED)(fn)

    def folder_deleted(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'folderDeleted' webhook events."""
        return self(ClickUpWebhookEventType.FOLDER_DELETED)(fn)

    # Space events
    def space_created(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'spaceCreated' webhook events."""
        return self(ClickUpWebhookEventType.SPACE_CREATED)(fn)

    def space_updated(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'spaceUpdated' webhook events."""
        return self(ClickUpWebhookEventType.SPACE_UPDATED)(fn)

    def space_deleted(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'spaceDeleted' webhook events."""
        return self(ClickUpWebhookEventType.SPACE_DELETED)(fn)

    # Goal events
    def goal_created(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'goalCreated' webhook events."""
        return self(ClickUpWebhookEventType.GOAL_CREATED)(fn)

    def goal_updated(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'goalUpdated' webhook events."""
        return self(ClickUpWebhookEventType.GOAL_UPDATED)(fn)

    def goal_deleted(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'goalDeleted' webhook events."""
        return self(ClickUpWebhookEventType.GOAL_DELETED)(fn)

    # Key Result events
    def key_result_created(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'keyResultCreated' webhook events."""
        return self(ClickUpWebhookEventType.KEY_RESULT_CREATED)(fn)

    def key_result_updated(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'keyResultUpdated' webhook events."""
        return self(ClickUpWebhookEventType.KEY_RESULT_UPDATED)(fn)

    def key_result_deleted(self, fn: Handler) -> Handler:
        """Decorator for ClickUp 'keyResultDeleted' webhook events."""
        return self(ClickUpWebhookEventType.KEY_RESULT_DELETED)(fn)

    # Fallback for unknown attributes (kept for robustness)
    def __getattr__(self, name: str):
        enum_name = name.upper()
        try:
            event_type = ClickUpWebhookEventType[enum_name]
        except KeyError as exc:
            raise AttributeError(f"Unknown ClickUp webhook event alias: {name}") from exc
        return self(event_type)

    # Help IDEs and dir() show decorator attributes explicitly
    def __dir__(self):  # pragma: no cover
        base = set(super().__dir__())
        for et in ClickUpWebhookEventType:
            base.add(et.name.lower())
        return sorted(base)


clickup_event = ClickUpEventDecorator()

__all__ = ["clickup_event"]
