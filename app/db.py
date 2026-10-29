"""SQLite storage: connections (LMS accounts / feeds), assignments, settings."""

import json
import os
import sqlite3
import threading
from datetime import datetime, timezone

DB_PATH = os.environ.get("SCHOOLBOARD_DB", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "schoolboard.db"))

_lock = threading.Lock()
_conn: sqlite3.Connection | None = None

# Fields the user owns; a sync never overwrites them.
USER_FIELDS = ("status", "est_minutes", "progress_minutes", "notes", "ai_coach", "priority")

SCHEMA = """
CREATE TABLE IF NOT EXISTS connections (
    id INTEGER PRIMARY KEY,
    kind TEXT NOT NULL,
    name TEXT NOT NULL,
    config TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    last_sync TEXT,
    last_error TEXT,
    item_count INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY,
    connection_id INTEGER NOT NULL REFERENCES connections(id) ON DELETE CASCADE,
    external_id TEXT NOT NULL,
    course TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    due_at TEXT,
    points REAL,
    url TEXT NOT NULL DEFAULT '',
    kind TEXT NOT NULL DEFAULT 'assignment',
    submission_types TEXT NOT NULL DEFAULT '[]',
    allowed_extensions TEXT NOT NULL DEFAULT '[]',
    platform_status TEXT,
    status TEXT NOT NULL DEFAULT 'todo',
    priority TEXT NOT NULL DEFAULT 'normal',
    est_minutes INTEGER,
    progress_minutes INTEGER NOT NULL DEFAULT 0,
    notes TEXT NOT NULL DEFAULT '',
    ai_coach TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(connection_id, external_id)
);
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def db() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        if DB_PATH != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA foreign_keys = ON")
    return _conn


def init():
    with _lock:
        db().executescript(SCHEMA)
        db().commit()


def reset_for_tests(path: str):
    global _conn, DB_PATH
    if _conn is not None:
        _conn.close()
    _conn = None
    DB_PATH = path
    init()


# ------------------------------------------------------------ connections

def _conn_row(r: sqlite3.Row) -> dict:
    d = dict(r)
    d["config"] = json.loads(d["config"] or "{}")
    return d


def list_connections() -> list[dict]:
    return [_conn_row(r) for r in db().execute("SELECT * FROM connections ORDER BY id")]


def get_connection(cid: int) -> dict | None:
    r = db().execute("SELECT * FROM connections WHERE id = ?", (cid,)).fetchone()
    return _conn_row(r) if r else None


def find_connection(kind: str) -> dict | None:
    r = db().execute("SELECT * FROM connections WHERE kind = ? ORDER BY id LIMIT 1", (kind,)).fetchone()
    return _conn_row(r) if r else None


def create_connection(kind: str, name: str, config: dict) -> int:
    with _lock:
        cur = db().execute("INSERT INTO connections (kind, name, config, created_at) VALUES (?, ?, ?, ?)",
                           (kind, name, json.dumps(config), now_iso()))
        db().commit()
        return cur.lastrowid


def update_connection(cid: int, **fields):
    if "config" in fields:
        fields["config"] = json.dumps(fields["config"])
    sets = ", ".join(f"{k} = ?" for k in fields)
    with _lock:
        db().execute(f"UPDATE connections SET {sets} WHERE id = ?", (*fields.values(), cid))
        db().commit()


def delete_connection(cid: int):
    with _lock:
        db().execute("DELETE FROM assignments WHERE connection_id = ?", (cid,))
        db().execute("DELETE FROM connections WHERE id = ?", (cid,))
        db().commit()


# ------------------------------------------------------------ assignments

def _row(r: sqlite3.Row) -> dict:
    d = dict(r)
    d["submission_types"] = json.loads(d["submission_types"] or "[]")
    d["allowed_extensions"] = json.loads(d["allowed_extensions"] or "[]")
    d["ai_coach"] = json.loads(d["ai_coach"]) if d["ai_coach"] else None
    return d


def list_assignments() -> list[dict]:
    rows = db().execute(
        "SELECT a.*, c.kind AS source_kind, c.name AS source_name FROM assignments a "
        "JOIN connections c ON c.id = a.connection_id "
        "ORDER BY a.due_at IS NULL, a.due_at, a.title").fetchall()
    return [_row(r) for r in rows]


def get_assignment(aid: int) -> dict | None:
    r = db().execute(
        "SELECT a.*, c.kind AS source_kind, c.name AS source_name FROM assignments a "
        "JOIN connections c ON c.id = a.connection_id WHERE a.id = ?", (aid,)).fetchone()
    return _row(r) if r else None


def update_assignment(aid: int, **fields):
    if "ai_coach" in fields and fields["ai_coach"] is not None:
        fields["ai_coach"] = json.dumps(fields["ai_coach"])
    for k in ("submission_types", "allowed_extensions"):
        if k in fields:
            fields[k] = json.dumps(fields[k])
    fields["updated_at"] = now_iso()
    sets = ", ".join(f"{k} = ?" for k in fields)
    with _lock:
        db().execute(f"UPDATE assignments SET {sets} WHERE id = ?", (*fields.values(), aid))
        db().commit()


def insert_assignment(connection_id: int, item: dict) -> int:
    ts = now_iso()
    with _lock:
        cur = db().execute(
            "INSERT INTO assignments (connection_id, external_id, course, title, description, due_at, points, url, kind, "
            "submission_types, allowed_extensions, platform_status, status, est_minutes, notes, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (connection_id, item["external_id"], item.get("course", ""), item["title"], item.get("description", ""),
             item.get("due_at"), item.get("points"), item.get("url", ""), item.get("kind", "assignment"),
             json.dumps(item.get("submission_types", [])), json.dumps(item.get("allowed_extensions", [])),
             item.get("platform_status"), item.get("status", "todo"), item.get("est_minutes"),
             item.get("notes", ""), ts, ts))
        db().commit()
        return cur.lastrowid


def delete_assignment(aid: int):
    with _lock:
        db().execute("DELETE FROM assignments WHERE id = ?", (aid,))
        db().commit()


def sync_assignments(connection_id: int, items: list[dict]) -> dict:
    """Upsert what a platform returned; keep the user's own fields; drop items the platform no longer lists."""
    added = updated = 0
    seen = set()
    ts = now_iso()
    with _lock:
        c = db()
        for item in items:
            ext = str(item["external_id"])
            if ext in seen:
                continue
            seen.add(ext)
            existing = c.execute("SELECT id, status, platform_status FROM assignments WHERE connection_id = ? AND external_id = ?",
                                 (connection_id, ext)).fetchone()
            submitted = item.get("platform_status") in ("submitted", "graded")
            values = (item.get("course", ""), item["title"], item.get("description", ""), item.get("due_at"),
                      item.get("points"), item.get("url", ""), item.get("kind", "assignment"),
                      json.dumps(item.get("submission_types", [])), json.dumps(item.get("allowed_extensions", [])),
                      item.get("platform_status"))
            if existing:
                status = existing["status"]
                # Newly submitted on the platform -> tick it off here too.
                if submitted and existing["platform_status"] not in ("submitted", "graded"):
                    status = "done"
                c.execute("UPDATE assignments SET course=?, title=?, description=?, due_at=?, points=?, url=?, kind=?, "
                          "submission_types=?, allowed_extensions=?, platform_status=?, status=?, updated_at=? WHERE id=?",
                          (*values, status, ts, existing["id"]))
                updated += 1
            else:
                c.execute("INSERT INTO assignments (connection_id, external_id, course, title, description, due_at, points, "
                          "url, kind, submission_types, allowed_extensions, platform_status, status, created_at, updated_at) "
                          "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (connection_id, ext, *values, "done" if submitted else "todo", ts, ts))
                added += 1
        removed = 0
        if seen:
            marks = ",".join("?" * len(seen))
            removed = c.execute(f"DELETE FROM assignments WHERE connection_id = ? AND external_id NOT IN ({marks})",
                                (connection_id, *seen)).rowcount
        else:
            removed = c.execute("DELETE FROM assignments WHERE connection_id = ?", (connection_id,)).rowcount
        c.execute("UPDATE connections SET last_sync = ?, last_error = NULL, item_count = ? WHERE id = ?",
                  (ts, len(seen), connection_id))
        c.commit()
    return {"added": added, "updated": updated, "removed": removed, "total": len(seen)}


# ------------------------------------------------------------ settings

DEFAULT_SETTINGS = {
    "timezone": "",
    "student_name": "",
    # Mon=0 .. Sun=6, each a list of free windows "HH:MM"-"HH:MM".
    "availability": {
        "0": [["16:00", "19:30"]], "1": [["16:00", "19:30"]], "2": [["16:00", "19:30"]],
        "3": [["16:00", "19:30"]], "4": [["15:30", "17:30"]], "5": [["10:00", "13:00"]], "6": [["13:00", "17:00"]],
    },
    "block_minutes": 45,
    "break_minutes": 10,
    "max_minutes_per_day": 180,
    "buffer_hours": 12,
    "horizon_days": 14,
    "busy": [],  # one-off busy times: {"date": "YYYY-MM-DD", "start": "HH:MM", "end": "HH:MM", "label": "..."}
}


def get_settings() -> dict:
    s = dict(DEFAULT_SETTINGS)
    for r in db().execute("SELECT key, value FROM settings"):
        if r["key"] in DEFAULT_SETTINGS:
            s[r["key"]] = json.loads(r["value"])
    return s


# Secrets live beside the settings but are never part of get_settings(), so they never reach the browser.
def get_secret(name: str) -> str:
    r = db().execute("SELECT value FROM settings WHERE key = ?", (f"_secret:{name}",)).fetchone()
    return json.loads(r["value"]) if r else ""


def set_secret(name: str, value: str):
    with _lock:
        if value:
            db().execute("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                         (f"_secret:{name}", json.dumps(value)))
        else:
            db().execute("DELETE FROM settings WHERE key = ?", (f"_secret:{name}",))
        db().commit()


def save_settings(values: dict):
    with _lock:
        for k, v in values.items():
            if k in DEFAULT_SETTINGS:
                db().execute("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                             (k, json.dumps(v)))
        db().commit()
