# School Dashboard

One dashboard for all your schoolwork. It connects to the platforms your classes use, shows what's due, explains how to do it and how to submit it, and builds a study schedule around your free time.

![Dashboard](docs/dashboard.png)

## What it does

- **Connects your platforms** and merges everything into one list. You can connect several at once.
  - **Canvas**: uses a personal access token. You get full detail: instructions, points, submission types, allowed file types, and whether you've already submitted.
  - **Schoology**: uses your own API key and secret.
  - **Moodle**: uses your mobile-app security key.
  - **Calendar feed (any platform)**: paste an iCal link from Google Classroom, Blackboard, Brightspace (D2L), Schoology, Canvas, Moodle, Teams/Outlook, PowerSchool or anywhere else. The connect form shows where to find the link on each platform.
  - **Add by hand**: for paper handouts or anything your teacher said in class.
  - **Sample data**: try everything before connecting a real account.
- **Interactive dashboard**:
  - **Focus card**: suggests what to work on next (overdue first, then starred, then soonest due). Start a 15/25/45/60-minute focus timer, pause it, then finish it to log the time; the timer survives a page reload and shows in the sidebar while it runs. Use **Skip** to see the next suggestion.
  - **Tiles that filter**: Overdue, Due today, Next 7 days and Done this week. Click a tile, a tab or a class chip to filter the list in place.
  - **Quick add with plain-English dates**: type `Bio worksheet fri 5pm #Biology` and it fills in the due date and class.
  - **Row actions**: tick something off (with **Undo**), start a focus session, log 15 minutes, or star it as a priority.
  - **Interactive week strip**: click a day to see that day's study sessions and what's due.
  - **Search and commands**: press **⌘K / Ctrl+K** (or `/`) to search assignments and jump anywhere. Press `n` to quick-add.
- **Monotone design**: the whole app uses shades of one color. Pick the tone (Graphite, Slate, Ocean, Sage, Plum or Sepia) from the dashboard or Settings. Light and dark modes are both supported.
- **Every assignment** opens a detail panel with:
  - **What to do**: the teacher's instructions, cleaned up and safe to display.
  - **How to submit**: file upload, text entry, link, recording, on paper, quiz, discussion, outside tool, with practical advice for each and the allowed file types. There's also a button that goes straight to the submission page.
  - **Game plan and tips**: steps with time estimates and tips for the kind of work it is (essay, lab report, presentation, project, quiz prep, discussion post, reading, problem set, video, vocab practice), plus a checklist for before you submit. This part works with no AI.
  - **AI study coach** (optional, uses Claude). It gives:
    - a plain-English summary of what's being asked and the requirements it pulled out;
    - steps tailored to that assignment, with tips and pitfalls;
    - a checklist for before you submit, and questions worth asking your teacher.

    It coaches; it doesn't do the work for you.
  - Status (to do / in progress / done), priority, your time estimate, time logging, and notes.
- **Schedule builder**:
  - You set the times you're free each week and add one-off busy times (practice, work…).
  - You choose session length, break length, a daily maximum, and how many hours before the deadline you want to be finished.
  - The planner fits your remaining work into those times, earliest deadline first. Large tasks are split across days, and anything that can't make its deadline is flagged.
  - You can view the plan as a week calendar or a list, tick off sessions ("Did it"), or **export it to your calendar** (.ics).
- **Stays in sync**:
  - When you open the dashboard, it re-syncs if the last sync is over 30 minutes old.
  - Your own notes, estimates and statuses are kept across syncs.
  - Anything you submit on Canvas is marked done automatically.
- Works on a phone or iPad (bottom tab bar, list-style schedule).

| Schedule | Assignment detail |
|---|---|
| ![Schedule](docs/schedule.png) | ![Assignment](docs/assignment.png) |

## Desktop app

SchoolBoard runs as a normal desktop app: it opens in its own window with its own Dock/taskbar icon. You don't need a browser, a terminal or Python.

### Download

1. Open the repository on GitHub and go to **Actions → Desktop app**. Open the latest successful run. (Once a version is tagged, use the **Releases** page instead.)
2. Under **Artifacts**, download the build for your computer:
   - **Mac with Apple silicon (M1–M4):** `SchoolBoard-macOS-ARM64`
   - **Intel Mac:** `SchoolBoard-macOS-X64`
   - **Windows:** `SchoolBoard-Windows-X64`
3. Unzip it.
   - **Mac:** drag **SchoolBoard.app** into Applications.
   - **Windows:** keep **SchoolBoard.exe** wherever you like, for example on the Desktop.

