# Weekend handoff: checking the Bahn-Puls collector

A robot on GitHub collects Bluesky posts about Deutsche Bahn **every 10 minutes**,
on its own. Your job is just to **look** about twice a day and tell me if
something is wrong. You don't need to install anything or edit any code.

## Check it (2 minutes, from any browser)

**Step 1: open the status page.** Bookmark this link:
<https://github.com/flxr8/ai4g-portfolio-felix-reichle/blob/bahn-puls-data/STATUS.md>

**Step 2: read the title.**
- `Bahn-Puls collector status: ✅ OK` means it's fine.
- `❌ PROBLEM: message your teammate` means send me a screenshot of the page.

**Step 3: check the last line, `(checked ...)`.** The page refreshes after every
run, so that time should be **less than about an hour ago** (Berlin time).
If it's older, the robot has stopped. Go to Step 4.

**Step 4 (only if the page looks old): open the run list.**
<https://github.com/flxr8/ai4g-portfolio-felix-reichle/actions/workflows/bahn-puls-collect.yml>
- Each line is one run. ✅ green tick = worked, ❌ red cross = failed,
  🟡 yellow dot = running right now.
- A few red crosses in a row, or **no new line for over an hour**: message me
  with a screenshot.
- A single red cross between green ticks is normal (e.g. a network hiccup). Ignore it.
- Click any run, then the **Summary** tab: the same status report appears there.

GitHub's timer is not exact. Runs are often 10–30 minutes apart instead of 10.
That's normal.

## What a healthy page looks like

```
Total items collected: 512
Items collected per day:
    Fri 09 Oct: 301
    Sat 10 Oct: 211
Items collected in the last hour: 14
Last successful run: Sat 10 Oct, 15:23 (Berlin time) (3 min ago)
Last errors: none
VERDICT: OK
```
- **Items collected in the last hour** is usually 5–30. Late at night it can be 0–3. That's fine.
- **Items per day** should go up each day, roughly 150–300 per day.

## Do NOT touch
- Don't edit, rename or delete anything in the repository, **especially** the
  `bahn-puls-data` branch and the file `.github/workflows/bahn-puls-collect.yml`.
- Don't click **"Disable workflow"** or **"Re-run"** in the Actions tab. One
  manual run is harmless, but you don't need to.
- Don't change **Settings → Secrets**. That's where the Bluesky login is kept.

## When to message me
Message me if any of these happen: the page says **PROBLEM**, the `(checked ...)`
time is **over 1 hour old**, or **several red crosses in a row**. Send a screenshot.
I'm back on **Monday**.
