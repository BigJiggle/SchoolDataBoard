"""Built-in guidance (no AI needed): what kind of work this is, how long it may take, steps, tips and how to submit."""

import re
from datetime import datetime, timezone

from .htmlclean import to_text

CATEGORIES = {
    # key: (label, default minutes, keyword pattern)
    "essay": ("Essay / writing", 180, r"\b(essay|paper|write|writing|thesis|argument|persuasive|narrative|reflection|response paper|draft|report on)\b"),
    "lab": ("Lab report", 120, r"\b(lab|experiment|hypothesis)\b"),
    "presentation": ("Presentation", 150, r"\b(presentation|present|slides?|slideshow|speech|oral|poster)\b"),
    "project": ("Project", 240, r"\b(project|portfolio|capstone|research)\b"),
    "quiz": ("Quiz / test prep", 60, r"\b(quiz|test|exam|midterm|final|assessment|check-?in)\b"),
    "discussion": ("Discussion post", 30, r"\b(discussion|forum|reply|respond to|post)\b"),
    "reading": ("Reading", 45, r"\b(read|reading|chapter|pages?|annotate|novel)\b"),
    "problem_set": ("Problem set / worksheet", 60, r"\b(problem set|problems?|worksheet|homework|exercises?|practice|workbook|p\.?\s?\d+)\b"),
    "media": ("Video / audio", 60, r"\b(video|record|recording|podcast|vlog|audio)\b"),
    "vocab": ("Practice / vocabulary", 25, r"\b(vocab|vocabulary|flashcards?|spelling|duolingo|ixl|quizlet|deltamath)\b"),
}
ORDER = ["vocab", "quiz", "discussion", "lab", "presentation", "media", "essay", "project", "problem_set", "reading"]

STEPS = {
    "essay": [("Unpack the prompt", "Highlight the task verbs (argue, compare, analyze), length, sources and format. Open the rubric.", .08),
              ("Research & collect evidence", "Gather 3+ credible sources; copy quotes with page numbers and the citation as you go.", .2),
              ("Thesis + outline", "Write a one-sentence claim and a bullet outline: each body paragraph = one reason + evidence.", .12),
              ("Rough draft", "Write fast without editing. Intro → body → counter-argument → conclusion.", .35),
              ("Revise", "Check every paragraph supports the thesis; strengthen topic sentences and transitions.", .15),
              ("Proofread, cite & format", "Read it aloud, fix grammar, format citations (MLA/APA) and the heading, then export.", .1)],
    "lab": [("Organize your data", "Put the raw data in a clean table with units.", .15),
            ("Make the graph", "Independent variable on x, dependent on y, labeled axes with units and a title.", .2),
            ("Write purpose, hypothesis, methods", "Past tense, passive voice is fine; enough detail to repeat it.", .2),
            ("Analysis", "Describe the trend, use numbers, explain it with the science from class, name sources of error.", .3),
            ("Conclusion & check", "Was the hypothesis supported? Check the template/rubric headings are all there.", .15)],
    "presentation": [("Plan the message", "Write your main point and 3–5 supporting points; check time limit and slide count.", .15),
                     ("Research & gather visuals", "Collect facts, images and sources (keep the links for a works-cited slide).", .25),
                     ("Build the slides", "One idea per slide, few words, big visuals. Add speaker notes.", .3),
                     ("Rehearse", "Run through out loud twice with a timer; trim anything over time.", .2),
                     ("Final check", "Spelling, sources slide, file format/link sharing permissions.", .1)],
    "project": [("Break it down", "List every deliverable and due checkpoint; split work if it's a group project.", .1),
                ("Research / gather materials", "Collect what you need and save sources.", .25),
                ("Build the first version", "Get a complete rough version done before polishing anything.", .35),
                ("Get feedback & improve", "Show a classmate, parent or teacher; fix the weakest part.", .2),
                ("Finish & submit", "Check the rubric line by line and submit early.", .1)],
    "quiz": [("Find what's covered", "Check the sections/topics listed and any study guide.", .1),
             ("Active recall", "Close the notes and write/say what you remember; then check. Make flashcards for misses.", .4),
             ("Practice problems", "Do practice questions under a timer, especially ones you got wrong before.", .35),
             ("Quick review before", "Skim your flashcards and formulas; sleep beats cramming.", .15)],
    "discussion": [("Read the prompt & materials", "Note exactly what to answer and the word count.", .25),
                   ("Draft your post", "Answer directly in the first sentence, then support it with evidence/examples.", .45),
                   ("Reply to classmates", "Add something new: agree + extend, ask a question, or politely challenge.", .3)],
    "reading": [("Preview", "Skim headings, bold words and questions at the end (2–3 minutes).", .1),
                ("Read in chunks", "Read a section, then write a one-line summary in the margin or notes.", .7),
                ("Review", "Answer the guide questions; write 3 key takeaways.", .2)],
    "problem_set": [("Review examples", "Re-read the notes/examples for this section first.", .15),
                    ("Work the problems", "Show every step. Mark ones you're stuck on and move on.", .65),
                    ("Check & fix", "Check answers (odd answers in the back, or plug back in). Revisit the marked ones.", .2)],
    "media": [("Script or outline", "Bullet what you'll say; hit every required element.", .3),
              ("Practice", "Say it out loud a couple of times.", .2),
              ("Record", "Quiet room, good light, phone horizontal. Do a test clip first.", .35),
              ("Upload & check", "Watch it back once, then upload/submit and confirm it plays.", .15)],
    "vocab": [("Do the practice set", "Work in short focused bursts; aim for accuracy.", .8),
              ("Review misses", "Re-do the ones you got wrong.", .2)],
    "general": [("Read the instructions", "Note what's required, the format and how it's graded.", .15),
                ("Do the work", "Work in focused blocks with short breaks.", .7),
                ("Check & submit", "Compare against the instructions/rubric, then submit.", .15)],
}

