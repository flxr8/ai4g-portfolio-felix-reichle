"""Bahn-Puls dashboard (read-only).

    streamlit run dashboard.py

Reads data/pulse.db (get the live copy with `python -m pulse.pull` or the
refresh button in the sidebar). The dashboard never writes to the database and
has no free-text input that produces answers: it is a chart and a table, not a
chatbot.
"""
from __future__ import annotations

import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from pulse.analysis import MIN_N, TZ, load_items, load_last_run, negative_share, rises
from pulse.config import DB_PATH, load_config

# Colours by job (dataviz reference palette): one series hue for the measured
# share, neutral grey for the reference (baseline) and for unreliable points,
# so "grey" consistently means "don't read too much into this".
SERIES = "#2a78d6"
NEUTRAL = "#8a8984"
MODEL_NAMES = {"m2": "Model 2 · twitter-xlm-roberta (multilingual)",
               "m1": "Model 1 · german-sentiment-bert (German only)"}

st.set_page_config(page_title="Bahn-Puls", page_icon="🚆", layout="wide")
cfg = load_config()
TOPIC_LABELS = {"all": "All topics"} | {k: v["label"] for k, v in cfg["topics"].items()}

st.title("Bahn-Puls · rail passenger sentiment on Bluesky")
st.warning(
    "**Not a representative survey.** Bluesky users skew young, urban and very online, "
    "and people post more when something goes wrong. Read changes against each topic's "
    f"own baseline, not absolute levels. Points based on fewer than {MIN_N} posts are greyed "
    "out and unreliable.",
    icon="⚠️",
)

# --------------------------------------------------------------- data
with st.sidebar:
    st.subheader("Data")
    if st.button("Refresh from GitHub", help="Download the latest database the collector published"):
        from pulse.pull import pull
        try:
            pull()
            st.cache_data.clear()
            st.success("Updated.")
        except Exception as e:  # noqa: BLE001
            st.error(f"Download failed: {e}")


@st.cache_data(ttl=600)
def get_data(_mtime: float):
    return load_items(DB_PATH), load_last_run(DB_PATH)


if not DB_PATH.exists():
    st.error("No data yet. Click **Refresh from GitHub** in the sidebar, or run `python -m pulse.pull`.")
    st.stop()
items, last_run = get_data(DB_PATH.stat().st_mtime)

with st.sidebar:
    st.caption(
        f"{len(items):,} posts · {items['created_at'].min():%d %b %H:%M} – "
        f"{items['created_at'].max():%d %b %H:%M} (Berlin time)"
    )
    if last_run is not None:
        st.caption(f"Last collector run: {last_run:%a %d %b %H:%M}")
    st.divider()
    st.caption(
        "Sentiment comes from two pre-trained Hugging Face models run locally. "
        "Posts are shown in the original German; there is no translation "
        "(no suitable local model within our dependencies)."
    )

# --------------------------------------------------------------- controls (one row)
c1, c2, c3 = st.columns([1, 1.3, 2])
granularity = c1.radio("Time step", ["Daily", "Hourly"], horizontal=True)
sources = c2.radio(
    "Posts", ["Personal", "News", "Both"], horizontal=True,
    help="Personal = posts without a link to a news site. News posts report events and "
         "read as 'negative' even when neutral in tone, so they are off by default.",
)
model = c3.radio("Sentiment model", list(MODEL_NAMES), format_func=MODEL_NAMES.get, horizontal=True)

freq = "D" if granularity == "Daily" else "h"
sel = items if sources == "Both" else items[items["kind"] == sources.lower()]
if granularity == "Hourly":
    # 48 h keeps hourly points readable; the daily view shows the full history.
    sel = sel[sel["created_at"] >= sel["created_at"].max() - pd.Timedelta(hours=48)]
shares = negative_share(sel, model, freq)
if shares.empty:
    st.info("No classified posts for this selection yet.")
    st.stop()

# --------------------------------------------------------------- the morning answer
latest = shares["period"].max()
period_fmt = "%a %d %b" if freq == "D" else "%a %d %b %H:00"
st.subheader(f"Topics against their baseline · {latest:{period_fmt}}")
r = rises(shares, latest)


