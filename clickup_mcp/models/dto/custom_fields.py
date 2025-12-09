"""Typed representations of ClickUp custom field values.

This module defines discriminated-union DTOs for common ClickUp custom field
types and small helpers to serialize them into request payloads.

Notes:
- These DTOs are intended for use inside request models (e.g., TaskCreate).
- Serialization helpers output snake_case keys to match the OpenAPI spec.
"""

from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import Field

from .base import BaseDTO
from .common import EpochMs, UserId


class CFText(BaseDTO):
    """Custom field: Text.

    Attributes:
        id: Custom field ID
        type: Literal discriminator ("text")
        value: Text value

    Examples:
        cf = CFText(id="fld_text", value="hello")
    """
    id: str
    type: Literal["text"] = "text"
    value: str


class CFNumber(BaseDTO):
    """Custom field: Number.

    Attributes:
        id: Custom field ID
        type: Literal discriminator ("number")
        value: Numeric value (float)

    Examples:
        cf = CFNumber(id="fld_num", value=3.14)
    """
    id: str
    type: Literal["number"] = "number"
    value: float


class CFCheckbox(BaseDTO):
    """Custom field: Checkbox (boolean).

    Attributes:
        id: Custom field ID
        type: Literal discriminator ("checkbox")
        value: Boolean value

    Examples:
        cf = CFCheckbox(id="fld_flag", value=True)
    """
    id: str
    type: Literal["checkbox"] = "checkbox"
    value: bool


class CFURL(BaseDTO):
    """Custom field: URL.

    Attributes:
        id: Custom field ID
        type: Literal discriminator ("url")
        value: URL string

    Examples:
        cf = CFURL(id="fld_url", value="https://example.com")
    """
    id: str
    type: Literal["url"] = "url"
    value: str


class CFDropdown(BaseDTO):
    """Custom field: Dropdown.

    In ClickUp, dropdown selection values are typically option IDs (string).

    Attributes:
        id: Custom field ID
        type: Literal discriminator ("dropdown")
        value: Selected option ID

    Examples:
        cf = CFDropdown(id="fld_dd", value="opt_123")
    """
    id: str
    type: Literal["dropdown"] = "dropdown"
    # In ClickUp, dropdowns typically use option IDs
    value: str


class CFLabels(BaseDTO):
    """Custom field: Labels (multi-select).

    Attributes:
        id: Custom field ID
        type: Literal discriminator ("labels")
        value: List of selected label names

    Examples:
        cf = CFLabels(id="fld_labels", value=["backend", "priority:high"])
    """
    id: str
    type: Literal["labels"] = "labels"
    value: list[str]


class CFDate(BaseDTO):
    """Custom field: Date (epoch ms).

    Attributes:
        id: Custom field ID
        type: Literal discriminator ("date")
        value: Epoch milliseconds for the date (or None to clear)

    Examples:
        cf = CFDate(id="fld_due", value=1702080000000)
    """
    id: str
    type: Literal["date"] = "date"
    value: EpochMs | None


class CFUsers(BaseDTO):
    """Custom field: Users (multi-select users).

    Attributes:
        id: Custom field ID
        type: Literal discriminator ("users")
        value: List of user IDs

    Examples:
        cf = CFUsers(id="fld_users", value=[12345, 67890])
    """
    id: str
    type: Literal["users"] = "users"
    value: list[UserId]


CustomField = Annotated[
    Union[CFText, CFNumber, CFCheckbox, CFURL, CFDropdown, CFLabels, CFDate, CFUsers],
    Field(discriminator="type"),
]


def cf_to_create_payload(cf: CustomField) -> dict:
    """
    Convert a typed custom field DTO to the create-task payload shape.

    Returns a minimal dict with keys ``id`` and ``value`` suitable for
    ClickUp's task creation endpoint.

    Args:
        cf: A typed custom field instance (e.g., CFText, CFNumber)

    Returns:
        dict: Payload with ``{"id": <field_id>, "value": <value>}``

    Examples:
        cf_to_create_payload(CFText(id="fld", value="hello"))
        # {"id": "fld", "value": "hello"}
    """
    return {"id": cf.id, "value": cf.value}


def cf_to_update_value(cf: CustomField) -> dict:
    """
    Convert a typed custom field DTO to the update value shape.

    Returns a dict with key ``value`` as expected by ClickUp's
    set-custom-field endpoint.

    Args:
        cf: A typed custom field instance (e.g., CFDate)

    Returns:
        dict: Payload with ``{"value": <value>}``

    Examples:
        cf_to_update_value(CFDate(id="due", value=None))
        # {"value": null}
    """
    return {"value": cf.value}