TIPS = {
    "essay": ["Start with the rubric: it tells you exactly where the points are.",
              "Write the body paragraphs before the introduction; it's easier to introduce what you've already written.",
              "Every quote needs a sentence after it explaining why it proves your point.",
              "Ask your teacher or the writing center to look at your thesis early."],
    "lab": ["Graphs: label axes with units and use the right type (line for continuous data).",
            "Explain *why* the data looks the way it does using the science concept, not just *what* happened.",
            "Sources of error should be specific (e.g. 'the water bath cooled while timing'), not 'human error'."],
    "presentation": ["Fewer words, bigger images: slides support you, they aren't a script.",
                     "Practice with a timer; most people run 30% longer than they expect.",
                     "If it's a shared link, set sharing to 'anyone with the link can view' (or your teacher's email)."],
    "project": ["Set your own mini-deadlines for each piece, a couple of days before the real one.",
                "For group work, write down who does what in a shared doc on day one."],
    "quiz": ["Testing yourself (flashcards, practice problems) beats re-reading notes.",
             "Spread studying over 2–3 short sessions instead of one long one.",
             "For timed online quizzes: stable internet, no extra tabs, read every option before answering."],
    "discussion": ["Answer the actual question in your first sentence.",
                   "Replies count: a good reply adds evidence, a question, or a new angle, not just 'I agree'.",
                   "Write in a doc first so a page refresh doesn't eat your post."],
    "reading": ["Read with a question in mind (use the guide questions or the chapter headings).",
                "Summaries in your own words stick far better than highlighting."],
    "problem_set": ["Don't get stuck: skip, finish the rest, then come back.",
                    "Write the formula/step before plugging in numbers; teachers give partial credit for process.",
                    "Photo submissions: good light, flat page, one page per image, in order."],
    "media": ["Record in landscape with the light in front of you.",
              "Check the file size/length limit before you upload."],
    "vocab": ["Short daily practice beats one long session.", "Say words out loud and use each in a sentence."],
    "general": ["Break the work into pieces you can finish in one sitting.",
                "If anything is unclear, ask your teacher early, not the night before."],
}

