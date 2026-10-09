# Bahn-Puls: live passenger sentiment for Deutsche Bahn (Bluesky)

> Hackathon, Term 1 Week 6 · SDG 9 (Industry, Innovation and Infrastructure) · pair project
> Status: collector live on GitHub Actions since 2026-10-09. Evaluation code, labelling tool and dashboard built; hand labels TODO.

## 1. The problem
Passengers voice delays, crowding, app failures and construction chaos on social media
long before these show up in official complaint statistics. A regional customer-
communication team has to decide **every morning which issue deserves proactive
communication**, today mostly by gut feeling or by whichever complaint was loudest.
Bahn-Puls turns the public stream into one signal: *for which topic is negative
sentiment rising above its own recent baseline, and which posts are behind it?*

TODO (team): one or two sentences with a concrete example from our data
(e.g. a Stellwerksstörung day).

## 2. The stream and Bluesky's terms of use
- **Source:** Bluesky public search, `app.bsky.feed.searchPosts`, `sort=latest`, 29
  German queries in [`config.yaml`](config.yaml). Reddit was out of scope (API access
  needs approval).
- **Auth (checked 2026-10-09):** search works anonymously via `api.bsky.app` but is
  blocked (403) on `public.api.bsky.app`. The collector logs in with an **app password**
  when one is configured and falls back to anonymous access otherwise.
- **Terms (our reading, TODO verify against the current text):** Bluesky's developer
  guidelines permit working with public data, ask developers to respect deletions and
  user intent, and rule out profiling individuals. We store **no author data** (see Ethics). Rate use is ~30–60 requests
  per 10 minutes, well within the documented limits.
  TODO (team): link the current Bluesky Developer Guidelines / ToS and quote the
  relevant lines.

## 3. The user and the decision
**User:** a regional DB customer-communication team, or a passenger association such
as Pro Bahn.
**Decision (daily, morning):** *Which issue gets proactive communication today?*
**What the tool shows them:** per topic, the share of negative passenger posts per
day/hour against that topic's 7-day baseline, the number of posts behind every point,
and the posts themselves.

## 4. SDG 9 rationale
SDG 9.1 calls for "quality, reliable, sustainable and resilient infrastructure … with a
focus on affordable and equitable access for all". Rail is the backbone of low-carbon
mobility in Germany, and its *perceived* reliability decides whether people keep using
it. Bahn-Puls gives infrastructure operators a cheap, continuous, passenger-centred
feedback channel. It complements punctuality statistics with what the delays mean to the
people affected (missed connections, overcrowding, inaccessible platforms).
TODO (team): link to the specific SDG 9 target(s) your course expects.

## 5. Models (summary; full version in [docs/model_cards.md](docs/model_cards.md))
| | Model 1 | Model 2 |
|---|---|---|
| | `oliverguhr/german-sentiment-bert` | `cardiffnlp/twitter-xlm-roberta-base-sentiment` |
| Data | 1.8 M German reviews, tweets, Facebook, Wikipedia | 198 M tweets; sentiment fine-tuned in 8 languages incl. German |
| Licence | MIT | not stated on Hub (code repo Apache-2.0) |
| Known limits | weaker on tweets (F1 0.68–0.74); preprocessing strips emojis (sarcasm signal) | no German-specific score on card |

Both run **locally on CPU** via `transformers`, at pinned revisions. No chat-model API is used.
Labels are normalised to negative / neutral / positive, and label + probability are
stored for both.
**Evaluation** (`python -m pulse.evaluate`): agreement and Cohen's κ against our own hand labels,
overall and personal vs news, confusion matrices, every disagreement, and a **SentiWS word-list
baseline** (CC BY-NC-SA 3.0, downloaded on demand, not redistributed) to show what the
transformers add. Results: TODO, in `eval/results.md` once the 50 items are labelled.

## 6. Architecture
```
GitHub Actions (cron, every 10 min)
  └─ python -m pulse.collect
       1. restore data/pulse.db from branch `bahn-puls-data`
       2. for each query: page searchPosts (sort=latest) until the per-query
          watermark (newest indexedAt already seen) or 24 h on first run
       3. filters (in memory): empty, <4 words, cross-posted RTs, bots
          (self-label, name pattern, template repeats, posting rate),
          rail-context check for ambiguous queries
       4. derive: id = sha256(URI), kind = news|personal (linked domain),
          topics (German keyword regexes), lang
       5. INSERT OR IGNORE into items    → idempotent
       6. classify unlabelled items with Model 1 and Model 2 (batched, CPU)
       7. log the run in `runs` (start, end, counts, errors)
  └─ python -m pulse.status → STATUS.md + job summary
  └─ force-push pulse.db + STATUS.md as one commit to `bahn-puls-data`
python -m pulse.pull → local copy of pulse.db
streamlit run dashboard.py → read-only dashboard on that copy
```
**Design choices:**
- *Store first, classify second.* A model failure never loses posts; the next run labels them.
- *Separate data branch, single commit.* No merge conflicts with code commits and no
  repo bloat from ~430 binary DB versions. A guard refuses to publish if the item count
  ever shrinks.
