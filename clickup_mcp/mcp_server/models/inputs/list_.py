"""MCP input models for list operations.

High-signal schemas for FastMCP with constraints and examples.
"""

from typing import Optional

from pydantic import BaseModel, Field


class ListCreateInput(BaseModel):
    """Create a list. HTTP: POST /folder/{folder_id}/list

    When to use: You know the parent folder and want to create a list. If you don’t know `folder_id`,
    call `workspace.list` → `space.list` → `folder.list_in_space` first.
    Constraints: `priority` 1..4; time fields are epoch ms.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"folder_id": "folder_1", "name": "Sprint Backlog", "status": "Open", "priority": 2}
            ]
        }
    }

    folder_id: str = Field(..., min_length=1, description="Parent folder ID.")
    name: str = Field(..., min_length=1, description="List name.")
    content: Optional[str] = Field(None, description="List description.")
    status: Optional[str] = Field(None, description="Status label.")
    priority: Optional[int] = Field(None, ge=1, le=4, description="1..4 priority.")
    assignee: Optional[int | str] = Field(None, description="Assignee user ID.")
    due_date: Optional[int] = Field(None, description="Due date (epoch ms).")
    due_date_time: Optional[bool] = Field(None, description="Whether due date includes time.")


class ListGetInput(BaseModel):
    """Get a list. HTTP: GET /list/{list_id}

    When to use: Retrieve list details by ID.
    """

    model_config = {
        "json_schema_extra": {"examples": [{"list_id": "list_1"}]}
    }

    list_id: str = Field(..., min_length=1, description="List ID.")


class ListUpdateInput(BaseModel):
    """Update a list. HTTP: PUT /list/{list_id}

    When to use: Change list metadata (name/content/status/priority/assignee/due fields).
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"list_id": "list_1", "name": "Sprint 12", "status": "In progress", "priority": 3}
            ]
        }
    }

    list_id: str = Field(..., min_length=1, description="List ID.")
    name: Optional[str] = Field(None, min_length=1, description="List name.")
    content: Optional[str] = Field(None, description="List description.")
    status: Optional[str] = Field(None, description="Status label.")
    priority: Optional[int] = Field(None, ge=1, le=4, description="1..4 priority.")
    assignee: Optional[int | str] = Field(None, description="Assignee user ID.")
    due_date: Optional[int] = Field(None, description="Due date (epoch ms).")
    due_date_time: Optional[bool] = Field(None, description="Whether due date includes time.")


class ListDeleteInput(BaseModel):
    """Delete a list. HTTP: DELETE /list/{list_id}

    When to use: Permanently remove a list (and associated tasks per permissions).
    """

    model_config = {
        "json_schema_extra": {"examples": [{"list_id": "list_1"}]}
    }

    list_id: str = Field(..., min_length=1, description="List ID.")


class ListListInFolderInput(BaseModel):
    """List lists in a folder. HTTP: GET /folder/{folder_id}/list

    When to use: Discover lists within a given folder.
    """

    model_config = {
        "json_schema_extra": {"examples": [{"folder_id": "folder_1"}]}
    }

    folder_id: str = Field(..., min_length=1, description="Folder ID.")


class ListListInSpaceFolderlessInput(BaseModel):
    """List folderless lists in a space. HTTP: GET /space/{space_id}/list

    When to use: Discover lists that exist directly under a space (not in folders).
    """

    model_config = {
        "json_schema_extra": {"examples": [{"space_id": "space_1"}]}
    }

    space_id: str = Field(..., min_length=1, description="Space ID.")


class ListAddTaskInput(BaseModel):
    """Add task to list (TIML). HTTP: POST /list/{list_id}/task/{task_id}

    When to use: TIML is enabled and you want to add an existing task to another list.
    """

    model_config = {
        "json_schema_extra": {"examples": [{"list_id": "list_2", "task_id": "task_123"}]}
    }

    list_id: str = Field(..., min_length=1, description="Target list ID.")
    task_id: str = Field(..., min_length=1, description="Existing task ID.")


class ListRemoveTaskInput(BaseModel):
    """Remove task from list (TIML). HTTP: DELETE /list/{list_id}/task/{task_id}

    When to use: TIML is enabled and you want to remove a task from a secondary list.
    """

    model_config = {
        "json_schema_extra": {"examples": [{"list_id": "list_2", "task_id": "task_123"}]}
    }

    list_id: str = Field(..., min_length=1, description="Target list ID.")
    task_id: str = Field(..., min_length=1, description="Existing task ID.")

