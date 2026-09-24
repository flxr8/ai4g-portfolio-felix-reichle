"""UI tests via Streamlit's AppTest harness. Only the crisis path touches no API."""
# Make the project importable when this file is run directly from tests/.
import pathlib as _pathlib
import sys as _sys
_ROOT = _pathlib.Path(__file__).resolve().parent.parent
_sys.path.insert(0, str(_ROOT))

import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

import os as _os

# These tests stub out every LLM call, so no real key is needed - but the app
# refuses to render the intake form without one. Set a placeholder first;
# load_dotenv() inside llm.py will not override an existing variable.
_os.environ.setdefault("GEMINI_API_KEY", "stub-key-for-ui-tests-only")

import llm
import storage

APP = str(_ROOT / "app.py")
FAILS = []

# Stub the LLM so UI flow tests are deterministic and cost nothing. AppTest runs
# app.py in-process, and app.py calls these through the `llm` module object, so
# patching here takes effect inside the app.
STUB_STEPS = [
    {"id": "s1", "domain": "documents_id", "title": "Stub step one",
     "description": "A stubbed description.", "depends_on": [], "urgency": "high",
     "est_time": "1 day"},
    {"id": "s2", "domain": "housing", "title": "Stub step two",
     "description": "Another stubbed description.", "depends_on": ["s1"],
     "urgency": "medium", "est_time": "1 week"},
]
CALLS = {"generate_plan": 0, "crisis_check": 0}


def _stub_generate_plan(intake_text):
    CALLS["generate_plan"] += 1
    return {"type": "plan", "summary": "Stub summary.", "steps": STUB_STEPS}, []


def _stub_crisis_check(text):
    CALLS["crisis_check"] += 1
    return False  # keyword screen is what we're exercising


llm.generate_plan = _stub_generate_plan
llm.llm_crisis_check = _stub_crisis_check


def check(label, cond, extra=""):
    if not cond:
        FAILS.append(label)
        print(f"  [FAIL] {label}  -> {extra}")
    else:
        print(f"  [PASS] {label}")


def texts(at):
    """All rendered text on the page, lowercased, for substring assertions."""
    out = []
    for attr in ("markdown", "caption", "warning", "error", "info", "success", "title"):
        for el in getattr(at, attr, []):
            out.append(str(el.value))
    # st.progress has no typed accessor in AppTest (it comes back as
    # UnknownElement), so pull its label text off the proto directly.
    for el in at.get("progress"):
        out.append(str(getattr(el, "text", "")))
    return " ".join(out).lower()


print("\n== 1. app boots cleanly ==")
at = AppTest.from_file(APP, default_timeout=30).run()
check("no unhandled exception", not at.exception, str(at.exception))
page = texts(at)
check("title rendered", any("Rebuild" in str(t.value) for t in at.title))
check("disclaimer banner present", "does not give legal, medical or immigration advice" in page)
check("crisis line in banner", "988" in page)
check("intake view by default", at.session_state["view"] == "intake")
check("session id generated", bool(at.session_state["session_id"]))
check("intake textarea present", len(at.text_area) >= 1)

print("\n== 2. empty submit is rejected without an API call ==")
at = AppTest.from_file(APP, default_timeout=30).run()
at.text_area[0].set_value("").run()
[b for b in at.button if "Build my plan" in b.label][0].click().run()
check("no exception", not at.exception, str(at.exception))
check("shows a warning", len(at.warning) >= 1)
check("still on intake", at.session_state["view"] == "intake")
print(f"    -> {at.warning[0].value if at.warning else '(none)'}")

print("\n== 3. too-short input is rejected without an API call ==")
at = AppTest.from_file(APP, default_timeout=30).run()
at.text_area[0].set_value("help").run()
[b for b in at.button if "Build my plan" in b.label][0].click().run()
check("no exception", not at.exception, str(at.exception))
check("shows a warning", len(at.warning) >= 1)
check("still on intake", at.session_state["view"] == "intake")
print(f"    -> {at.warning[0].value if at.warning else '(none)'}")

print("\n== 4. crisis keyword routes to crisis screen (no API call) ==")
at = AppTest.from_file(APP, default_timeout=60).run()
at.text_area[0].set_value(
    "I got out last month and honestly I want to kill myself, there is nothing left for me here."
).run()
[b for b in at.button if "Build my plan" in b.label][0].click().run()
check("no exception", not at.exception, str(at.exception))
check("switched to crisis view", at.session_state["view"] == "crisis", at.session_state["view"])
check("crisis reason recorded (keyword)",
      "keyword" in at.session_state.get("crisis_reason", ""),
      at.session_state.get("crisis_reason"))
