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
    return {"id": cf.id, "value": cf.value}


def cf_to_update_value(cf: CustomField) -> dict:
    return {"value": cf.value}
