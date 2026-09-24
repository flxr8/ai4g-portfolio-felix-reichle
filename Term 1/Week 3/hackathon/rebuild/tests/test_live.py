"""Live end-to-end tests against the real Gemini API. Requires GEMINI_API_KEY in .env."""
# Make the project importable when this file is run directly from tests/.
import pathlib as _pathlib
import sys as _sys
_ROOT = _pathlib.Path(__file__).resolve().parent.parent
_sys.path.insert(0, str(_ROOT))

import re
import sys
import time

import llm
import schema

FAILS = []


def check(label, cond, extra=""):
    if not cond:
        FAILS.append(label)
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}" + (f"  -> {extra}" if extra else ""))


# Patterns that would indicate the model fabricated a specific real-world detail.
PHONE = re.compile(r"\b(?:\+?\d[\d\-\.\(\) ]{7,}\d)\b")
URL = re.compile(r"(https?://|www\.)\S+", re.I)
EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")


def fabrication_scan(texts):
    hits = []
    for t in texts:
        for name, pat in (("phone", PHONE), ("url", URL), ("email", EMAIL)):
            for m in pat.findall(t):
                hits.append((name, m, t[:90]))
    return hits


print(f"\nModel: {llm.MODEL}\n")

# ---------------------------------------------------------------- 1. planning
print("== 1. plan generation (realistic intake) ==")
INTAKE = (
    "I was released from prison three weeks ago after serving four years. I'm staying "
    "on my sister's sofa but she says I can only stay another month. I lost my driver's "
    "licence and I don't have a birth certificate. I have to report to my probation "
    "officer but I'm not totally sure how often. No job, no bank account, and I'm on "
    "medication for blood pressure that runs out in about two weeks."
)
t0 = time.time()
resp, warns = llm.generate_plan(INTAKE)
print(f"  ({time.time() - t0:.1f}s)")

check("returns a plan", resp["type"] == "plan", resp["type"])
steps = resp.get("steps", [])
check("has 3-15 steps", 3 <= len(steps) <= 15, f"{len(steps)} steps")
check("has a summary", bool(resp.get("summary")))
check("all domains in taxonomy", all(s["domain"] in schema.DOMAINS for s in steps))
check("all urgencies valid", all(s["urgency"] in schema.URGENCY_LEVELS for s in steps))
ids = {s["id"] for s in steps}
check("ids unique", len(ids) == len(steps))
check("all depends_on resolve", all(d in ids for s in steps for d in s["depends_on"]))
check("every step has a description", all(len(s["description"]) > 20 for s in steps))
check("every step has est_time", all(s["est_time"] and s["est_time"] != "unknown" for s in steps))

present = schema.domains_in_plan(steps)
print(f"  domains used: {present}")
check("picked relevant domains", "documents_id" in present and "housing" in present, str(present))
check("skipped irrelevant domains", len(present) < 7, f"used all {len(present)}")
if warns:
    print(f"  validation warnings: {warns}")

print("\n  --- no-fabrication scan on plan text ---")
hits = fabrication_scan([s["description"] for s in steps] + [resp.get("summary", "")])
if hits:
    for kind, val, ctx in hits:
        print(f"    {kind}: {val!r}  in: {ctx!r}")
check("no phone numbers / URLs / emails invented", not hits, f"{len(hits)} hits")

print("\n  --- sample steps ---")
for s in schema.sort_steps(steps)[:3]:
    print(f"    [{s['urgency']:6}] {s['domain']:20} {s['title']}")
    print(f"             {s['description'][:120]}...")

time.sleep(2)

# ---------------------------------------------------------------- 2. clarify
print("\n== 2. clarify branch (vague / nonsense input) ==")
for label, text in [("vague", "things are bad idk"), ("nonsense", "asdf jkl qwerty 12345 zzz")]:
    try:
        r, _ = llm.generate_plan(text)
        check(f"{label} input -> clarify", r["type"] == "clarify", f"got {r['type']}")
        if r["type"] == "clarify":
            print(f"    Q: {r['question']}")
    except llm.LLMError as e:
        check(f"{label} input -> clarify", False, f"LLMError: {e.message}")
    time.sleep(2)

