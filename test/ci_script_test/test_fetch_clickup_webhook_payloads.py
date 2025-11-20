from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import pytest

import scripts.ci.fetch_clickup_webhook_payloads as crawler


def html_with_blocks(blocks: list[str]) -> str:
    parts = []
    for b in blocks:
        parts.append(f"<pre><code>{b}</code></pre>")
    return "\n".join(parts)


def test_extract_json_examples_parses_valid_event_payloads() -> None:
    valid1 = '{"event": "taskCreated", "foo": 1}'
    valid2_in_fence = """```json\n{\n  \"event\": \"listUpdated\", \n  \"bar\": true\n}\n```"""
    invalid_no_event = '{"not_event": 1}'
    not_json = "some text without json"

    html = html_with_blocks([valid1, valid2_in_fence, invalid_no_event, not_json])

    out = crawler.extract_json_examples(html)
    events = sorted(p["event"] for p in out)
    assert events == ["listUpdated", "taskCreated"]


def test_collect_remote_fixtures_dedup_and_numbering(monkeypatch: pytest.MonkeyPatch) -> None:
    # Two pages, same event appears twice with one duplicate and one distinct variant
    page1 = html_with_blocks(
        [
            '{"event": "taskUpdated", "a": 1}',
            '{"event": "taskUpdated", "a": 1}',  # dup
        ]
    )
    page2 = html_with_blocks(
        [
            '{"event": "taskUpdated", "a": 2}',  # distinct
            '{"event": "spaceCreated", "x": 0}',
        ]
    )

    pages: Dict[str, str] = {
        "u1": page1,
        "u2": page2,
    }

    def fake_fetch(url: str, *, timeout: float = 20.0) -> str:
        return pages[url]

    monkeypatch.setattr(crawler, "fetch_html", fake_fetch)

    remote = crawler.collect_remote_fixtures(["u1", "u2"])

    # Should have: taskUpdated.json, taskUpdated_2.json, spaceCreated.json
    assert set(remote.keys()) == {"taskUpdated.json", "taskUpdated_2.json", "spaceCreated.json"}

    # Numbering is deterministic based on discovery order
    assert json.loads(remote["taskUpdated.json"].normalized)["a"] == 1
    assert json.loads(remote["taskUpdated_2.json"].normalized)["a"] == 2


def test_write_load_compare_roundtrip(tmp_path: Path) -> None:
    fixtures_dir = tmp_path / "fixtures"
    remote = {
        "taskCreated.json": crawler.RemoteFixture(
            filename="taskCreated.json",
            json_obj={"event": "taskCreated", "k": 1},
            normalized=json.dumps({"event": "taskCreated", "k": 1}, sort_keys=True, indent=2) + "\n",
        )
    }

    # Write and load
    crawler.write_fixtures(fixtures_dir, remote)
    local = crawler.load_local_fixtures(fixtures_dir)
    assert set(local.keys()) == {"taskCreated.json"}
    assert local["taskCreated.json"] == remote["taskCreated.json"].normalized

    # No differences
    diff = crawler.compare_fixtures(remote, local)
    assert diff == 0

    # Change local to force CHANGED
    (fixtures_dir / "taskCreated.json").write_text('{\n  "event": "taskCreated", \n  "k": 2\n}\n')
    local2 = crawler.load_local_fixtures(fixtures_dir)
    diff2 = crawler.compare_fixtures(remote, local2)
    assert diff2 == 1

    # Add a stale local file
    (fixtures_dir / "stale.json").write_text("{}\n")
    local3 = crawler.load_local_fixtures(fixtures_dir)
    diff3 = crawler.compare_fixtures(remote, local3)
    # One changed + one stale => >= 2 differences (order independent)
    assert diff3 >= 2


def test_load_local_fixtures_handles_invalid_json(tmp_path: Path) -> None:
    fixtures_dir = tmp_path / "fx"
    fixtures_dir.mkdir()
    p = fixtures_dir / "broken.json"
    p.write_text("{ not json\n")

    local = crawler.load_local_fixtures(fixtures_dir)
    # Should include raw content for broken file
    assert set(local.keys()) == {"broken.json"}
    assert local["broken.json"].startswith("{ not json")


def test_main_noncheck_and_check_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Fake HTML with one payload
    html = html_with_blocks(['{"event": "goalCreated", "v": 1}'])

    def fake_fetch(url: str, *, timeout: float = 20.0) -> str:
        return html

    monkeypatch.setattr(crawler, "fetch_html", fake_fetch)

    fixtures_dir = tmp_path / "fixtures"

    # Non-check: writes files
    rc = crawler.main(["--fixtures-dir", str(fixtures_dir)])
    assert rc == 0
    created = list(fixtures_dir.glob("*.json"))
    assert any(p.name == "goalCreated.json" for p in created)

    # Check mode with no differences
    rc2 = crawler.main(["--fixtures-dir", str(fixtures_dir), "--check"])
    assert rc2 == 0

    # Modify file to force difference
    (fixtures_dir / "goalCreated.json").write_text('{\n  "event": "goalCreated", \n  "v": 2\n}\n')
    rc3 = crawler.main(["--fixtures-dir", str(fixtures_dir), "--check"])
    assert rc3 == 1


def test_collect_remote_fixtures_synthesizes_referenced_events(monkeypatch: pytest.MonkeyPatch) -> None:
    # HTML page with only textual references, no code blocks
    html = """
    <html><body>
    <h2>Task payloads</h2>
    <p>This webhook is triggered when tasks are created or updated.</p>
    <h3>taskStatusUpdated payload</h3>
    <p>We also send the taskUpdated payload.</p>
    <h3>taskAssigneeUpdated payload</h3>
    </body></html>
    """

    def fake_fetch(url: str, *, timeout: float = 20.0) -> str:
        return html

    monkeypatch.setattr(crawler, "fetch_html", fake_fetch)

    remote = crawler.collect_remote_fixtures(["dummy"])
    # Should synthesize minimal fixtures for the referenced events
    assert "taskStatusUpdated.json" in remote
    assert "taskAssigneeUpdated.json" in remote
    assert json.loads(remote["taskStatusUpdated.json"].normalized) == {"event": "taskStatusUpdated"}
