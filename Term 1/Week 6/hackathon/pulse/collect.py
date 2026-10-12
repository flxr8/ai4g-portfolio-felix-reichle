"""One full collection cycle: fetch -> filter -> store -> classify. Then exit.

Run with:  python -m pulse.collect

Designed to be started by a scheduler every 10 minutes, so it must be:
  * idempotent: items are keyed by sha256(URI) and inserted with
    INSERT OR IGNORE, so rerunning never creates duplicates;
  * crash-tolerant: the run is logged in `runs` *before* any work starts and
    finished in a `finally`, so even a crash leaves a trace for `status`;
  * self-healing: posts are stored first and classified second. If a model
    fails to load, the posts are still saved with NULL labels and the next run
    classifies them. A bad run never loses data or blocks the next one.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
import traceback
from collections import Counter

from dotenv import load_dotenv

from .bluesky import make_client, search_new_posts
from .config import PROJECT_DIR, load_config, setup_logging
from .db import connect, utcnow_iso
from .filters import Filters, _parse_ts

log = logging.getLogger("pulse.collect")


def fetch_and_store(conn, cfg: dict, errors: list[str]) -> tuple[int, int, int, bool]:
    """Returns (fetched, new, dropped, reached_api)."""
    client, mode = make_client()
    log.info("Bluesky client mode: %s", mode)
    filters = Filters(cfg)
    fetched_at = utcnow_iso()

    watermarks = dict(conn.execute("SELECT query, newest_indexed FROM query_state").fetchall())
    # uri -> (post, query, needs_context). First query to find a post wins.
    found: dict[str, tuple[dict, str, bool]] = {}
    new_watermarks: dict[str, str] = {}
    fetched = 0
    queries_ok = 0

    for qcfg in cfg["queries"]:
        q = qcfg["q"]
        try:
            posts, newest = search_new_posts(client, q, watermarks.get(q), cfg["fetch"])
            queries_ok += 1
        except Exception as e:  # noqa: BLE001 - one bad query must not stop the rest
            msg = f"query {q!r}: {type(e).__name__}: {str(e)[:200]}"
            log.warning(msg)
            errors.append(msg)
            continue
        fetched += len(posts)
        if newest:
            new_watermarks[q] = newest
        needs_ctx = qcfg.get("needs_context", False)
        for p in posts:
            prev = found.get(p["uri"])
            # Prefer a query that doesn't need the context check: if any
            # unambiguous query matched the post, it is relevant.
            if prev is None or (prev[2] and not needs_ctx):
                found[p["uri"]] = (p, q, needs_ctx)
        time.sleep(cfg["fetch"]["request_pause_seconds"])

    if queries_ok == 0:
        return fetched, 0, 0, False

    # Template signatures of recently stored texts, so a status bot that posts
    # once per run (and so never repeats inside one batch) is still caught.
    recent_sigs = Counter(
        filters.template_sig(r[0]) for r in conn.execute(
            "SELECT text FROM items WHERE fetched_at >= strftime('%Y-%m-%dT%H:%M:%SZ', 'now', '-3 days')"
        )
    )
    recent_sigs.pop("", None)

    # Bot detection looks at the whole batch at once (rate and template rules
    # need to see several posts by the same author).
    bot_dids = filters.find_bot_authors([p for p, _, _ in found.values()], recent_sigs)

    items, dropped = [], {}
    for p, q, needs_ctx in found.values():
        if p.get("author", {}).get("did") in bot_dids:
            reason = "bot"
        elif filters.template_sig(p["record"].get("text", "")) in recent_sigs:
            reason = "duplicate"  # same text (modulo numbers/links) already stored
        else:
            reason = filters.drop_reason(p, needs_ctx)
        if reason:
            dropped[reason] = dropped.get(reason, 0) + 1
            continue
        items.append(filters.to_item(p, q, fetched_at))
    # Author info is no longer needed; drop the references explicitly so the
    # privacy boundary is visible in the code.
    del found, bot_dids

    before = conn.total_changes
    with conn:  # one transaction: items and watermarks are saved together or not at all
        conn.executemany(
            """INSERT OR IGNORE INTO items
               (id, url, created_at, fetched_at, text, lang, query, kind, topics)
               VALUES (:id, :url, :created_at, :fetched_at, :text, :lang, :query, :kind, :topics)""",
            items,
        )
        new = conn.total_changes - before
        for q, ts in new_watermarks.items():
            old = watermarks.get(q)
            # Never move a watermark backwards.
            if old is None or _parse_ts(ts) > _parse_ts(old):
                conn.execute(
                    "INSERT INTO query_state(query, newest_indexed) VALUES (?, ?) "
                    "ON CONFLICT(query) DO UPDATE SET newest_indexed = excluded.newest_indexed",
                    (q, ts),
                )
    log.info("fetched=%d kept=%d new=%d dropped=%s", fetched, len(items), new, dropped)
    return fetched, new, sum(dropped.values()), True


def classify_pending(conn, cfg: dict, errors: list[str]) -> None:
    """Label every item that is still missing a label, model by model."""
    # Imported here so a broken torch install can't stop fetching.
    from .sentiment import SentimentModel

    mcfg = cfg["models"]
    for key in ("m1", "m2"):
        rows = conn.execute(
            f"SELECT id, text FROM items WHERE {key}_label IS NULL ORDER BY created_at DESC LIMIT ?",
            (mcfg["max_items_per_run"],),
        ).fetchall()
        if not rows:
            continue
        try:
            model = SentimentModel(mcfg[key])
            preds = model.predict([r["text"] for r in rows], mcfg["batch_size"])
            del model  # free ~1 GB before loading the next model
        except Exception as e:  # noqa: BLE001 - keep items, retry next run
            msg = f"{key} ({mcfg[key]['name']}): {type(e).__name__}: {str(e)[:200]}"
            log.error(msg)
            errors.append(msg)
            continue
        with conn:
            conn.executemany(
                f"UPDATE items SET {key}_label = ?, {key}_score = ? WHERE id = ?",
                [(lab, score, r["id"]) for (lab, score), r in zip(preds, rows)],
            )
        log.info("%s classified %d items", key, len(rows))


def main() -> int:
    setup_logging()
    load_dotenv(PROJECT_DIR / ".env")  # local runs; in CI the env comes from secrets
    cfg = load_config()
    conn = connect()
    # Several machines have run the collector (GitHub Actions, a teammate's
    # PC); recording which one keeps the run log honest after merging.
    source = os.getenv("PULSE_SOURCE", "local")
    run_id = conn.execute(
        "INSERT INTO runs(start, source) VALUES (?, ?)", (utcnow_iso(), source)
    ).lastrowid
    conn.commit()

    errors: list[str] = []
    fetched = new = dropped = 0
    ok = False
    try:
        fetched, new, dropped, ok = fetch_and_store(conn, cfg, errors)
        if not ok:
            errors.append("all queries failed - Bluesky unreachable or blocked")
        classify_pending(conn, cfg, errors)
    except Exception as e:  # noqa: BLE001 - always record the run
        ok = False
        errors.append(f"crash: {type(e).__name__}: {str(e)[:300]}")
        log.error(traceback.format_exc())
    finally:
        conn.execute(
            """UPDATE runs SET end = ?, items_fetched = ?, items_new = ?,
               items_dropped = ?, errors = ?, ok = ? WHERE id = ?""",
            (utcnow_iso(), fetched, new, dropped, json.dumps(errors, ensure_ascii=False), int(ok), run_id),
        )
        conn.commit()
        conn.close()
    log.info("run %d finished ok=%s new=%d errors=%d", run_id, ok, new, len(errors))
    # Non-zero exit only when the run achieved nothing, so the GitHub Actions
    # tab shows a red X for real outages but not for one flaky query.
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
