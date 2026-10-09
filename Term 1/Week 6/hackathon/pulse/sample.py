"""Export a stratified sample for hand-labelling.

    python -m pulse.sample            # 50 items -> eval/to_label.csv
    python -m pulse.sample --n 80 --seed 7

Stratified by (topic, kind) with round-robin picking, so rare strata such as
"strike/news" still get a few items instead of the sample being dominated by
the biggest group (personal posts tagged "other").

The CSV deliberately does NOT contain the model labels: seeing them while
labelling would anchor the human labeller and inflate agreement. evaluate.py
joins the model outputs back in by `id`.
"""
from __future__ import annotations

import argparse
import json
import random
import sqlite3
import sys

import pandas as pd

from .config import DB_PATH, EVAL_DIR


def primary_topic(topics_json: str) -> str:
    topics = json.loads(topics_json)
    specific = [t for t in topics if t != "other"]
    return specific[0] if specific else "other"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42, help="fixed so the sample is reproducible")
    ap.add_argument("--out", default=str(EVAL_DIR / "to_label.csv"))
    args = ap.parse_args()

    df = pd.read_sql("SELECT id, created_at, kind, topics, lang, text, url FROM items", sqlite3.connect(DB_PATH))
    if df.empty:
        print("No items in the database yet.")
        return 1
    df["stratum"] = df["topics"].map(primary_topic) + " / " + df["kind"]

    rng = random.Random(args.seed)
    pools = {s: g.sample(frac=1, random_state=args.seed).index.tolist() for s, g in df.groupby("stratum")}
    order = sorted(pools)
    rng.shuffle(order)
    picked: list[int] = []
    while len(picked) < min(args.n, len(df)):
        for s in order:
            if pools[s] and len(picked) < args.n:
                picked.append(pools[s].pop())

    out = df.loc[picked].drop(columns=["stratum"]).sort_values("created_at")
    out["human_label"] = ""  # fill with: negative / neutral / positive
    out.to_csv(args.out, index=False, encoding="utf-8")

    sys.stdout.reconfigure(encoding="utf-8")
    print(f"Wrote {len(out)} items to {args.out}")
    print(df.loc[picked, "stratum"].value_counts().to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
