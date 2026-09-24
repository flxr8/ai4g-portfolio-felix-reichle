"""Offline smoke tests for Rebuild - no API key or network required."""
# Make the project importable when this file is run directly from tests/.
import pathlib as _pathlib
import sys as _sys
_ROOT = _pathlib.Path(__file__).resolve().parent.parent
_sys.path.insert(0, str(_ROOT))

import json
import sys

import resources
import schema
import storage
from schema import PlanValidationError, validate_plan_response

FAILS = []


def check(label, cond, extra=""):
    status = "PASS" if cond else "FAIL"
    if not cond:
        FAILS.append(label)
    print(f"  [{status}] {label}" + (f"  {extra}" if extra and not cond else ""))


print("\n== schema: happy path ==")
good = {
    "type": "plan",
    "summary": "Start with ID.",
    "steps": [
        {"id": "id1", "domain": "documents_id", "title": "Get ID", "description": "d",
         "depends_on": [], "urgency": "high", "est_time": "1 week"},
        {"id": "h1", "domain": "housing", "title": "Find housing", "description": "d",
         "depends_on": ["id1"], "urgency": "medium", "est_time": "2 weeks"},
    ],
}
plan, warns = validate_plan_response(good)
check("valid plan accepted", plan["type"] == "plan" and len(plan["steps"]) == 2)
check("no spurious warnings", warns == [], str(warns))
check("domains_in_plan canonical order",
      schema.domains_in_plan(plan["steps"]) == ["documents_id", "housing"])
check("sort_steps puts high first",
      schema.sort_steps(plan["steps"])[0]["urgency"] == "high")

print("\n== schema: clarify branch ==")
c, w = validate_plan_response({"type": "clarify", "question": "Where are you staying?"})
check("clarify accepted", c["type"] == "clarify" and c["question"])

print("\n== schema: repairs ==")
messy = {
    "type": "plan",
    "steps": [
        {"id": "a", "domain": "housing", "title": "A", "description": "d",
         "depends_on": ["ghost", "a"], "urgency": "NOPE", "est_time": ""},
        {"id": "a", "domain": "housing", "title": "Dup id", "description": "d",
         "depends_on": [], "urgency": "low", "est_time": "1d"},
        {"id": "b", "domain": "invented_domain", "title": "B", "description": "d",
         "depends_on": [], "urgency": "low", "est_time": "1d"},
        {"id": "", "domain": "housing", "title": "", "description": "d",
         "depends_on": [], "urgency": "low", "est_time": "1d"},
        "not even an object",
    ],
}
plan2, warns2 = validate_plan_response(messy)
ids = [s["id"] for s in plan2["steps"]]
check("bad domain step dropped", "b" not in ids)
check("empty id/title step dropped", len(plan2["steps"]) == 2, str(ids))
check("duplicate id renamed", len(set(ids)) == len(ids), str(ids))
check("dangling dep removed", plan2["steps"][0]["depends_on"] == [])
check("invalid urgency defaulted", plan2["steps"][0]["urgency"] == "medium")
check("empty est_time defaulted", plan2["steps"][0]["est_time"] == "unknown")
check("warnings recorded", len(warns2) >= 4, str(warns2))

print("\n== schema: cycle breaking ==")
cyc = {"type": "plan", "steps": [
    {"id": "x", "domain": "housing", "title": "X", "description": "", "depends_on": ["y"],
     "urgency": "low", "est_time": "1d"},
    {"id": "y", "domain": "housing", "title": "Y", "description": "", "depends_on": ["x"],
     "urgency": "low", "est_time": "1d"},
]}
plan3, warns3 = validate_plan_response(cyc)
total_deps = sum(len(s["depends_on"]) for s in plan3["steps"])
check("cycle broken", total_deps < 2, f"deps={total_deps}")
check("cycle warned", any("circular" in w for w in warns3))

print("\n== schema: hard rejections ==")
for label, payload in [
    ("non-dict", ["a"]),
    ("no type, no content", {"foo": "bar"}),
    ("plan with empty steps", {"type": "plan", "steps": []}),
    ("clarify with no question", {"type": "clarify"}),
    ("all steps invalid", {"type": "plan", "steps": [{"id": "", "title": ""}]}),
]:
    try:
        validate_plan_response(payload)
        check(f"rejects {label}", False)
    except PlanValidationError:
        check(f"rejects {label}", True)

print("\n== schema: type inference fallback ==")
p4, w4 = validate_plan_response({"steps": good["steps"]})
check("infers plan when type missing", p4["type"] == "plan" and len(w4) == 1)

print("\n== crisis keyword check ==")
POS = ["I want to kill myself", "there's no way out of this",
       "I keep thinking I'd be better off dead", "I've been having suicidal thoughts",
       "I don't want to live anymore"]
NEG = ["I just got out of prison and have no ID", "I killed it at the interview",
       "my landlord wants to kill the lease early", "I'm exhausted and broke",
       "I was deported and lost everything", ""]
for t in POS:
    hit, m = resources.keyword_crisis_check(t)
    check(f"flags: {t[:38]!r}", hit, str(m))
