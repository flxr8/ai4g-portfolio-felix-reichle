"""Download the live database from the `bahn-puls-data` branch.

    python -m pulse.pull          # -> data/pulse.db

The collector runs on GitHub, so the source of truth is the copy it publishes.
sample / evaluate / the dashboard all read data/pulse.db, so pull first to work
on fresh data. This overwrites the local data/pulse.db; the local file is only
ever a copy, so nothing is lost.
"""
from __future__ import annotations

import sqlite3
import sys
import urllib.error
import urllib.request
from pathlib import Path

from .config import DB_PATH

REMOTE_DB_URL = (
    "https://raw.githubusercontent.com/flxr8/ai4g-portfolio-felix-reichle/"
    "bahn-puls-data/pulse.db"
)


def pull(dest: Path = DB_PATH) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".download")
    urllib.request.urlretrieve(REMOTE_DB_URL, tmp)
    # Check the download is a readable DB before replacing the local copy,
    # so a half-finished download never clobbers a good file.
    conn = sqlite3.connect(tmp)
    try:
        conn.execute("SELECT COUNT(*) FROM items").fetchone()
    finally:
        conn.close()  # Windows won't rename a file that is still open
    tmp.replace(dest)
    return dest


def main() -> int:
    try:
        path = pull()
    except urllib.error.HTTPError as e:
        print(f"Download failed (HTTP {e.code}). 404 means the collector hasn't published yet.")
        return 1
    n = sqlite3.connect(path).execute("SELECT COUNT(*) FROM items").fetchone()[0]
    print(f"Downloaded the live database ({n} items) to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
