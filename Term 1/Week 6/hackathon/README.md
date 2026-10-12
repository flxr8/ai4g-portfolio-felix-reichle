# Bahn-Puls: live passenger sentiment for Deutsche Bahn (Bluesky)

Hackathon, Term 1 Week 6 · SDG 9 (Industry, Innovation and Infrastructure) · pair project

## 1. The problem
Passengers voice delays, crowding, app failures and construction chaos on social media long
before these show up in complaint statistics. A regional customer-communication team decides
every morning which issue gets proactive communication, today mostly by gut feeling. Bahn-Puls
turns the public stream into one signal: **which topic's negative sentiment is rising above its
own recent baseline, and which posts are behind it?**

## 2. The stream and Bluesky's terms of use
- **Source:** Bluesky search (`app.bsky.feed.searchPosts`, `sort=latest`) with 29 German queries
  ([config.yaml](config.yaml)). Reddit was out of scope (API access needs approval).
- **Viability:** a 3-day test run (9–12 Oct) found ~250 relevant posts per day after filtering,
  enough for the 300-item requirement within 48 h.
- **Access:** search works anonymously via `api.bsky.app` (`public.api.bsky.app` returns 403).
  The collector logs in with an app password (repository secrets) when available.
- **Terms:** TODO (team): link and quote the current Bluesky developer guidelines. We store no
  author data, use public posts only, and make ~30 requests per 10 minutes.

## 3. The user and the decision
**User:** a regional DB customer-communication team, or a passenger association (Pro Bahn).
**Decision:** every morning, which issue gets proactive communication today.
**Shown:** per topic, the share of negative passenger posts against that topic's 7-day baseline,
the number of posts behind every point, and the posts themselves.

## 4. SDG 9 rationale
SDG 9.1 asks for "quality, reliable, sustainable and resilient infrastructure … with a focus on
affordable and equitable access for all". Rail is the backbone of low-carbon mobility, and its
perceived reliability decides whether people keep using it. Bahn-Puls gives operators a cheap,
continuous, passenger-centred feedback channel: what delays and disruptions mean to the people
affected, next to punctuality statistics.

## 5. Models and evaluation
| | Model 1 | Model 2 |
|---|---|---|
| | `oliverguhr/german-sentiment-bert` | `cardiffnlp/twitter-xlm-roberta-base-sentiment` |
| Training data | 1.8 M German reviews, tweets, Facebook, Wikipedia | 198 M tweets; sentiment fine-tuned in 8 languages incl. German |
| Licence | MIT | not stated on the Hub (code repo Apache-2.0) |

Both run locally on CPU via `transformers` at pinned revisions; no chat-model API. Details and
concerns: [docs/model_cards.md](docs/model_cards.md).

**Evaluation** on 50 hand-labelled posts, stratified by topic and news/personal
([eval/results.md](eval/results.md)):

| | agreement | Cohen's κ |
|---|---|---|
| Model 1 | 50% | 0.11 |
| Model 2 | 54% | 0.18 |
| SentiWS word list (baseline) | 54% | 0.25 |

Neither transformer beats a simple word list here. Their main error is reading neutral posts as
negative (Model 1: 12 of 23 neutral posts), which inflates the negative share. Model 2 is closer
(48% predicted negative vs 46% by hand), so it is the dashboard default. 18% of sampled posts
were not about rail at all. Read the dashboard as a trend indicator, not a measurement.

## 6. Architecture
```
GitHub Actions (.github/workflows/bahn-puls-collect.yml)
  one run = ~5.5 h loop:  every 10 min → python -m pulse.collect → publish pulse.db
  then dispatches its own successor (hourly cron only restarts a broken chain)

python -m pulse.collect  (one cycle)
  1. searchPosts per query, paging until the stored per-query watermark (newest indexedAt)
  2. filters, in memory: empty, <4 words, crossposted RTs, bots (self-label, name pattern,
     repeated templates, posting rate), rail context for ambiguous queries, backdated posts
  3. derive: id = sha256(URI), kind = news|personal (linked domain), topics (keyword regexes)
  4. INSERT OR IGNORE → idempotent;  5. classify unlabelled rows with both models
  6. log the run in `runs` (start, end, counts, errors)

dashboard.py  (Streamlit, read-only) ← pulse.db from the `bahn-puls-data` branch
```
**Why it looks like this:**
- *GitHub's cron is not the clock.* In the test run it fired only every 3–10 h, so each run
  loops internally and starts the next one itself.
- *Store first, classify second:* a model failure never loses posts.
- *Data on its own branch, force-pushed as one commit:* no merge conflicts with code and no
  history bloat. A guard refuses to publish if the item count shrinks.
- *Watermark on `indexedAt`:* `createdAt` is client-set (imported posts claim 2020).

## 7. How to run
```bash
cd "Term 1/Week 6/hackathon"
python -m venv .venv && .venv/Scripts/activate      # Linux/macOS: source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
cp .env.example .env                                # optional Bluesky app password

python -m pulse.collect             # one cycle (first run downloads ~1.5 GB of models)
python -m pulse.evaluate sample     # 50 stratified posts -> eval/to_label.csv
python -m pulse.evaluate            # labelled CSV -> eval/results.md, eval/test_table.csv
streamlit run dashboard.py          # fetches the live DB automatically
```
Collection runs on GitHub Actions; check it in the repo's **Actions** tab. It stops itself on
15 Oct, 23:30 Berlin, and commits the final `data/pulse.db` to `main`. The hosted dashboard
uses [deploy/bahn-puls/streamlit_app.py](../../../deploy/bahn-puls/streamlit_app.py), because
Streamlit Cloud can't install requirements from a path containing spaces.

## 8. Dashboard
- **Topics against their baseline:** latest negative share per topic vs its baseline, with
  status ▲ above / ● around / ▼ below / ◌ too few posts / ◌ no baseline yet.
- **One chart per topic:** negative share per day (or hour, last 48 h), baseline dashed, `n=`
  next to every daily point. Points with fewer than 10 posts are hollow grey.
- **Toggles:** daily/hourly, personal/news/both (personal by default), Model 1/Model 2.
- **Posts behind a point:** pick a day and topic for time, text, label, confidence and link.
- **Baseline:** pooled negative share over the previous 7 days, excluding the current period
  (a spike must not hide in its own baseline). It needs ≥ 10 earlier posts, otherwise it's blank.
- **Limitation:** no English translation. The open local model (opus-mt-de-en) needs the
  `sentencepiece` package, outside our agreed dependencies.

## 9. Ethics
- **Data minimisation:** only text, timestamps and derived fields. No handles, DIDs, names or
  profile data. Author info is used in memory to detect bots, then discarded.
- **Exception: the post URL** contains the author's DID. We keep it so readers can check
  context (`store_post_url: false` turns it off). TODO (team): decide before submission.
- **Public repo:** the dataset is published with the repo. Posts are public on Bluesky, but
  republishing them in bulk is a different act.
- **No deletion sync:** posts deleted on Bluesky stay in our snapshot (acceptable for a one-week
  dataset, not for long-term use).
- **Not representative:** Bluesky users skew young, urban and online, and people post when things
  go wrong.

## 10. What this must NOT be used for
- Judging or disciplining individual staff.
- Claiming a problem is solved because people stopped posting about it.
- Profiling or contacting individual passengers.
- Ranking lines or regions on a handful of posts.
- Replacing punctuality data or proper customer surveys.
