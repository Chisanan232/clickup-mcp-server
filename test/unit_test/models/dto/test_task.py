from clickup_mcp.models.dto.custom_fields import CFText
from clickup_mcp.models.dto.task import TaskCreate


def test_task_create_to_payload_custom_fields_union_and_dict() -> None:
    # Mixed: union DTO + legacy dict
    cf1 = CFText(id="field_1", value="hello")
    legacy = {"id": "field_2", "value": 123}

    dto = TaskCreate(
        name="My Task",
        status="open",
        priority=2,
        assignees=[1, 2],
        due_date=1731200000000,
        custom_fields=[cf1, legacy],
    )

    payload = dto.to_payload()

    # Snake_case keys (per OpenAPI spec)
    assert "name" in payload
    assert "due_date" in payload
    assert "custom_fields" in payload

    # Ensure custom fields mapped to list of {id, value}
    assert isinstance(payload["custom_fields"], list)
    assert payload["custom_fields"][0] == {"id": "field_1", "value": "hello"}
    assert payload["custom_fields"][1] == {"id": "field_2", "value": 123}
