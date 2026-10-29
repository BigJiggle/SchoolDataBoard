"""Canvas LMS (Instructure) through its REST API and a personal access token."""

import re

from . import ConnectorError, http, in_window, item, normalize_base, parse_iso, raise_for_status

KIND = "canvas"
LABEL = "Canvas"
DETAIL = "Full detail: instructions, points, submission types, allowed file types and whether you've submitted."
FIELDS = [
    {"key": "base_url", "label": "Canvas address", "type": "url", "placeholder": "https://yourschool.instructure.com"},
    {"key": "token", "label": "Access token", "type": "password", "secret": True, "placeholder": "Paste your token"},
]
HELP = ("In Canvas open <b>Account → Settings</b>, scroll to <b>Approved Integrations</b> and click "
        "<b>+ New Access Token</b>. Give it a name (e.g. “School Dashboard”), generate it, and paste it here. "
        "If your school has disabled tokens, use the <b>Calendar feed</b> option instead (Canvas → Calendar → "
        "Calendar Feed).")

SUBMISSION_MAP = {
    "online_upload": "upload", "online_text_entry": "text", "online_url": "url", "media_recording": "media",
    "on_paper": "paper", "external_tool": "external_tool", "online_quiz": "quiz", "discussion_topic": "discussion",
    "student_annotation": "annotation", "none": "none", "not_graded": "none", "wiki_page": "none",
}


def _get_all(client, url: str, headers: dict, params: dict | None = None, limit_pages: int = 20) -> list:
    out = []
    for _ in range(limit_pages):
        resp = client.get(url, headers=headers, params=params)
        raise_for_status(resp, "Canvas")
        data = resp.json()
        if isinstance(data, dict) and data.get("errors"):
            raise ConnectorError(f"Canvas: {data['errors']}")
        out.extend(data if isinstance(data, list) else [data])
        nxt = re.search(r'<([^>]+)>;\s*rel="next"', resp.headers.get("link", ""))
        if not nxt:
            break
        url, params = nxt.group(1), None
    return out


def _setup(config: dict):
    base = normalize_base(config.get("base_url"), "Canvas")
    token = (config.get("token") or "").strip()
    if not token:
        raise ConnectorError("Paste a Canvas access token.")
    return base, {"Authorization": f"Bearer {token}"}


def check(config: dict) -> dict:
    base, headers = _setup(config)
    with http() as c:
        resp = c.get(f"{base}/api/v1/users/self", headers=headers)
        raise_for_status(resp, "Canvas")
        me = resp.json()
    return {"account": me.get("name") or me.get("short_name") or "Canvas user"}


def _status(sub: dict | None) -> str | None:
    if not sub:
        return None
    if sub.get("missing"):
        return "missing"
    state = sub.get("workflow_state")
    if state in ("submitted", "pending_review"):
        return "submitted"
    if state == "graded":
        return "graded"
    return "unsubmitted"


def fetch(config: dict, settings: dict) -> list[dict]:
    base, headers = _setup(config)
    items = []
    with http() as c:
        courses = _get_all(c, f"{base}/api/v1/courses", headers,
                           {"enrollment_state": "active", "per_page": 100, "include[]": "term"})
        for course in courses:
            if not isinstance(course, dict) or "id" not in course or course.get("access_restricted_by_date"):
                continue
            cname = course.get("name") or course.get("course_code") or "Course"
            assignments = _get_all(c, f"{base}/api/v1/courses/{course['id']}/assignments", headers,
                                   {"include[]": "submission", "per_page": 100, "order_by": "due_at"})
            for a in assignments:
                if not a.get("published", True):
                    continue
                due = parse_iso(a.get("due_at"))
                status = _status(a.get("submission"))
                if not in_window(due):
                    continue
                if due is None and status in ("submitted", "graded"):
                    continue
                types = [SUBMISSION_MAP.get(t, t) for t in a.get("submission_types") or []]
                kind = "quiz" if a.get("is_quiz_assignment") or "quiz" in types else (
                    "discussion" if "discussion" in types else "assignment")
                items.append(item(
                    f"assignment:{a['id']}", a.get("name"), course=cname, description=a.get("description") or "",
                    due=due, points=a.get("points_possible"), url=a.get("html_url", ""), kind=kind,
                    submission_types=types, allowed_extensions=a.get("allowed_extensions") or [],
                    platform_status=status))
    return items
