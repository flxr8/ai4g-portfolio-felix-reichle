"""
Run the Rebuild test suite.

    python tests/run_all.py          # offline tests only (no API key needed)
    python tests/run_all.py --live   # also run the tests that call Gemini

The offline suites are the important ones to be able to run anywhere: the
safety-critical paths (validation, crisis keyword screening, error
classification, progress preservation) are exactly the ones that must keep
working when the network or the API does not.
"""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
PYTHON = sys.executable

OFFLINE = [
    ("offline logic", "test_offline.py"),
    ("error classification", "test_errors.py"),
    ("UI flows", "test_ui.py"),
]
LIVE = [("live Gemini API", "test_live.py")]


def main() -> int:
    suites = OFFLINE + (LIVE if "--live" in sys.argv else [])
    results = []

    for label, filename in suites:
        print(f"\n{'=' * 70}\n  {label}  ({filename})\n{'=' * 70}")
        proc = subprocess.run([PYTHON, str(ROOT / filename)])
        results.append((label, proc.returncode == 0))

    print(f"\n{'=' * 70}\n  SUMMARY\n{'=' * 70}")
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")

    if "--live" not in sys.argv:
        print("\n  (live API tests skipped - re-run with --live to include them)")

    return 0 if all(ok for _, ok in results) else 1


if __name__ == "__main__":
    sys.exit(main())
