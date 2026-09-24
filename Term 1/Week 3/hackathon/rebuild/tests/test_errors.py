"""Error-classification tests: synthetic exceptions + one real bad-key call."""
# Make the project importable when this file is run directly from tests/.
import pathlib as _pathlib
import sys as _sys
_ROOT = _pathlib.Path(__file__).resolve().parent.parent
_sys.path.insert(0, str(_ROOT))

import os
import sys

import llm

FAILS = []


def check(label, cond, extra=""):
    if not cond:
        FAILS.append(label)
        print(f"  [FAIL] {label}  -> {extra}")
    else:
        print(f"  [PASS] {label}")


# Stand-ins for both SDK exception families.
class NewStyle(Exception):
    """compat_errors flavour: .status_code"""
    def __init__(self, status_code, msg=""):
        super().__init__(msg or f"Error code: {status_code}")
        self.status_code = status_code


class OldStyle(Exception):
    """google.genai.errors flavour: .code"""
    def __init__(self, code, msg=""):
        super().__init__(msg or f"Error code: {code}")
        self.code = code


class APITimeoutError(Exception):
    pass


class APIConnectionError(Exception):
    pass


# The exact message Gemini returned in production on 2026-09-23 when the
# gemini-3.5-flash free-tier daily cap (20 requests/day) was hit. Captured
# verbatim so this regression test tracks the real wire format, not a guess.
DAILY_QUOTA_MSG = (
    "Error code: 429 - {'error': {'message': 'Rate limit exceeded for model "
    "gemini-3.5-flash (limit: 20 requests per day on Free Tier). Please retry "
    "later or upgrade your tier at https://ai.dev/rate-limit.', 'code': "
    "'too_many_requests'}}"
)

# Captured verbatim on 2026-09-24 from a brand-new API key on a freshly
# created Google account: the key itself was well-formed, but its project was
# blocked from API access entirely. Genuinely different from an invalid key -
# telling the user to re-check GEMINI_API_KEY here would be actively wrong.
PROJECT_DENIED_MSG = (
    "Error code: 403 - {'error': {'message': 'Your project has been denied "
    "access. Please contact support.', 'code': 'permission_denied'}}"
)

print("\n== _is_transient ==")
TRANSIENT = [NewStyle(429), NewStyle(500), NewStyle(503), NewStyle(408), OldStyle(429),
             OldStyle(500), APITimeoutError("timed out"), APIConnectionError("reset")]
PERMANENT = [NewStyle(400), NewStyle(401), NewStyle(403), NewStyle(404), OldStyle(400),
             OldStyle(403), ValueError("nope"), NewStyle(429, DAILY_QUOTA_MSG),
             NewStyle(403, PROJECT_DENIED_MSG)]
for e in TRANSIENT:
    check(f"retries {type(e).__name__}({getattr(e, 'status_code', getattr(e, 'code', '-'))})",
          llm._is_transient(e))
for e in PERMANENT:
    check(f"does not retry {type(e).__name__}({getattr(e, 'status_code', getattr(e, 'code', '-'))})",
          not llm._is_transient(e))

print("\n== _friendly_error messages ==")
cases = [
    (NewStyle(429), "rate-limit", ["rate-limiting"]),
    (OldStyle(429), "rate-limit (old style)", ["rate-limiting"]),
    (NewStyle(401), "401 -> key", ["key"]),
    (NewStyle(403), "403 -> key", ["key"]),
    (NewStyle(400, "Error code: 400 - API key not valid. Please pass a valid API key."),
     "400 API_KEY_INVALID -> key", ["key", ".env"]),
    (NewStyle(400, "Error code: 400 - {'reason': 'API_KEY_INVALID'}"),
     "400 reason code -> key", ["key"]),
    (NewStyle(500), "5xx -> try later", ["trouble"]),
    (NewStyle(503), "503 -> try later", ["trouble"]),
    (NewStyle(400, "malformed"), "plain 400 -> rejected", ["rejected"]),
    (APITimeoutError("x"), "timeout -> connection", ["timed out"]),
    (APIConnectionError("x"), "connection -> connection", ["timed out"]),
    (ValueError("weird"), "unknown -> generic", ["went wrong"]),
    (NewStyle(403, PROJECT_DENIED_MSG), "403 project denied -> distinct message, NOT 'check your key'",
     ["project", "not a typo or a bad key"]),
    (NewStyle(429, DAILY_QUOTA_MSG), "429 daily quota -> distinct message",
     ["today's free gemini quota", "gemini_model", "resets daily"]),
]
for exc, label, needles in cases:
    err = llm._friendly_error(exc)
    ok = all(n.lower() in err.message.lower() for n in needles)
    check(label, ok, err.message)
    check(f"{label}: detail populated", bool(err.detail))

print("\n== live: real invalid key ==")
real = os.environ.get("GEMINI_API_KEY", "")
if not real.strip():
    # Everything above is offline; only this last check needs the network.
    print("  [SKIP] no GEMINI_API_KEY set - skipping the live invalid-key check")
    print("\n" + "=" * 60)
    print("ALL OFFLINE ERROR-HANDLING TESTS PASSED" if not FAILS else "FAILURES")
    sys.exit(1 if FAILS else 0)

llm._client = None
os.environ["GEMINI_API_KEY"] = "definitely-not-a-valid-key"
try:
    llm.generate_plan("I was released from prison last week and have no ID or housing.")
    check("invalid key raises LLMError", False, "no exception")
except llm.LLMError as e:
    check("invalid key raises LLMError", True)
    check("message names the key", "key" in e.message.lower(), e.message)
    check("message points at .env", ".env" in e.message, e.message)
    print(f"    -> {e.message}")
except Exception as e:
    check("invalid key raises LLMError", False, f"{type(e).__name__}: {e}")
finally:
    os.environ["GEMINI_API_KEY"] = real
    llm._client = None

print("\n" + "=" * 60)
if FAILS:
    print(f"{len(FAILS)} FAILURES:")
    for f in FAILS:
        print("  -", f)
    sys.exit(1)
print("ALL ERROR-HANDLING TESTS PASSED")
