"""Streamlit Community Cloud entrypoint for the Bahn-Puls dashboard.

Why this file exists: Community Cloud splits the requirements path on spaces,
so it cannot install dependencies for an app inside "Term 1/Week 6/...". This
launcher lives in a space-free folder next to its own requirements.txt and
simply runs the real dashboard.
"""
import runpy
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[2] / "Term 1" / "Week 6" / "hackathon"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))  # so `import pulse` works

runpy.run_path(str(APP_DIR / "dashboard.py"), run_name="__main__")
