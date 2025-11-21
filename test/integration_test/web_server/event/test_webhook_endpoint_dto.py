from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from clickup_mcp.web_server.event.webhook import router as webhook_router

FIXTURE_DIR = Path(__file__).parents[3] / "contract_test" / "web_server" / "event" / "fixtures" / "clickup_webhooks"


# Discover all JSON fixtures under the directory at collection time
_FILES = sorted(FIXTURE_DIR.glob("*.json")) if FIXTURE_DIR.exists() else []


@pytest.mark.parametrize("fixture_path", _FILES, ids=[p.name for p in _FILES] if _FILES else None)
def test_clickup_webhook_endpoint_accepts_official_payload(fixture_path: Path) -> None:
    app = FastAPI()
    app.include_router(webhook_router)
    client = TestClient(app)

    body = fixture_path.read_text()
    resp = client.post(
        "/webhook/clickup",
        data=body,
        headers={"Content-Type": "application/json", "X-Request-Id": "req-1"},
    )

    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
