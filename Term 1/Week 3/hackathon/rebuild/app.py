"""
app.py - Rebuild: the Streamlit UI and main flow.

Rebuild helps someone reorganise their life during a major disruptive transition
- release from prison, moving country, divorce, losing housing - by turning a
messy free-text description of their situation into an ordered, tickable plan
across seven life domains.

Built for a hackathon on SDG 10 (Reduced Inequalities). The people this is aimed
at are, almost by definition, dealing with institutions that assume a stable
address, valid ID and a support network. The goal is a calm checklist, not
advice.

Flow:
    intake -> crisis screen (if triggered)
           -> clarifying question (if the input is too thin)
           -> plan, grouped by domain, with per-step explanations and re-planning

Run with:  streamlit run app.py
"""

from __future__ import annotations

from typing import Any

import streamlit as st

import llm
import resources
import storage
from schema import DOMAIN_LABELS, domains_in_plan, sort_steps

# --------------------------------------------------------------------------
# Page setup
# --------------------------------------------------------------------------

st.set_page_config(
    page_title="Rebuild",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Small amount of CSS purely for the urgency badges - Streamlit has no native
# inline badge that reads well next to a checkbox label.
st.markdown(
    """
    <style>
      .badge {
        display: inline-block; padding: 1px 8px; border-radius: 10px;
        font-size: 0.72rem; font-weight: 600; letter-spacing: .02em;
        vertical-align: middle; margin-right: 6px;
      }
      .badge-high   { background: #fdecea; color: #a4262c; }
      .badge-medium { background: #fff4e5; color: #8a5300; }
      .badge-low    { background: #eef3f8; color: #35506b; }
      .step-meta    { color: #6b7280; font-size: 0.8rem; margin: -4px 0 8px 0; }
      .blocked      { color: #8a5300; font-size: 0.8rem; margin: -4px 0 8px 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

URGENCY_BADGE = {
    "high": '<span class="badge badge-high">URGENT</span>',
    "medium": '<span class="badge badge-medium">SOON</span>',
    "low": '<span class="badge badge-low">WHEN YOU CAN</span>',
}


# --------------------------------------------------------------------------
# Session bootstrapping
# --------------------------------------------------------------------------


def init_session() -> None:
    """Set up per-browser-session keys exactly once.

    The session id is the only identity in this app: no login, no password. It
    is generated on first visit and can be pasted back into the sidebar to
    resume a plan later.
    """
    if "session_id" not in st.session_state:
        st.session_state.session_id = storage.new_session_id()

    st.session_state.setdefault("view", "intake")        # intake | crisis | plan
    st.session_state.setdefault("pending_question", "")  # clarifying question, if any
    st.session_state.setdefault("error", None)           # LLMError to display
    st.session_state.setdefault("crisis_reason", "")     # why the crisis screen fired
    st.session_state.setdefault("explain_error", {})     # step id -> error message
    # What triggered the crisis screen, so "I'm safe" can resume the right flow:
    # {"flow": "intake"|"replan", "text": str}
    st.session_state.setdefault("crisis_pending", None)
    # The exact text the user has clicked through. Scoped to the text, never to
    # the session - see _needs_crisis_screen().
    st.session_state.setdefault("crisis_acknowledged_text", "")


def current_state() -> dict[str, Any]:
    """Load this session's persisted state fresh from disk."""
    return storage.load_state(st.session_state.session_id)


# --------------------------------------------------------------------------
# Persistent chrome: disclaimer banner + sidebar
# --------------------------------------------------------------------------


def render_banner() -> None:
    """The always-visible disclaimer and crisis links.

    Required on every screen, including the crisis screen and error states.
    Deliberately compact so it doesn't crowd the actual content, with the full
    text one click away.
    """
    st.caption(
        "⚠️ **Rebuild does not give legal, medical or immigration advice.** "
        "It helps you get organised — always confirm anything official with a "
        "qualified person. · Crisis support: **call or text 988** (US) · "
        "[findahelpline.com](https://findahelpline.com) (international)"
    )

    with st.expander("What this tool is, and what it isn't"):
        st.markdown(
            """
**Rebuild is a planning aid.** It uses an AI model to turn what you describe
into an ordered checklist, so that a large situation becomes a set of small
steps.

**It is not a lawyer, doctor, immigration adviser or caseworker.** It cannot
tell you your legal obligations, your visa conditions, your parole requirements
or your medical options. Anything with a deadline or a legal consequence must be
confirmed with the office or professional responsible for it.

**It deliberately does not name specific organisations, phone numbers or
addresses.** The AI has no way to check whether a particular local service still
exists, and being sent to a dead phone number when you are already stretched is
worse than being sent nowhere. Instead it tells you what *kind* of service to
look for. The verified starting points in the sidebar were checked by a human.

**It can still be wrong.** Treat every step as a suggestion to sanity-check, not
an instruction.

**Your privacy:** this is a hackathon prototype. What you type is stored
unencrypted in a local file on the machine running this app, and is sent to
Google's Gemini API to generate your plan. Please don't enter anything you would
not want stored in plain text.
            """
        )


def render_sidebar() -> None:
    """Session controls and the human-verified resource list."""
    with st.sidebar:
        st.markdown("### 🧭 Rebuild")
        st.caption("One large problem, broken into small steps.")

        st.divider()

        # --- session / resume -------------------------------------------
        st.markdown("**Your session**")
        st.code(st.session_state.session_id, language=None)
        st.caption(
            "Save this code to pick up where you left off. Anyone with it can "
            "read your plan, so keep it to yourself."
        )

        with st.form("resume_form", clear_on_submit=True):
            resume_id = st.text_input("Resume a session", placeholder="paste your code")
            if st.form_submit_button("Resume") and resume_id.strip():
                st.session_state.session_id = resume_id.strip()
                existing = current_state()
                # Jump straight to the plan if that code has one.
                st.session_state.view = "plan" if existing.get("plan") else "intake"
                st.session_state.pending_question = ""
                st.session_state.error = None
                st.rerun()

        st.divider()

        # --- verified resources -----------------------------------------
        st.markdown("**If you need help now**")
        for item in resources.CRISIS_RESOURCES:
            if item["url"]:
                st.markdown(f"- [{item['name']}]({item['url']}) — {item['contact']}")
            else:
                st.markdown(f"- **{item['name']}** — {item['contact']}")

        st.markdown("**General starting points**")
        for item in resources.GENERAL_RESOURCES:
            if item["url"]:
                st.markdown(f"- [{item['name']}]({item['url']}) — {item['contact']}")
            else:
                st.markdown(f"- **{item['name']}** — {item['contact']}")

        st.caption("These were checked by a person, not generated by the AI.")

        st.divider()

        # --- data controls ----------------------------------------------
        if st.button("Delete my data", use_container_width=True):
            storage.delete_state(st.session_state.session_id)
            st.session_state.session_id = storage.new_session_id()
            st.session_state.view = "intake"
            st.session_state.pending_question = ""
            st.session_state.error = None
            st.rerun()
        st.caption("Erases this plan from the local file immediately.")


def render_error() -> None:
    """Show a stored LLMError, if any, without taking the app down."""
    err = st.session_state.get("error")
    if not err:
        return

    st.error(err.message)
    if err.detail:
        with st.expander("Technical detail"):
            st.code(err.detail)
    if st.button("Dismiss"):
        st.session_state.error = None
        st.rerun()


# --------------------------------------------------------------------------
# Crisis screen
# --------------------------------------------------------------------------


def render_crisis() -> None:
    """Shown instead of a plan when the crisis check triggers.

    A checklist is the wrong response to someone in crisis. We show human help
    first and make it the visually dominant thing on the screen - but we do not
    lock the person out of the app, because deciding for an adult that they may
    not proceed is its own kind of harm.
    """
    st.markdown("## You don't have to sort this out alone")
    st.markdown(
        "Something you wrote suggests you might be having a really hard time right "
        "now. Before anything else — a checklist isn't what you need at this moment, "
        "and a person is. These are free, confidential, and open right now."
    )

    for item in resources.CRISIS_RESOURCES:
        with st.container(border=True):
            st.markdown(f"**{item['name']}**")
            st.markdown(f"### {item['contact']}")
            if item["note"]:
                st.caption(item["note"])
            if item["url"]:
                st.markdown(f"[{item['url']}]({item['url']})")

    st.info(
        "This list is US- and English-centric because those services are the ones "
        "we could verify. **Find A Helpline** covers over 100 countries — please "
        "use it if you are elsewhere. If you are deploying this tool in another "
        "country, add your local equivalents to `resources.py` first."
    )

    st.divider()
    st.caption(
        "If you're safe and you'd still like to carry on making a plan, you can. "
        "The support above isn't going anywhere."
    )
    if st.button("I'm safe — continue to my plan"):
        # Acknowledge only the exact text that triggered this screen, then resume
        # whichever flow was interrupted so they don't have to retype it.
        pending = st.session_state.get("crisis_pending") or {}
        st.session_state.crisis_acknowledged_text = pending.get("text", "")
        st.session_state.crisis_pending = None

        if pending.get("flow") == "replan":
            st.session_state.view = "plan"
            _handle_replan(pending.get("text", ""))
        else:
            st.session_state.view = "intake"
            if pending.get("text"):
                _handle_new_plan(pending["text"])
        st.rerun()


# --------------------------------------------------------------------------
# Intake
# --------------------------------------------------------------------------

INTAKE_MIN_CHARS = 25  # below this, any plan would be generic filler


def _run_crisis_checks(text: str) -> bool:
    """Keyword screen, then optional LLM screen. True if the crisis view is due.

    The keyword pass is free and cannot fail, so it always runs first. The LLM
    pass only runs if the keyword pass came back clean, and fails open.
    """
    triggered, matched = resources.keyword_crisis_check(text)
    if triggered:
        st.session_state.crisis_reason = f"keyword match: {', '.join(matched)}"
        return True

    if llm.ENABLE_LLM_CRISIS_CHECK:
        with st.spinner("One moment..."):
            if llm.llm_crisis_check(text):
                st.session_state.crisis_reason = "model-flagged"
                return True

    return False


def _needs_crisis_screen(text: str, flow: str) -> bool:
    """Decide whether to interrupt this submission with the crisis screen.

    An "I'm safe" click acknowledges *that specific text*, not the session. If
    the acknowledgement were session-wide, one click would silently disable the
    check for everything the person wrote afterwards - including an update weeks
    later saying something quite different. Scoping it to the exact text still
    avoids trapping them in a loop on the message they already dismissed.
    """
    stripped = text.strip()
    if stripped and stripped == st.session_state.get("crisis_acknowledged_text", "").strip():
        return False

    if _run_crisis_checks(text):
        st.session_state.crisis_pending = {"flow": flow, "text": text}
        return True
    return False


def _handle_new_plan(intake_text: str) -> None:
    """Crisis-check, then generate and persist a plan. Never raises."""
    if _needs_crisis_screen(intake_text, "intake"):
        st.session_state.view = "crisis"
        st.rerun()

    try:
        # This can genuinely take 30-60s: Gemini reasons through the full
        # domain classification and dependency ordering before writing the
        # plan, which is slower than a normal chat reply.
        with st.spinner("Working out where to start... this can take up to a minute."):
            response, warnings = llm.generate_plan(intake_text)
    except llm.LLMError as exc:
        # Caught, stored, rendered as a friendly error - the app stays up.
        # render_error() runs near the top of main(), *before* this function is
        # reached in the current script run, so without a rerun the message
        # would sit in session_state unrendered until the user's next click -
        # the spinner would just vanish with nothing to show for it.
        st.session_state.error = exc
        st.rerun()

    if response["type"] == "clarify":
        # The model judged the input too thin to plan from. Ask, don't guess.
        st.session_state.pending_question = response["question"]
        state = current_state()
        state["intake_text"] = intake_text
        storage.save_state(state)
        st.rerun()

    state = current_state()
    state["intake_text"] = intake_text
    state["plan"] = {"summary": response["summary"], "steps": response["steps"]}
    state["completed"] = []
    state["explanations"] = {}
    state["warnings"] = warnings
    storage.save_state(state)

    st.session_state.pending_question = ""
    st.session_state.view = "plan"
    st.rerun()


def render_intake() -> None:
    """The opening free-text prompt, and the clarifying-question follow-up."""
    st.markdown("## Let's work out where to start")

    if not llm.api_key_present():
        st.error(
            "No Gemini API key configured. Copy `.env.example` to `.env`, add your "
            "`GEMINI_API_KEY`, and restart the app. See the README for setup steps."
        )
        return

    # --- the model asked for more detail ------------------------------------
    if st.session_state.pending_question:
        st.info(f"**{st.session_state.pending_question}**")
        st.caption(
            "There wasn't quite enough to build a useful plan from yet — a couple "
            "more sentences will do it."
        )

        with st.form("clarify_form"):
            answer = st.text_area(
                "Your answer",
                height=140,
                placeholder="A few more details...",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("Try again", type="primary")

        if submitted:
            if not answer.strip():
                st.warning("Add a sentence or two so there's something to work from.")
            else:
                # Combine the original intake with the answer so context is kept.
                previous = current_state().get("intake_text", "")
                combined = f"{previous}\n\n{answer.strip()}".strip()
                _handle_new_plan(combined)

        if st.button("Start over instead"):
            st.session_state.pending_question = ""
            st.rerun()
        return

    # --- first-time intake --------------------------------------------------
    st.markdown(
        "Tell me what's going on and where you're starting from. Write it however "
        "it comes out — it doesn't need to be organised, that's my job."
    )

    with st.form("intake_form"):
        intake_text = st.text_area(
            "Your situation",
            height=220,
            placeholder=(
                "For example: what's just changed, where you're staying, what "
                "documents you do or don't have, whether you've got money coming "
                "in, anything with a deadline, and who (if anyone) is helping you."
            ),
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Build my plan", type="primary")

    if submitted:
        stripped = intake_text.strip()
        # Edge case: empty or near-empty input. Handled in code, not just in the
        # prompt, so we never spend an API call on an empty string.
        if not stripped:
            st.warning("Write a little about your situation first, and I'll take it from there.")
        elif len(stripped) < INTAKE_MIN_CHARS:
            st.warning(
                "That's not quite enough to work from yet. A couple of sentences "
                "about what's changed and what you're worried about is plenty."
            )
        else:
            _handle_new_plan(stripped)

    st.caption(
        "Nothing here is sent anywhere except Google's Gemini API, which generates "
        "your plan. Please don't include anything you wouldn't want stored in plain text."
    )


# --------------------------------------------------------------------------
# Plan rendering
# --------------------------------------------------------------------------


def _on_toggle_step(step_id: str) -> None:
    """Checkbox callback: persist the tick immediately.

    State is re-read from disk here rather than closed over, because Streamlit
    callbacks can fire against a stale snapshot after a rerun.
    """
    state = storage.load_state(st.session_state.session_id)
    storage.set_step_completed(state, step_id, st.session_state[f"done_{step_id}"])


def render_step(state: dict[str, Any], step: dict[str, Any], all_steps: list[dict[str, Any]]) -> None:
    """One step: checkbox, metadata, prerequisites, and its explanation."""
    step_id = step["id"]
    completed = set(state.get("completed", []))
    is_done = step_id in completed

    with st.container(border=True):
        st.checkbox(
            step["title"],
            value=is_done,
            key=f"done_{step_id}",
            on_change=_on_toggle_step,
            args=(step_id,),
        )

        st.markdown(
            f"{URGENCY_BADGE.get(step['urgency'], '')}"
            f"<span class='step-meta'>≈ {step['est_time']}</span>",
            unsafe_allow_html=True,
        )

        # Surface unfinished prerequisites so the order is visible, but never
        # disable the checkbox - the user knows their own situation better than
        # the model does, and may well have done things out of order.
        titles_by_id = {s["id"]: s["title"] for s in all_steps}
        blockers = [
            titles_by_id[d]
            for d in step.get("depends_on", [])
            if d in titles_by_id and d not in completed
        ]
        if blockers and not is_done:
            st.markdown(
                f"<div class='blocked'>⤷ Usually easier after: {', '.join(blockers)}</div>",
                unsafe_allow_html=True,
            )

        if step.get("description"):
            st.write(step["description"])

        # --- explain this -------------------------------------------------
        explanation = state.get("explanations", {}).get(step_id)

        if explanation:
            with st.expander("What this involves", expanded=False):
                st.write(explanation)
        else:
            if st.button("Explain this", key=f"explain_{step_id}"):
                try:
                    with st.spinner("Thinking..."):
                        text = llm.explain_step(step, state.get("intake_text", ""), all_steps)
                except llm.LLMError as exc:
                    # Per-step failure must not break the rest of the plan.
                    st.session_state.explain_error[step_id] = exc.message
                else:
                    fresh = storage.load_state(st.session_state.session_id)
                    fresh.setdefault("explanations", {})[step_id] = text
                    storage.save_state(fresh)
                    st.session_state.explain_error.pop(step_id, None)
                st.rerun()

        if st.session_state.explain_error.get(step_id):
            st.warning(st.session_state.explain_error[step_id])


def _handle_replan(update_text: str) -> None:
    """Re-generate the plan, preserving completed steps. Never raises."""
    state = current_state()
    plan = state.get("plan") or {}

    # New free text goes through the same crisis screen as the original intake.
    if update_text.strip() and _needs_crisis_screen(update_text, "replan"):
        st.session_state.view = "crisis"
        st.rerun()

    try:
        with st.spinner("Rethinking your plan... this can take up to a minute."):
            response, warnings = llm.replan(
                intake_text=state.get("intake_text", ""),
                update_text=update_text,
                current_steps=plan.get("steps", []),
                completed_ids=state.get("completed", []),
            )
    except llm.LLMError as exc:
        # See the matching comment in _handle_new_plan: without a rerun this
        # never reaches the screen, since render_error() already ran earlier
        # in this same script execution.
        st.session_state.error = exc
        st.rerun()

    if response["type"] == "clarify":
        # Nothing is discarded - the existing plan stays exactly as it was.
        st.session_state.error = llm.LLMError(
            f"Before updating the plan: {response['question']}",
            "The model asked for more detail instead of re-planning.",
        )
        st.rerun()

    state["plan"] = {"summary": response["summary"], "steps": response["steps"]}
    state["warnings"] = warnings
    if update_text.strip():
        state.setdefault("updates", []).append(update_text.strip())

    # Drop cached explanations for steps that no longer exist, and drop completed
    # ids for the same reason, so progress counts stay honest.
    live_ids = {s["id"] for s in response["steps"]}
    state["explanations"] = {
        k: v for k, v in state.get("explanations", {}).items() if k in live_ids
    }
    state["completed"] = [sid for sid in state.get("completed", []) if sid in live_ids]

    storage.save_state(state)
    st.rerun()


def render_plan() -> None:
    """The main plan view: progress, domain tabs, and the update controls."""
    state = current_state()
    plan = state.get("plan")

    if not plan or not plan.get("steps"):
        # Defensive: someone resumed a session id that has no plan.
        st.session_state.view = "intake"
        st.rerun()

    steps = plan["steps"]

    st.markdown("## Your plan")
    if plan.get("summary"):
        st.markdown(plan["summary"])

    # --- progress -----------------------------------------------------------
    done, total = storage.progress_counts(state)
    st.progress(done / total if total else 0.0, text=f"{done} of {total} steps done")
    if total and done == total:
        st.success("That's everything on the list. If things have changed, update the plan below.")

    # Non-fatal repairs made while validating the model's output. Shown quietly
    # for transparency rather than hidden, but never as an alarming error.
    if state.get("warnings"):
        with st.expander(f"Notes on how this plan was built ({len(state['warnings'])})"):
            for warning in state["warnings"]:
                st.caption(f"• {warning}")

    st.divider()

    # --- steps grouped by domain -------------------------------------------
    present_domains = domains_in_plan(steps)
    completed = set(state.get("completed", []))

    labels = []
    for domain in present_domains:
        in_domain = [s for s in steps if s["domain"] == domain]
        domain_done = sum(1 for s in in_domain if s["id"] in completed)
        labels.append(f"{DOMAIN_LABELS[domain]} ({domain_done}/{len(in_domain)})")

    for tab, domain in zip(st.tabs(labels), present_domains):
        with tab:
            st.caption(resources.DOMAIN_RESOURCE_HINTS.get(domain, [""])[0])
            for step in sort_steps([s for s in steps if s["domain"] == domain]):
                render_step(state, step, steps)

    st.divider()

    # --- update the plan ----------------------------------------------------
    st.markdown("### Something changed?")
    st.caption(
        "Tell me what's different and I'll rework the plan around it. Anything "
        "you've already ticked off stays ticked off."
    )

    with st.form("replan_form"):
        update_text = st.text_area(
            "What's changed",
            height=120,
            placeholder="e.g. I got my ID back, but the hostel says I have to leave on Friday.",
            label_visibility="collapsed",
        )
        if st.form_submit_button("Update my plan", type="primary"):
            _handle_replan(update_text)

    with st.expander("Start a completely new plan"):
        st.caption("This clears the current plan and your progress on it.")
        if st.button("Clear and start over"):
            storage.delete_state(st.session_state.session_id)
            st.session_state.session_id = storage.new_session_id()
            st.session_state.view = "intake"
            st.session_state.pending_question = ""
            st.session_state.crisis_pending = None
            st.session_state.crisis_acknowledged_text = ""
            st.rerun()


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------


def main() -> None:
    init_session()

    st.title("Rebuild")
    st.caption("One large problem, broken into small steps.")

    render_banner()
    render_sidebar()
    render_error()
    st.divider()

    view = st.session_state.view
    if view == "crisis":
        render_crisis()
    elif view == "plan":
        render_plan()
    else:
        render_intake()


if __name__ == "__main__":
    main()
