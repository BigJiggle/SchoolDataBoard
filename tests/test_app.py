import json
from datetime import datetime, timedelta, timezone

import httpx
import pytest
from fastapi.testclient import TestClient

from app import ai, connectors, db, scheduler, tips
from app.connectors import ical
from app.htmlclean import clean, to_text
from app.main import app


@pytest.fixture(autouse=True)
def fresh_db(tmp_path):
    db.reset_for_tests(str(tmp_path / "test.db"))
    db.save_settings({"timezone": "America/New_York"})
    yield
    connectors.transport = None


@pytest.fixture
def client():
    return TestClient(app)


def iso(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def soon(days=0, hours=0):
    return datetime.now(timezone.utc) + timedelta(days=days, hours=hours)


def mock(handler):
    connectors.transport = httpx.MockTransport(handler)


# ------------------------------------------------------------------ html

def test_clean_strips_scripts_and_unsafe_links():
    out = clean('<p onclick="x()">Hi <script>alert(1)</script><a href="javascript:evil()">x</a>'
                '<a href="https://ok.com">ok</a><img src="a.png" alt="diagram"><iframe src="x"></iframe></p>')
    assert "script" not in out and "onclick" not in out and "javascript" not in out and "iframe" not in out
    assert 'href="https://ok.com"' in out and 'rel="noopener noreferrer"' in out
    assert "[diagram]" in out


def test_to_text_keeps_paragraphs():
    assert to_text("<p>One</p><p>Two <b>bold</b></p>") == "One\n\nTwo bold"


# ------------------------------------------------------------------ canvas

def canvas_handler(request: httpx.Request):
    assert request.headers["authorization"] == "Bearer tok"
    path = request.url.path
    if path == "/api/v1/users/self":
        return httpx.Response(200, json={"name": "Sam Student"})
    if path == "/api/v1/courses":
        return httpx.Response(200, json=[{"id": 1, "name": "Chemistry"}, {"id": 2, "access_restricted_by_date": True}])
    if path == "/api/v1/courses/1/assignments":
        if request.url.params.get("page") == "2":
            return httpx.Response(200, json=[{
                "id": 12, "name": "Quiz 3", "due_at": iso(soon(3)), "submission_types": ["online_quiz"],
                "is_quiz_assignment": True, "html_url": "https://s.instructure.com/courses/1/assignments/12",
                "submission": {"workflow_state": "graded", "submitted_at": "x", "score": 9}}])
        return httpx.Response(200, headers={"link": '<https://s.instructure.com/api/v1/courses/1/assignments?page=2>; rel="next"'}, json=[
            {"id": 11, "name": "Lab report", "description": "<p>Write it</p><script>x</script>", "due_at": iso(soon(2)),
             "points_possible": 50, "submission_types": ["online_upload"], "allowed_extensions": ["pdf"],
             "html_url": "https://s.instructure.com/courses/1/assignments/11", "submission": {"workflow_state": "unsubmitted"}},
            {"id": 13, "name": "Ancient", "due_at": iso(soon(-200)), "submission_types": ["none"]},
            {"id": 14, "name": "Draft", "published": False, "due_at": iso(soon(1))},
        ])
    return httpx.Response(404)


def test_canvas_sync_and_user_fields_survive(client):
    mock(canvas_handler)
    r = client.post("/api/connections", json={"kind": "canvas", "config": {"base_url": "s.instructure.com", "token": "tok"}})
    assert r.status_code == 200, r.text
    assert r.json()["sync"]["total"] == 2
    conn = r.json()["connection"]
    assert conn["config"]["token"] == "" and conn["secrets_set"] == ["token"]  # never echoed back
    items = {a["title"]: a for a in client.get("/api/assignments").json()}
    lab, quiz = items["Lab report"], items["Quiz 3"]
    assert lab["submission_types"] == ["upload"] and lab["allowed_extensions"] == ["pdf"] and lab["points"] == 50
    assert "script" not in lab["description"]
    assert quiz["kind"] == "quiz" and quiz["status"] == "done" and quiz["platform_status"] == "graded"

    client.patch(f"/api/assignments/{lab['id']}", json={"notes": "use graph paper", "est_minutes": 90, "priority": "high"})
    client.post(f"/api/connections/{conn['id']}/sync")
    lab2 = client.get(f"/api/assignments/{lab['id']}").json()
    assert lab2["notes"] == "use graph paper" and lab2["est_minutes"] == 90 and lab2["priority"] == "high"
    assert lab2["guide"]["submission"][0]["label"] == "File upload"


def test_canvas_bad_token_is_a_clear_error(client):
    mock(lambda req: httpx.Response(401, json={"errors": [{"message": "Invalid access token."}]}))
    r = client.post("/api/connections", json={"kind": "canvas", "config": {"base_url": "https://s.instructure.com", "token": "bad"}})
    assert r.status_code == 400 and "rejected the credentials" in r.json()["detail"]
    assert client.get("/api/connections").json() == []


def test_edit_connection_keeps_saved_secret(client):
    mock(canvas_handler)
    cid = client.post("/api/connections", json={"kind": "canvas", "config": {"base_url": "s.instructure.com", "token": "tok"}}).json()["connection"]["id"]
    r = client.patch(f"/api/connections/{cid}", json={"name": "My Canvas", "config": {"base_url": "s.instructure.com", "token": ""}})
    assert r.status_code == 200 and r.json()["connection"]["name"] == "My Canvas"
    assert db.get_connection(cid)["config"]["token"] == "tok"


# ------------------------------------------------------------------ schoology

def test_schoology_fetch():
    def handler(req):
        auth = req.headers["authorization"]
        assert 'oauth_consumer_key="key"' in auth and 'oauth_signature="sec%26"' in auth
        p = req.url.path
        if p == "/v1/users/me":
            return httpx.Response(200, json={"uid": "77", "name_first": "Sam", "name_last": "S"})
        if p == "/v1/users/77/sections":
            return httpx.Response(200, json={"section": [{"id": "5", "course_title": "Biology"}]})
        if p == "/v1/sections/5/assignments":
            due = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d 23:59:00")
            return httpx.Response(200, json={"total": 2, "assignment": [
                {"id": "1", "title": "Cell essay", "due": due, "type": "assignment", "allow_dropbox": "1", "max_points": "20",
                 "web_url": "https://d.schoology.com/assignment/1"},
                {"id": "2", "title": "Unit test", "due": due, "type": "assessment", "allow_dropbox": "0"}]})
        return httpx.Response(404)
    mock(handler)
    from app.connectors import schoology
    cfg = {"consumer_key": "key", "consumer_secret": "sec", "domain": "d.schoology.com"}
    assert schoology.check(cfg)["account"] == "Sam S"
    items = schoology.fetch(cfg, {"timezone": "America/Chicago"})
    assert [i["title"] for i in items] == ["Cell essay", "Unit test"]
    assert items[0]["submission_types"] == ["upload"] and items[0]["points"] == 20.0
    assert items[1]["kind"] == "quiz" and "quiz" in items[1]["submission_types"]
    assert items[0]["due_at"].endswith(":59:00Z")


# ------------------------------------------------------------------ moodle

def test_moodle_fetch_and_errors():
    def handler(req):
        fn = dict(x.split("=", 1) for x in req.content.decode().split("&"))["wsfunction"]
        if fn == "core_webservice_get_site_info":
            return httpx.Response(200, json={"fullname": "Sam", "sitename": "Uni"})
        return httpx.Response(200, json={"events": [
            {"id": 9, "instance": 4, "modulename": "assign", "activityname": "Essay 2", "timesort": int(soon(3).timestamp()),
             "course": {"fullname": "History"}, "url": "https://m.edu/mod/assign/view.php?id=4", "action": {"actionable": True}}]})
    mock(handler)
    from app.connectors import moodle
    cfg = {"base_url": "m.edu", "token": "t"}
    assert moodle.check(cfg)["account"] == "Sam @ Uni"
    [it] = moodle.fetch(cfg, {})
    assert it["title"] == "Essay 2" and it["course"] == "History" and it["submission_types"] == ["upload", "text"]

    mock(lambda req: httpx.Response(200, json={"exception": "x", "message": "Invalid token - token not found"}))
    with pytest.raises(connectors.ConnectorError, match="Invalid token"):
        moodle.check(cfg)


# ------------------------------------------------------------------ ical

ICS = """BEGIN:VCALENDAR\r
VERSION:2.0\r
BEGIN:VEVENT\r
UID:event-assignment-1\r
SUMMARY:Essay draft [English 10]\r
DTSTART:{due}\r
DESCRIPTION:Write 500 words.\\nSee https://lms.example/a/1 for the rubric\r
 , thanks.\r
BEGIN:VALARM\r
TRIGGER:-PT15M\r
END:VALARM\r
END:VEVENT\r
BEGIN:VEVENT\r
UID:quiz-2\r
SUMMARY:Chapter 4 Quiz\r
DTSTART;VALUE=DATE:{day}\r
CATEGORIES:Biology\r
URL:https://lms.example/q/2\r
END:VEVENT\r
BEGIN:VEVENT\r
UID:old\r
SUMMARY:Long ago\r
DTSTART:20200101T120000Z\r
END:VEVENT\r
END:VCALENDAR\r
"""


def test_ical_feed(client):
    due = soon(2).strftime("%Y%m%dT%H%M%SZ")
    day = (datetime.now() + timedelta(days=4)).strftime("%Y%m%d")
    body = ICS.format(due=due, day=day)
    mock(lambda req: httpx.Response(200, text=body, headers={"content-type": "text/calendar"}))
    r = client.post("/api/connections", json={"kind": "ical", "config": {"url": "webcal://feeds.example/cal.ics", "platform": "Google Classroom"}})
    assert r.status_code == 200, r.text
    assert r.json()["connection"]["name"] == "Google Classroom"
    assert r.json()["connection"]["config"]["url"] == ""  # feed URLs are secret too
    items = {a["title"]: a for a in client.get("/api/assignments").json()}
    assert set(items) == {"Essay draft", "Chapter 4 Quiz"}
    essay = items["Essay draft"]
    assert essay["course"] == "English 10" and essay["url"].startswith("https://lms.example/a/1")
    assert "rubric, thanks." in essay["description"]
    quiz = items["Chapter 4 Quiz"]
    assert quiz["course"] == "Biology" and quiz["kind"] == "quiz" and quiz["due_at"].endswith(("03:59:00Z", "04:59:00Z"))


def test_ical_rejects_web_page():
    mock(lambda req: httpx.Response(200, text="<html>login</html>"))
    with pytest.raises(connectors.ConnectorError, match="didn't return a calendar"):
        ical.check({"url": "https://x.example/cal"})


# ------------------------------------------------------------------ manual + demo

def test_manual_assignment_crud(client):
    r = client.post("/api/assignments", json={"title": "Poster", "course": "Art", "due_at": iso(soon(5)),
                                              "description": "Make a poster", "submission_types": ["paper"]})
    a = r.json()
    assert a["source_kind"] == "manual" and a["guide"]["submission"][0]["type"] == "paper"
    r = client.patch(f"/api/assignments/{a['id']}", json={"title": "Big poster", "status": "in_progress"})
    assert r.json()["title"] == "Big poster" and r.json()["status"] == "in_progress"
    assert client.delete(f"/api/assignments/{a['id']}").json()["ok"]
    assert client.get("/api/assignments").json() == []


def test_synced_items_hide_instead_of_delete(client):
    client.post("/api/connections", json={"kind": "demo", "config": {}})
    a = client.get("/api/assignments").json()[0]
    assert client.patch(f"/api/assignments/{a['id']}", json={"title": "x"}).status_code == 400
    client.delete(f"/api/assignments/{a['id']}")
    assert client.get(f"/api/assignments/{a['id']}").json()["status"] == "hidden"
    assert client.post("/api/connections", json={"kind": "demo", "config": {}}).status_code == 400


def test_progress_moves_to_in_progress(client):
    a = client.post("/api/assignments", json={"title": "Worksheet", "est_minutes": 60}).json()
    r = client.post(f"/api/assignments/{a['id']}/progress", json={"minutes": 45}).json()
    assert r["status"] == "in_progress" and r["progress_minutes"] == 45 and r["work_left"] == 15


# ------------------------------------------------------------------ tips

def test_classify_and_estimate():
    assert tips.classify({"title": "Persuasive Essay"}) == "essay"
    assert tips.classify({"title": "Lab Report: Enzymes"}) == "lab"
    assert tips.classify({"title": "Anything", "kind": "quiz"}) == "quiz"
    assert tips.estimate_minutes({"title": "Essay", "description": "Write 1500 words"}) >= 360
    g = tips.guide({"title": "Essay", "submission_types": ["upload"], "allowed_extensions": ["pdf"], "due_at": iso(soon(hours=5))})
    assert "Due within a day" in g["tips"][0] and ".pdf" in g["submission"][0]["how"]


# ------------------------------------------------------------------ scheduler

BASE = {"timezone": "UTC", "availability": {str(d): [["16:00", "19:00"]] for d in range(7)}, "block_minutes": 45,
        "break_minutes": 10, "max_minutes_per_day": 150, "buffer_hours": 12, "horizon_days": 7, "busy": []}
MONDAY_NOON = datetime(2026, 11, 2, 12, 0, tzinfo=timezone.utc)


def task(i, due_days, minutes, **kw):
    return {"id": i, "title": f"T{i}", "course": "C", "status": "todo", "est_minutes": minutes, "progress_minutes": 0,
            "due_at": iso(MONDAY_NOON + timedelta(days=due_days)), "platform_status": None, **kw}


def test_scheduler_earliest_deadline_first_and_limits():
    plan = scheduler.build([task(1, 5, 90), task(2, 1.5, 60), task(3, 3, 30, status="done")], BASE, now=MONDAY_NOON)
    blocks = plan["blocks"]
    assert blocks[0]["assignment_id"] == 2  # due first, scheduled first
    assert all(b["assignment_id"] != 3 for b in blocks)  # done work isn't scheduled
    assert sum(b["minutes"] for b in blocks if b["assignment_id"] == 1) == 90
    for b in blocks:
        s, e = datetime.fromisoformat(b["start"]), datetime.fromisoformat(b["end"])
        assert s.hour >= 16 and (e.hour, e.minute) <= (19, 0) and b["minutes"] <= 60
    per_day = {}
    for b in blocks:
        per_day[b["start"][:10]] = per_day.get(b["start"][:10], 0) + b["minutes"]
    assert max(per_day.values()) <= 150
    assert not [w for w in plan["warnings"] if w["severity"] == "high"]


def test_scheduler_flags_impossible_and_respects_busy():
    settings = {**BASE, "busy": [{"date": "2026-11-02", "start": "16:00", "end": "19:00", "label": "Game"}]}
    plan = scheduler.build([task(1, 1, 300)], settings, now=MONDAY_NOON)
    assert all(not b["start"].startswith("2026-11-02") for b in plan["blocks"])
    [w] = plan["warnings"]
    assert w["severity"] == "high" and "won't fit" in w["message"]


def test_scheduler_ics(client):
    client.post("/api/assignments", json={"title": "Read ch 3", "due_at": iso(soon(3)), "est_minutes": 30})
    db.save_settings({"availability": {str(d): [["00:00", "23:59"]] for d in range(7)}})
    r = client.get("/api/schedule.ics")
    assert r.status_code == 200 and "BEGIN:VEVENT" in r.text and "Study: Read ch 3" in r.text


# ------------------------------------------------------------------ ai

def test_coach_without_key_is_503(client, monkeypatch):
    a = client.post("/api/assignments", json={"title": "Essay"}).json()

    def boom(_):
        raise ai.AIUnavailable("Claude isn't set up")
    monkeypatch.setattr(ai, "coach", boom)
    r = client.post(f"/api/assignments/{a['id']}/coach")
    assert r.status_code == 503 and "set up" in r.json()["detail"]


def test_coach_parses_structured_output(client, monkeypatch):
    payload = {"summary": "Argue a side.", "requirements": ["600 words"], "steps": [{"title": "Outline", "detail": "d", "minutes": 20}],
               "tips": ["t"], "pitfalls": ["p"], "submission_checklist": ["pdf"], "questions_for_teacher": [], "estimated_minutes": 150}

    class Block:
        type = "text"
        text = json.dumps(payload)

    class Msg:
        stop_reason = "end_turn"
        content = [Block()]
        model = "claude-opus-5-5"

    calls = {}

    class Messages:
        def create(self, **kw):
            calls.update(kw)
            return Msg()

    class Client:
        messages = Messages()

    monkeypatch.setattr(ai, "client", lambda: Client())
    a = client.post("/api/assignments", json={"title": "Essay", "description": "Write 600 words"}).json()
    r = client.post(f"/api/assignments/{a['id']}/coach")
    assert r.status_code == 200
    assert r.json()["ai_coach"]["estimated_minutes"] == 150
    assert calls["model"] == ai.MODEL and calls["output_config"]["format"]["type"] == "json_schema"
    assert "Write 600 words" in calls["messages"][0]["content"]
