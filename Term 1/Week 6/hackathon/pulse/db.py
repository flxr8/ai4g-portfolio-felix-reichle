"""SQLite storage.

SQLite is a single file, so it can be committed to git, copied to a laptop
for the dashboard, and handed in with the submission. Data volume (thousands
of short posts) is far below anything that would need a server database.

Privacy by schema: there is deliberately no column for handle, DID, display
name or any profile data, so author information cannot leak into storage by
accident. (The one exception, the post URL, is discussed in config.yaml and
README.md.)
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id          TEXT PRIMARY KEY,   -- sha256 of the at:// URI (stable dedup key)
    url         TEXT,               -- link to the post (NULL if store_post_url=false)
    created_at  TEXT NOT NULL,      -- when the author posted it, UTC ISO-8601
    fetched_at  TEXT NOT NULL,      -- when we collected it, UTC ISO-8601
    text        TEXT NOT NULL,
    lang        TEXT,               -- Bluesky `langs`, comma-separated, may be NULL
    query       TEXT NOT NULL,      -- first search query that found it
    kind        TEXT NOT NULL,      -- 'news' or 'personal'
    topics      TEXT NOT NULL,      -- JSON list of topic keys
    m1_label    TEXT,               -- negative / neutral / positive (NULL = not yet classified)
    m1_score    REAL,               -- softmax probability of m1_label
    m2_label    TEXT,
    m2_score    REAL
);
CREATE INDEX IF NOT EXISTS idx_items_created ON items(created_at);

CREATE TABLE IF NOT EXISTS runs (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    start          TEXT NOT NULL,
    end            TEXT,            -- NULL means the run crashed before finishing
    items_fetched  INTEGER DEFAULT 0,  -- posts returned by the API (before filters)
    items_new      INTEGER DEFAULT 0,  -- rows actually inserted
    items_dropped  INTEGER DEFAULT 0,  -- removed by filters (bots, too short, ...)
    errors         TEXT DEFAULT '[]',  -- JSON list of error messages
    ok             INTEGER DEFAULT 0   -- 1 if the run reached the API and stored results
);

-- Per-query paging watermark: the newest `indexedAt` we have seen for each
-- query. Search results are ordered by indexedAt, so this is what we compare
-- against to stop paging. Kept separate from `items` because filtered-out
-- posts also advance the watermark.
CREATE TABLE IF NOT EXISTS query_state (
    query            TEXT PRIMARY KEY,
    newest_indexed   TEXT NOT NULL
);
"""


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def connect(path: Path = DB_PATH) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn
