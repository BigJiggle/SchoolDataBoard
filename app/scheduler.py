"""Builds a study plan: fits the remaining work into the student's free time, earliest deadline first.

Free time comes from weekly availability windows minus one-off busy times, cut into focus blocks with breaks and
capped per day. Each block goes to the unfinished task whose target (due time minus a safety buffer) is soonest,
which finishes everything on time whenever that is possible at all; tasks that can't make it are flagged.
"""

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from . import tips

MIN_BLOCK = 20  # minutes; shorter scraps of free time aren't worth scheduling
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _tz(settings: dict):
    try:
        return ZoneInfo(settings.get("timezone") or "UTC")
    except (ZoneInfoNotFoundError, ValueError):
        return ZoneInfo("UTC")


def _hm(value: str) -> time:
    h, m = (value or "0:0").split(":")[:2]
    h, m = int(h), int(m)
    return time(23, 59) if h >= 24 else time(h, m)


def _parse_due(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _subtract(intervals: list[tuple[datetime, datetime]], busy: list[tuple[datetime, datetime]]):
    out = []
    for s, e in intervals:
        pieces = [(s, e)]
        for bs, be in busy:
            nxt = []
            for ps, pe in pieces:
                if be <= ps or bs >= pe:
                    nxt.append((ps, pe))
                    continue
                if bs > ps:
                    nxt.append((ps, bs))
                if be < pe:
                    nxt.append((be, pe))
            pieces = nxt
        out.extend(pieces)
    return out


def free_windows(settings: dict, start: datetime, days: int) -> list[tuple[datetime, datetime]]:
    """Weekly availability for the next `days` days, minus one-off busy times, from `start` on."""
    tz = _tz(settings)
    avail = settings.get("availability") or {}
    busy_by_day: dict[date, list] = {}
    for b in settings.get("busy") or []:
        try:
            d = date.fromisoformat(b["date"])
            busy_by_day.setdefault(d, []).append((datetime.combine(d, _hm(b["start"]), tz),
                                                  datetime.combine(d, _hm(b["end"]), tz)))
        except (KeyError, ValueError):
            continue
    out = []
    first = start.astimezone(tz).date()
    for i in range(days):
        d = first + timedelta(days=i)
        windows = []
        for w in avail.get(str(d.weekday()), []):
            ws, we = datetime.combine(d, _hm(w[0]), tz), datetime.combine(d, _hm(w[1]), tz)
            ws = max(ws, start)
            if we > ws:
                windows.append((ws, we))
        out.extend(w for w in sorted(_subtract(windows, busy_by_day.get(d, [])))
                   if w[1] - w[0] >= timedelta(minutes=MIN_BLOCK))
    return out


def tasks_from(assignments: list[dict], settings: dict, start: datetime, horizon_end: datetime) -> list[dict]:
    buffer = timedelta(hours=float(settings.get("buffer_hours") or 0))
    out = []
    for a in assignments:
        if a.get("status") in ("done", "hidden") or a.get("platform_status") in ("submitted", "graded"):
            continue
        total = a.get("est_minutes") or tips.estimate_minutes(a)
        remaining = max(0, total - (a.get("progress_minutes") or 0))
        if remaining <= 0:
            continue
        due = _parse_due(a.get("due_at"))
        if due is None:
            target = horizon_end
        elif due <= start:
            target = start - timedelta(days=1)  # overdue work goes first
        else:
            target = max(due - buffer, start)
            if due - buffer < start:  # too close for the buffer: aim for the due time itself
                target = start + (due - start) / 2
        if a.get("priority") == "high":
            target -= timedelta(hours=24)
        elif a.get("priority") == "low":
            target += timedelta(hours=24)
        out.append({"id": a["id"], "title": a["title"], "course": a.get("course", ""), "due": due, "target": target,
                    "remaining": remaining, "total": total, "scheduled": 0, "finish": None, "late_minutes": 0})
    return out


def build(assignments: list[dict], settings: dict, now: datetime | None = None) -> dict:
    tz = _tz(settings)
    now = (now or datetime.now(timezone.utc)).astimezone(tz)
    start = now.replace(second=0, microsecond=0) + timedelta(minutes=(15 - now.minute % 15) % 15)
    days = max(1, min(60, int(settings.get("horizon_days") or 14)))
    horizon_end = datetime.combine(start.date() + timedelta(days=days), time(0, 0), tz)
    cap = int(settings.get("max_minutes_per_day") or 0) or 24 * 60
    tasks = tasks_from(assignments, settings, start, horizon_end)
    block = max(MIN_BLOCK, int(settings.get("block_minutes") or 45))
    brk = timedelta(minutes=max(0, int(settings.get("break_minutes") or 0)))
    used: dict[date, int] = {}
    blocks = []
    streak_id, streak = None, 0
    for ws, we in free_windows(settings, start, days):
        cur = ws
        while True:
            fits = min(int((we - cur).total_seconds() // 60), cap - used.get(cur.date(), 0))
            room = min(fits, block)
            open_tasks = sorted((t for t in tasks if t["remaining"] > 0), key=lambda t: (t["target"], t["id"]))
            if room < MIN_BLOCK or not open_tasks:
                break
            pick = open_tasks[0]
            # Variety: after two blocks in a row on one task, switch if another is nearly as urgent (within a day).
            if pick["id"] == streak_id and streak >= 2 and len(open_tasks) > 1 \
                    and open_tasks[1]["target"] - pick["target"] <= timedelta(hours=24):
                pick = open_tasks[1]
            minutes = min(room, pick["remaining"])
            # Run a little over the block length rather than leave a sliver (< MIN_BLOCK) for another day.
            if 0 < pick["remaining"] - minutes < MIN_BLOCK and fits >= pick["remaining"]:
                minutes = pick["remaining"]
            end = cur + timedelta(minutes=minutes)
            pick["remaining"] -= minutes
            pick["scheduled"] += minutes
            pick["finish"] = end
            if pick["due"] is not None and pick["due"] > start and end > pick["due"]:
                pick["late_minutes"] += max(1, int(min(minutes, (end - pick["due"]).total_seconds() // 60)))
            used[cur.date()] = used.get(cur.date(), 0) + minutes
            streak = streak + 1 if pick["id"] == streak_id else 1
            streak_id = pick["id"]
            blocks.append({"assignment_id": pick["id"], "title": pick["title"], "course": pick["course"],
                           "start": cur.isoformat(), "end": end.isoformat(), "minutes": minutes,
                           "due_at": pick["due"].isoformat() if pick["due"] else None})
            cur = end + brk
    # Number the parts of each task ("2 of 3").
    counts: dict[int, int] = {}
    for b in blocks:
        counts[b["assignment_id"]] = counts.get(b["assignment_id"], 0) + 1
    seen: dict[int, int] = {}
    for b in blocks:
        seen[b["assignment_id"]] = seen.get(b["assignment_id"], 0) + 1
        b["part"], b["parts"] = seen[b["assignment_id"]], counts[b["assignment_id"]]

    warnings, summary = [], []
    for t in tasks:
        due = t["due"]
        overdue = due is not None and due <= start
        short = t["late_minutes"] + (t["remaining"] if due is not None and due < horizon_end else 0)
        late = not overdue and short > 0
        if overdue:
            reason = "Already past due: scheduled first."
        elif late:
            reason = (f"About {short} of {t['total']} min won't fit before it's due. "
                      "Free up time, raise the daily limit, or lower the estimate.")
        elif t["remaining"] > 0:
            reason = f"{t['remaining']} min didn't fit in the next {days} days."
        else:
            reason = None
        if reason:
            warnings.append({"assignment_id": t["id"], "title": t["title"], "message": reason,
                             "severity": "high" if overdue or late else "low"})
        summary.append({"assignment_id": t["id"], "title": t["title"], "course": t["course"], "total": t["total"],
                        "scheduled": t["scheduled"], "remaining": t["remaining"],
                        "finish": t["finish"].isoformat() if t["finish"] else None,
                        "due_at": due.isoformat() if due else None, "on_track": not (overdue or late)})
    per_day = []
    for i in range(days):
        d = start.date() + timedelta(days=i)
        per_day.append({"date": d.isoformat(), "weekday": DAY_NAMES[d.weekday()], "minutes": used.get(d, 0)})
    return {"generated_at": now.isoformat(), "timezone": str(tz), "start": start.isoformat(), "days": days,
            "blocks": blocks, "warnings": warnings, "tasks": summary, "per_day": per_day,
            "total_minutes": sum(b["minutes"] for b in blocks)}


def _ics_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def to_ics(plan: dict) -> str:
    def stamp(iso: str) -> str:
        return datetime.fromisoformat(iso).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//School Dashboard//Study Plan//EN", "CALSCALE:GREGORIAN",
             "X-WR-CALNAME:Study plan"]
    for b in plan["blocks"]:
        title = f"Study: {b['title']}" + (f" ({b['part']}/{b['parts']})" if b["parts"] > 1 else "")
        desc = f"{b['course']}" + (f"\nDue {b['due_at']}" if b.get("due_at") else "")
        lines += ["BEGIN:VEVENT", f"UID:plan-{b['assignment_id']}-{stamp(b['start'])}@schooldashboard", f"DTSTAMP:{now}",
                  f"DTSTART:{stamp(b['start'])}", f"DTEND:{stamp(b['end'])}", f"SUMMARY:{_ics_escape(title)}",
                  f"DESCRIPTION:{_ics_escape(desc)}", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
