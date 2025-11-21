import pytest
from clickup_mcp.web_server.event.handler import get_registry


@pytest.fixture(autouse=True)
def reset_clickup_event_registry():
    registry = get_registry()
    registry.clear()
    yield
    registry.clear()
