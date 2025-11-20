from enum import Enum


class ClickUpWebhookEventType(str, Enum):
    # Task events
    TASK_CREATED = "taskCreated"
    TASK_UPDATED = "taskUpdated"
    TASK_DELETED = "taskDeleted"
    TASK_STATUS_UPDATED = "taskStatusUpdated"

    # List events
    LIST_CREATED = "listCreated"
    LIST_UPDATED = "listUpdated"
    LIST_DELETED = "listDeleted"

    # Folder events
    FOLDER_CREATED = "folderCreated"
    FOLDER_UPDATED = "folderUpdated"
    FOLDER_DELETED = "folderDeleted"

    # Space events
    SPACE_CREATED = "spaceCreated"
    SPACE_UPDATED = "spaceUpdated"
    SPACE_DELETED = "spaceDeleted"

    # Goal events
    GOAL_CREATED = "goalCreated"
    GOAL_UPDATED = "goalUpdated"
    GOAL_DELETED = "goalDeleted"

    # Key Result events
    KEY_RESULT_CREATED = "keyResultCreated"
    KEY_RESULT_UPDATED = "keyResultUpdated"
    KEY_RESULT_DELETED = "keyResultDeleted"