crisis_page = texts(at)
check("988 shown prominently", "988" in crisis_page)
check("international option shown", "findahelpline" in crisis_page)
check("no plan was generated", storage.load_state(at.session_state["session_id"])["plan"] is None)
check("continue button offered", any("continue" in b.label.lower() for b in at.button))

CRISIS_TEXT_1 = (
    "I got out last month and honestly I want to kill myself, there is nothing left for me here."
)

print("\n== 4b. 'I'm safe' acknowledges only THAT text and resumes ==")
before = CALLS["generate_plan"]
[b for b in at.button if "continue" in b.label.lower()][0].click().run()
check("no exception", not at.exception, str(at.exception))
check("left the crisis screen", at.session_state["view"] != "crisis", at.session_state["view"])
check("acknowledged the exact text",
      at.session_state.get("crisis_acknowledged_text", "").strip() == CRISIS_TEXT_1.strip(),
      repr(at.session_state.get("crisis_acknowledged_text"))[:80])
check("pending cleared", at.session_state.get("crisis_pending") is None)
check("resumed without making them retype", CALLS["generate_plan"] == before + 1,
      f"generate_plan calls: {before} -> {CALLS['generate_plan']}")
check("landed on the plan", at.session_state["view"] == "plan", at.session_state["view"])

print("\n== 4c. a DIFFERENT crisis message re-triggers the screen ==")
# The bug this guards: a session-wide override would silently disable crisis
# screening for everything written afterwards.
at2c = AppTest.from_file(APP, default_timeout=60).run()
at2c.session_state["crisis_acknowledged_text"] = CRISIS_TEXT_1
at2c.run()
at2c.text_area[0].set_value(
    "Update: the hostel fell through and I've decided there is no reason to live anymore."
).run()
[b for b in at2c.button if "Build my plan" in b.label][0].click().run()
check("no exception", not at2c.exception, str(at2c.exception))
check("new crisis text still screened", at2c.session_state["view"] == "crisis",
      at2c.session_state["view"])

print("\n== 4d. the acknowledged text is not re-screened ==")
at2d = AppTest.from_file(APP, default_timeout=60).run()
at2d.session_state["crisis_acknowledged_text"] = CRISIS_TEXT_1
at2d.run()
check("acknowledged text bypasses the screen",
      not at2d.session_state.get("crisis_pending"),
      "pending was set before submit")

print("\n== 5. plan view renders from stored state (no API call) ==")
PLAN_STEPS = [
    {"id": "id1", "domain": "documents_id", "title": "Order your birth certificate",
     "description": "Find the registry office for where you were born.",
     "depends_on": [], "urgency": "high", "est_time": "2-3 weeks"},
    {"id": "id2", "domain": "documents_id", "title": "Replace your photo ID",
     "description": "You will usually need the birth certificate first.",
     "depends_on": ["id1"], "urgency": "medium", "est_time": "1 week"},
    {"id": "h1", "domain": "housing", "title": "Contact housing services",
     "description": "Search for housing assistance in your area.",
     "depends_on": [], "urgency": "high", "est_time": "1 day"},
]
sid = storage.new_session_id()
state = storage.load_state(sid)
state["intake_text"] = "released from prison, no id, sofa surfing"
state["plan"] = {"summary": "Start with your documents.", "steps": PLAN_STEPS}
state["warnings"] = ["A test warning about how this plan was built."]
storage.save_state(state)

at = AppTest.from_file(APP, default_timeout=30)
at.session_state["session_id"] = sid
at.session_state["view"] = "plan"
at.run()
check("no exception", not at.exception, str(at.exception))
plan_page = texts(at)
check("summary rendered", "start with your documents" in plan_page)
check("progress text shown", "0 of 3 steps done" in plan_page)
check("validation warnings surfaced", "a test warning" in plan_page)
check("three checkboxes rendered", len(at.checkbox) == 3, f"{len(at.checkbox)} checkboxes")
labels = [c.label for c in at.checkbox]
check("all step titles rendered", all(s["title"] in labels for s in PLAN_STEPS), str(labels))
check("tabs created per domain", len(at.tabs) >= 2, f"{len(at.tabs)} tabs")
check("explain buttons present",
      len([b for b in at.button if b.label == "Explain this"]) == 3)
check("update form present", any("Update my plan" in b.label for b in at.button))
check("disclaimer still visible on plan view",
      "does not give legal, medical or immigration advice" in plan_page)

