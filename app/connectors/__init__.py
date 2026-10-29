"""Connectors turn a school platform account (or calendar feed) into a list of normalized assignments.

Every connector module exposes:
    KIND, LABEL, FIELDS        - what the Connections page shows and asks for
    check(config) -> dict       - verify credentials, return {"account": "..."}
    fetch(config, settings) -> list[dict]   - normalized items (see `item()`)
"""

from datetime import datetime, timedelta, timezone

import httpx

# Tests swap in httpx.MockTransport here.
transport: httpx.BaseTransport | None = None

LOOKBACK_DAYS = 21   # keep recently-due work (late / missing) on the board
LOOKAHEAD_DAYS = 120


class ConnectorError(Exception):
    """A problem the person can fix (bad token, wrong URL...). The message is shown as-is."""


def http() -> httpx.Client:
    return httpx.Client(timeout=30, follow_redirects=True, transport=transport,
                        headers={"User-Agent": "SchoolDashboard/1.0", "Accept": "application/json"})


def window() -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)
    return now - timedelta(days=LOOKBACK_DAYS), now + timedelta(days=LOOKAHEAD_DAYS)


def utc_iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def in_window(due: datetime | None) -> bool:
    if due is None:
        return True
    start, end = window()
    return start <= due <= end


def item(external_id, title, *, course="", description="", due: datetime | None = None, points=None, url="",
         kind="assignment", submission_types=None, allowed_extensions=None, platform_status=None) -> dict:
    return {
        "external_id": str(external_id), "title": (title or "Untitled").strip(), "course": (course or "").strip(),
        "description": description or "", "due_at": utc_iso(due), "points": points, "url": url or "",
        "kind": kind, "submission_types": submission_types or [], "allowed_extensions": allowed_extensions or [],
        "platform_status": platform_status,
    }


def raise_for_status(resp: httpx.Response, service: str):
    if resp.status_code in (401, 403):
        raise ConnectorError(f"{service} rejected the credentials (HTTP {resp.status_code}). Check the token/key and try again.")
    if resp.status_code == 404:
        raise ConnectorError(f"{service} returned 'not found' for {resp.request.url}. Check the school address.")
    if resp.status_code >= 400:
        raise ConnectorError(f"{service} returned HTTP {resp.status_code}.")


def normalize_base(url: str, service: str) -> str:
    url = (url or "").strip().rstrip("/")
    if not url:
        raise ConnectorError(f"Enter your school's {service} address.")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


from . import canvas, demo, ical, moodle, schoology  # noqa: E402

REGISTRY = {m.KIND: m for m in (canvas, schoology, moodle, ical, demo)}


def describe() -> list[dict]:
    return [{"kind": m.KIND, "label": m.LABEL, "fields": m.FIELDS, "help": getattr(m, "HELP", ""),
             "detail": getattr(m, "DETAIL", "")} for m in REGISTRY.values()]