def verdict(row) -> str:
    # Icon + words, never colour alone.
    if row["low_n"]:
        return "◌ too few posts"
    if pd.isna(row["baseline"]):
        return "◌ no baseline yet"
    if row["delta"] >= 0.10:
        return "▲ above baseline"
    if row["delta"] <= -0.10:
        return "▼ below baseline"
    return "● around baseline"


table = pd.DataFrame({
    "Topic": r["topic"].map(TOPIC_LABELS),
    "Status": r.apply(verdict, axis=1),
    "Negative share": r["share"],
    "Baseline": r["baseline"],
    "Change (points)": r["delta"] * 100,
    "Posts": r["n"],
})
st.dataframe(
    table, hide_index=True, width="stretch",
    column_config={
        "Negative share": st.column_config.NumberColumn(format="percent"),
        "Baseline": st.column_config.NumberColumn(format="percent"),
        "Change (points)": st.column_config.NumberColumn(format="%+.0f"),
    },
)
st.caption(
    f"Baseline = negative share over the previous 7 days ({'7 days' if freq == 'D' else '168 hours'}, "
    f"or all earlier data if less), excluding the period itself. It needs at least {MIN_N} earlier "
    "posts, so it stays blank until a topic has enough history. ±10 points counts as a change."
)

# --------------------------------------------------------------- small multiples
topics = ["all"] + [t for t in cfg["topics"] if t in set(shares["topic"])]
ncols = 3
nrows = math.ceil(len(topics) / ncols)
fig = make_subplots(
    rows=nrows, cols=ncols, subplot_titles=[TOPIC_LABELS[t] for t in topics],
    shared_xaxes=True, vertical_spacing=0.12 if nrows > 2 else 0.18, horizontal_spacing=0.06,
)
show_counts = freq == "D" or shares["period"].nunique() <= 30
for i, topic in enumerate(topics):
    row, col = i // ncols + 1, i % ncols + 1
    d = shares[shares["topic"] == topic]
    first = i == 0
    hover = (
        "%{x|" + period_fmt + "}<br>Negative: %{y:.0%} (%{customdata[2]} of %{customdata[1]} posts)"
        "<br>Baseline: %{customdata[3]}<extra></extra>"
    )
    custom = list(zip(
        d["topic"], d["n"], d["neg"],
        d["baseline"].map(lambda b: "n/a" if pd.isna(b) else f"{b:.0%}"),
        d["period"].dt.strftime("%Y-%m-%dT%H:%M"),
    ))
    # Line through all points, so the shape is visible...
    fig.add_trace(go.Scatter(
        x=d["period"], y=d["share"], mode="lines", line=dict(color=SERIES, width=2),
        connectgaps=False, hoverinfo="skip", showlegend=False,
    ), row=row, col=col)
    # ...reliable points as solid markers...
    ok = ~d["low_n"].to_numpy()
    fig.add_trace(go.Scatter(
        x=d["period"][ok], y=d["share"][ok], mode="markers+text" if show_counts else "markers",
        marker=dict(color=SERIES, size=8), text=[f"n={n}" for n in d["n"][ok]],
        textposition="top center", textfont=dict(size=10, color=NEUTRAL),
        customdata=[c for c, k in zip(custom, ok) if k], hovertemplate=hover,
        name="Negative share", legendgroup="share", showlegend=first,
    ), row=row, col=col)
    # ...and low-count points as hollow grey markers.
    low = ~ok & d["n"].gt(0).to_numpy()
    fig.add_trace(go.Scatter(
        x=d["period"][low], y=d["share"][low], mode="markers+text" if show_counts else "markers",
        marker=dict(color="rgba(0,0,0,0)", size=8, line=dict(color=NEUTRAL, width=2)),
        text=[f"n={n}" for n in d["n"][low]], textposition="top center",
        textfont=dict(size=10, color=NEUTRAL),
        customdata=[c for c, k in zip(custom, low) if k], hovertemplate=hover,
        name=f"Fewer than {MIN_N} posts (unreliable)", legendgroup="low", showlegend=first,
    ), row=row, col=col)
    fig.add_trace(go.Scatter(
        x=d["period"], y=d["baseline"], mode="lines", line=dict(color=NEUTRAL, width=2, dash="dash"),
        hoverinfo="skip", name="Baseline (previous 7 days)", legendgroup="base", showlegend=first,
    ), row=row, col=col)

