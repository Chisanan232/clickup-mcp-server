"""MCP input models for list operations.

High-signal schemas for FastMCP with constraints and examples.
"""

from typing import Optional

from pydantic import BaseModel, Field


class ListCreateInput(BaseModel):
    """
    Create a list. HTTP: POST /folder/{folder_id}/list

    When to use: You know the parent folder and want to create a list. If you don’t know `folder_id`,
    call `workspace.list` → `space.list` → `folder.list_in_space` first.

    Constraints:
        - `priority` must be between 1 and 4
        - Time fields are epoch milliseconds

    Attributes:
        folder_id: Parent folder ID
        name: List name
        content: Optional description
        status: Initial status label
        priority: Priority (1..4)
        assignee: Assignee user ID
        due_date: Due date in epoch ms
        due_date_time: Whether due date includes time

    Examples:
        # Minimal
        ListCreateInput(folder_id="folder_1", name="Sprint Backlog")

        # With scheduling
        ListCreateInput(folder_id="folder_1", name="Bugs", priority=2, due_date=1731523200000)
    """

    model_config = {
        "json_schema_extra": {
            "examples": [{"folder_id": "folder_1", "name": "Sprint Backlog", "status": "Open", "priority": 2}]
        }
    }

    folder_id: str = Field(..., min_length=1, description="Parent folder ID.", examples=["folder_1", "fld_abc"])
    name: str = Field(..., min_length=1, description="List name.", examples=["Sprint Backlog", "Bugs"])
    content: Optional[str] = Field(
        None, description="List description.", examples=["Backlog for sprint 12", "Bug queue"]
    )
    status: Optional[str] = Field(None, description="Status label.", examples=["Open", "In progress", "Done"])
    priority: Optional[int] = Field(None, ge=1, le=4, description="1..4 priority.", examples=[1, 2, 3, 4])
    assignee: Optional[int | str] = Field(None, description="Assignee user ID.", examples=[42, "usr_abc"])
    due_date: Optional[int] = Field(None, description="Due date (epoch ms).", examples=[1731523200000])
    due_date_time: Optional[bool] = Field(None, description="Whether due date includes time.", examples=[True, False])


class ListGetInput(BaseModel):
    """
    Get a list. HTTP: GET /list/{list_id}

    When to use: Retrieve list details by ID.

    Attributes:
        list_id: Target list ID

    Examples:
        ListGetInput(list_id="list_1")
    """

    model_config = {"json_schema_extra": {"examples": [{"list_id": "list_1"}]}}

    list_id: str = Field(..., min_length=1, description="List ID.", examples=["list_1", "lst_abc"])


class ListUpdateInput(BaseModel):
    """
    Update a list. HTTP: PUT /list/{list_id}

    When to use: Change list metadata (name/content/status/priority/assignee/due fields).

    Attributes:
        list_id: Target list ID
        name: New list name
        content: New description
        status: New status label
        priority: New priority (1..4)
        assignee: New assignee user ID
        due_date: New due date in epoch ms
        due_date_time: Whether due date includes time

    Examples:
        ListUpdateInput(list_id="list_1", name="Sprint 12", status="In progress", priority=3)
    """

    model_config = {
        "json_schema_extra": {
            "examples": [{"list_id": "list_1", "name": "Sprint 12", "status": "In progress", "priority": 3}]
        }
    }

    list_id: str = Field(..., min_length=1, description="List ID.", examples=["list_1", "lst_abc"])
    name: Optional[str] = Field(None, min_length=1, description="List name.", examples=["Sprint 12", "Bugs"])
    content: Optional[str] = Field(
        None, description="List description.", examples=["Scope for sprint 12", "Known issues"]
    )
    status: Optional[str] = Field(None, description="Status label.", examples=["Open", "In progress", "Done"])
    priority: Optional[int] = Field(None, ge=1, le=4, description="1..4 priority.", examples=[1, 2, 3, 4])
    assignee: Optional[int | str] = Field(None, description="Assignee user ID.", examples=[42, "usr_abc"])
    due_date: Optional[int] = Field(None, description="Due date (epoch ms).", examples=[1731523200000])
    due_date_time: Optional[bool] = Field(None, description="Whether due date includes time.", examples=[True, False])


class ListDeleteInput(BaseModel):
    """
    Delete a list. HTTP: DELETE /list/{list_id}

    When to use: Permanently remove a list (and associated tasks per permissions).

    Attributes:
        list_id: Target list ID

    Examples:
        ListDeleteInput(list_id="list_1")
    """

    model_config = {"json_schema_extra": {"examples": [{"list_id": "list_1"}]}}

    list_id: str = Field(
        ..., min_length=1, description="List ID.", json_schema_extra={"examples": ["list_1", "lst_abc"]}
    )


class ListListInFolderInput(BaseModel):
    """
    List lists in a folder. HTTP: GET /folder/{folder_id}/list

    When to use: Discover lists within a given folder.

    Attributes:
        folder_id: Parent folder ID

    Examples:
        ListListInFolderInput(folder_id="folder_1")
    """

    model_config = {"json_schema_extra": {"examples": [{"folder_id": "folder_1"}]}}

    folder_id: str = Field(..., min_length=1, description="Folder ID.", examples=["folder_1", "fld_abc"])


class ListListInSpaceFolderlessInput(BaseModel):
    """
    List folderless lists in a space. HTTP: GET /space/{space_id}/list

    When to use: Discover lists that exist directly under a space (not in folders).

    Attributes:
        space_id: Space ID

    Examples:
        ListListInSpaceFolderlessInput(space_id="space_1")
    """

    model_config = {"json_schema_extra": {"examples": [{"space_id": "space_1"}]}}

    space_id: str = Field(..., min_length=1, description="Space ID.", examples=["space_1", "spc_abc"])


class ListAddTaskInput(BaseModel):
    """
    Add task to list (TIML). HTTP: POST /list/{list_id}/task/{task_id}

    When to use: TIML is enabled and you want to add an existing task to another list.

    Attributes:
        list_id: Target list ID
        task_id: Existing task ID to add

    Examples:
        ListAddTaskInput(list_id="list_2", task_id="task_123")
    """

    model_config = {"json_schema_extra": {"examples": [{"list_id": "list_2", "task_id": "task_123"}]}}

    list_id: str = Field(..., min_length=1, description="Target list ID.", examples=["list_2", "lst_abc"])
    task_id: str = Field(..., min_length=1, description="Existing task ID.", examples=["task_123", "tsk_abc"])


class ListRemoveTaskInput(BaseModel):
    """
    Remove task from list (TIML). HTTP: DELETE /list/{list_id}/task/{task_id}

    When to use: TIML is enabled and you want to remove a task from a secondary list.

    Attributes:
        list_id: Target list ID
        task_id: Task ID to remove

    Examples:
        ListRemoveTaskInput(list_id="list_2", task_id="task_123")
    """

    model_config = {"json_schema_extra": {"examples": [{"list_id": "list_2", "task_id": "task_123"}]}}

    list_id: str = Field(
        ..., min_length=1, description="Target list ID.", json_schema_extra={"examples": ["list_2", "lst_abc"]}
    )
    task_id: str = Field(
        ..., min_length=1, description="Existing task ID.", json_schema_extra={"examples": ["task_123", "tsk_abc"]}
    )
