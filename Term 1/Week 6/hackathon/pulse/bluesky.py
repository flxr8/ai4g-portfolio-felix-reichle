"""Bluesky search client.

Auth check done on 2026-10-09:
  * public.api.bsky.app/xrpc/app.bsky.feed.searchPosts -> 403 (blocked at the CDN)
  * api.bsky.app/xrpc/app.bsky.feed.searchPosts        -> 200 without login
So search currently works anonymously, but only via one host, and that has
changed before. Datacenter IPs (like GitHub's runners) are the most likely to
be blocked. We therefore log in with an app password when one is configured
and fall back to anonymous access otherwise. Either way the run never stops
just because one mode fails.
"""
from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timedelta, timezone

from atproto import Client

from .filters import _parse_ts

log = logging.getLogger(__name__)

ANON_BASE_URL = "https://api.bsky.app/xrpc"


def make_client() -> tuple[Client, str]:
    """Return (client, mode) where mode is 'auth' or 'anonymous'."""
    handle = os.getenv("BSKY_HANDLE", "").strip()
    password = os.getenv("BSKY_APP_PASSWORD", "").strip()
    if handle and password:
        try:
            client = Client()
            # fetch_bsky_profile=False: we don't need our own profile, and it
            # saves a request.
            client.login(handle, password, fetch_bsky_profile=False)
            return client, "auth"
        except Exception as e:  # noqa: BLE001 - any login failure -> fall back
            log.warning("Login failed (%s); falling back to anonymous search", type(e).__name__)
    return Client(base_url=ANON_BASE_URL), "anonymous"


def search_new_posts(
    client: Client,
    query: str,
    newest_seen: str | None,
    cfg_fetch: dict,
) -> tuple[list[dict], str | None]:
    """Page through `sort=latest` results until we reach what we already have.

    Returns (posts, newest_indexed_at_seen_in_this_call).

    Stop conditions, in order:
      1. a post at or before `newest_seen` (the per-query watermark): every
         later page is older still, so it is all already stored;
      2. on the first run of a query (no watermark), posts older than
         `backfill_hours`;
      3. no cursor (end of results) or `max_pages_per_query` reached.
    """
    cutoff = _parse_ts(newest_seen) if newest_seen else (
        datetime.now(timezone.utc) - timedelta(hours=cfg_fetch["backfill_hours"])
    )
    posts: list[dict] = []
    newest: str | None = None
    cursor = None
    for _page in range(cfg_fetch["max_pages_per_query"]):
        params = {"q": query, "sort": "latest", "limit": cfg_fetch["page_size"]}
        if cursor:
            params["cursor"] = cursor
        resp = client.app.bsky.feed.search_posts(params=params)
        data = resp.model_dump(mode="json", by_alias=True, exclude_none=True)
        page = data.get("posts", [])
        reached_old = False
        for p in page:
            ts = p["indexedAt"]
            if newest is None or _parse_ts(ts) > _parse_ts(newest):
                newest = ts
            if _parse_ts(ts) <= cutoff:
                reached_old = True
                continue  # don't `break`: ordering is not guaranteed to be strict
            posts.append(p)
        cursor = data.get("cursor")
        if reached_old or not cursor or not page:
            break
        time.sleep(cfg_fetch["request_pause_seconds"])
    return posts, newest
