"""Optional Claude study coach: explains an assignment, breaks it into steps and gives tailored tips."""

import os
from datetime import datetime, timezone

import anthropic
from pydantic import BaseModel, Field

from . import db
from .htmlclean import to_text

MODEL = os.environ.get("SCHOOLBOARD_MODEL", "claude-opus-5-5")
EFFORT = os.environ.get("SCHOOLBOARD_EFFORT", "medium")
FALLBACK_BETA = "server-side-fallback-2026-07-01"
_use_fallbacks = os.environ.get("SCHOOLBOARD_FALLBACKS", "1") != "0"

_client = None
_client_key = None


class AIUnavailable(Exception):
    pass


class Step(BaseModel):
    title: str = Field(description="Short imperative step, e.g. 'Outline three body paragraphs'")
    detail: str = Field(description="One or two sentences on how to do this step well")
    minutes: int = Field(description="Realistic minutes for a typical high-school/college student")


class Coach(BaseModel):
    summary: str = Field(description="Plain-language explanation of what the assignment is actually asking for (2-4 sentences)")
    requirements: list[str] = Field(description="Concrete requirements pulled from the instructions (length, sources, format, parts)")
    steps: list[Step] = Field(description="4-7 ordered steps from start to submission")
    tips: list[str] = Field(description="3-6 specific tips for doing this assignment well")
    pitfalls: list[str] = Field(description="2-4 common mistakes to avoid on this kind of work")
    submission_checklist: list[str] = Field(description="Things to check right before submitting, including how it's submitted")
    questions_for_teacher: list[str] = Field(description="Anything ambiguous in the instructions worth asking the teacher; empty if none")
    estimated_minutes: int = Field(description="Total realistic time to complete, in minutes")


SYSTEM = (
    "You are a friendly, practical study coach for a student. Given one assignment from their school platform, "
    "help them understand it and plan how to do it well. Be specific to this assignment's instructions; avoid generic "
    "filler. Coach, don't do the work: never write the essay, answers or solutions for them. Pointers to concepts, "
    "structure and strategies are good. If the instructions are thin, say what to check on the assignment page or ask "
    "the teacher. Keep the language clear and encouraging, suitable for a high-school or college student."
)


def _env_credentials() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
                or os.path.isdir(os.path.expanduser("~/.config/anthropic")))


def client() -> anthropic.Anthropic:
    """A key saved in Settings wins; otherwise the SDK's own credential lookup (env var, `ant auth login`)."""
    global _client, _client_key
    key = db.get_secret("anthropic_api_key")
    if _client is None or key != _client_key:
        if not key and not _env_credentials():
            raise AIUnavailable("Add your Claude API key in Settings to use the coach.")
        try:
            _client = anthropic.Anthropic(api_key=key) if key else anthropic.Anthropic()
            _client_key = key
        except Exception as e:  # unusable credentials etc.
            raise AIUnavailable(f"Claude isn't set up: {e}. Add your API key in Settings.") from e
    return _client


def status() -> dict:
    saved = bool(db.get_secret("anthropic_api_key"))
    return {"configured": saved or _env_credentials(), "source": "app" if saved else "environment" if _env_credentials() else None,
            "model": MODEL}


def _extra() -> dict:
    """Server-side refusal fallback ('default' routing): a declined request is re-run on Anthropic's recommended model."""
    if not _use_fallbacks:
        return {}
    return {"extra_headers": {"anthropic-beta": FALLBACK_BETA}, "extra_body": {"fallbacks": "default"}}


def _friendly(err: Exception) -> str:
    if isinstance(err, anthropic.AuthenticationError) or "authentication method" in str(err):
        return "The Claude API key is missing or invalid. Check it in Settings."
    if isinstance(err, anthropic.RateLimitError):
        return "Claude is rate limited right now; try again in a minute."
    if isinstance(err, anthropic.APIConnectionError):
        return "Couldn't reach the Claude API (network)."
    if isinstance(err, anthropic.APIStatusError):
        return f"Claude API error ({err.status_code}): {err.message}"
    return f"AI error: {err}"


def _schema(model) -> dict:
    """Pydantic JSON schema with additionalProperties:false and every property required (structured outputs)."""
    schema = model.model_json_schema()

    def fix(node):
        if isinstance(node, dict):
            if node.get("type") == "object":
                node["additionalProperties"] = False
                node["required"] = list(node.get("properties", {}).keys())
            if isinstance(node.get("title"), str):
                node.pop("title")
            for v in node.values():
                fix(v)
        elif isinstance(node, list):
            for v in node:
                fix(v)
    fix(schema)
    return schema


def _prompt(a: dict) -> str:
    due = a.get("due_at") or "no due date"
    if a.get("due_at"):
        hours = (datetime.fromisoformat(a["due_at"].replace("Z", "+00:00")) - datetime.now(timezone.utc)).total_seconds() / 3600
        due += f" (in {hours:.0f} hours)" if hours >= 0 else f" ({-hours:.0f} hours ago - overdue)"
    return (
        f"Course: {a.get('course') or 'unknown'}\n"
        f"Assignment: {a.get('title')}\n"
        f"Type: {a.get('kind')}\n"
        f"Due: {due}\n"
        f"Points: {a.get('points') if a.get('points') is not None else 'not given'}\n"
        f"How it's submitted: {', '.join(a.get('submission_types') or ['unknown'])}\n"
        f"Allowed file types: {', '.join(a.get('allowed_extensions') or []) or 'any / not stated'}\n"
        f"Student's own notes: {a.get('notes') or '(none)'}\n\n"
        f"Instructions from the teacher:\n{to_text(a.get('description')) or '(no instructions were provided)'}\n\n"
        "Coach me on this assignment."
    )


def coach(a: dict) -> dict:
    global _use_fallbacks
    c = client()

    def run():
        return c.messages.create(
            model=MODEL, max_tokens=16000, system=SYSTEM,
            output_config={"effort": EFFORT, "format": {"type": "json_schema", "schema": _schema(Coach)}},
            messages=[{"role": "user", "content": _prompt(a)}], **_extra())

    try:
        try:
            msg = run()
        except anthropic.BadRequestError as e:
            # Older accounts/proxies may not accept the fallback beta; retry once without it.
            if not (_use_fallbacks and "fallback" in str(e).lower()):
                raise
            _use_fallbacks = False
            msg = run()
    except Exception as e:
        raise AIUnavailable(_friendly(e)) from e
    if msg.stop_reason == "refusal":
        raise AIUnavailable("Claude declined to coach on this assignment.")
    if msg.stop_reason == "max_tokens":
        raise AIUnavailable("The answer was cut off; try again.")
    raw = next((b.text for b in msg.content if b.type == "text"), "")
    try:
        data = Coach.model_validate_json(raw).model_dump()
    except ValueError as e:
        raise AIUnavailable(f"Claude's answer couldn't be read: {e}") from e
    data["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data["model"] = msg.model
    return data
