"""SchoolBoard desktop app: the dashboard in its own window, with no browser tab or terminal.

    python desktop.py              open the app
    python desktop.py --selftest   start the server, check it answers, exit (the build runs this on the packaged app)

The same FastAPI app runs on a private 127.0.0.1 port inside the process; the window (pywebview: WebKit on macOS,
Edge WebView2 on Windows) shows it. Data lives in the per-user app-data folder, not next to the program.
"""

import json
import os
import socket
import sys
import tempfile
import threading
import time
import urllib.request

APP_NAME = "SchoolBoard"
PREFERRED_PORT = 8765  # fixed so the window's saved preferences (theme, tone, timer) stay with the same origin


def data_dir() -> str:
    if sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    elif os.name == "nt":
        base = os.environ.get("APPDATA") or os.path.expanduser("~\\AppData\\Roaming")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    path = os.path.join(base, APP_NAME)
    os.makedirs(path, exist_ok=True)
    return path


def _get(url: str, timeout: float = 2.0) -> bytes:
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.read()


def _is_ours(port: int) -> bool:
    try:
        return "platforms" in json.loads(_get(f"http://127.0.0.1:{port}/api/status", 0.7))
    except (OSError, ValueError):
        return False


def _port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def _any_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def choose_port() -> tuple[int, bool]:
    """(port, already_running): reuse a SchoolBoard that's already open, else the usual port, else any free one."""
    if _port_free(PREFERRED_PORT):
        return PREFERRED_PORT, False
    if _is_ours(PREFERRED_PORT):
        return PREFERRED_PORT, True
    return _any_free_port(), False


def start_server(port: int):
    import uvicorn

    from app.main import app

    # log_config=None: uvicorn's own console logging setup fails in a windowed app, which has no console.
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning", access_log=False,
                                           log_config=None))
    threading.Thread(target=server.run, daemon=True).start()
    deadline = time.time() + 20
    while not server.started:
        if time.time() > deadline:
            raise RuntimeError("The SchoolBoard server didn't start.")
        time.sleep(0.05)
    return server


def _quiet_streams(log_path: str):
    """A windowed build has no console: send output to a log file instead of crashing on a missing stream."""
    if sys.stdout is None or sys.stderr is None or getattr(sys, "frozen", False):
        log = open(log_path, "a", buffering=1, encoding="utf-8")
        sys.stdout = log
        sys.stderr = log


def selftest() -> int:
    """Exits 0 if the app works. Output goes to $SCHOOLBOARD_LOG (the build prints it); a failure never opens a dialog."""
    _quiet_streams(os.environ.get("SCHOOLBOARD_LOG") or os.path.join(tempfile.gettempdir(), "schoolboard-selftest.log"))
    try:
        _selftest()
    except BaseException:
        import traceback

        traceback.print_exc()
        sys.stderr.flush()
        os._exit(1)
    sys.stdout.flush()
    os._exit(0)  # don't wait on the server thread


def _selftest():
    from zoneinfo import ZoneInfo

    ZoneInfo("America/New_York")  # raises if the packaged app is missing its time-zone data
    os.environ["SCHOOLBOARD_DB"] = os.path.join(tempfile.mkdtemp(prefix="schoolboard-"), "test.db")
    port = _any_free_port()
    server = start_server(port)
    base = f"http://127.0.0.1:{port}"
    try:
        assert b"School Dashboard" in _get(base + "/")
        assert b"renderDashboard" in _get(base + "/static/app.js")
        assert len(_get(base + "/static/styles.css")) > 1000
        status = json.loads(_get(base + "/api/status"))
        assert {p["kind"] for p in status["platforms"]} >= {"canvas", "schoology", "moodle", "ical"}
        # Time zones must work in the packaged app too (Windows has no system tz database).
        req = urllib.request.Request(base + "/api/settings", data=json.dumps({"timezone": "America/New_York"}).encode(),
                                     method="PUT", headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5).read()
        req = urllib.request.Request(base + "/api/connections", data=json.dumps({"kind": "demo", "config": {}}).encode(),
                                     method="POST", headers={"Content-Type": "application/json"})
        assert json.loads(urllib.request.urlopen(req, timeout=10).read())["sync"]["total"] > 0
        assert json.loads(_get(base + "/api/schedule"))["blocks"]
    finally:
        server.should_exit = True
    print("selftest ok")


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    folder = data_dir()
    _quiet_streams(os.path.join(folder, "schoolboard.log"))
    os.environ.setdefault("SCHOOLBOARD_DB", os.path.join(folder, "schoolboard.db"))

    import webview

    port, running = choose_port()
    server = None if running else start_server(port)
    webview.settings["ALLOW_DOWNLOADS"] = True                 # "Export to calendar" saves an .ics file
    webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = True  # Canvas/Schoology links open in the normal browser
    webview.create_window(APP_NAME, f"http://127.0.0.1:{port}/#dashboard", width=1440, height=920, min_size=(1000, 660),
                          text_select=True, background_color="#F5F6F7")
    # Keep localStorage (theme, tone, focus timer) between launches.
    webview.start(private_mode=False, storage_path=os.path.join(folder, "webview"))
    if server:
        server.should_exit = True
    return 0


if __name__ == "__main__":
    sys.exit(main())
