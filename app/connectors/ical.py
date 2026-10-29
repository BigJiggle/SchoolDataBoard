"""Any platform that offers a calendar (iCal / .ics) feed: Google Classroom, Blackboard, Brightspace (D2L),
Schoology, Canvas, Moodle, Teams, Edmodo, a teacher's Google Calendar... One read-only URL, no password."""

import re
from datetime import datetime, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from . import ConnectorError, http, in_window, item
from ..htmlclean import text_to_html

KIND = "ical"
LABEL = "Calendar feed (any platform)"
DETAIL = "Works with almost every platform. Gives titles, due dates, courses and links; details depend on the platform."
FIELDS = [
    {"key": "url", "label": "Calendar feed URL", "type": "url", "secret": True,
     "placeholder": "https://... .ics  or  webcal://..."},
    {"key": "platform", "label": "Platform", "type": "select",
     "options": ["Google Classroom", "Blackboard", "Brightspace (D2L)", "Schoology", "Canvas", "Moodle",
                 "Microsoft Teams / Outlook", "PowerSchool", "Other"]},
]
HELP = ("<b>Google Classroom:</b> open Google Calendar → Settings → pick the class calendar → <i>Integrate calendar</i> → "
        "copy the <b>Secret address in iCal format</b>.<br>"
        "<b>Blackboard:</b> Calendar → gear/Settings → <b>Share Calendar</b> → copy the link.<br>"
        "<b>Brightspace (D2L):</b> Calendar → Subscribe → enable feeds → copy the URL.<br>"
        "<b>Schoology:</b> Calendar → Export → copy the <i>iCal feed</i> link.<br>"
        "<b>Canvas:</b> Calendar → <b>Calendar Feed</b> (bottom right) → copy the link.<br>"
        "<b>Moodle:</b> Calendar → Export calendar → All courses → Get calendar URL.<br>"
        "<b>Teams / Outlook:</b> Outlook Calendar → Settings → Shared calendars → Publish → copy the ICS link.")

COURSE_SUFFIX = re.compile(r"^(.*?)\s*\[([^\]]+)\]\s*$")
URL_IN_TEXT = re.compile(r"https?://[^\s<>\"]+")


def _unescape(v: str) -> str:
    return v.replace("\\n", "\n").replace("\\N", "\n").replace("\\,", ",").replace("\\;", ";").replace("\\\\", "\\")


def parse(text: str) -> list[dict]:
    """Minimal RFC 5545 reader: VEVENT and VTODO components, properties with params."""
    lines: list[str] = []
    for raw in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if raw[:1] in (" ", "\t") and lines:
            lines[-1] += raw[1:]
        else:
            lines.append(raw)
    comps, cur, depth = [], None, 0
    for line in lines:
        if line.startswith("BEGIN:"):
            name = line[6:].strip()
            if name in ("VEVENT", "VTODO") and cur is None:
                cur, depth = {"_type": name}, 0
            elif cur is not None:
                depth += 1  # nested VALARM etc.
            continue
        if line.startswith("END:"):
            if cur is not None:
                if depth:
                    depth -= 1
                else:
                    comps.append(cur)
                    cur = None
            continue
        if cur is None or depth or ":" not in line:
            continue
        head, value = line.split(":", 1)
        name, *params = head.split(";")
        pmap = {}
        for p in params:
            if "=" in p:
                k, v = p.split("=", 1)
                pmap[k.upper()] = v.strip('"')
        cur.setdefault(name.upper(), (value, pmap))
    return comps


def _when(prop, tz) -> datetime | None:
    if not prop:
        return None
    value, params = prop
    value = value.strip()
    try:
        if params.get("VALUE") == "DATE" or re.fullmatch(r"\d{8}", value):
            d = datetime.strptime(value[:8], "%Y%m%d").date()
            return datetime.combine(d, time(23, 59), tz)
        if value.endswith("Z"):
            return datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=ZoneInfo("UTC"))
        local = datetime.strptime(value[:15], "%Y%m%dT%H%M%S")
        zone = tz
        if params.get("TZID"):
            try:
                zone = ZoneInfo(params["TZID"])
            except (ZoneInfoNotFoundError, ValueError):
                pass
        return local.replace(tzinfo=zone)
    except ValueError:
        return None


def _kind(title: str) -> str:
    t = title.lower()
    if re.search(r"\b(quiz|test|exam|midterm|final|assessment)\b", t):
        return "quiz"
    if re.search(r"\b(discussion|forum|reply|post)\b", t):
        return "discussion"
    return "assignment"


def _url(config: dict) -> str:
    url = (config.get("url") or "").strip()
    if not url:
        raise ConnectorError("Paste the calendar feed URL.")
    if url.startswith("webcal://"):
        url = "https://" + url[len("webcal://"):]
    if not url.startswith(("http://", "https://")):
        raise ConnectorError("The feed URL should start with https:// or webcal://")
    return url


def _download(config: dict) -> str:
    with http() as c:
        resp = c.get(_url(config), headers={"Accept": "text/calendar, */*"})
    if resp.status_code >= 400:
        raise ConnectorError(f"The calendar feed returned HTTP {resp.status_code}. Copy the link again; it may have been reset.")
    body = resp.text
    if "BEGIN:VCALENDAR" not in body:
        raise ConnectorError("That link didn't return a calendar (.ics) file. Make sure you copied the iCal/feed link, "
                             "not the calendar's web page.")
    return body


def check(config: dict) -> dict:
    comps = parse(_download(config))
    return {"account": f"{len(comps)} calendar entries"}


def fetch(config: dict, settings: dict) -> list[dict]:
    try:
        tz = ZoneInfo(settings.get("timezone") or "UTC")
    except ZoneInfoNotFoundError:
        tz = ZoneInfo("UTC")
    platform = config.get("platform") or ""
    items = []
    for comp in parse(_download(config)):
        title = _unescape(comp.get("SUMMARY", ("", {}))[0]).strip() or "Untitled"
        due = _when(comp.get("DUE") or comp.get("DTSTART") or comp.get("DTEND"), tz)
        if not in_window(due):
            continue
        course = ""
        m = COURSE_SUFFIX.match(title)
        if m:
            title, course = m.group(1), m.group(2)
        elif comp.get("CATEGORIES"):
            course = _unescape(comp["CATEGORIES"][0]).split(",")[0]
        desc = _unescape(comp.get("DESCRIPTION", ("", {}))[0])
        url = comp.get("URL", ("", {}))[0].strip()
        if not url:
            found = URL_IN_TEXT.search(desc)
            url = found.group(0) if found else ""
        uid = comp.get("UID", (f"{title}-{due}", {}))[0]
        rid = comp.get("RECURRENCE-ID", ("", {}))[0]
        status = "submitted" if comp.get("STATUS", ("", {}))[0].upper() == "COMPLETED" else None
        items.append(item(f"{uid}{'#' + rid if rid else ''}", title, course=course or platform,
                          description=text_to_html(desc), due=due, url=url, kind=_kind(title),
                          submission_types=["unknown"], platform_status=status))
    return items
