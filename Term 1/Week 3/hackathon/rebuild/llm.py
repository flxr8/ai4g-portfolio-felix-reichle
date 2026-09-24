"""
llm.py - Every Gemini API call the app makes, plus the defensive plumbing.

The rest of the app talks to Gemini only through this module, and this module
never lets a raw API exception or a malformed model response escape: callers get
either clean validated data or an `LLMError` carrying a message that is safe to
show a user.

Layers of defence, outermost first:
  1. retry with exponential backoff on transient failures (429s, 5xx, timeouts)
  2. markdown-fence stripping and tolerant JSON extraction
  3. one automatic re-ask with a stricter nudge if parsing or validation failed
  4. schema.validate_plan_response(), which repairs what it can and rejects the rest

SDK note: google-genai >= 2.x uses `client.interactions.create(...)`, which
replaced the older `client.models.generate_content(...)`. Structured output is
requested through `response_format`, and the text comes back on `.output_text`.
"""

from __future__ import annotations

import json
import os
import random
import re
import time
from typing import Any

from dotenv import load_dotenv
from google import genai

import prompts
from schema import (
    PLAN_RESPONSE_SCHEMA,
    PlanValidationError,
    DOMAIN_LABELS,
    validate_plan_response,
)

# Read .env once at import time. Never hardcode a key; see .env.example.
load_dotenv()

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

# Free-tier friendly default. Overridable via .env so the model can be swapped
# without touching code - useful if quota runs out mid-demo (each model tracks
# its free-tier daily cap separately). Other current free-tier options:
# gemini-3.6-flash, gemini-3.7-flash, gemini-3.8-flash, gemini-3.1-flash-lite.
# The old 2.x generation (gemini-2.5-flash etc.) is no longer available to new
# API keys as of late 2026 - Google's own 404 for it points at gemini-3.6-flash.
# Check https://aistudio.google.com/rate-limit for what's currently live/free.
DEFAULT_MODEL = "gemini-3.5-flash"
MODEL = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)

# Per-request timeout in milliseconds (the SDK expects ms, not seconds).
#
# 90s, not the more typical 20-30s, because Gemini 3.x are reasoning ("thinking")
# models: they spend time and output-token budget on internal reasoning before
# writing the actual response. A trivial prompt returns in ~10s, but this app's
# planning call - a long system prompt plus a large nested JSON schema - can
# legitimately take much longer, and a too-short timeout here doesn't just fail
# fast, it can cut the model off mid-generation and come back as a technically
# valid but EMPTY plan (type: "plan", steps: []) rather than a clean error.
REQUEST_TIMEOUT_MS = int(os.getenv("GEMINI_TIMEOUT_MS", "90000"))

# How much internal reasoning the model does before answering. NOT set to the
# lowest level ("minimal") on purpose - that was tried and made things worse,
# not better, confirmed live: with zero thinking, gemini-3.1-flash-lite fell
# into a genuine repetition loop (tens of thousands of characters of "one step
# at a time... stay dedicated..." on repeat) and never finished the JSON at
# all. A small amount of reasoning ("low") gave the model a chance to reflect
# before answering, which is what actually stopped the loop. Less "thinking"
# is not free - for a small/fast model especially, it can trade correctness
# for speed in exactly this way.
# Valid values: "minimal", "low", "medium", "high".
THINKING_LEVEL = os.getenv("GEMINI_THINKING_LEVEL", "low")

# Generous enough that a full 15-step plan (each step has several text fields)
# has room to complete without being cut off. Kept high as a safety margin
# even after the THINKING_LEVEL and schema fixes above addressed the actual
# root causes of truncation - it doesn't cost anything on the free tier to
# leave headroom, and there's no guarantee some other model/prompt combination
# won't hit the same wall in a different way.
MAX_OUTPUT_TOKENS = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "16384"))

# How many times to retry a *transient* failure before giving up. Kept low
# (rather than the more typical 2-3) because REQUEST_TIMEOUT_MS is already
# generous here - stacking several 90s attempts would make a genuine failure
# take several minutes to surface, which is worse for the user than accepting
# a somewhat higher chance of failing on a blip that a second attempt might
# have cleared.
MAX_TRANSIENT_RETRIES = 1
BACKOFF_BASE_SECONDS = 1.5

