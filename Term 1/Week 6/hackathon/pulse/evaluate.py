"""Compare both models against the hand labels.

    python -m pulse.evaluate                     # reads eval/to_label.csv
    python -m pulse.evaluate --labels other.csv

Outputs:
  eval/results.md     agreement (overall, personal, news), confusion matrices,
                      every disagreement
  eval/test_table.csv one row per labelled item with human + both model outputs

Model outputs are joined in from the database by `id`, because the labelling
CSV intentionally hides them (see sample.py).
"""
from __future__ import annotations

import argparse
import sqlite3
import sys

import pandas as pd

from .config import DB_PATH, EVAL_DIR

LABELS = ["negative", "neutral", "positive"]
MODELS = {"m1": "Model 1 (german-sentiment-bert)", "m2": "Model 2 (twitter-xlm-roberta)"}
BASELINE = ("b0", "Baseline (SentiWS word list)")


def add_baseline(df: pd.DataFrame) -> bool:
    """Score with SentiWS in place; returns False (and skips) if unavailable."""
    try:
        from .sentiws import label, load_lexicon
        lex = load_lexicon()
    except Exception as e:  # noqa: BLE001 - baseline is optional
        print(f"SentiWS baseline skipped ({type(e).__name__}: {e})")
        return False
    df["b0_label"], df["b0_score"] = zip(*(label(t, lex) for t in df["text"]))
    return True


def kappa(df: pd.DataFrame, key: str) -> float:
    """Cohen's kappa: agreement corrected for chance. Raw agreement flatters a
    system that mostly predicts the majority classes (here negative/neutral)."""
    if df.empty:
        return float("nan")
    po = (df[f"{key}_label"] == df["human_label"]).mean()
    pe = sum((df["human_label"] == l).mean() * (df[f"{key}_label"] == l).mean() for l in LABELS)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def load(labels_path: str) -> pd.DataFrame:
    # utf-8-sig strips the BOM sample.py writes; sep=None sniffs "," vs ";"
    # because German Excel saves CSVs with semicolons.
    human = pd.read_csv(labels_path, dtype=str, encoding="utf-8-sig", sep=None, engine="python").fillna("")
    human["human_label"] = human["human_label"].str.strip().str.lower()
    bad = human[(human["human_label"] != "") & ~human["human_label"].isin(LABELS)]
    if not bad.empty:
        raise SystemExit(f"Unknown labels {sorted(bad['human_label'].unique())}; use {LABELS}")
    human = human[human["human_label"] != ""]
    models = pd.read_sql(
        "SELECT id, m1_label, m1_score, m2_label, m2_score FROM items", sqlite3.connect(DB_PATH)
    )
    df = human.merge(models, on="id", how="left")
    missing = df["m1_label"].isna() | df["m2_label"].isna()
    if missing.any():
        print(f"Warning: {missing.sum()} labelled items have no model output in the DB; skipped.")
    return df[~missing]


def agreement(df: pd.DataFrame, key: str) -> str:
    if df.empty:
        return "n/a (0 items)"
    acc = (df[f"{key}_label"] == df["human_label"]).mean()
    return f"{acc:.0%} ({(df[f'{key}_label'] == df['human_label']).sum()}/{len(df)})"


def confusion(df: pd.DataFrame, key: str) -> str:
    cm = pd.crosstab(
        pd.Categorical(df["human_label"], LABELS), pd.Categorical(df[f"{key}_label"], LABELS),
        rownames=["human"], colnames=["model"], dropna=False,
    )
    rows = ["| human ↓ / model → | " + " | ".join(LABELS) + " |", "|---|" + "---|" * len(LABELS)]
    rows += [f"| **{h}** | " + " | ".join(str(cm.loc[h, m]) for m in LABELS) + " |" for h in LABELS]
    return "\n".join(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", default=str(EVAL_DIR / "to_label.csv"))
    args = ap.parse_args()
    df = load(args.labels)
    if df.empty:
        print("No labelled items found. Fill the human_label column first.")
        return 1

    systems = dict(MODELS)
    if add_baseline(df):
        systems[BASELINE[0]] = BASELINE[1]

    md = ["# Evaluation: models vs. human labels", "",
          f"{len(df)} hand-labelled items ({(df['kind'] == 'personal').sum()} personal, "
          f"{(df['kind'] == 'news').sum()} news). Labeller saw text only, not model output.", "",
          "## Agreement with the human label", "",
          "| | overall | Cohen's κ | personal | news |", "|---|---|---|---|---|"]
    for key, name in systems.items():
        md.append(f"| {name} | {agreement(df, key)} | {kappa(df, key):.2f} | "
                  f"{agreement(df[df.kind == 'personal'], key)} | {agreement(df[df.kind == 'news'], key)} |")
    md.append(f"| Model 1 vs Model 2 (with each other) | {(df.m1_label == df.m2_label).mean():.0%} | | | |")
    md += ["", "κ: 0 = no better than chance, 1 = perfect. Small sample: treat differences "
           "of a few items as noise."]
    md += ["", "Human label distribution: " +
           ", ".join(f"{l} {(df.human_label == l).sum()}" for l in LABELS), ""]
    if "off_topic" in df:
        n_off = (df["off_topic"].str.lower() == "yes").sum()
        md += [f"Not about rail (query noise): {n_off}/{len(df)} ({n_off / len(df):.0%})", ""]

    for key, name in systems.items():
        md += [f"## Confusion matrix: {name}", "", confusion(df, key), ""]

    dis = df[(df.m1_label != df.human_label) | (df.m2_label != df.human_label)]
    md += [f"## Disagreements ({len(dis)} items where at least one model differs from the human)", "",
           "| kind | human | M1 (score) | M2 (score) | SentiWS (sum) | text |", "|---|---|---|---|---|---|"]
    for _, r in dis.iterrows():
        text = r["text"].replace("\n", " ").replace("|", "\\|")[:200]
        md.append(f"| {r['kind']} | {r['human_label']} | {r['m1_label']} ({float(r['m1_score']):.2f}) | "
                  f"{r['m2_label']} ({float(r['m2_score']):.2f}) | "
                  f"{r.get('b0_label', '-')} ({float(r.get('b0_score', 0)):.2f}) | {text} |")

    EVAL_DIR.mkdir(exist_ok=True)
    (EVAL_DIR / "results.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    cols = ["id", "created_at", "kind", "topics", "lang", "text", "human_label", "off_topic",
            "m1_label", "m1_score", "m2_label", "m2_score", "b0_label", "b0_score"]
    out = df[[c for c in cols if c in df]].copy()
    for key in systems:
        out[f"{key}_correct"] = out[f"{key}_label"] == out.human_label
    out.to_csv(EVAL_DIR / "test_table.csv", index=False, encoding="utf-8")

    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(md[:md.index("## Confusion matrix: " + MODELS["m1"])]))
    print(f"\nWrote {EVAL_DIR / 'results.md'} and {EVAL_DIR / 'test_table.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
