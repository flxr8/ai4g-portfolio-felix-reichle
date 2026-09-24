"""
storage.py - Local JSON persistence for plans and progress.

One file, `data/state.json`, holding a dict of {session_id: state}. No accounts,
no passwords - a session id is generated on first visit and can be pasted back in
to resume. That is enough for a demo and deliberately not enough for production.

*** PRIVACY WARNING - READ BEFORE USING THIS WITH REAL PEOPLE ***
This file is PLAINTEXT and UNENCRYPTED. Users of this app are asked to describe
things like criminal records, immigration status, health conditions and domestic
situations, and all of it lands here in the clear on whatever machine is running
the app. Anyone with read access to the disk can read all of it, and a session id
is a bearer token with no expiry - anyone who has it can read that plan.

This is a hackathon prototype. Before this went anywhere near a real user it
would need at minimum: encryption at rest, real authentication, a retention and
deletion policy, and a lawful basis for processing what is, under GDPR, special
category data. See the README for the full list.
"""

from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Stored next to the code so the demo is self-contained and easy to inspect.
DATA_DIR = Path(__file__).parent / "data"
STATE_FILE = DATA_DIR / "state.json"


def _now() -> str:
    """UTC timestamp in ISO 8601, for created_at / updated_at."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_session_id() -> str:
    """Generate a fresh, unguessable-enough session id for a new user."""
    return uuid.uuid4().hex[:12]


def empty_state(session_id: str) -> dict[str, Any]:
    """The shape of a brand-new, empty user state.

    Defined in one place so every reader can rely on these keys existing.
    """
    return {
        "session_id": session_id,
        "created_at": _now(),
        "updated_at": _now(),
        "intake_text": "",       # what they first told us
        "plan": None,            # {"summary": str, "steps": [...]} once generated
        "completed": [],         # list of step ids they have ticked off
        "explanations": {},      # step id -> cached "Explain this" text
        "updates": [],           # log of re-plan inputs, newest last
        "warnings": [],          # non-fatal repairs from the last validation pass
    }


# --------------------------------------------------------------------------
# Whole-file read / write
# --------------------------------------------------------------------------


def _read_all() -> dict[str, Any]:
    """Load the whole store, tolerating a missing or corrupt file.

    A corrupt state file must never take the app down - we start fresh instead.
    The bad file is kept alongside as `.corrupt` so nothing is silently destroyed.
    """
    if not STATE_FILE.exists():
        return {}

    try:
        with STATE_FILE.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            raise ValueError("state.json did not contain an object")
        return data
    except (json.JSONDecodeError, OSError, ValueError):
        backup = STATE_FILE.with_suffix(".json.corrupt")
        try:
            STATE_FILE.replace(backup)
        except OSError:
            pass  # best effort; never block the app on a backup failing
        return {}


def _write_all(store: dict[str, Any]) -> None:
    """Write the whole store atomically.

    Streamlit reruns constantly and can interrupt mid-write; writing to a temp
    file in the same directory and then os.replace() means readers only ever see
    a complete file, never a half-written one.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(dir=DATA_DIR, prefix=".state-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(store, fh, indent=2, ensure_ascii=False)
        os.replace(tmp_path, STATE_FILE)  # atomic on POSIX and on Windows
    except BaseException:
        # Don't leave temp files behind if anything went wrong.
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# --------------------------------------------------------------------------
# Per-session API - what app.py actually calls
# --------------------------------------------------------------------------


def load_state(session_id: str) -> dict[str, Any]:
    """Load one session's state, or a fresh empty state if it is unknown.

    Missing keys on an older saved state are backfilled, so a state file written
    by a previous version of the app still loads.
    """
    store = _read_all()
    state = store.get(session_id)

    if not isinstance(state, dict):
        return empty_state(session_id)

    defaults = empty_state(session_id)
    for key, value in defaults.items():
        state.setdefault(key, value)
    state["session_id"] = session_id
    return state


def save_state(state: dict[str, Any]) -> None:
    """Persist one session's state, leaving every other session untouched."""
    session_id = state.get("session_id")
    if not session_id:
        raise ValueError("Cannot save a state with no session_id.")

    state["updated_at"] = _now()

    store = _read_all()
    store[session_id] = state
    _write_all(store)


def delete_state(session_id: str) -> None:
    """Remove one session entirely.

    Wired to the "Delete my data" button - given what people type into this app,
    being able to erase it is the bare minimum.
    """
    store = _read_all()
    if session_id in store:
        del store[session_id]
        _write_all(store)


# --------------------------------------------------------------------------
# Progress helpers
# --------------------------------------------------------------------------


def set_step_completed(state: dict[str, Any], step_id: str, done: bool) -> dict[str, Any]:
    """Tick or untick one step, then persist. Returns the updated state."""
    completed: list[str] = list(state.get("completed", []))

    if done and step_id not in completed:
        completed.append(step_id)
    elif not done and step_id in completed:
        completed.remove(step_id)

    state["completed"] = completed
    save_state(state)
    return state


def progress_counts(state: dict[str, Any]) -> tuple[int, int]:
    """Return (completed, total) counted against the CURRENT plan only.

    Completed ids left over from steps that a re-plan removed are ignored here,
    so the progress bar can never read 7/5.
    """
    plan = state.get("plan") or {}
    steps = plan.get("steps") or []
    if not steps:
        return 0, 0

    live_ids = {s["id"] for s in steps}
    done = sum(1 for sid in state.get("completed", []) if sid in live_ids)
    return done, len(steps)