# Whether to spend an extra API call on the LLM crisis check after the free
# keyword screen has come back clean. Turn off to conserve free-tier quota;
# the keyword screen in resources.py always runs regardless.
ENABLE_LLM_CRISIS_CHECK = os.getenv("ENABLE_LLM_CRISIS_CHECK", "true").lower() != "false"


class LLMError(RuntimeError):
    """A failure the UI should show as a friendly error state, never a traceback.

    `message` is written for the user. `detail` is the underlying cause, shown
    only behind an expander for debugging.
    """

    def __init__(self, message: str, detail: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail


# --------------------------------------------------------------------------
# Client
# --------------------------------------------------------------------------

_client: genai.Client | None = None


def get_client() -> genai.Client:
    """Build (and cache) the Gemini client.

    Raises LLMError with setup instructions rather than a KeyError if the API
    key is missing - that is by far the most common first-run problem.
    """
    global _client
    if _client is not None:
        return _client

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise LLMError(
            "No Gemini API key found. Copy `.env.example` to `.env`, add your key as "
            "`GEMINI_API_KEY=...`, then restart the app. You can get a free key at "
            "https://aistudio.google.com/apikey."
        )

    try:
        _client = genai.Client(
            api_key=api_key,
            http_options={
                "timeout": REQUEST_TIMEOUT_MS,
                # The SDK retries transient failures internally by default, on
                # top of the retry loop in _generate() below. Left alone, one
                # rate-limited call becomes two nested retry loops and a spinner
                # that hangs for minutes. We do our own retrying (with a check
                # for non-retryable cases like a daily quota that a retry can
                # never fix), so tell the SDK not to duplicate it.
                "retry_options": {"attempts": 1},
            },
        )
    except Exception as exc:  # pragma: no cover - misconfiguration only
        raise LLMError("Could not initialise the Gemini client.", str(exc)) from exc

    return _client


def api_key_present() -> bool:
    """Cheap check so the UI can warn about setup before the user types an essay."""
    return bool(os.getenv("GEMINI_API_KEY", "").strip())


# --------------------------------------------------------------------------
# Low-level call with retry / backoff
# --------------------------------------------------------------------------


def _status_code(exc: Exception) -> int | None:
    """Pull the HTTP status out of an SDK exception, whichever flavour it is.

    The SDK raises two different exception families depending on the entry point:
    `google.genai.errors.ClientError/ServerError` (with `.code`) from the older
    surfaces, and a `compat_errors` family (with `.status_code`) from
    `interactions.create`. The latter lives in a private module, so we duck-type
    on the attribute rather than importing it - that keeps this working if the
    SDK reshuffles its internals again.
    """
    for attr in ("status_code", "code"):
        value = getattr(exc, attr, None)
        if isinstance(value, int):
            return value
    return None


def _is_connection_error(exc: Exception) -> bool:
    """Network-level failure (timeout, DNS, reset) rather than an HTTP response."""
    name = type(exc).__name__.lower()
    return "timeout" in name or "connect" in name


# Statuses where trying again might genuinely work. Everything else fails fast:
# retrying a bad API key or a malformed request just wastes the user's time.
_TRANSIENT_STATUSES = {408, 409, 429, 500, 502, 503, 504}


def _is_daily_quota_exhausted(exc: Exception) -> bool:
    """A 429 that retrying cannot fix: the free tier's per-day cap is used up.

    Gemini reports both a short-lived rate limit ("slow down") and a hard daily
    cap ("come back tomorrow") as the same 429 status code, distinguishable only
    by the message text. Retrying the former is worthwhile; retrying the latter
    just burns time and, per the message below, additional quota.
    """
    text = str(exc).lower()
    return "per day" in text and ("quota" in text or "rate limit" in text or "limit" in text)


def _is_transient(exc: Exception) -> bool:
    """Is this worth retrying, or will it fail identically every time?"""
    if _is_daily_quota_exhausted(exc):
        return False

    if _is_connection_error(exc):
        return True

    status = _status_code(exc)
    if status is None:
        return False
    return status in _TRANSIENT_STATUSES or 500 <= status < 600


def _looks_like_bad_key(exc: Exception) -> bool:
    """Detect an invalid key regardless of the status code used to report it.

    Gemini reports an invalid API key as a 400 with reason API_KEY_INVALID, not
    the 401 you would expect, so the status code alone is not enough.
    """
    text = str(exc).lower()
    return "api_key_invalid" in text or "api key not valid" in text


def _looks_like_project_denied(exc: Exception) -> bool:
    """A well-formed key rejected because its GOOGLE CLOUD PROJECT is blocked.

    Distinct from a bad key: this is "permission_denied" with a message like
    "Your project has been denied access. Please contact support." - seen in
    practice with a brand-new Google account's freshly created key. Telling a
    user in this situation to "check GEMINI_API_KEY is correct" (the generic
    401/403 message) sends them re-copying a key that was never the problem.
    """
    text = str(exc).lower()
    return "denied access" in text or ("permission_denied" in text and "project" in text)


def _friendly_error(exc: Exception) -> LLMError:
    """Translate an SDK exception into something a stressed user can act on."""
    detail = f"{type(exc).__name__}: {exc}"

    if _is_connection_error(exc):
        return LLMError(
            "Could not reach Gemini - the request timed out. Check your internet "
            "connection and try again.",
            detail,
        )

    if _looks_like_bad_key(exc):
        return LLMError(
            "Gemini rejected the API key. Check `GEMINI_API_KEY` in your `.env` file "
            "and restart the app. You can get a free key at "
            "https://aistudio.google.com/apikey.",
            detail,
        )

    if _looks_like_project_denied(exc):
        return LLMError(
            "Google denied API access to this key's project entirely (not a typo "
            "or a bad key - the key format is fine). This usually happens with a "
            "very new, unverified Google account requesting API access. Try: "
            "(1) create the key at https://aistudio.google.com/apikey specifically "
            "(not the raw Google Cloud Console) if you haven't already, which "
            "provisions the project correctly, (2) make sure the account has "
            "completed any pending verification, or (3) contact Google support as "
            "the error itself suggests. This is on Google's side, not something "
            "this app or retrying can fix.",
            detail,
        )

    if _is_daily_quota_exhausted(exc):
        return LLMError(
            f"You've used today's free Gemini quota for `{MODEL}`. It resets daily "
            "(check aistudio.google.com/rate-limit for the exact time). To keep "
            "testing sooner, set `GEMINI_MODEL` in `.env` to a different free-tier "
            "model - each model has its own separate daily allowance - then restart "
            "the app. Your progress is saved either way.",
            detail,
        )

    status = _status_code(exc)

    if status == 429:
        return LLMError(
            "Gemini's free tier is rate-limiting us right now. Wait a minute and "
            "try again - your progress is saved.",
            detail,
        )

    if status in (401, 403):
        return LLMError(
            "Gemini rejected the API key. Check `GEMINI_API_KEY` in your `.env` file "
            "and restart the app.",
            detail,
        )

    if status is not None and 500 <= status < 600:
        return LLMError(
            "Gemini is having trouble at the moment. Please try again shortly - "
            "your progress is saved.",
            detail,
        )

    if status is not None and 400 <= status < 500:
        return LLMError("Gemini rejected the request.", detail)

    return LLMError("Something went wrong talking to Gemini.", detail)


def _generate(
    system_instruction: str,
    user_input: str,
    json_schema: dict[str, Any] | None = None,
) -> str:
    """One Gemini call, retried on transient failures. Returns raw output text.

    Raises LLMError on definitive failure - callers never see an SDK exception.
    """
    client = get_client()

    kwargs: dict[str, Any] = {
        "model": MODEL,
        "input": user_input,
        "system_instruction": system_instruction,
        # Keep reasoning light and leave room for the actual answer - see the
        # THINKING_LEVEL / MAX_OUTPUT_TOKENS comments above for why this matters
        # specifically for the JSON-schema calls (generate_plan / replan).
        "generation_config": {
            "thinking_level": THINKING_LEVEL,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
        },
    }

    # Ask the API itself to constrain the output to our schema. This is the first
    # line of defence for JSON validity - but we still parse defensively below,
    # because structured output is a strong hint, not a hard guarantee.
    if json_schema is not None:
        kwargs["response_format"] = {
            "type": "text",
            "mime_type": "application/json",
            "schema": json_schema,
        }

    last_exc: Exception | None = None

    for attempt in range(MAX_TRANSIENT_RETRIES + 1):
        try:
            interaction = client.interactions.create(**kwargs)
        except Exception as exc:
            last_exc = exc
            if not _is_transient(exc) or attempt == MAX_TRANSIENT_RETRIES:
                raise _friendly_error(exc) from exc
            # Exponential backoff with jitter, so simultaneous users don't
            # retry in lockstep and re-trigger the same rate limit.
            delay = BACKOFF_BASE_SECONDS * (2**attempt) + random.uniform(0, 0.5)
            time.sleep(delay)
            continue

        # The call succeeded at the transport level - now check the result.
        status = str(getattr(interaction, "status", "") or "")
        text = getattr(interaction, "output_text", None)

        if status == "failed":
            detail = str(getattr(interaction, "errors", "") or "unknown error")
            raise LLMError("Gemini could not complete the request.", detail)

        if not text or not text.strip():
            # An empty completion is usually a safety block or a truncated
            # response. Retrying occasionally helps; failing loudly is honest.
            if attempt < MAX_TRANSIENT_RETRIES:
                time.sleep(BACKOFF_BASE_SECONDS * (2**attempt))
                continue
            raise LLMError(
                "Gemini returned an empty response. This sometimes happens with "
                "sensitive topics. Try rephrasing, or try again in a moment."
            )

        return text

    # Only reachable if every attempt was a transient failure.
    raise _friendly_error(last_exc or RuntimeError("Unknown failure"))


# --------------------------------------------------------------------------
# Tolerant JSON extraction
# --------------------------------------------------------------------------

_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE)


