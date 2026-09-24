# Rebuild

**One large problem, broken into small steps.**

Rebuild helps someone reorganise their life during a major disruptive transition —
release from prison, moving to a new country, divorce, losing housing — by turning a
messy free-text description of their situation into an ordered, tickable plan.

Built for a hackathon on **SDG 10 (Reduced Inequalities)**. The people this is aimed
at are, almost by definition, dealing with systems that assume a stable address, valid
ID, and someone to ask. The bottleneck usually isn't motivation — it's that the
situation is *large and unsorted*, and every task seems to depend on another one you
haven't done yet. Rebuild does the sorting.

---

## What it does

1. **Free-text intake.** "Tell me what's going on and where you're starting from."
2. **Crisis screen.** A keyword check runs on the text *before* anything else. If it
   trips, the app shows crisis support instead of a checklist.
3. **Plan generation.** Gemini classifies which of seven life domains actually apply,
   then returns an ordered set of steps as strict JSON.
4. **Domain tabs.** Steps are grouped by domain, sorted by urgency, with dependencies
   surfaced ("usually easier after: *get your ID*").
5. **Tick things off.** Progress is saved immediately and survives a restart.
6. **"Explain this."** Per-step plain-language explanation of what it involves, why it
   matters, and what usually goes wrong.
7. **"Update my plan."** Re-plans around what's changed — and completed steps are
   preserved in code, not just requested in the prompt.

### The seven domains

`documents_id` · `housing` · `income_employment` · `healthcare` ·
`legal_compliance` · `support_network` · `mental_stability`

The taxonomy is hardcoded in [`schema.py`](schema.py). The model only chooses *which*
domains are relevant — it can't invent an eighth. Irrelevant domains are left out
entirely, so a divorce plan shows no parole tab.

---

## Setup

Requires Python 3.10+.

```bash
# 1. From this directory, create and activate a virtual environment
python -m venv .venv

#    Windows (PowerShell)
.venv\Scripts\Activate.ps1
#    macOS / Linux
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API key
cp .env.example .env        # Windows: copy .env.example .env
#    then edit .env and set GEMINI_API_KEY=your_key_here

# 4. Run
streamlit run app.py
```

