#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
import sys
import time
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


_DEFAULT_HEADERS = {
    "User-Agent": "clickup-mcp-fixtures/1.0 (+https://github.com/Chisanan232/clickup-mcp-server)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def fetch_html(url: str, *, timeout: float = 20.0, retries: int = 3, backoff: float = 1.0) -> str:
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            resp = httpx.get(url, timeout=timeout, headers=_DEFAULT_HEADERS, follow_redirects=True)
            resp.raise_for_status()
            return resp.text
        except Exception as exc:  # pragma: no cover - network variability
            last_exc = exc
            if attempt >= retries:
                break
            time.sleep(backoff * attempt)
    assert last_exc is not None
    raise last_exc


def _normalize_json(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, indent=2) + "\n"


def _maybe_extract_json(text: str) -> dict | None:
    s = text.strip()
    # Remove wrapping backticks if present
    if s.startswith("```") and s.endswith("```"):
        s = s.strip("`")
        s = s.strip()
    # Some sites put language hints like ```json\n...``` — already stripped above
    # Try to locate a JSON object/array substring
    if not (("{" in s and "}" in s) or ("[" in s and "]" in s)):
        return None
    # Prefer full object or array if it already looks proper
    candidate = s
    # If it's an array, keep as-is for parsing
    if s.lstrip().startswith("[") and s.rstrip().endswith("]"):
        candidate = s
    # Else if it's an object, keep as-is
    elif s.lstrip().startswith("{") and s.rstrip().endswith("}"):
        candidate = s
    else:
        # Try to slice from first { to last } to capture an object
        start = s.find("{")
        end = s.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        candidate = s[start : end + 1]
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        return None

    # Accept top-level dict with event
    if isinstance(parsed, dict):
        if isinstance(parsed.get("event"), str):
            return parsed
        # Sometimes nested under a key like 'payload'
        payload = parsed.get("payload")
        if isinstance(payload, dict) and isinstance(payload.get("event"), str):
            return payload
        return None

    # Accept list of objects; pick the first that has an 'event' string
    if isinstance(parsed, list):
        for item in parsed:
            if isinstance(item, dict) and isinstance(item.get("event"), str):
                return item
        return None

    return None


def extract_json_examples(html: str) -> List[dict]:
    soup = BeautifulSoup(html, "html.parser")
    candidates: List[str] = []
    seen_texts: set[str] = set()

    # Prefer explicit code/pre
    for tag in soup.select("pre code, code, pre"):
        text = tag.get_text("\n", strip=False)
        if text and text not in seen_texts:
            seen_texts.add(text)
            candidates.append(text)

    # Also include common Docusaurus/Prism code wrappers
    for sel in [
        'div[class*="theme-code-block"]',
        'div[class*="codeBlock"]',
        'div[class*="prism-code"]',
        'div[data-language="json"]',
        'div[class*="language-json"]',
    ]:
        for tag in soup.select(sel):
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


_EVENT_NAME_PATTERN = re.compile(r"\b((?:task|list|folder|space|goal|keyResult)[A-Z][A-Za-z]+)\s+payload\b")


def extract_event_names_from_text(html: str) -> List[str]:
    """Extract event names mentioned in page text like 'taskStatusUpdated payload'.

    Returns a list of unique event names in discovery order.
    """
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    seen: set[str] = set()
    names: List[str] = []
    for m in _EVENT_NAME_PATTERN.finditer(text):
        name = m.group(1)
        if name not in seen:
            seen.add(name)
            names.append(name)
    return names


def collect_remote_fixtures(urls: Iterable[str]) -> tuple[Dict[str, RemoteFixture], int]:
    """Return (mapping filename -> RemoteFixture, fetch_error_count).

    Handles deduplication and sequencing for multiple examples per event, and
    tolerates per-URL fetch errors.
    """
    # Track unique normalized payloads per event value
    by_event: Dict[str, List[RemoteFixture]] = {}
    fetch_errors = 0

    for url in urls:
        try:
            html = fetch_html(url)
        except Exception as exc:  # pragma: no cover - network variability
            print(f"[ERROR] Failed to fetch {url}: {exc}", file=sys.stderr)
            fetch_errors += 1
            continue

        examples = extract_json_examples(html)
        # 1) Add concrete examples from code blocks
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

        # 2) Synthesize minimal fixtures for events referenced in text but missing examples
        referenced = extract_event_names_from_text(html)
        for event in referenced:
            if event not in by_event:
                minimal = {"event": event}
                normalized = _normalize_json(minimal)
                by_event[event] = [RemoteFixture(filename=f"{event}.json", json_obj=minimal, normalized=normalized)]

    # Flatten
    out: Dict[str, RemoteFixture] = {}
    for lst in by_event.values():
        for rf in lst:
            out[rf.filename] = rf
    return out, fetch_errors


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

    remote, fetch_errors = collect_remote_fixtures(DOC_URLS)

    if ns.check:
        if fetch_errors == len(DOC_URLS):
            print("[ERROR] All sources failed to fetch. Aborting.", file=sys.stderr)
            return 2
        local = load_local_fixtures(fixtures_dir)
        diff_count = compare_fixtures(remote, local)
        return 1 if diff_count > 0 else 0

    # Default: write/update fixtures
    if fetch_errors > 0:
        print(f"[WARN] {fetch_errors} source(s) failed to fetch; writing what we have.", file=sys.stderr)
    write_fixtures(fixtures_dir, remote)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