def extract_json(text: str) -> Any:
    """Parse JSON out of model output, tolerating the usual LLM decorations.

    Handles: markdown code fences, a stray sentence before or after the object,
    and leading/trailing whitespace. Raises PlanValidationError if there is no
    parseable JSON at all, which the caller treats as a reason to re-ask.
    """
    if not text:
        raise PlanValidationError("Empty response.")

    cleaned = _FENCE_RE.sub("", text.strip()).strip()

    # Fast path: the whole thing is valid JSON.
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Slow path: grab the outermost {...} and try that. Covers "Here's your
    # plan: {...} Hope that helps!" and similar.
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError as exc:
            raise PlanValidationError(f"Could not parse JSON from response: {exc}") from exc

    if start != -1:
        # There's an opening brace but no closing one anywhere after it - this
        # is the signature of a response that got cut off mid-generation
        # (usually hitting the output-token limit) rather than one that never
        # produced JSON in the first place. Distinguishing the two matters for
        # debugging: this points at MAX_OUTPUT_TOKENS or a runaway field, the
        # other points at the model ignoring response_format entirely.
        raise PlanValidationError(
            "Response looked like it was cut off mid-generation (an opening "
            "'{' with no matching closing '}') - likely hit the output token "
            "limit before finishing, e.g. a field the model wrote at unusual "
            "length. See MAX_OUTPUT_TOKENS / the schema's maxLength fields."
        )

    raise PlanValidationError("Response contained no JSON object at all.")


