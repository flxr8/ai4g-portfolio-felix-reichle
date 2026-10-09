"""Hand-labelling tool for eval/to_label.csv.

    streamlit run label_app.py

Shows one post at a time with three buttons and saves to the CSV after every
click, so you can stop and resume any time. Model predictions are never shown
here, so they can't anchor your judgement.

This is a local labelling aid for us, not part of the user-facing product.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from pulse.config import EVAL_DIR

CSV = EVAL_DIR / "to_label.csv"
LABELS = ["negative", "neutral", "positive"]

st.set_page_config(page_title="Bahn-Puls labelling", layout="centered")
st.title("Label posts")

if not CSV.exists():
    st.error("No eval/to_label.csv yet. Run `python -m pulse.sample` first.")
    st.stop()


def load() -> pd.DataFrame:
    df = pd.read_csv(CSV, dtype=str, encoding="utf-8-sig").fillna("")
    if "off_topic" not in df:
        df["off_topic"] = ""
    return df


def save(df: pd.DataFrame) -> None:
    df.to_csv(CSV, index=False, encoding="utf-8-sig")


df = load()
done = (df["human_label"] != "").sum()
st.progress(done / len(df), text=f"{done} of {len(df)} labelled")

with st.sidebar:
    st.subheader("Labelling guide")
    st.markdown(
        """
Label **the author's attitude**, not whether the event is bad.

- **negative**: complaint, frustration, sarcasm ("Danke, DB 🙃"), criticism
- **neutral**: factual report or announcement, question, no clear attitude.
  A news headline about a disruption is *neutral* unless it editorialises.
- **positive**: praise, relief, satisfaction ("pünktlich und leer, herrlich")

Mixed? Pick the dominant tone. Not about rail at all (e.g. "ein Zug der
Polizei")? Tick **not about rail** below, then still pick the tone, so we can
report how much noise the queries let through.
        """
    )
    show_all = st.checkbox("Revisit already-labelled items")

todo = df.index if show_all else df.index[df["human_label"] == ""]
if len(todo) == 0:
    st.success("All items labelled. Now run `python -m pulse.evaluate`.")
    st.stop()

if "pos" not in st.session_state or st.session_state.pos >= len(todo):
    st.session_state.pos = 0
i = todo[st.session_state.pos]
row = df.loc[i]

st.caption(f"Item {i + 1} · {row['kind']} · topics {row['topics']} · lang {row['lang'] or 'n/a'}")
st.markdown(f"> {row['text']}".replace("\n", "\n> "))
if row.get("url"):
    st.markdown(f"[Open on Bluesky for context]({row['url']})")
if row["human_label"]:
    st.info(f"Current label: **{row['human_label']}**")

off = st.checkbox("not about rail", value=row["off_topic"] == "yes", key=f"off_{i}")
cols = st.columns(len(LABELS) + 1)
for col, label in zip(cols, LABELS):
    if col.button(label, width="stretch", type="primary" if label == row["human_label"] else "secondary"):
        df.loc[i, "human_label"] = label
        df.loc[i, "off_topic"] = "yes" if off else ""
        save(df)
        if show_all:
            st.session_state.pos += 1
        st.rerun()
if cols[-1].button("skip", width="stretch"):
    st.session_state.pos += 1
    st.rerun()