for t in NEG:
    hit, m = resources.keyword_crisis_check(t)
    check(f"ignores: {t[:38]!r}", not hit, f"matched {m}")

print("\n== storage ==")
storage.STATE_FILE.unlink(missing_ok=True)
sid = storage.new_session_id()
s = storage.load_state(sid)
check("fresh state has all keys", set(s) == set(storage.empty_state(sid)))
s["intake_text"] = "test"
s["plan"] = {"summary": "s", "steps": good["steps"]}
storage.save_state(s)
s2 = storage.load_state(sid)
check("round-trips", s2["intake_text"] == "test" and len(s2["plan"]["steps"]) == 2)
storage.set_step_completed(s2, "id1", True)
check("progress 1/2", storage.progress_counts(storage.load_state(sid)) == (1, 2))
storage.set_step_completed(storage.load_state(sid), "id1", False)
check("untick works", storage.progress_counts(storage.load_state(sid)) == (0, 2))
# stale completed ids must not inflate the count
s3 = storage.load_state(sid)
s3["completed"] = ["id1", "long_gone_step"]
storage.save_state(s3)
check("stale ids ignored in count", storage.progress_counts(storage.load_state(sid)) == (1, 2))
# isolation between sessions
other = storage.new_session_id()
o = storage.load_state(other)
o["intake_text"] = "other"
storage.save_state(o)
check("sessions isolated", storage.load_state(sid)["intake_text"] == "test")
# corrupt file recovery
storage.STATE_FILE.write_text("{ this is not json", encoding="utf-8")
check("corrupt file recovers", storage.load_state(sid)["plan"] is None)
check("corrupt file backed up", storage.STATE_FILE.with_suffix(".json.corrupt").exists())
storage.delete_state(sid)
storage.STATE_FILE.unlink(missing_ok=True)
storage.STATE_FILE.with_suffix(".json.corrupt").unlink(missing_ok=True)

print("\n== llm.extract_json (no network) ==")
import llm  # noqa: E402  (imported late: reads .env at import time)
cases = [
    ('{"type":"plan"}', True),
    ('```json\n{"type":"plan"}\n```', True),
    ('```\n{"type":"plan"}\n```', True),
    ('Here you go: {"type":"plan"} hope that helps!', True),
    ('  \n {"type": "plan"}  \n ', True),
    ('no json at all', False),
    ('', False),
    ('{"broken": ', False),
]
for text, should_parse in cases:
    try:
        llm.extract_json(text)
        ok = should_parse
    except PlanValidationError:
        ok = not should_parse
    check(f"extract_json {text[:30]!r}", ok)

print("\n== llm.merge_preserving_progress ==")
completed = [{"id": "done1", "domain": "housing", "title": "Done thing", "description": "",
              "depends_on": [], "urgency": "low", "est_time": "1d"}]
new_steps = [{"id": "new1", "domain": "housing", "title": "New thing", "description": "",
              "depends_on": [], "urgency": "low", "est_time": "1d"}]
merged, mw = llm.merge_preserving_progress(new_steps, completed)
check("dropped completed step restored", [s["id"] for s in merged] == ["done1", "new1"])
check("restoration warned", len(mw) == 1)
merged2, mw2 = llm.merge_preserving_progress(completed + new_steps, completed)
check("no duplication when kept", len(merged2) == 2 and mw2 == [])

print("\n== prompts wiring ==")
import prompts  # noqa: E402
check("taxonomy in planner prompt", all(d in prompts.PLANNER_SYSTEM for d in schema.DOMAINS))
check("no-fabrication rule present", "NEVER INVENT" in prompts.PLANNER_SYSTEM)
check("no-fabrication in explain", "NEVER INVENT" in prompts.EXPLAIN_SYSTEM)
check("replan preserves-progress rule", "not yours to discard" in prompts.REPLAN_SYSTEM)
check("retry nudge has literal braces", "{ and end it with }" in prompts.JSON_RETRY_NUDGE)
check("plan template formats", "hello" in prompts.PLAN_USER_TEMPLATE.format(intake_text="hello"))
check("replan template formats",
      bool(prompts.REPLAN_USER_TEMPLATE.format(completed_block="a", outstanding_block="b",
                                               intake_text="c", update_text="d")))
check("explain template formats",
      bool(prompts.EXPLAIN_USER_TEMPLATE.format(title="t", domain_label="d", description="x",
                                                est_time="1d", prerequisite_line="", intake_text="i")))
check("crisis template formats", bool(prompts.CRISIS_CHECK_USER_TEMPLATE.format(text="t")))

print("\n== json schema sanity ==")
check("schema is JSON-serialisable", bool(json.dumps(schema.PLAN_RESPONSE_SCHEMA)))
check("step required fields complete",
      set(schema.STEP_SCHEMA["required"]) ==
      {"id", "domain", "title", "description", "depends_on", "urgency", "est_time"})

print("\n" + "=" * 60)
if FAILS:
    print(f"{len(FAILS)} FAILURES:")
    for f in FAILS:
        print("  -", f)
    sys.exit(1)
print("ALL OFFLINE TESTS PASSED")