SUBMISSION = {
    "upload": ("File upload", "Upload a file on the assignment page. Export to PDF unless another type is required, "
               "and give it a clear name (e.g. Last_First_Assignment)."),
    "text": ("Text entry", "Type or paste straight into the box on the assignment page. Draft it in a doc first so nothing is lost."),
    "url": ("Website link", "Paste a link (Google Doc/Slides, website). Set sharing to 'anyone with the link can view' "
            "or share with your teacher first."),
    "media": ("Media recording", "Record or upload audio/video on the assignment page. Test your mic/camera first."),
    "paper": ("On paper / in class", "Nothing to upload: bring it to class or hand it in as your teacher says."),
    "external_tool": ("Outside tool", "Opens another site/app from the assignment page (e.g. a practice platform). "
                      "Your work is saved there; make sure it says complete."),
    "quiz": ("Online quiz/test", "Taken on the platform. Check time limits and attempts before starting; use a stable connection."),
    "discussion": ("Discussion post", "Post in the discussion thread. Many require replies to classmates as well."),
    "annotation": ("Annotate a document", "Highlight/comment directly on the document inside the platform."),
    "none": ("No online submission", "Nothing to submit online; check with your teacher what's expected."),
    "unknown": ("See assignment page", "This source doesn't say how to submit. Open the assignment page to check."),
}


def classify(a: dict) -> str:
    if a.get("kind") == "quiz" or "quiz" in (a.get("submission_types") or []):
        return "quiz"
    if a.get("kind") == "discussion" or "discussion" in (a.get("submission_types") or []):
        return "discussion"
    title = (a.get("title") or "").lower()
    body = to_text(a.get("description"))[:1500].lower()
    for key in ORDER:  # the title is the strongest signal
        if re.search(CATEGORIES[key][2], title):
            return key
    for key in ORDER:
        if re.search(CATEGORIES[key][2], body):
            return key
    if "media" in (a.get("submission_types") or []):
        return "media"
    return "general"


def estimate_minutes(a: dict, category: str | None = None) -> int:
    category = category or classify(a)
    base = CATEGORIES[category][1] if category in CATEGORIES else 45
    pts = a.get("points") or 0
    if pts >= 100:
        base = int(base * 1.25)
    elif 0 < pts <= 10:
        base = int(base * 0.7)
    words = re.search(r"(\d{3,4})\s*(?:-|–|to)?\s*(\d{3,4})?\s*words", to_text(a.get("description")).lower())
    if words and category in ("essay", "general"):
        n = int(words.group(2) or words.group(1))
        base = max(base, int(n / 250 * 60))  # ~250 finished words an hour, including planning
    return max(15, int(round(base / 5) * 5))


def guide(a: dict) -> dict:
    category = classify(a)
    minutes = a.get("est_minutes") or estimate_minutes(a, category)
    steps = [{"title": t, "detail": d, "minutes": max(5, int(round(minutes * share / 5) * 5))}
             for t, d, share in STEPS.get(category, STEPS["general"])]
    tips = list(TIPS.get(category, TIPS["general"]))
    due = a.get("due_at")
    if due and a.get("status") != "done":
        hours = (datetime.fromisoformat(due.replace("Z", "+00:00")) - datetime.now(timezone.utc)).total_seconds() / 3600
        if hours < 0:
            tips.insert(0, "This is past due. Check the late-work policy and submit what you have; a short, polite "
                           "message to your teacher helps.")
        elif hours < 24:
            tips.insert(0, "Due within a day: aim to meet every requirement first, polish second, and submit with time to spare.")
    exts = a.get("allowed_extensions") or []
    submission = []
    for t in a.get("submission_types") or ["unknown"]:
        label, how = SUBMISSION.get(t, (t.replace("_", " ").title(), "See the assignment page."))
        if t == "upload" and exts:
            how += f" Allowed file types: {', '.join('.' + e.lstrip('.') for e in exts)}."
        submission.append({"type": t, "label": label, "how": how})
    checklist = ["Re-read the instructions and rubric", "Every required part is done"]
    if "upload" in (a.get("submission_types") or []):
        checklist.append("File opens, right format, clear filename")
    if "url" in (a.get("submission_types") or []):
        checklist.append("Link sharing lets your teacher open it")
    checklist.append("Submitted and you can see the confirmation")
    return {"category": category, "category_label": CATEGORIES.get(category, ("General",))[0] if category in CATEGORIES
            else "General", "est_minutes": minutes, "steps": steps, "tips": tips, "submission": submission,
            "checklist": checklist}
