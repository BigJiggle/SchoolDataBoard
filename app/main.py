"""School Dashboard - local web app. Run with:  python run.py   (then open http://127.0.0.1:8010)"""

import os
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import ai, connectors, db, scheduler, tips
from .htmlclean import clean, text_to_html

STATIC = os.path.join(os.path.dirname(__file__), "static")

app = FastAPI(title="School Dashboard")
db.init()


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC, "index.html"))


app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/api/status")
def status():
    return {"ai": ai.status(), "platforms": connectors.describe(), "settings": db.get_settings(),
            "data_path": os.path.abspath(db.DB_PATH)}


# ------------------------------------------------------------------ connections

def _module(kind: str):
    mod = connectors.REGISTRY.get(kind)
    if not mod:
        raise HTTPException(400, f"Unknown platform '{kind}'.")
    return mod


def _secret_keys(kind: str) -> set[str]:
    mod = connectors.REGISTRY.get(kind)
    return {f["key"] for f in (mod.FIELDS if mod else []) if f.get("secret")}


def _public(conn: dict) -> dict:
    """Never send tokens/secrets back to the browser; just say whether they're set."""
    secrets = _secret_keys(conn["kind"])
    cfg = conn["config"]
    return {**conn, "config": {k: ("" if k in secrets else v) for k, v in cfg.items()},
            "secrets_set": sorted(k for k in secrets if cfg.get(k))}


def _sync(conn: dict) -> dict:
    if conn["kind"] == "manual":
        return {"added": 0, "updated": 0, "removed": 0, "total": conn["item_count"]}
    mod = _module(conn["kind"])
    try:
        items = mod.fetch(conn["config"], db.get_settings())
    except connectors.ConnectorError as e:
        db.update_connection(conn["id"], last_error=str(e))
        raise HTTPException(400, str(e)) from e
    except Exception as e:  # network trouble, unexpected payloads
        msg = f"Couldn't sync {conn['name']}: {type(e).__name__}: {e}"
        db.update_connection(conn["id"], last_error=msg)
        raise HTTPException(502, msg) from e
    for it in items:
        it["description"] = clean(it.get("description"))
    return db.sync_assignments(conn["id"], items)


class ConnectionIn(BaseModel):
    kind: str
    name: str = ""
    config: dict = {}


class ConnectionPatch(BaseModel):
    name: str | None = None
    config: dict | None = None


@app.get("/api/connections")
def list_connections():
    return [_public(c) for c in db.list_connections()]


@app.post("/api/connections")
def add_connection(body: ConnectionIn):
    mod = _module(body.kind)
    config = {k: (v.strip() if isinstance(v, str) else v) for k, v in body.config.items()}
    try:
        info = mod.check(config)
    except connectors.ConnectorError as e:
        raise HTTPException(400, str(e)) from e
    except Exception as e:
        raise HTTPException(502, f"Couldn't reach {mod.LABEL}: {type(e).__name__}: {e}") from e
    if body.kind == "demo" and db.find_connection("demo"):
        raise HTTPException(400, "Sample data is already loaded.")
    name = body.name.strip() or (config.get("platform") if body.kind == "ical" and config.get("platform") else mod.LABEL)
    cid = db.create_connection(body.kind, name, {**config, "account": info.get("account", "")})
    result = _sync(db.get_connection(cid))
    return {"connection": _public(db.get_connection(cid)), "sync": result}


@app.patch("/api/connections/{cid}")
def edit_connection(cid: int, body: ConnectionPatch):
    conn = db.get_connection(cid)
    if not conn:
        raise HTTPException(404, "Connection not found.")
    fields = {}
    if body.name is not None and body.name.strip():
        fields["name"] = body.name.strip()
    if body.config is not None:
        # An empty secret field means "keep the saved one".
        merged = dict(conn["config"])
        for k, v in body.config.items():
            v = v.strip() if isinstance(v, str) else v
            if v or k not in _secret_keys(conn["kind"]):
                merged[k] = v
        try:
            merged["account"] = _module(conn["kind"]).check(merged).get("account", "")
        except connectors.ConnectorError as e:
            raise HTTPException(400, str(e)) from e
        fields["config"] = merged
    if fields:
        db.update_connection(cid, **fields)
    return {"connection": _public(db.get_connection(cid)), "sync": _sync(db.get_connection(cid))}


@app.post("/api/connections/{cid}/sync")
def sync_connection(cid: int):
    conn = db.get_connection(cid)
    if not conn:
        raise HTTPException(404, "Connection not found.")
    return {"connection": _public(db.get_connection(cid)), "sync": _sync(conn)}


@app.post("/api/sync")
def sync_all():
    results = []
    for conn in db.list_connections():
        try:
            results.append({"id": conn["id"], "name": conn["name"], "ok": True, **_sync(conn)})
        except HTTPException as e:
            results.append({"id": conn["id"], "name": conn["name"], "ok": False, "error": e.detail})
    return {"results": results}


@app.delete("/api/connections/{cid}")
def remove_connection(cid: int):
    if not db.get_connection(cid):
        raise HTTPException(404, "Connection not found.")
    db.delete_connection(cid)
    return {"ok": True}


# ------------------------------------------------------------------ assignments

def _enrich(a: dict, full: bool = False) -> dict:
    category = tips.classify(a)
    a["category"] = category
    a["category_label"] = tips.CATEGORIES[category][0] if category in tips.CATEGORIES else "General"
    a["suggested_minutes"] = tips.estimate_minutes(a, category)
    if full:
        a["guide"] = tips.guide(a)
    return a


