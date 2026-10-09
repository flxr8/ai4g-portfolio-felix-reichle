# Backup trigger: when GitHub's cron doesn't fire

GitHub's `schedule` trigger is best-effort and sometimes doesn't start for hours
on a newly added workflow. This backup has an external cron service call the
workflow's "Run workflow" endpoint every 10 minutes instead. It is safe to run
alongside the built-in schedule: the workflow's `concurrency` group queues runs
instead of overlapping them, and the collector is idempotent.

## 1. Create a GitHub token (2 min)
GitHub → your avatar → **Settings → Developer settings → Personal access tokens →
Fine-grained tokens → Generate new token**
- Name: `bahn-puls-trigger`, expiration: **30 days**
- Repository access: **Only select repositories** → `ai4g-portfolio-felix-reichle`
- Permissions → Repository permissions → **Actions: Read and write** (nothing else)
- Generate and copy the token (`github_pat_…`). It can only start workflows in this
  one repo, and you can revoke it any time.

## 2. Create the cron job (3 min)
Free account at <https://cron-job.org> → **Create cronjob**
- URL: `https://api.github.com/repos/flxr8/ai4g-portfolio-felix-reichle/actions/workflows/bahn-puls-collect.yml/dispatches`
- Schedule: every **10 minutes**
- **Advanced** tab:
  - Request method: **POST**
  - Headers:
    - `Accept: application/vnd.github+json`
    - `Authorization: Bearer github_pat_…` (your token)
    - `X-GitHub-Api-Version: 2022-11-28`
  - Request body: `{"ref":"main"}`
- Save, then click **Test run**: the response should be **204 No Content**, and a new
  run appears in the Actions tab within seconds (event: `workflow_dispatch`).

## 3. Afterwards
Revoke the token after the deadline (GitHub → Settings → Developer settings), and
delete the cron job.
