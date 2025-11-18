"""
Space DTOs for ClickUp API requests and responses.

These DTOs handle serialization/deserialization of Space data
for API interactions.
"""

from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO

PROPERTY_NAME_DESCRIPTION: str = "The name of the space"
PROPERTY_MULTIPLE_ASSIGNEES_DESCRIPTION: str = "Whether multiple assignees are allowed"


class FeatureToggle(BaseRequestDTO):
    """Base toggle for a Space feature."""

    enabled: bool = Field(default=True, description="Whether this feature is enabled")


class DueDatesFeature(FeatureToggle):
    start_date: bool | None = Field(default=None)
    remap_due_dates: bool | None = Field(default=None)
    remap_closed_due_date: bool | None = Field(default=None)


class TimeTrackingFeature(FeatureToggle):
    required: bool | None = Field(default=None)


class TagsFeature(FeatureToggle):
    pass


class TimeEstimatesFeature(FeatureToggle):
    pass


class ChecklistsFeature(FeatureToggle):
    pass


class CustomFieldsFeature(FeatureToggle):
    pass


class PrioritiesFeature(FeatureToggle):
    pass


class DependenciesFeature(FeatureToggle):
    pass


class SprintsFeature(FeatureToggle):
    pass


class SpaceFeatures(BaseRequestDTO):
    """Typed container for Space feature configuration.

    Notes:
    - All JSON keys are serialized in snake_case to match the ClickUp OpenAPI spec.
    - Unknown feature blobs can be provided via ``extra_features`` and are merged
      into the top-level payload produced by ``to_payload()``.
    - This object can act like a mapping for backward-compat tests via
      ``_as_legacy_dict()``, ``__contains__``, and ``__getitem__``.
    """

    due_dates: Optional[DueDatesFeature] = None
    time_tracking: Optional[TimeTrackingFeature] = None
    tags: Optional[TagsFeature] = None
    time_estimates: Optional[TimeEstimatesFeature] = None
    checklists: Optional[ChecklistsFeature] = None
    custom_fields: Optional[CustomFieldsFeature] = None
    priorities: Optional[PrioritiesFeature] = None
    dependencies: Optional[DependenciesFeature] = None
    sprints: Optional[SprintsFeature] = None
    extra_features: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        """Serialize features to a request payload.

        Behavior:
        - Uses snake_case keys and excludes ``None`` values.
        - Merges ``extra_features`` into the top-level dict to match ClickUp's
          expected payload shape for feature toggles.
        """
        # Dump with snake_case keys
        payload: dict[str, Any] = self.model_dump(exclude_none=True)
        # Remove extra_features key and merge its contents into the top-level features object
        extra = payload.pop("extra_features", None)
        if isinstance(extra, dict):
            payload.update(extra)
        return payload

    # Back-compat: Behave like a mapping for tests expecting dict semantics
    def _as_legacy_dict(self) -> dict[str, Any]:
        """Return a dict view used by legacy tests/consumers.

        Produces a best-effort mapping combining typed feature toggles, any
        unknown attributes attached to this instance, and the "extra_features"
        blob, all as snake_case keys.
        """
        result: dict[str, Any] = {}
        typed_keys = [
            "due_dates",
            "time_tracking",
            "tags",
            "time_estimates",
            "checklists",
            "custom_fields",
            "priorities",
            "dependencies",
            "sprints",
        ]
        # Include known typed features
        for key in typed_keys:
            val = getattr(self, key, None)
            if val is not None:
                # Dump nested model with snake_case keys to match legacy tests
                result[key] = val.model_dump(exclude_none=True, by_alias=False)
        # Include unknown/extra feature blobs captured as attributes
        for key, val in self.__dict__.items():
            if key in typed_keys or key in {"extra_features"} or key.startswith("_"):
                continue
            result[key] = val
        # Merge explicitly provided extras
        result.update(self.extra_features)
        return result

    def __contains__(self, key: str) -> bool:  # support 'in' checks in tests
        """Support ``in`` checks against the legacy dict view."""
        return key in self._as_legacy_dict()

    def __getitem__(self, key: str) -> Any:  # support indexing like a dict
        """Support ``[]`` access via the legacy dict view."""
        return self._as_legacy_dict()[key]

    def keys(self):  # optional helper for iteration
        """Return keys of the legacy dict view (for iteration/testing)."""
        return self._as_legacy_dict().keys()


class SpaceCreate(BaseRequestDTO):
    """DTO for creating a new space.

    POST /team/{team_id}/space
    https://developer.clickup.com/reference/createspace
    """

    name: str = Field(description=PROPERTY_NAME_DESCRIPTION)
    multiple_assignees: bool = Field(default=False, description=PROPERTY_MULTIPLE_ASSIGNEES_DESCRIPTION)
    color: str | None = Field(default=None, description="Hex color for the space")
    features: SpaceFeatures | None = Field(default=None, description="Features to enable for this space")

    def to_payload(self) -> dict[str, Any]:
        """Serialize to request payload using snake_case keys.

        If ``features`` is provided, its structured payload from
        ``SpaceFeatures.to_payload()`` is included under the ``features`` key.
        """
        payload = super().to_payload()
        # Inject typed features payload
        if self.features is not None:
            payload["features"] = self.features.to_payload()
        return payload


class SpaceUpdate(BaseRequestDTO):
    """DTO for updating an existing space.

    PUT /space/{space_id}
    """

    name: str | None = Field(default=None, description=PROPERTY_NAME_DESCRIPTION)
    private: bool | None = Field(default=None, description="Whether the space is private")
    multiple_assignees: bool | None = Field(default=None, description=PROPERTY_MULTIPLE_ASSIGNEES_DESCRIPTION)
    color: str | None = Field(default=None, description="Hex color for the space")
    features: SpaceFeatures | None = Field(default=None, description="Updated features configuration")

    def to_payload(self) -> dict[str, Any]:
        """Serialize only provided fields (exclude ``None``) using snake_case keys.

        If ``features`` is provided, its structured payload from
        ``SpaceFeatures.to_payload()`` is included under the ``features`` key.
        """
        payload = super().to_payload()
        if self.features is not None:
            payload["features"] = self.features.to_payload()
        return payload


class SpaceResp(BaseResponseDTO):
    """DTO for space API responses.

    Represents a space returned from the ClickUp API.
    """

    id: str = Field(description="The unique identifier for the space")
    name: str = Field(description=PROPERTY_NAME_DESCRIPTION)
    private: bool = Field(default=False, description="Whether the space is private")

    # Typed status entries for clarity while allowing extra fields
    class SpaceStatus(BaseResponseDTO):
        id: str | None = Field(default=None)
        status: str | None = Field(default=None)
        type: str | None = Field(default=None)
        color: str | None = Field(default=None)
        orderindex: int | None = Field(default=None)

    statuses: List[SpaceStatus] = Field(default_factory=list, description="The statuses defined for this space")
    multiple_assignees: bool = Field(default=False, description=PROPERTY_MULTIPLE_ASSIGNEES_DESCRIPTION)
    # Use typed features container for responses as well
    features: SpaceFeatures | None = Field(default=None, description="Features enabled for this space")
    team_id: str | None = Field(default=None, description="The team ID this space belongs to")