def _generate_validated_plan(system: str, user_text: str) -> tuple[dict[str, Any], list[str]]:
    """Call Gemini for a plan, and re-ask once if the result is unusable.

    The retry is a *content* retry (bad JSON), distinct from the transport-level
    retries inside _generate() (rate limits, timeouts). Both can happen in one
    user action.
    """
    attempts = [user_text, user_text + prompts.JSON_RETRY_NUDGE]
    last_problem = ""

    for prompt_text in attempts:
        try:
            raw_text = _generate(system, prompt_text, json_schema=PLAN_RESPONSE_SCHEMA)
            decoded = extract_json(raw_text)
            return validate_plan_response(decoded)
        except PlanValidationError as exc:
            last_problem = str(exc)
            continue  # re-ask with the stricter nudge

    raise LLMError(
        "Gemini kept returning a response we couldn't read. This is usually "
        "temporary - please try again.",
        last_problem,
    )


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------


def generate_plan(intake_text: str) -> tuple[dict[str, Any], list[str]]:
    """Turn free-text intake into a validated plan (or a clarifying question).

    Returns `(response, warnings)` where response is either
    `{"type": "plan", "summary": str, "steps": [...]}` or
    `{"type": "clarify", "question": str}`.
    """
    user_text = prompts.PLAN_USER_TEMPLATE.format(intake_text=intake_text.strip())
    return _generate_validated_plan(prompts.PLANNER_SYSTEM, user_text)