- *Watermark on `indexedAt`, not `createdAt`.* Search is ordered by index time, and
  `createdAt` is set by the client and can be wrong.

**Schema:** `items(id, url, created_at, fetched_at, text, lang, query, kind, topics,
m1_label, m1_score, m2_label, m2_score)`, `runs(start, end, items_fetched, items_new,
items_dropped, errors, ok)`, `query_state(query, newest_indexed)`.

## 7. How to run
```bash
cd "Term 1/Week 6/hackathon"
python -m venv .venv && .venv/Scripts/activate          # Windows (Linux/macOS: source .venv/bin/activate)
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
cp .env.example .env                                    # optional: Bluesky app password

python -m pulse.collect            # one cycle (first run downloads ~1.5 GB of models)
python -m pulse.status             # health check of local data/pulse.db
python -m pulse.status --remote    # health check of the live DB on GitHub
python -m pulse.pull               # download the live DB -> data/pulse.db
python -m pulse.sample             # 50 stratified items -> eval/to_label.csv
streamlit run label_app.py         # label them, one post at a time
python -m pulse.evaluate           # -> eval/results.md, eval/test_table.csv
streamlit run dashboard.py         # the dashboard
```

**Scheduler:** [`.github/workflows/bahn-puls-collect.yml`](../../../.github/workflows/bahn-puls-collect.yml)
(at the repo root, because GitHub only reads workflows there). Bluesky credentials are
repository secrets `BSKY_HANDLE` and `BSKY_APP_PASSWORD`. Teammate guide: [HANDOFF.md](HANDOFF.md).

## 8. Dashboard
`streamlit run dashboard.py` (read-only; English UI; Europe/Berlin times)
- **Topics against their baseline:** the morning answer. Per topic: negative share in the latest
  period, its baseline, the change, post count and a status with icon + words
  (▲ above / ● around / ▼ below / ◌ too few posts / ◌ no baseline yet).
- **Small multiples, one per topic:** negative share per day (or hour, last 48 h) with the
  baseline as a dashed line and `n=` next to every point. Points with fewer than 10 posts are
  grey hollow markers. In the hourly view the counts are in the hover only, because 48 labels
  per panel are unreadable.
- **Toggles:** daily/hourly, personal/news/both (personal by default), Model 1/Model 2.
- **Drill-down:** click a point, or pick day + topic (+ hour), to list the posts behind it with
  time, text, label, confidence and link.
- **Baseline definition:** pooled negative share over the previous 7 days, *excluding* the
  current period (a spike must not raise its own baseline), or all earlier data if shorter.
  It needs at least 10 earlier posts, otherwise it is blank, as for low-count points.
- **Hosted copy:** Streamlit Community Cloud, entrypoint
  [`deploy/bahn-puls/streamlit_app.py`](../../../deploy/bahn-puls/streamlit_app.py) (repo root).
  Community Cloud can't install requirements from a path with spaces, so this launcher sits in
  a space-free folder with a dashboard-only `requirements.txt` (no torch). It downloads the
  live DB on start and every 10 minutes.
- **No translation column.** The open local de→en model (Helsinki-NLP opus-mt-de-en,
  Apache-2.0) needs the `sentencepiece` package, which is outside our agreed dependencies.
  Posts are shown in the original German. Limitation.

## 9. Ethics
- **Data minimisation:** only post text, timestamps and derived fields are stored. No
  handles, DIDs, display names, avatars or follower data. Author info is used in
  memory during a run to detect bots, then discarded (`pulse/filters.py`).
- **The one exception is the post URL**, which contains the author's DID
  (`bsky.app/profile/did:plc:…/post/…`). We keep it so users can open the post in
  context and so deleted posts disappear at the source. Set `store_post_url: false` to
  turn this off. TODO (team): decide whether to strip URLs before submission.
- **Public repository:** the database is pushed to a public branch. Posts are public on
  Bluesky already, but republishing them in bulk is a different act. TODO (team): consider
  publishing only aggregates or an anonymised export for the final submission.
- **Deletions:** we do not currently re-check whether stored posts were deleted.
  Limitation; acceptable for a 1-week dataset, not for long-term use.
- **Not representative:** Bluesky users skew young, urban, politically engaged and
  online, and people post when things go wrong. Shares of negative posts are not
  satisfaction rates.
- **Model bias:** both models struggle with sarcasm ("Danke, Deutsche Bahn"), and Model 1
  is German-only. See the evaluation.

## 10. What this must NOT be used for
- **Judging or disciplining individual staff** (train crews, station staff). Posts that
  mention staff are an unverified one-sided account; the tool is about topics, not people.
- **Claiming a problem is solved because posting stopped.** Fewer posts can mean the
  news cycle moved on, the weather changed, or people gave up complaining.
- **Profiling or contacting individual passengers.**
- **Replacing official punctuality data or proper customer surveys.**
- **Ranking regions or lines on low counts.** Points with fewer than 10 posts are
  flagged as unreliable on the dashboard.
