"""Unit tests for Space DTO to_payload behavior.

This module verifies that:
- SpaceFeatures.to_payload() merges extra_features into the top-level and uses
  snake_case keys while excluding None values.
- SpaceCreate/SpaceUpdate.to_payload() include a structured features block when
  provided.
"""

from clickup_mcp.models.dto.space import (
    DueDatesFeature,
    SpaceCreate,
    SpaceFeatures,
    SpaceUpdate,
    TagsFeature,
)


def test_space_features_to_payload_merges_extra_and_snake_case() -> None:
    features = SpaceFeatures(
        due_dates=DueDatesFeature(enabled=True, start_date=True, remap_due_dates=False),
        extra_features={
            "some_feature": {"enabled": True, "custom": 1},
        },
    )

    payload = features.to_payload()

    # Known typed feature serialized with snake_case keys
    assert "due_dates" in payload
    assert isinstance(payload["due_dates"], dict)
    assert payload["due_dates"]["enabled"] is True
    assert payload["due_dates"]["start_date"] is True
    assert payload["due_dates"]["remap_due_dates"] is False

    # Extra features are merged into top-level and not nested under extra_features
    assert "some_feature" in payload
    assert payload["some_feature"]["enabled"] is True
    assert payload["some_feature"]["custom"] == 1
    assert "extra_features" not in payload


def test_space_create_to_payload_includes_features_block() -> None:
    features = SpaceFeatures(due_dates=DueDatesFeature(enabled=True))
    dto = SpaceCreate(name="My Space", multiple_assignees=True, features=features)

    payload = dto.to_payload()

    # Top-level fields
    assert payload["name"] == "My Space"
    assert payload["multiple_assignees"] is True

    # Features block should be present and contain snake_case keys
    assert "features" in payload
    assert payload["features"]["due_dates"]["enabled"] is True


def test_space_update_to_payload_partial_and_features() -> None:
    features = SpaceFeatures(tags=TagsFeature(enabled=False))
    dto = SpaceUpdate(name="Renamed", features=features)

    payload = dto.to_payload()

    # Only provided fields should be present (exclude None)
    assert payload["name"] == "Renamed"
    assert "color" not in payload

    # Features block with provided toggle
    assert payload["features"]["tags"]["enabled"] is False
