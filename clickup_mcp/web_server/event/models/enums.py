from enum import Enum


class ClickUpWebhookEventType(str, Enum):
    # Task events
    TASK_CREATED = "taskCreated"
    TASK_UPDATED = "taskUpdated"
    TASK_DELETED = "taskDeleted"
    TASK_STATUS_UPDATED = "taskStatusUpdated"
    TASK_ASSIGNEE_UPDATED = "taskAssigneeUpdated"
    TASK_DUE_DATE_UPDATED = "taskDueDateUpdated"
    TASK_TAG_UPDATED = "taskTagUpdated"
    TASK_MOVED = "taskMoved"
    TASK_COMMENT_POSTED = "taskCommentPosted"
    TASK_COMMENT_UPDATED = "taskCommentUpdated"
    TASK_TIME_ESTIMATE_UPDATED = "taskTimeEstimateUpdated"
    TASK_TIME_TRACKED_UPDATED = "taskTimeTrackedUpdated"
    TASK_PRIORITY_UPDATED = "taskPriorityUpdated"

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