print("\n== 6. ticking a checkbox persists ==")
target = [c for c in at.checkbox if c.label == "Order your birth certificate"][0]
target.check().run()
check("no exception", not at.exception, str(at.exception))
saved = storage.load_state(sid)
check("completion persisted to disk", "id1" in saved["completed"], str(saved["completed"]))
check("progress counts updated", storage.progress_counts(saved) == (1, 3),
      str(storage.progress_counts(saved)))
check("progress text refreshed", "1 of 3 steps done" in texts(at))

print("\n== 6b. unticking persists too ==")
target = [c for c in at.checkbox if c.label == "Order your birth certificate"][0]
target.uncheck().run()
saved = storage.load_state(sid)
check("untick persisted", "id1" not in saved["completed"], str(saved["completed"]))

print("\n== 7. resuming a session id loads its plan ==")
at2 = AppTest.from_file(APP, default_timeout=30).run()
at2.text_input[0].set_value(sid)
[b for b in at2.button if b.label == "Resume"][0].click().run()
check("no exception", not at2.exception, str(at2.exception))
check("resumed into plan view", at2.session_state["view"] == "plan", at2.session_state["view"])
check("resumed session id", at2.session_state["session_id"] == sid)
check("resumed plan rendered", "start with your documents" in texts(at2))

print("\n== 8. delete my data ==")
[b for b in at2.button if b.label == "Delete my data"][0].click().run()
check("no exception", not at2.exception, str(at2.exception))
check("state erased", storage.load_state(sid)["plan"] is None)
check("new session id issued", at2.session_state["session_id"] != sid)
check("back to intake", at2.session_state["view"] == "intake")

print("\n== 8b. an LLMError during plan generation shows up on THE SAME run ==")
# Regression test for a real bug: render_error() runs near the top of main(),
# before render_intake()/render_plan() are reached in the same script
# execution. Catching the exception and setting session_state.error WITHOUT
# calling st.rerun() left the message stuck until the user's next click - the
# spinner would just stop with nothing on screen. See app.py's _handle_new_plan
# and _handle_replan.
def _stub_generate_plan_fails(intake_text):
    raise llm.LLMError("Stub failure: the free tier is out of quota for today.",
                        "stub detail for test")


def _stub_replan_fails(**kwargs):
    raise llm.LLMError("Stub failure: replan rejected.", "stub detail for test")


_real_generate_plan = llm.generate_plan
_real_replan = llm.replan
llm.generate_plan = _stub_generate_plan_fails

at8b = AppTest.from_file(APP, default_timeout=30).run()
at8b.text_area[0].set_value(
    "I just got out of prison and have nowhere to stay and no ID."
).run()
[b for b in at8b.button if "Build my plan" in b.label][0].click().run()
check("no exception", not at8b.exception, str(at8b.exception))
check("error appears on the SAME run (not the next one)",
      len(at8b.error) >= 1 and "out of quota" in at8b.error[0].value.lower(),
      str([e.value for e in at8b.error]))
check("stayed on intake view", at8b.session_state["view"] == "intake")
llm.generate_plan = _real_generate_plan

# Same bug, same fix, on the "Update my plan" path.
sid8b = storage.new_session_id()
state8b = storage.load_state(sid8b)
state8b["plan"] = {"summary": "S", "steps": STUB_STEPS}
storage.save_state(state8b)

llm.replan = _stub_replan_fails
at8c = AppTest.from_file(APP, default_timeout=30)
at8c.session_state["session_id"] = sid8b
at8c.session_state["view"] = "plan"
at8c.run()
at8c.text_area[0].set_value("Something changed.").run()
[b for b in at8c.button if "Update my plan" in b.label][0].click().run()
check("no exception (replan)", not at8c.exception, str(at8c.exception))
check("replan error appears on the SAME run",
      len(at8c.error) >= 1 and "rejected" in at8c.error[0].value.lower(),
      str([e.value for e in at8c.error]))
llm.replan = _real_replan
storage.delete_state(sid8b)

print("\n== 9. missing API key shows setup help, not a crash ==")
import os  # noqa: E402

real = os.environ.get("GEMINI_API_KEY")
os.environ["GEMINI_API_KEY"] = ""
try:
    at3 = AppTest.from_file(APP, default_timeout=30).run()
    check("no exception", not at3.exception, str(at3.exception))
    check("setup error shown", len(at3.error) >= 1 and "api key" in at3.error[0].value.lower(),
          str([e.value for e in at3.error]))
    check("no intake textarea offered", len(at3.text_area) == 0)
finally:
    os.environ["GEMINI_API_KEY"] = real

storage.delete_state(sid)

print("\n" + "=" * 60)
if FAILS:
    print(f"{len(FAILS)} FAILURES:")
    for f in FAILS:
        print("  -", f)
    sys.exit(1)
print("ALL UI TESTS PASSED")
