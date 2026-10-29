"""Moodle through its web-service API and the student's mobile-app security key."""

from datetime import datetime, timezone

from . import ConnectorError, http, item, normalize_base, raise_for_status, window

KIND = "moodle"
LABEL = "Moodle"
DETAIL = "Everything on your Moodle timeline that still needs action: assignments, quizzes and forum posts."
FIELDS = [
    {"key": "base_url", "label": "Moodle address", "type": "url", "placeholder": "https://moodle.yourschool.edu"},
    {"key": "token", "label": "Security key", "type": "password", "secret": True},
]
HELP = ("In Moodle open your profile menu → <b>Preferences → Security keys</b> and copy the key for "
        "<b>Moodle mobile web service</b>. (If there's no such page, open the Moodle app once, or ask your school "
        "whether mobile access is enabled, or use the <b>Calendar feed</b> option: Calendar → Export calendar.)")

MODULE_KIND = {"quiz": "quiz", "forum": "discussion", "hsuforum": "discussion", "assign": "assignment",
               "workshop": "assignment", "lesson": "assignment", "h5pactivity": "quiz", "lti": "assignment"}
MODULE_SUBMIT = {"assign": ["upload", "text"], "quiz": ["quiz"], "forum": ["discussion"], "lti": ["external_tool"],
                 "workshop": ["upload"]}


def _call(client, base: str, token: str, function: str, **params):
    resp = client.post(f"{base}/webservice/rest/server.php",
                       data={"wstoken": token, "wsfunction": function, "moodlewsrestformat": "json", **params})
    raise_for_status(resp, "Moodle")
    data = resp.json()
    if isinstance(data, dict) and data.get("exception"):
        msg = data.get("message") or data.get("errorcode")
        raise ConnectorError(f"Moodle: {msg}")
    return data


def _setup(config: dict):
    base = normalize_base(config.get("base_url"), "Moodle")
    token = (config.get("token") or "").strip()
    if not token:
        raise ConnectorError("Paste your Moodle security key.")
    return base, token


def check(config: dict) -> dict:
    base, token = _setup(config)
    with http() as c:
        info = _call(c, base, token, "core_webservice_get_site_info")
    return {"account": f"{info.get('fullname', 'Moodle user')} @ {info.get('sitename', base)}"}


def fetch(config: dict, settings: dict) -> list[dict]:
    base, token = _setup(config)
    start, end = window()
    with http() as c:
        data = _call(c, base, token, "core_calendar_get_action_events_by_timesort",
                     timesortfrom=int(start.timestamp()), timesortto=int(end.timestamp()), limitnum=100)
    items = []
    for ev in data.get("events") or []:
        module = ev.get("modulename") or ""
        due = datetime.fromtimestamp(ev["timesort"], tz=timezone.utc) if ev.get("timesort") else None
        title = ev.get("activityname") or ev.get("name") or "Activity"
        items.append(item(
            f"event:{ev.get('instance') or ev.get('id')}:{module}", title,
            course=(ev.get("course") or {}).get("fullname", ""), description=ev.get("description") or "",
            due=due, url=ev.get("url") or (ev.get("action") or {}).get("url", ""),
            kind=MODULE_KIND.get(module, "assignment"), submission_types=MODULE_SUBMIT.get(module, ["unknown"]),
            platform_status="unsubmitted" if (ev.get("action") or {}).get("actionable") else None))
    return items
