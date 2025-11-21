from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from clickup_mcp.web_server.event.webhook import router as webhook_router

FIXTURE_DIR = Path(__file__).parents[3] / "contract_test" / "web_server" / "event" / "fixtures" / "clickup_webhooks"


def test_clickup_webhook_endpoint_accepts_official_payload_task_created():
    app = FastAPI()
    app.include_router(webhook_router)
    client = TestClient(app)

    body = (FIXTURE_DIR / "taskCreated_full.json").read_text()
    resp = client.post(
        "/webhook/clickup",
        data=body,
        headers={"Content-Type": "application/json", "X-Request-Id": "req-1"},
    )

    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
