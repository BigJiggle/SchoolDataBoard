"""Sample data so the dashboard can be tried before connecting a real account."""

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from . import item

KIND = "demo"
LABEL = "Sample data"
DETAIL = "A realistic week of made-up assignments across five classes. Remove it any time."
FIELDS: list = []
HELP = "Loads example assignments so you can explore the dashboard and the scheduler. Nothing is sent anywhere."


def check(config: dict) -> dict:
    return {"account": "Sample student"}


def _at(days: int, hour: int, tz) -> datetime:
    """`days` from today at `hour`:00 local time; 3 stands for 23:59, when most work is due."""
    hh = 23 if hour == 3 else hour
    day = datetime.now(tz).date() + timedelta(days=days)
    return datetime.combine(day, time(hh, 59 if hh == 23 else 0), tz)


SAMPLES = [
    ("eng-essay", "Persuasive Essay: Should school start later?", "English 10", 2, 3,
     "<p>Write a <strong>5-paragraph persuasive essay</strong> (600–900 words) arguing for or against later school "
     "start times.</p><ul><li>Clear thesis in the introduction</li><li>At least <b>three cited sources</b> (MLA)</li>"
     "<li>Address one counter-argument</li></ul><p>Submit as a .docx or .pdf. Rubric is attached in the course page.</p>",
     100, ["upload"], ["docx", "pdf"], "assignment", None),
    ("bio-lab", "Lab Report: Enzyme Activity & Temperature", "Biology", 4, 3,
     "<p>Using the data from Tuesday's lab, write a formal lab report: Title, Purpose, Hypothesis, Materials, "
     "Procedure, Data (table + graph), Analysis, Conclusion.</p><p>Graph reaction rate vs. temperature.</p>",
     50, ["upload", "text"], ["pdf", "docx"], "assignment", None),
    ("alg-ps7", "Problem Set 7: Quadratic Functions", "Algebra II", 1, 3,
     "<p>Complete problems 1–24 (even) on page 212. Show all work. Upload a photo or scan of your work.</p>",
     20, ["upload"], ["pdf", "jpg", "png"], "assignment", None),
    ("alg-quiz", "Quiz: Factoring & Completing the Square", "Algebra II", 5, 14, "<p>20-minute timed quiz. One attempt. "
     "Calculator allowed. Covers sections 4.3–4.5.</p>", 25, ["quiz"], [], "quiz", None),
    ("hist-disc", "Discussion: Causes of World War I", "World History", 2, 3,
     "<p>Post a 150–200 word response ranking the MAIN causes (Militarism, Alliances, Imperialism, Nationalism). "
     "Reply to <b>two</b> classmates by Friday.</p>", 15, ["discussion"], [], "discussion", None),
    ("hist-read", "Read Chapter 12 & annotate", "World History", 0, 3,
     "<p>Read pages 340–368. Annotate 5 key passages using the reading guide.</p>", 10, ["paper"], [], "assignment", None),
    ("span-voice", "Oral Presentation: Mi rutina diaria", "Spanish II", 7, 3,
     "<p>Record a 2-minute video describing your daily routine using reflexive verbs. Use at least 10 reflexive "
     "verbs and 5 time expressions.</p>", 40, ["media"], [], "assignment", None),
    ("eng-vocab", "Vocabulary Unit 6 Practice", "English 10", -1, 3, "<p>Complete the online practice set.</p>",
     10, ["external_tool"], [], "assignment", "missing"),
    ("bio-quiz", "Cell Respiration Check-in Quiz", "Biology", -3, 3, "<p>Short quiz on glycolysis and the Krebs cycle.</p>",
     10, ["quiz"], [], "quiz", "graded"),
    ("span-wb", "Workbook pp. 45–47", "Spanish II", 3, 3, "<p>Complete the workbook pages and bring them to class.</p>",
     10, ["paper"], [], "assignment", None),
    ("hist-proj", "Group Project: WWI Propaganda Poster Analysis", "World History", 10, 3,
     "<p>In groups of 3, analyze two propaganda posters and present your findings in a <b>5–7 slide</b> "
     "presentation. Submit a link to your shared slides.</p>", 60, ["url"], [], "assignment", None),
]


def fetch(config: dict, settings: dict) -> list[dict]:
    try:
        tz = ZoneInfo(settings.get("timezone") or "UTC")
    except ZoneInfoNotFoundError:
        tz = ZoneInfo("UTC")
    out = []
    for ext, title, course, days, hour, desc, pts, types, exts, kind, status in SAMPLES:
        out.append(item(f"demo:{ext}", title, course=course, description=desc, due=_at(days, hour, tz), points=pts,
                        url="", kind=kind, submission_types=types, allowed_extensions=exts, platform_status=status))
    return out
