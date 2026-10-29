"""Schoology through its REST API (two-legged OAuth with the student's own API key and secret)."""

import secrets
import time
from datetime import datetime
from urllib.parse import quote
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from . import ConnectorError, http, in_window, item, raise_for_status

KIND = "schoology"
LABEL = "Schoology"
DETAIL = "Assignments, tests and discussions from every section you're enrolled in, with instructions and points."
API = "https://api.schoology.com/v1"
FIELDS = [
    {"key": "domain", "label": "Schoology address", "type": "url", "placeholder": "https://yourdistrict.schoology.com"},
    {"key": "consumer_key", "label": "Consumer key", "type": "text", "placeholder": "From your-school.schoology.com/api"},
    {"key": "consumer_secret", "label": "Consumer secret", "type": "password", "secret": True},
]
HELP = ("Sign in to Schoology, then open <b>https://&lt;your-school&gt;.schoology.com/api</b> (replace with your "
        "school's address). Copy the <b>Current Consumer Key</b> and <b>Current Consumer Secret</b> here. If that "
        "page isn't available, your district has turned off API keys: use the <b>Calendar feed</b> option instead "
        "(Schoology → Calendar → Export / iCal).")

TYPE_KIND = {"assessment": "quiz", "assessment_v2": "quiz", "quiz": "quiz", "test": "quiz", "discussion": "discussion"}


def _auth(config: dict) -> dict:
    key = (config.get("consumer_key") or "").strip()
    secret = (config.get("consumer_secret") or "").strip()
    if not key or not secret:
        raise ConnectorError("Enter your Schoology consumer key and secret.")
    # Schoology accepts PLAINTEXT signatures over HTTPS: the signature is "<consumer secret>&<token secret>".
    parts = {
        "oauth_consumer_key": key, "oauth_token": "", "oauth_nonce": secrets.token_hex(8),
        "oauth_timestamp": str(int(time.time())), "oauth_signature_method": "PLAINTEXT", "oauth_version": "1.0",
        "oauth_signature": quote(secret, safe="") + "%26",
    }
    header = "OAuth realm=\"Schoology API\"," + ",".join(f'{k}="{v}"' for k, v in parts.items())
    return {"Authorization": header}


def _get(client, url: str, config: dict, params: dict | None = None) -> dict:
    resp = client.get(url, headers=_auth(config), params=params)
    raise_for_status(resp, "Schoology")
    return resp.json() if resp.content else {}


def _me(client, config: dict) -> dict:
    return _get(client, f"{API}/users/me", config)


def check(config: dict) -> dict:
    with http() as c:
        me = _me(c, config)
    name = " ".join(x for x in (me.get("name_first"), me.get("name_last")) if x) or me.get("name_display")
    return {"account": name or "Schoology user"}


def _tz(settings: dict):
    try:
        return ZoneInfo(settings.get("timezone") or "UTC")
    except ZoneInfoNotFoundError:
        return ZoneInfo("UTC")


def _due(value: str | None, tz) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(value.strip(), fmt)
            if fmt == "%Y-%m-%d":
                dt = dt.replace(hour=23, minute=59)
            return dt.replace(tzinfo=tz)
        except ValueError:
            continue
    return None


def fetch(config: dict, settings: dict) -> list[dict]:
    tz = _tz(settings)
    domain = (config.get("domain") or "").strip().rstrip("/")
    if domain and not domain.startswith("http"):
        domain = "https://" + domain
    items = []
    with http() as c:
        me = _me(c, config)
        uid = me.get("uid") or me.get("id")
        if not uid:
            raise ConnectorError("Schoology didn't return your user id; check the key and secret.")
        sections = _get(c, f"{API}/users/{uid}/sections", config).get("section") or []
        for sec in sections:
            course = sec.get("course_title") or sec.get("section_title") or "Course"
            start = 0
            while True:
                data = _get(c, f"{API}/sections/{sec['id']}/assignments", config, {"start": start, "limit": 200})
                rows = data.get("assignment") or []
                for a in rows:
                    due = _due(a.get("due"), tz)
                    if not in_window(due):
                        continue
                    kind = TYPE_KIND.get(a.get("type") or "", "assignment")
                    types = []
                    if str(a.get("allow_dropbox")) == "1":
                        types.append("upload")
                    if kind == "quiz":
                        types.append("quiz")
                    if kind == "discussion":
                        types.append("discussion")
                    if not types:
                        types.append("paper" if str(a.get("allow_dropbox")) == "0" else "unknown")
                    status = "submitted" if str(a.get("completed") or "0") == "1" else None
                    url = a.get("web_url") or (f"{domain}/assignment/{a['id']}" if domain else "")
                    pts = a.get("max_points")
                    items.append(item(
                        f"assignment:{a['id']}", a.get("title"), course=course, description=a.get("description") or "",
                        due=due, points=float(pts) if pts not in (None, "") else None, url=url, kind=kind,
                        submission_types=types, platform_status=status))
                start += len(rows)
                if not rows or start >= int(data.get("total") or 0):
                    break
    return items