def _format_steps_for_prompt(steps: list[dict[str, Any]]) -> str:
    """Render a step list compactly for inclusion in the re-plan prompt."""
    if not steps:
        return "  (none)"
    lines = []
    for s in steps:
        lines.append(f"  - id: {s['id']} | domain: {s['domain']} | {s['title']}")
    return "\n".join(lines)


def replan(
    intake_text: str,
    update_text: str,
    current_steps: list[dict[str, Any]],
    completed_ids: list[str],
) -> tuple[dict[str, Any], list[str]]:
    """Regenerate the plan in light of progress and new information.

    Completed steps are re-merged in code afterwards (see `merge_preserving_progress`),
    so the user's progress survives even if the model ignores the instruction to
    carry those steps over.
    """
    done_set = set(completed_ids)
    completed_steps = [s for s in current_steps if s["id"] in done_set]
    outstanding_steps = [s for s in current_steps if s["id"] not in done_set]

    user_text = prompts.REPLAN_USER_TEMPLATE.format(
        completed_block=_format_steps_for_prompt(completed_steps),
        outstanding_block=_format_steps_for_prompt(outstanding_steps),
        intake_text=intake_text.strip() or "(not recorded)",
        update_text=update_text.strip() or "(no new information given)",
    )

    response, warnings = _generate_validated_plan(prompts.REPLAN_SYSTEM, user_text)

    if response["type"] == "plan":
        response["steps"], merge_warnings = merge_preserving_progress(
            response["steps"], completed_steps
        )
        warnings.extend(merge_warnings)

    return response, warnings


def merge_preserving_progress(
    new_steps: list[dict[str, Any]],
    completed_steps: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Guarantee that completed steps survive a re-plan.

    The prompt asks the model to carry completed steps over unchanged, but asking
    is not the same as enforcing. Any completed step the model dropped is added
    back here, so ticking a box can never be undone by pressing "Update my plan".
    """
    warnings: list[str] = []
    new_ids = {s["id"] for s in new_steps}

    restored = [s for s in completed_steps if s["id"] not in new_ids]
    if restored:
        titles = ", ".join(repr(s["title"]) for s in restored)
        warnings.append(
            f"The updated plan had dropped {len(restored)} step(s) you had already "
            f"completed ({titles}); they were restored."
        )

    # Completed work goes first so it reads as history, then the new plan.
    return restored + new_steps, warnings


def explain_step(step: dict[str, Any], intake_text: str, all_steps: list[dict[str, Any]]) -> str:
    """Plain-language explanation of one step. Returns prose, not JSON."""
    # Name prerequisites by title rather than by opaque id.
    titles_by_id = {s["id"]: s["title"] for s in all_steps}
    prereq_titles = [titles_by_id[d] for d in step.get("depends_on", []) if d in titles_by_id]
    prerequisite_line = (
        f"This step depends on first doing: {', '.join(prereq_titles)}.\n"
        if prereq_titles
        else ""
    )

    user_text = prompts.EXPLAIN_USER_TEMPLATE.format(
        title=step.get("title", ""),
        domain_label=DOMAIN_LABELS.get(step.get("domain", ""), step.get("domain", "")),
        description=step.get("description", ""),
        est_time=step.get("est_time", "unknown"),
        prerequisite_line=prerequisite_line,
        intake_text=intake_text.strip() or "(not recorded)",
    )

    return _generate(prompts.EXPLAIN_SYSTEM, user_text).strip()


def llm_crisis_check(text: str) -> bool:
    """Second-pass crisis screen, for phrasing the keyword list cannot anticipate.

    Fails OPEN on purpose: if the API is down or the answer is unreadable, we
    return False and let the normal flow continue. The keyword screen in
    resources.py has already run and cannot fail, the crisis resources stay
    visible in the banner on every screen, and blocking someone out of the app
    because an API call errored would help no one.
    """
    if not ENABLE_LLM_CRISIS_CHECK or not text.strip():
        return False

    try:
        answer = _generate(
            prompts.CRISIS_CHECK_SYSTEM,
            prompts.CRISIS_CHECK_USER_TEMPLATE.format(text=text.strip()),
        )
    except LLMError:
        return False

    return answer.strip().lower().startswith("yes")
