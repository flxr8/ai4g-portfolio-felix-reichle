"""Merge databases from several collectors into one.

    python -m pulse.merge data/pulse_github.db:github-actions \\
                          data/pulse_dylan_final.db:partner-pc \\
                          --out data/pulse.db

Each input is PATH or PATH:SOURCE. SOURCE labels that DB's runs (when they
don't already carry one), so the merged run log still shows which machine
collected when.

Why merging is safe: items are keyed by sha256(post URI), and every collector
runs the same code, models and pinned revisions. When two collectors stored
the same post, we keep the copy fetched first (earliest fetched_at); its
labels are identical anyway, which the merge checks and reports.

Backdated posts (created more than max_backdate_days before they were
fetched, e.g. imported tweet archives) are dropped here too, for data
collected before collect.py filtered them.
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

from .config import load_config
from .db import connect

ITEM_COLS = ["id", "url", "created_at", "fetched_at", "text", "lang", "query", "kind",
             "topics", "m1_label", "m1_score", "m2_label", "m2_score"]
RUN_COLS = ["start", "end", "items_fetched", "items_new", "items_dropped", "errors", "ok"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="PATH or PATH:SOURCE")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out = Path(args.out)
    inputs = []
    for spec in args.inputs:
        path, sep, source = spec.rpartition(":")
        # No label given, or the ':' belongs to a Windows drive ("C:\...").
        if not sep or len(path) <= 1 or "/" in source or "\\" in source:
            path, source = spec, ""
        p = Path(path).resolve()
        if p == out.resolve():
            raise SystemExit(f"--out must not be one of the inputs ({p}); write to a new file.")
        inputs.append((p, source or None))
    if out.exists():
        raise SystemExit(f"{out} exists; remove it first (merging is never done in place).")

    max_days = load_config()["filters"].get("max_backdate_days", 7)
    conn = connect(out)
    rows: list[tuple] = []
    for path, source in inputs:
        src = sqlite3.connect(path)
        rows += src.execute(f"SELECT {', '.join(ITEM_COLS)} FROM items").fetchall()
        run_cols = RUN_COLS + (["source"] if "source" in {r[1] for r in src.execute("PRAGMA table_info(runs)")} else [])
        for r in src.execute(f"SELECT {', '.join(run_cols)} FROM runs ORDER BY start"):
            r = dict(zip(run_cols, r))
            r["source"] = r.get("source") or source or "unknown"
            conn.execute(
                "INSERT INTO runs(start, end, items_fetched, items_new, items_dropped, errors, ok, source) "
                "VALUES (:start, :end, :items_fetched, :items_new, :items_dropped, :errors, :ok, :source)", r,
            )
        for q, ts in src.execute("SELECT query, newest_indexed FROM query_state"):
            # Keep the newest watermark per query (ISO strings sort chronologically).
            conn.execute(
                "INSERT INTO query_state VALUES (?, ?) ON CONFLICT(query) DO UPDATE SET "
                "newest_indexed = MAX(newest_indexed, excluded.newest_indexed)", (q, ts),
            )
        src.close()

    # Earliest fetch first, so INSERT OR IGNORE keeps the first-collected copy.
    rows.sort(key=lambda r: r[ITEM_COLS.index("fetched_at")])
    seen: dict[str, tuple] = {}
    label_conflicts = 0
    for r in rows:
        prev = seen.setdefault(r[0], r)
        if prev is not r and (prev[9], prev[11], prev[8], prev[7]) != (r[9], r[11], r[8], r[7]):
            label_conflicts += 1
    conn.executemany(f"INSERT OR IGNORE INTO items VALUES ({', '.join('?' * len(ITEM_COLS))})", rows)
    backdated = conn.execute(
        "DELETE FROM items WHERE julianday(fetched_at) - julianday(created_at) > ?", (max_days,)
    ).rowcount
    # Runs from different machines interleave; renumber them by start time.
    conn.execute("CREATE TEMP TABLE r AS SELECT * FROM runs ORDER BY start")
    conn.execute("DELETE FROM runs")
    conn.execute("DELETE FROM sqlite_sequence WHERE name = 'runs'")
    conn.execute(f"INSERT INTO runs({', '.join(RUN_COLS)}, source) SELECT {', '.join(RUN_COLS)}, source FROM r")
    conn.commit()

    n = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"Merged {len(rows)} item rows from {len(inputs)} databases -> {n} unique items in {out}")
    print(f"  dropped as backdated (> {max_days} days): {backdated}")
    print(f"  duplicates with different labels/topics/kind: {label_conflicts} (expected 0)")
    for source, cnt, first, last in conn.execute(
        "SELECT source, COUNT(*), MIN(start), MAX(start) FROM runs GROUP BY source"
    ):
        print(f"  runs from {source}: {cnt} ({first} -> {last})")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
