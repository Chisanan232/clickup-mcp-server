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
    id: str
    type: Literal["text"] = "text"
    value: str


class CFNumber(BaseDTO):
    id: str
    type: Literal["number"] = "number"
    value: float


class CFCheckbox(BaseDTO):
    id: str
    type: Literal["checkbox"] = "checkbox"
    value: bool


class CFURL(BaseDTO):
    id: str
    type: Literal["url"] = "url"
    value: str


class CFDropdown(BaseDTO):
    id: str
    type: Literal["dropdown"] = "dropdown"
    # In ClickUp, dropdowns typically use option IDs
    value: str


class CFLabels(BaseDTO):
    id: str
    type: Literal["labels"] = "labels"
    value: list[str]


class CFDate(BaseDTO):
    id: str
    type: Literal["date"] = "date"
    value: EpochMs | None


class CFUsers(BaseDTO):
    id: str
    type: Literal["users"] = "users"
    value: list[UserId]


CustomField = Annotated[
    Union[CFText, CFNumber, CFCheckbox, CFURL, CFDropdown, CFLabels, CFDate, CFUsers],
    Field(discriminator="type"),
]


def cf_to_create_payload(cf: CustomField) -> dict:
    """Convert a typed custom field DTO to the create-task payload shape.

    Returns a minimal dict with keys ``id`` and ``value`` suitable for
    ClickUp's task creation endpoint.
    """
    return {"id": cf.id, "value": cf.value}


def cf_to_update_value(cf: CustomField) -> dict:
    """Convert a typed custom field DTO to the update value shape.

    Returns a dict with key ``value`` as expected by ClickUp's
    set-custom-field endpoint.
    """
    return {"value": cf.value}