fig.update_yaxes(range=[0, 1.12], tickformat=".0%", tickvals=[0, 0.25, 0.5, 0.75, 1], gridcolor="rgba(128,128,128,0.15)")
fig.update_xaxes(showgrid=False, tickformat="%d %b" if freq == "D" else "%d %b\n%H:00")
fig.update_layout(
    height=260 * nrows + 60, margin=dict(l=10, r=10, t=60, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.04, x=0),
    hovermode="closest",
)
st.subheader("Negative share per topic")
st.caption("Click a point to list the posts behind it.")
event = st.plotly_chart(fig, width="stretch", on_select="rerun", selection_mode="points", key="chart")

# --------------------------------------------------------------- drill-down
st.subheader("Posts behind a point")
sel_days = sorted(sel["created_at"].dt.floor("D").unique(), reverse=True)
topic_keys = list(TOPIC_LABELS)

# A click on the chart pre-fills the selectors below.
pts = (event or {}).get("selection", {}).get("points", []) if event else []
# The selection persists across reruns, so only act on a *new* click;
# otherwise it would undo every manual change to the selectors.
if pts and pts[0].get("customdata") and pts[0]["customdata"] != st.session_state.get("last_click"):
    st.session_state["last_click"] = pts[0]["customdata"]
    t_clicked, *_rest, p_clicked = pts[0]["customdata"]
    p_clicked = pd.Timestamp(p_clicked).tz_localize(TZ)
    st.session_state["dd_topic"] = t_clicked
    st.session_state["dd_day"] = p_clicked.floor("D")
    if freq == "h":
        st.session_state["dd_hour"] = p_clicked.hour

d1, d2, d3 = st.columns([1, 1.3, 1])
day = d1.selectbox("Day", sel_days, format_func=lambda d: f"{d:%a %d %b}", key="dd_day")
topic = d2.selectbox("Topic", topic_keys, format_func=TOPIC_LABELS.get, key="dd_topic")
hour = d3.selectbox("Hour", [None] + list(range(24)), key="dd_hour",
                    format_func=lambda h: "All day" if h is None else f"{h:02d}:00–{h:02d}:59")

posts = sel[sel["created_at"].dt.floor("D") == day]
if topic != "all":
    posts = posts[posts["topics"].map(lambda ts: topic in ts)]
if hour is not None:
    posts = posts[posts["created_at"].dt.hour == hour]
posts = posts.sort_values("created_at")

neg = (posts[f"{model}_label"] == "negative").sum()
st.caption(f"{len(posts)} posts · {neg} negative" + (" · fewer than 10, treat with care" if len(posts) < MIN_N else ""))
st.dataframe(
    pd.DataFrame({
        "Time": posts["created_at"].dt.strftime("%H:%M"),
        "Text (original German)": posts["text"],
        "Label": posts[f"{model}_label"],
        "Confidence": posts[f"{model}_score"],
        "Type": posts["kind"],
        "Link": posts["url"],
    }),
    hide_index=True, width="stretch",
    column_config={
        "Text (original German)": st.column_config.TextColumn(width="large"),
        "Confidence": st.column_config.ProgressColumn(min_value=0, max_value=1, format="%.2f"),
        "Link": st.column_config.LinkColumn(display_text="open"),
    },
)

with st.expander("How to read this / what not to use it for"):
    st.markdown(
        f"""
- **Negative share** = share of posts in a topic that the selected model labels negative.
  A post can belong to several topics (keyword match on the German text).
- **Baseline** = the same share over the previous 7 days. A topic matters when it rises
  above *its own* baseline: some topics (delays) are always more negative than others.
- **Confidence** is the model's probability for its label, not a measure of truth.
  Check the hand-labelled evaluation (`eval/results.md`) for how often each model is right.
- **Do not** use this to judge individual staff, to rank lines or regions on a handful of posts,
  or to claim a problem is solved because people stopped posting about it.
- Times are Europe/Berlin. Only posts are stored, never who wrote them.
"""
    )
