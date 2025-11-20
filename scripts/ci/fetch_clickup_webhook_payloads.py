#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import httpx
from bs4 import BeautifulSoup

DEFAULT_FIXTURES_DIR = Path("test/contract_test/web_server/event/fixtures/clickup_webhooks")

DOC_URLS: Tuple[str, ...] = (
    "https://developer.clickup.com/docs/webhooktaskpayloads",
    "https://developer.clickup.com/docs/webhooklistpayloads",
    "https://developer.clickup.com/docs/webhookfolderpayloads",
    "https://developer.clickup.com/docs/webhookspacepayloads",
    "https://developer.clickup.com/docs/webhookgoaltargetpayloads",
)


@dataclass(frozen=True)
class RemoteFixture:
    filename: str
    json_obj: dict
    normalized: str


def fetch_html(url: str, *, timeout: float = 20.0) -> str:
    resp = httpx.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def _normalize_json(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, indent=2) + "\n"


def _maybe_extract_json(text: str) -> dict | None:
    s = text.strip()
    # Remove wrapping backticks if present
    if s.startswith("```") and s.endswith("```"):
        s = s.strip("`")
        s = s.strip()
    # Some sites put language hints like ```json\n...``` — already stripped above
    # Try to locate a JSON object substring
    if not ("{" in s and "}" in s):
        return None
    # Prefer full object if it already looks proper
    candidate = s
    if not (candidate.lstrip().startswith("{") and candidate.rstrip().endswith("}")):
        # Try to slice from first { to last }
        start = s.find("{")
        end = s.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        candidate = s[start : end + 1]
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    if "event" not in parsed or not isinstance(parsed["event"], str):
        return None
    return parsed


def extract_json_examples(html: str) -> List[dict]:
    soup = BeautifulSoup(html, "html.parser")
    candidates: List[str] = []
    seen_texts: set[str] = set()

    # Prefer <code> blocks
    for tag in soup.find_all("code"):
        text = tag.get_text("\n", strip=False)
        if text and text not in seen_texts:
            seen_texts.add(text)
            candidates.append(text)

    # Include <pre> blocks that do not contain a <code> child
    for tag in soup.find_all("pre"):
        if tag.find("code") is not None:
            continue
        text = tag.get_text("\n", strip=False)
        if text and text not in seen_texts:
            seen_texts.add(text)
            candidates.append(text)

    results: List[dict] = []
    for txt in candidates:
        obj = _maybe_extract_json(txt)
        if obj is not None:
            results.append(obj)
    return results


def collect_remote_fixtures(urls: Iterable[str]) -> Dict[str, RemoteFixture]:
    """Return mapping filename -> RemoteFixture.

    Handles deduplication and sequencing for multiple examples per event.
    """
    # Track unique normalized payloads per event value
    by_event: Dict[str, List[RemoteFixture]] = {}

    for url in urls:
        html = fetch_html(url)
        examples = extract_json_examples(html)
        for payload in examples:
            event = payload.get("event")
            if not isinstance(event, str):
                continue
            normalized = _normalize_json(payload)
            existing = by_event.setdefault(event, [])
            # Skip duplicates
            if any(r.normalized == normalized for r in existing):
                continue
            # Determine filename (first -> event.json, second -> event_2.json, ...)
            index = len(existing) + 1
            filename = f"{event}.json" if index == 1 else f"{event}_{index}.json"
            existing.append(RemoteFixture(filename=filename, json_obj=payload, normalized=normalized))

    # Flatten
    out: Dict[str, RemoteFixture] = {}
    for lst in by_event.values():
        for rf in lst:
            out[rf.filename] = rf
    return out


def load_local_fixtures(fixtures_dir: Path) -> Dict[str, str]:
    """Return mapping filename -> normalized_json.

    If a file cannot be parsed as JSON, store its raw content under the same filename
    (callers can treat that as a difference).
    """
    local: Dict[str, str] = {}
    if not fixtures_dir.exists():
        return local
    for p in fixtures_dir.glob("*.json"):
        content = p.read_text()
        try:
            obj = json.loads(content)
            local[p.name] = _normalize_json(obj)
        except json.JSONDecodeError:
            # Keep raw content to signal difference
            local[p.name] = content
    return local


def write_fixtures(fixtures_dir: Path, remote: Dict[str, RemoteFixture]) -> None:
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    for name, rf in sorted(remote.items()):
        target = fixtures_dir / name
        if target.exists():
            current = target.read_text()
            if current == rf.normalized:
                continue
        print(f"[UPDATE] Writing {target}")
        target.write_text(rf.normalized)


def compare_fixtures(remote: Dict[str, RemoteFixture], local: Dict[str, str]) -> int:
    """Print differences; return number of differences found."""
    differences = 0

    # New or changed
    for name, rf in sorted(remote.items()):
        if name not in local:
            print(f"[NEW] {name} present in docs but missing locally")
            differences += 1
            continue
        if local[name] != rf.normalized:
            print(f"[CHANGED] {name} differs from docs")
            differences += 1

    # Stale
    for name in sorted(local.keys() - remote.keys()):
        print(f"[STALE] {name} exists locally but not in docs anymore")
        differences += 1

    if differences == 0:
        print("[INFO] No differences detected.")
    return differences


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch ClickUp webhook JSON example payloads.")
    parser.add_argument(
        "--fixtures-dir",
        default=str(DEFAULT_FIXTURES_DIR),
        help="Directory to write or check fixtures (default: test/contract_test/web_server/event/fixtures/clickup_webhooks)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check mode: do not write; exit 1 if differences found",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    ns = parse_args(argv or sys.argv[1:])
    fixtures_dir = Path(ns.fixtures_dir)

    remote = collect_remote_fixtures(DOC_URLS)

    if ns.check:
        local = load_local_fixtures(fixtures_dir)
        diff_count = compare_fixtures(remote, local)
        return 1 if diff_count > 0 else 0

    # Default: write/update fixtures
    write_fixtures(fixtures_dir, remote)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