A **free** Gemini API key is available at
[aistudio.google.com/apikey](https://aistudio.google.com/apikey). No paid services are
used. The app opens at `http://localhost:8501`.

### Configuration

All optional, all via `.env` — see [`.env.example`](.env.example):

| Variable | Default | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | *(required)* | Your free API key |
| `GEMINI_MODEL` | `gemini-3.5-flash` | Swap models if the app's own docs say so — see the quota note below before assuming this gives you a fresh allowance. The older 2.x generation (`gemini-2.5-flash` etc.) is no longer available to new API keys |
| `GEMINI_TIMEOUT_MS` | `90000` | Per-request timeout, in milliseconds. Gemini 3.x models "think" before answering, so this app's schema-constrained planning call needs more headroom than a simple chat reply — a too-short timeout can cut generation off mid-response and return an empty plan instead of a clean error |
| `GEMINI_THINKING_LEVEL` | `low` | How much internal reasoning Gemini does before answering (`minimal`/`low`/`medium`/`high`). See the note below — the floor setting (`minimal`) was tried and made things *worse*, not better |
| `GEMINI_MAX_OUTPUT_TOKENS` | `16384` | Output budget per call — needs room for a full multi-step plan to avoid being cut off |
| `ENABLE_LLM_CRISIS_CHECK` | `true` | Set `false` to skip the second-pass crisis check and save quota — the keyword check always runs |

**A note on the empty/truncated-plan failure, found the hard way:** this was chased through three different causes during real testing, in order:
1. *Thinking-budget exhaustion.* Gemini 3.x models reason before answering; a too-short timeout (originally 45s) could cut generation off mid-response. Fixed by raising the timeout to 90s.
2. *A genuine repetition loop.* Setting `thinking_level="minimal"` (the lowest level, tried to save latency) caused `gemini-3.1-flash-lite` to spiral into tens of thousands of characters of repeated filler ("one step at a time... stay dedicated...") and never finish the JSON. A small amount of reasoning (`"low"`) is what actually stopped it — less "thinking" is not free, especially for a small/fast model. `maxLength` on the schema's string fields did **not** reliably constrain this either; it's enforced loosely at best.
3. *A real schema gap.* `PLAN_RESPONSE_SCHEMA` only required the `type` field at the top level (needed so the separate "clarify" shape stays valid), which meant a model could legally satisfy the whole schema with just `{"type": "plan"}` and nothing else — and in production, more than one model took exactly that shortcut. Fixed with an `if`/`then` schema constraint: `type: "plan"` now requires `summary` and `steps` too.

If you still see this failure after all three fixes, it's most likely `gemini-3.1-flash-lite` specifically — see the model note below — or the free tier under heavy load. The "Notes on how this plan was built" expander and the technical-detail expander under any error message will show what actually happened; `extract_json()`'s error message also now distinguishes "cut off mid-generation" from "no JSON at all," which point at different causes.

**A note on daily quota, and on model choice generally:** the `gemini-3.x-flash` models (3.5/3.6/3.7/3.8) all carry the same tight 20-requests/day free-tier cap, easy to exhaust during active development since every automatic retry in `llm.py` counts as a separate request. `gemini-3.1-flash-lite` carries a much larger allowance (500/day, confirmed on [aistudio.google.com/rate-limit](https://aistudio.google.com/rate-limit), which requires login) and is a separate quota bucket from the `-flash` models. That dashboard's "RPD" column is a **28-day peak-usage chart, not a live "remaining today" counter** — a number shown above a model's limit means some single day in the past month went over, not that every day since has been blocked.

However: `gemini-3.1-flash-lite`'s generous quota comes with a real reliability cost for this app specifically. In repeated live testing it produced a correct plan roughly 1 time in 3, with the other attempts hitting the repetition-loop failure above even after every mitigation - a long system prompt plus a large nested JSON schema seems to be genuinely difficult for a model this size. The full `gemini-3.x-flash` models never showed this pattern in testing, only the (now-fixed) schema and timeout issues. If daily quota allows it, a full flash model is the more dependable choice for this app's task; flash-lite is the fallback for when quota is the binding constraint, not the first choice.

---

## Project structure

| File | Role |
|---|---|
| [`app.py`](app.py) | Streamlit UI and the intake → crisis → plan flow |
| [`llm.py`](llm.py) | Every Gemini call, plus retry/backoff and defensive JSON parsing |
| [`prompts.py`](prompts.py) | All prompt templates as constants — the safety rules live here |
| [`schema.py`](schema.py) | Domain taxonomy, the JSON schema, and the validator |
| [`storage.py`](storage.py) | Local JSON persistence keyed by session id |
| [`resources.py`](resources.py) | Human-verified fallback resources + crisis keyword list |
| [`tests/`](tests/) | Offline + live test suites — see [Testing](#testing) |

Uses `google-genai` ≥ 2.x, where `client.interactions.create(...)` replaced the older
`client.models.generate_content(...)`, structured output is requested via
`response_format`, and text comes back on `.output_text`.

---

## Ethical safeguards

This app talks to people at the worst point of their year, about things like criminal
records and immigration status. A confidently wrong answer here isn't an inconvenience
— it can cost someone a deadline, a benefit, or a place to sleep. Four safeguards are
built in, and each is enforced **in code**, not only by asking the model nicely.

**1. No fabricated real-world details.** The `NO_FABRICATION_RULE` in
[`prompts.py`](prompts.py) forbids the model from producing organisation names, phone
numbers, addresses, URLs, or specific legal/immigration/parole requirements — none of
which it can verify, and all of which it can generate very persuasively. Instead it
names the *type* of service and how to find it ("search for 'legal aid' plus your
city"). Where the app shows something concrete, it comes from
[`resources.py`](resources.py), which a human wrote and checked. Steps that hinge on an
unverifiable rule are reframed as *finding out* the rule: "confirm your exact reporting
requirements with your officer and write the dates down."

**2. Crisis detection before planning.** A keyword pass
(`resources.keyword_crisis_check`) runs on the raw text before any API call — so it
works even with no network and no API key, and it cannot fail. It's tuned to
over-trigger, with word-boundary matching so "I killed it at the interview" doesn't
false-positive. An optional second-pass LLM check catches phrasing the list can't
anticipate, and **fails open**: if that call errors, the user is not locked out. When
the screen fires, the user gets real crisis lines — 988, Crisis Text Line, Find A
Helpline for outside the US — instead of a checklist, because a to-do list is the wrong
response to someone in crisis. They can still choose to continue; deciding for an adult
that they may not proceed is its own harm.

**3. Ask rather than guess.** Thin, empty or nonsense input returns a `clarify`
response — one specific question — instead of a generic plan. A length check in
[`app.py`](app.py) catches the empty case before spending an API call at all. The app
would rather admit it doesn't know enough than produce plausible filler.

**4. It never crashes, and it never loses your progress.** Every API call retries with
exponential backoff and jitter on transient failures (429s, 5xx, timeouts) and fails
fast on permanent ones (bad key, malformed request). Model output is stripped of
markdown fences and parsed tolerantly; if it still won't parse, the app re-asks once
with a stricter nudge. Whatever survives goes through `validate_plan_response()`, which
drops off-taxonomy steps, renames duplicate ids, strips dangling dependencies, and
breaks dependency cycles that would otherwise leave a step permanently "blocked".
Repairs are shown to the user rather than hidden. Every failure surfaces as a readable
message with the cause behind an expander — never a traceback. And because a prompt
instruction is not a guarantee, `merge_preserving_progress()` re-inserts any completed
step the model dropped during a re-plan: ticking a box can't be undone by pressing
"Update my plan".

**Plus:** a persistent banner on every screen states that this is not legal, medical or
immigration advice, and carries crisis links. User text is fenced in `<user_input>`
tags with an explicit instruction to treat it as data, so intake text can't be used to
talk the model out of its own safety rules.

---

## Limitations — this is a prototype

Honest list, because the gap between this and something deployable is the interesting
part:

- **No encryption, no authentication.** `data/state.json` is plaintext on disk. The
  session id is a bearer token with no expiry — anyone holding it can read that plan.
  Users are asked about criminal records, immigration status and health, which under
  GDPR is *special category* data. Real deployment needs encryption at rest, real auth,
  a retention and deletion policy, and a lawful basis for processing. (A "Delete my
  data" button is wired up, which is the bare minimum, not sufficiency.)
- **Data leaves the machine.** Intake text is sent to Google's Gemini API. This is
  disclosed in the UI, but it's a real consideration for someone whose immigration
  status is precarious.
- **US- and English-centric.** 988 is a US service, and the model's implicit knowledge
  of bureaucracy skews Anglophone. `resources.py` needs local equivalents before use
  elsewhere.
- **Crisis detection is a blunt instrument.** Keyword matching plus a one-shot
  classifier is not a clinical screen. It will miss people and it will over-trigger.
  It's a floor, not a solution.
- **No human in the loop.** The highest-value version of this connects to a caseworker.

---

## Testing

```bash
python tests/run_all.py          # offline suites - no API key, no network
python tests/run_all.py --live   # also exercises the real Gemini API
```

| Suite | Needs a key? | Covers |
|---|---|---|
| `tests/test_offline.py` | no | Schema validation and repair (bad domains, duplicate ids, dangling `depends_on`, dependency cycles), crisis keyword matching including false-positive cases, storage round-trips, corrupt-file recovery, JSON extraction from fenced//noisy output, progress preservation |
| `tests/test_errors.py` | no* | Retry classification and user-facing messages across both SDK exception families |
| `tests/test_ui.py` | no | Full UI flows via Streamlit's `AppTest` — empty/short input rejection, crisis routing, plan rendering, checkbox persistence, resume, delete, missing-key state. LLM calls are stubbed |
| `tests/test_live.py` | **yes** | End-to-end plan generation, the clarify branch, `explain_step`, re-planning with progress preserved, the LLM crisis check, and a no-fabrication scan over real model output |

\* `test_errors.py` skips a single live invalid-key check when no key is set.

That the offline suites need neither a key nor a network is deliberate: the
safety-critical paths are exactly the ones that must keep working when everything else
doesn't.

A note on the no-fabrication scan in `test_live.py` — it regex-checks real model output
for invented phone numbers, URLs and email addresses. It's a smoke test, not a proof:
it can't catch a plausible-but-wrong *organisation name* or a fabricated legal
requirement, which is why the rule is stated so forcefully in the prompt rather than
relied upon to be caught afterwards.
