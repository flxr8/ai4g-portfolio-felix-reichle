"""
resources.py - Curated, human-verified fallback resources.

Everything in this file was written by a person and checked by hand. The LLM is
explicitly forbidden from inventing organisation names, phone numbers or URLs
(see prompts.py), so when the app needs to point someone at something concrete,
it points at *this* list rather than at model output.

Deliberately generic: these are national/international entry points and
categories of service, not local listings. A hackathon prototype has no way to
verify that a particular shelter in a particular city is still open, and sending
someone in crisis to a dead phone number is worse than sending them nowhere.
"""

from __future__ import annotations

import re

# --------------------------------------------------------------------------
# Crisis resources - shown instead of a plan when the crisis check triggers
# --------------------------------------------------------------------------
#
# US-centric by necessity (988 is a US service). The "add your local equivalent"
# note is load-bearing, not a disclaimer: anyone deploying this outside the US
# should extend this list before use.

CRISIS_RESOURCES: list[dict[str, str]] = [
    {
        "name": "988 Suicide & Crisis Lifeline (US)",
        "contact": "Call or text 988",
        "url": "https://988lifeline.org",
        "note": "Free, confidential, 24/7. Chat is available on the website too.",
    },
    {
        "name": "Crisis Text Line",
        "contact": "Text HOME to 741741 (US), 686868 (Canada), 85258 (UK)",
        "url": "https://www.crisistextline.org",
        "note": "Text-based support with a trained volunteer, 24/7.",
    },
    {
        "name": "Find A Helpline",
        "contact": "findahelpline.com",
        "url": "https://findahelpline.com",
        "note": "Free helplines in over 100 countries - pick your country to get a local number.",
    },
    {
        "name": "Befrienders Worldwide",
        "contact": "befrienders.org",
        "url": "https://www.befrienders.org",
        "note": "International network of emotional-support centres.",
    },
    {
        "name": "Emergency services",
        "contact": "911 (US/Canada), 112 (EU), 999 (UK), or your local emergency number",
        "url": "",
        "note": "If you or someone else is in immediate physical danger.",
    },
]

# Shown in the persistent banner on every screen - a short subset of the above.
BANNER_RESOURCES: list[dict[str, str]] = [
    {
        "name": "988 Suicide & Crisis Lifeline (US)",
        "contact": "Call or text 988",
        "url": "https://988lifeline.org",
    },
    {
        "name": "Find A Helpline (international)",
        "contact": "findahelpline.com",
        "url": "https://findahelpline.com",
    },
]

# --------------------------------------------------------------------------
# General-purpose starting points
# --------------------------------------------------------------------------

GENERAL_RESOURCES: list[dict[str, str]] = [
    {
        "name": "211 (US & Canada)",
        "contact": "Dial 211, or visit 211.org",
        "url": "https://www.211.org",
        "note": "Free referral line for housing, food, benefits and local services.",
    },
    {
        "name": "FindHelp",
        "contact": "findhelp.org",
        "url": "https://www.findhelp.org",
        "note": "Search free and reduced-cost services near a US ZIP code.",
    },
    {
        "name": "Your local public library",
        "contact": "Walk in and ask at the desk",
        "url": "",
        "note": (
            "Free internet, printing and scanning - which most paperwork needs - plus "
            "staff who can usually point you at local services. No ID or address needed to enter."
        ),
    },
]

# Generic, location-free hints per domain. These give the model (and the UI)
# something honest to say instead of inventing a specific agency name.
DOMAIN_RESOURCE_HINTS: dict[str, list[str]] = {
    "documents_id": [
        "Search for the government office that issues ID in your country or state.",
        "Ask a library or community centre if they help with document applications.",
    ],
    "housing": [
        "Search for 'emergency shelter' or 'housing assistance' plus your city.",
        "In the US and Canada, 211 can refer you to local housing help.",
    ],
    "income_employment": [
        "Search for your local employment or jobcentre office.",
        "Ask about benefits you may already be eligible for before job-hunting.",
        "Some banks offer basic accounts with lighter ID requirements - ask what they accept.",
    ],
    "healthcare": [
        "Search for 'community health centre' or 'sliding scale clinic' plus your area.",
        "Many areas have clinics that see patients without insurance or ID.",
    ],
    "legal_compliance": [
        "Search for 'legal aid' plus your city or region for free or low-cost advice.",
        "Write down every date and requirement you have been given, and confirm each "
        "one with the office that set it - do not rely on memory or on this app.",
    ],
    "support_network": [
        "Look for peer support or mutual aid groups for people in your situation.",
        "A caseworker, if you have one, can often unlock several steps at once.",
    ],
    "mental_stability": [
        "Search for low-cost counselling in your area, or ask a clinic for a referral.",
        "Crisis lines are not only for emergencies - many take calls from people who "
        "are simply overwhelmed.",
    ],
}


# --------------------------------------------------------------------------
# Crisis-language detection (keyword first pass)
# --------------------------------------------------------------------------
#
# This is a deliberately blunt instrument, and it runs BEFORE any API call so it
# still works when the network or the API key does not. It is tuned to
# over-trigger rather than under-trigger: showing crisis resources to someone who
# did not need them costs a click, missing someone who did costs much more.
#
# Phrases are matched with word boundaries so that, e.g., "I killed it at the
# interview" does not match "kill myself". llm.py adds an optional second-pass
# LLM check to catch phrasing this list cannot anticipate.

CRISIS_PHRASES: list[str] = [
    # explicit self-harm / suicide
    "kill myself",
    "killing myself",
    "end my life",
    "ending my life",
    "take my own life",
    "taking my own life",
    "suicide",
    "suicidal",
    "self harm",
    "self-harm",
    "hurt myself",
    "hurting myself",
    "cut myself",
    "overdose",
    "not want to live",
    "don't want to live",
    "dont want to live",
    "want to die",
    "wish i was dead",
    "wish i were dead",
    "better off dead",
    "better off without me",
    "no reason to live",
    "nothing to live for",
    # hopelessness that warrants a human, not a checklist
    "no way out",
    "can't go on",
    "cant go on",
    "cannot go on",
    "give up on life",
    "no point in living",
    "end it all",
]

# Pre-compiled for speed and so the word-boundary logic lives in one place.
_CRISIS_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(p) for p in CRISIS_PHRASES) + r")\b",
    re.IGNORECASE,
)


def keyword_crisis_check(text: str) -> tuple[bool, list[str]]:
    """First-pass crisis screen on raw user text.

    Returns `(triggered, matched_phrases)`. Pure string matching - no API call,
    no cost, and it cannot fail. Always run this before the planning flow.
    """
    if not text or not text.strip():
        return False, []

    matches = _CRISIS_PATTERN.findall(text)
    # findall returns the captured group; de-duplicate while preserving order.
    seen: list[str] = []
    for m in matches:
        lowered = m.lower()
        if lowered not in seen:
            seen.append(lowered)
    return bool(seen), seen