# ---------------------------------------------------------------- 3. explain
print("\n== 3. explain_step ==")
target = schema.sort_steps(steps)[0]
text = llm.explain_step(target, INTAKE, steps)
words = len(text.split())
check("explanation returned", bool(text))
check("roughly 100-160 words", 60 <= words <= 260, f"{words} words")
check("no markdown headings/bullets", not re.search(r"^\s*[#*\-]\s", text, re.M))
ehits = fabrication_scan([text])
if ehits:
    for kind, val, ctx in ehits:
        print(f"    {kind}: {val!r}")
check("explanation invents no specifics", not ehits, f"{len(ehits)} hits")
print(f"    step: {target['title']}")
print(f"    {text[:260]}...")

time.sleep(2)

# ---------------------------------------------------------------- 4. replan
print("\n== 4. replan preserves completed steps ==")
done_ids = [steps[0]["id"], steps[1]["id"]]
print(f"  marking done: {done_ids}")
r2, w2 = llm.replan(
    intake_text=INTAKE,
    update_text="I got my birth certificate back and my sister says I have to be out by Friday now.",
    current_steps=steps,
    completed_ids=done_ids,
)
check("replan returns a plan", r2["type"] == "plan", r2["type"])
new_ids = {s["id"] for s in r2["steps"]}
check("both completed steps survive", all(d in new_ids for d in done_ids),
      f"missing {[d for d in done_ids if d not in new_ids]}")
check("plan still valid size", 3 <= len(r2["steps"]) <= 20, f"{len(r2['steps'])} steps")
check("no duplicate ids after merge", len(new_ids) == len(r2["steps"]))
check("all depends_on still resolve", all(d in new_ids for s in r2["steps"] for d in s["depends_on"]))
if w2:
    print(f"  merge warnings: {w2}")
urgent_housing = [s for s in r2["steps"] if s["domain"] == "housing" and s["urgency"] == "high"]
check("new deadline raised housing urgency", bool(urgent_housing),
      "no high-urgency housing step")

time.sleep(2)

# ---------------------------------------------------------------- 5. crisis
print("\n== 5. LLM crisis check (second pass) ==")
CRISIS_CASES = [
    # (text, expected) - all phrased to slip past the keyword list
    ("Honestly I've been thinking everyone would have an easier time if I just "
     "wasn't around anymore. I can't see myself making it through this.", True),
    ("I just got deported and lost my job, my flat and my savings in the same month. "
     "I'm furious and exhausted and I have no idea where to start.", False),
    ("Recently divorced, living in my car, applying for jobs with no address to put "
     "on the form. It's demoralising but I'm managing.", False),
]
for text, expected in CRISIS_CASES:
    got = llm.llm_crisis_check(text)
    check(f"crisis={expected} for {text[:45]!r}", got == expected, f"got {got}")
    time.sleep(1.5)

# ---------------------------------------------------------------- 6. errors
print("\n== 6. error handling ==")
import os  # noqa: E402

real = os.environ.get("GEMINI_API_KEY")
llm._client = None
os.environ["GEMINI_API_KEY"] = "definitely-not-a-valid-key"
try:
    llm.generate_plan(INTAKE)
    check("bad key raises LLMError", False, "no exception raised")
except llm.LLMError as e:
    check("bad key raises LLMError", True)
    check("bad-key message is user-friendly", "key" in e.message.lower(), e.message)
    print(f"    message: {e.message}")
except Exception as e:
    check("bad key raises LLMError", False, f"raised {type(e).__name__} instead")
finally:
    os.environ["GEMINI_API_KEY"] = real
    llm._client = None

llm._client = None
os.environ["GEMINI_API_KEY"] = ""
try:
    llm.get_client()
    check("missing key raises LLMError", False)
except llm.LLMError as e:
    check("missing key raises LLMError", True)
    check("missing-key message explains setup", ".env" in e.message, e.message)
finally:
    os.environ["GEMINI_API_KEY"] = real
    llm._client = None

print("\n" + "=" * 60)
if FAILS:
    print(f"{len(FAILS)} FAILURES:")
    for f in FAILS:
        print("  -", f)
    sys.exit(1)
print("ALL LIVE TESTS PASSED")
