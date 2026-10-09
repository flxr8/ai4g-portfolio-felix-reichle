"""Plain-English health check for the collector.

    python -m pulse.status             # check the local data/pulse.db
    python -m pulse.status --remote    # download the latest DB from GitHub first
    python -m pulse.status --markdown STATUS.md   # also write a Markdown copy

Written for a teammate who doesn't code: every line is a sentence, and the
last line is a single verdict, "OK" or "PROBLEM: message your teammate".
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .config import DB_PATH, load_config

try:
    from zoneinfo import ZoneInfo
    BERLIN = ZoneInfo("Europe/Berlin")
except Exception:  # noqa: BLE001 - Windows without the tzdata package
    BERLIN = timezone.utc

# The GitHub Actions workflow pushes the database to this branch.
REMOTE_DB_URL = (
    "https://raw.githubusercontent.com/flxr8/ai4g-portfolio-felix-reichle/"
    "bahn-puls-data/pulse.db"
)


def _ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _berlin(dt: datetime) -> str:
    return dt.astimezone(BERLIN).strftime("%a %d %b, %H:%M") + (" (Berlin time)" if BERLIN is not timezone.utc else " UTC")


def _ago(dt: datetime, now: datetime) -> str:
    mins = int((now - dt).total_seconds() // 60)
    if mins < 60:
        return f"{mins} min ago"
    return f"{mins // 60} h {mins % 60} min ago"


def build_report(db_path: Path) -> tuple[list[str], bool]:
    cfg = load_config()["status"]
    now = datetime.now(timezone.utc)
    lines: list[str] = []
    problems: list[str] = []

    if not db_path.exists():
        return [f"No database found at {db_path}."], False
    conn = sqlite3.connect(db_path)
    try:
        total = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        fetched = [_ts(r[0]) for r in conn.execute("SELECT fetched_at FROM items")]
        runs = conn.execute(
            "SELECT start, end, items_new, errors, ok FROM runs ORDER BY id DESC"
        ).fetchall()
        unclassified = conn.execute(
            "SELECT COUNT(*) FROM items WHERE m1_label IS NULL OR m2_label IS NULL"
        ).fetchone()[0]
    except sqlite3.OperationalError as e:
        return [f"The database exists but can't be read ({e})."], False
    finally:
        conn.close()

    # --- volume (by collection time, which is what proves continuous running)
    lines.append(f"Total items collected: {total}")
    per_day: dict[str, int] = {}
    for dt in fetched:
        day = dt.astimezone(BERLIN).strftime("%a %d %b")
        per_day[day] = per_day.get(day, 0) + 1
    lines.append("Items collected per day:")
    lines += [f"    {day}: {n}" for day, n in per_day.items()] or ["    (none yet)"]
    last_hour = sum(1 for dt in fetched if now - dt <= timedelta(hours=1))
    lines.append(f"Items collected in the last hour: {last_hour}")

    # --- runs
    ok_runs = [r for r in runs if r[4] == 1 and r[1]]
    if runs:
        first = _ts(runs[-1][0])
        hours = (now - first).total_seconds() / 3600
        lines.append(f"Collector running since: {_berlin(first)} ({hours:.0f} hours, {len(runs)} runs, {len(ok_runs)} successful)")
        lines.append(
            f"Goal: {cfg['target_items']} items and {cfg['target_hours']} hours. "
            f"Progress: {total}/{cfg['target_items']} items, {hours:.0f}/{cfg['target_hours']} hours."
        )
    if ok_runs:
        last_ok = _ts(ok_runs[0][1])
        lines.append(f"Last successful run: {_berlin(last_ok)} ({_ago(last_ok, now)})")
        if now - last_ok > timedelta(minutes=cfg["max_minutes_since_success"]):
            problems.append(f"no successful run for over {cfg['max_minutes_since_success']} minutes")
    else:
        lines.append("Last successful run: never")
        problems.append("the collector has never completed a successful run")

    # --- errors
    recent_errors = []
    for start, _end, _new, errs, _ok in runs:
        for e in json.loads(errs or "[]"):
            recent_errors.append((start, e))
        if len(recent_errors) >= 3:
            break
    if recent_errors:
        lines.append("Last errors (a few are normal, e.g. a network hiccup):")
        lines += [f"    {_berlin(_ts(s))}: {e}" for s, e in recent_errors[:3]]
    else:
        lines.append("Last errors: none")
    if len(runs) >= 3 and all(r[4] == 0 for r in runs[:3]):
        problems.append("the last 3 runs all failed")

    # --- silent failure: runs succeed but nothing new arrives
    if fetched and ok_runs:
        newest = max(fetched)
        if now - newest > timedelta(hours=cfg["max_hours_without_new_items"]):
            problems.append(f"no new items for over {cfg['max_hours_without_new_items']} hours")
    if unclassified > cfg["max_unclassified_items"]:
        problems.append(f"{unclassified} items are waiting for sentiment labels (models may be failing)")

    lines.append("")
    if problems:
        lines.append("VERDICT: PROBLEM: message your teammate")
        lines += [f"    Reason: {p}" for p in problems]
    else:
        lines.append("VERDICT: OK")
    lines.append(f"(checked {_berlin(now)})")
    return lines, not problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--remote", action="store_true", help="download the latest DB from GitHub first")
    ap.add_argument("--markdown", metavar="FILE", help="also write the report as Markdown")
    ap.add_argument("--count", action="store_true", help="print only the item count (used by the workflow)")
    args = ap.parse_args()

    db_path = DB_PATH
    if args.remote:
        db_path = DB_PATH.with_name("pulse_remote.db")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(REMOTE_DB_URL, db_path)

    if args.count:
        try:
            print(sqlite3.connect(db_path).execute("SELECT COUNT(*) FROM items").fetchone()[0])
        except sqlite3.OperationalError:
            print(0)  # brand-new or missing DB
        return 0

    lines, ok = build_report(db_path)
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(lines))
    if args.markdown:
        verdict = "✅ OK" if ok else "❌ PROBLEM: message your teammate"
        md = [f"# Bahn-Puls collector status: {verdict}", "", "```"] + lines + ["```", ""]
        Path(args.markdown).write_text("\n".join(md), encoding="utf-8")
    # Always exit 0: the verdict is the message. A non-zero exit here would
    # mark the GitHub run red even though collection itself worked.
    return 0


if __name__ == "__main__":
    sys.exit(main())