**The first time you open it**, your computer warns you because the app isn't signed with a paid developer certificate:

- **Mac:**
  1. Double-click the app and press **Done** on the warning.
  2. Open **System Settings → Privacy & Security** and click **Open Anyway** next to SchoolBoard.
  3. Confirm. On older macOS you can instead right-click the app → **Open** → **Open**.
- **Windows:** on the blue SmartScreen box, press **More info → Run anyway**.

After that it opens normally.

### Where your data lives

| | |
|---|---|
| macOS | `~/Library/Application Support/SchoolBoard/` |
| Windows | `%APPDATA%\SchoolBoard\` |
| Linux | `~/.local/share/SchoolBoard/` |

The data folder holds `schoolboard.db` (assignments, notes and tokens), the window's saved preferences and a log file. Your data survives app updates. To start fresh, delete the folder.

### Turn on the AI study coach

Open **Settings → AI study coach**, paste a Claude API key from [platform.claude.com](https://platform.claude.com) and press **Save key**. The key is stored only on your computer.

### Build it yourself

```bash
pip install -r requirements.txt -r requirements-desktop.txt
python desktop.py                  # run the desktop app straight from the source
python desktop/build.py            # package it for this computer → dist/
```

`desktop/build.py` packages the app with PyInstaller (a `.app` on macOS, a single `.exe` on Windows). It then runs the packaged app with `--selftest` to check that it starts, serves the dashboard and handles time zones, and finally zips it. GitHub Actions (`.github/workflows/desktop.yml`) runs the same script on macOS and Windows on every push. To redraw the icon, run `python desktop/make_icon.py`.

## Run it in a browser instead (development)

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python run.py                      # opens http://127.0.0.1:8010
```

Then go to **Connections** and connect your platform, or press **Load sample data** to look around first. For the AI coach, paste a key in Settings, or set `ANTHROPIC_API_KEY` before starting.

### Settings (environment variables)

| Variable | Default | Purpose |
|---|---|---|
| `SCHOOLBOARD_DB` | `data/schoolboard.db` (browser version) | Where your data is stored (SQLite) |
| `SCHOOLBOARD_MODEL` | `claude-opus-5-5` | Claude model for the coach |
| `SCHOOLBOARD_EFFORT` | `medium` | Coach effort (`low`…`max`) |
| `SCHOOLBOARD_FALLBACKS` | `1` | Server-side refusal fallback (`0` to turn off) |
| `PORT` / `HOST` | `8010` / `127.0.0.1` | Server address |

## Connecting each platform

| Platform | What you need | Where to find it |
|---|---|---|
| Canvas | School address + access token | Canvas → Account → Settings → Approved Integrations → **+ New Access Token** |
| Schoology | Consumer key + secret | `https://<your-school>.schoology.com/api` while signed in |
| Moodle | Site address + security key | Profile → Preferences → **Security keys** → *Moodle mobile web service* |
| Google Classroom | Calendar feed link | Google Calendar → Settings → the class calendar → Integrate calendar → **Secret address in iCal format** |
| Blackboard | Calendar feed link | Calendar → Settings → **Share Calendar** |
| Brightspace (D2L) | Calendar feed link | Calendar → **Subscribe** |
| Anything else | Calendar feed link | Look for "Export", "Subscribe", "iCal" or "Calendar feed" |

If a school has turned off tokens or API keys, use that platform's calendar feed instead.

Calendar feeds can include things that aren't assignments, such as class meetings. Open one and press **Hide from my list** to remove it.

## Privacy

Your assignments, notes, platform tokens and Claude key are stored only on your computer (see [Where your data lives](#where-your-data-lives)). The app's internal server only listens on `127.0.0.1`, so nothing else on your network can reach it, and saved tokens and keys are never sent back to the page. Each token is only sent to the platform it belongs to. The AI coach sends a single assignment's details to Claude, and only when you press **Coach me on this**.

## Project layout

```
desktop.py              desktop app: starts the server inside the app and opens the window
desktop/                build script, icon
run.py                  start the server for the browser version
app/main.py             FastAPI routes
app/connectors/         canvas, schoology, moodle, ical (any platform), demo
app/tips.py             built-in categories, time estimates, steps, tips, submission guidance
app/ai.py               optional Claude study coach (structured output)
app/scheduler.py        study-plan builder + .ics export
app/htmlclean.py        sanitizes teacher-written HTML
app/db.py               SQLite storage
app/static/             front end (plain HTML/CSS/JS, no build step, works offline)
tests/                  pytest suite (platform APIs are mocked)
```

Run the tests with `pip install pytest httpx && pytest`.