def _get(aid: int) -> dict:
    a = db.get_assignment(aid)
    if not a:
        raise HTTPException(404, "Assignment not found.")
    return a


@app.get("/api/assignments")
def list_assignments():
    return [_enrich(a) for a in db.list_assignments()]


@app.get("/api/assignments/{aid}")
def get_assignment(aid: int):
    return _enrich(_get(aid), full=True)


class AssignmentIn(BaseModel):
    title: str
    course: str = ""
    due_at: str | None = None
    description: str = ""
    url: str = ""
    points: float | None = None
    est_minutes: int | None = None
    submission_types: list[str] = []


class AssignmentPatch(BaseModel):
    status: str | None = None
    priority: str | None = None
    est_minutes: int | None = None
    progress_minutes: int | None = None
    notes: str | None = None
    # Manual entries only:
    title: str | None = None
    course: str | None = None
    due_at: str | None = None
    description: str | None = None
    url: str | None = None
    points: float | None = None


def _due(value: str | None) -> str | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as e:
        raise HTTPException(400, "Due date isn't a valid date/time.") from e
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@app.post("/api/assignments")
def add_assignment(body: AssignmentIn):
    if not body.title.strip():
        raise HTTPException(400, "Give the assignment a title.")
    conn = db.find_connection("manual")
    cid = conn["id"] if conn else db.create_connection("manual", "Added by me", {})
    aid = db.insert_assignment(cid, {
        "external_id": f"manual:{datetime.now(timezone.utc).timestamp()}", "title": body.title.strip(),
        "course": body.course.strip(), "description": text_to_html(body.description), "due_at": _due(body.due_at),
        "points": body.points, "url": body.url.strip(), "kind": "assignment",
        "submission_types": body.submission_types or ["unknown"], "est_minutes": body.est_minutes})
    return _enrich(_get(aid), full=True)


STATUSES = {"todo", "in_progress", "done", "hidden"}
PRIORITIES = {"low", "normal", "high"}


@app.patch("/api/assignments/{aid}")
def edit_assignment(aid: int, body: AssignmentPatch):
    a = _get(aid)
    data = body.model_dump(exclude_unset=True)
    if "status" in data and data["status"] not in STATUSES:
        raise HTTPException(400, "Unknown status.")
    if "priority" in data and data["priority"] not in PRIORITIES:
        raise HTTPException(400, "Unknown priority.")
    manual_only = {"title", "course", "due_at", "description", "url", "points"}
    if manual_only & data.keys() and a["source_kind"] != "manual":
        raise HTTPException(400, "Only assignments you added yourself can be edited; synced ones come from your platform.")
    if "due_at" in data:
        data["due_at"] = _due(data["due_at"])
    if "description" in data:
        data["description"] = text_to_html(data["description"] or "")
    for k in ("est_minutes", "progress_minutes"):
        if k in data and data[k] is not None:
            data[k] = max(0, int(data[k]))
    if data:
        db.update_assignment(aid, **data)
    return _enrich(_get(aid), full=True)


class ProgressIn(BaseModel):
    minutes: int


@app.post("/api/assignments/{aid}/progress")
def add_progress(aid: int, body: ProgressIn):
    a = _get(aid)
    total = a["est_minutes"] or tips.estimate_minutes(a)
    progress = max(0, (a["progress_minutes"] or 0) + body.minutes)
    fields = {"progress_minutes": progress}
    if progress > 0 and a["status"] == "todo":
        fields["status"] = "in_progress"
    db.update_assignment(aid, **fields)
    out = _enrich(_get(aid), full=True)
    out["work_left"] = max(0, total - progress)
    return out


@app.delete("/api/assignments/{aid}")
def delete_assignment(aid: int):
    a = _get(aid)
    if a["source_kind"] == "manual":
        db.delete_assignment(aid)
    else:
        db.update_assignment(aid, status="hidden")  # it would come back on the next sync
    return {"ok": True}


@app.post("/api/assignments/{aid}/coach")
def coach(aid: int):
    a = _get(aid)
    try:
        result = ai.coach(a)
    except ai.AIUnavailable as e:
        raise HTTPException(503, str(e)) from e
    db.update_assignment(aid, ai_coach=result)
    return _enrich(_get(aid), full=True)


class AIKeyIn(BaseModel):
    key: str


@app.put("/api/ai-key")
def save_ai_key(body: AIKeyIn):
    key = body.key.strip()
    if not key.startswith("sk-ant-"):
        raise HTTPException(400, "That doesn't look like a Claude API key (they start with sk-ant-).")
    db.set_secret("anthropic_api_key", key)
    return ai.status()


@app.delete("/api/ai-key")
def remove_ai_key():
    db.set_secret("anthropic_api_key", "")
    return ai.status()


# ------------------------------------------------------------------ settings & schedule

@app.get("/api/settings")
def get_settings():
    return db.get_settings()


@app.put("/api/settings")
def put_settings(values: dict):
    db.save_settings(values)
    return db.get_settings()


@app.get("/api/schedule")
def schedule():
    return scheduler.build(db.list_assignments(), db.get_settings())


@app.get("/api/schedule.ics")
def schedule_ics():
    plan = scheduler.build(db.list_assignments(), db.get_settings())
    return Response(scheduler.to_ics(plan), media_type="text/calendar",
                    headers={"Content-Disposition": 'attachment; filename="study-plan.ics"'})
