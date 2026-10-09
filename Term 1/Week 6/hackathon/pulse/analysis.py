"""Aggregations behind the dashboard, kept free of Streamlit so they can be
tested and reused in the report.

Key definitions (so we can explain every number on screen):
  * negative share = negative items / all items in that topic and period.
  * baseline       = pooled negative share over the PREVIOUS 7 days (168 hourly
    periods), excluding the current period, or all earlier data if there is less.
    Excluding the current period matters: a spike shouldn't raise its own
    baseline and hide itself. Pooling (sum of negatives / sum of items) instead
    of averaging daily shares stops a 2-item day from weighing as much as a
    200-item day.
  * low count     = fewer than MIN_N items: shown greyed, never flagged as a rise.
    The same minimum applies to the baseline; with less history it is blank.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd

TZ = "Europe/Berlin"
MIN_N = 10


def load_items(db_path: Path) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql(
            "SELECT id, url, created_at, text, lang, kind, topics, "
            "m1_label, m1_score, m2_label, m2_score FROM items",
            conn,
        )
    finally:
        conn.close()
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True).dt.tz_convert(TZ)
    df["topics"] = df["topics"].map(json.loads)
    return df


def load_last_run(db_path: Path) -> pd.Timestamp | None:
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute("SELECT MAX(end) FROM runs WHERE ok = 1").fetchone()
    finally:
        conn.close()
    return pd.Timestamp(row[0]).tz_convert(TZ) if row and row[0] else None


def explode_topics(df: pd.DataFrame) -> pd.DataFrame:
    """One row per (item, topic); an item with two topics counts in both."""
    return df.explode("topics").rename(columns={"topics": "topic"})


def negative_share(df: pd.DataFrame, model: str, freq: str) -> pd.DataFrame:
    """Per topic and period: n, negatives, share, baseline, low_n.

    Includes an "all" pseudo-topic (each item once). `freq` is "D" or "h".
    Empty periods are kept (n=0) so the time axis has no silent gaps.
    """
    label = f"{model}_label"
    d = df[df[label].notna()].copy()
    if d.empty:
        return pd.DataFrame(columns=["topic", "period", "n", "neg", "share", "baseline", "low_n"])
    d["period"] = d["created_at"].dt.floor(freq)
    d["is_neg"] = d[label] == "negative"

    per_topic = explode_topics(d)
    all_rows = d.assign(topic="all")
    both = pd.concat([all_rows, per_topic], ignore_index=True)

    periods = pd.date_range(d["period"].min(), d["period"].max(), freq=freq, tz=TZ)
    window = 7 if freq == "D" else 7 * 24
    out = []
    for topic, g in both.groupby("topic"):
        agg = g.groupby("period").agg(n=("id", "size"), neg=("is_neg", "sum")).reindex(periods, fill_value=0)
        agg.index.name = "period"
        prev_n = agg["n"].shift(1).rolling(window, min_periods=1).sum()
        prev_neg = agg["neg"].shift(1).rolling(window, min_periods=1).sum()
        agg["share"] = agg["neg"] / agg["n"].where(agg["n"] > 0)
        # A baseline built on 1-2 posts is as unreliable as a point built on
        # 1-2 posts, so it needs MIN_N items behind it too.
        agg["baseline"] = prev_neg / prev_n.where(prev_n >= MIN_N)
        agg["baseline_n"] = prev_n.fillna(0).astype(int)
        agg["low_n"] = agg["n"] < MIN_N
        agg["topic"] = topic
        out.append(agg.reset_index())
    return pd.concat(out, ignore_index=True)


def rises(shares: pd.DataFrame, period: pd.Timestamp) -> pd.DataFrame:
    """Topics in `period` ranked by how far negative share is above baseline."""
    cur = shares[(shares["period"] == period) & (shares["topic"] != "all")].copy()
    cur["delta"] = cur["share"] - cur["baseline"]
    return cur.sort_values(["low_n", "delta"], ascending=[True, False])
