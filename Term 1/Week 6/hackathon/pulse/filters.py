"""Turn raw Bluesky posts into clean, privacy-safe items.

Everything about the author (handle, display name, labels) is looked at here,
in memory, to decide whether the account is automated. None of it is
returned, so it can never reach the database.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from urllib.parse import urlparse

URL_RE = re.compile(r"https?://\S+|\b[\w-]+(\.[\w-]+)+/\S*", re.IGNORECASE)
MENTION_RE = re.compile(r"@[\w.\-]+")
HASHTAG_RE = re.compile(r"#\w+")
WORD_RE = re.compile(r"[^\W\d_]{2,}")  # a "word" = 2+ letters, so emoji/numbers/links don't count


class Filters:
    def __init__(self, cfg: dict):
        f = cfg["filters"]
        self.min_words = f["min_words"]
        self.bot_name_re = re.compile("|".join(f["bot_name_patterns"]), re.IGNORECASE)
        self.max_per_author_hour = f["max_posts_per_author_per_hour"]
        self.template_threshold = f["template_repeat_threshold"]
        self.rail_context_re = re.compile("|".join(cfg["rail_context"]), re.IGNORECASE)
        self.news_domains = [d.lower() for d in cfg["news_domains"]]
        self.store_url = cfg.get("store_post_url", True)
        # Each topic keyword must start at a word boundary, otherwise "app"
        # would match inside "Rappel" and "evg" inside "Bevgel..." style noise.
        self.topics = {
            key: re.compile("|".join(r"\b" + k for k in t["keywords"]), re.IGNORECASE)
            for key, t in cfg["topics"].items()
            if t["keywords"]
        }

    # ----------------------------------------------------------- bot logic
    def find_bot_authors(self, posts: list[dict], prior_sigs: Counter | None = None) -> set[str]:
        """Return the author DIDs in this batch that look automated.

        `prior_sigs` are template signatures of recently stored texts (text
        only, no author info), so repetition across runs counts too.
        The returned set lives only for the duration of one run.
        """
        bots: set[str] = set()
        by_author: dict[str, list[dict]] = defaultdict(list)
        templates: Counter = Counter(prior_sigs or {})
        template_authors: dict[str, set[str]] = defaultdict(set)

        for p in posts:
            a = p.get("author", {})
            did = a.get("did", "")
            by_author[did].append(p)
            # Rule 1: the account labels itself as a bot.
            labels = [lab.get("val", "") for lab in a.get("labels", []) or []]
            if any("bot" in v.lower() for v in labels):
                bots.add(did)
            # Rule 2: name looks like a feed/bot ("...rssfeed", "Störungsmelder").
            name = f'{a.get("handle", "")} {a.get("displayName", "") or ""}'
            if self.bot_name_re.search(name):
                bots.add(did)
            # Rule 3 input: template signature (numbers/links/hashtags removed).
            sig = self.template_sig(p["record"].get("text", ""))
            if sig:
                templates[sig] += 1
                template_authors[sig].add(did)

        # Rule 3: the same template text appears several times -> status bot.
        for sig, n in templates.items():
            if n >= self.template_threshold:
                bots.update(template_authors[sig])

        # Rule 4: posting rate far above a human's (per hour of covered time).
        for did, ps in by_author.items():
            if len(ps) <= self.max_per_author_hour:
                continue
            times = [_parse_ts(p["indexedAt"]) for p in ps]
            hours = max((max(times) - min(times)).total_seconds() / 3600, 1.0)
            if len(ps) / hours > self.max_per_author_hour:
                bots.add(did)
        return bots

    @staticmethod  # also used by collect.py on stored texts
    def template_sig(text: str) -> str:
        t = URL_RE.sub("", text.lower())
        t = HASHTAG_RE.sub("", t)
        t = re.sub(r"[\d:.,+\-]+", "", t)
        t = " ".join(t.split())
        return t if len(t) >= 15 else ""

    # ---------------------------------------------------------- item logic
    def drop_reason(self, post: dict, needs_context: bool) -> str | None:
        text = (post["record"].get("text") or "").strip()
        if not text:
            return "empty"
        # searchPosts only returns original post records (reposts are separate
        # records it never returns), but cross-posted retweets still show up.
        if text.startswith("RT @"):
            return "repost"
        cleaned = URL_RE.sub(" ", MENTION_RE.sub(" ", text))
        if len(WORD_RE.findall(cleaned)) < self.min_words:
            return "too_short"
        if needs_context and not self.rail_context_re.search(text):
            return "no_rail_context"
        return None

    def kind(self, post: dict) -> str:
        for domain in _linked_domains(post):
            if any(domain == d or domain.endswith("." + d) for d in self.news_domains):
                return "news"
        return "personal"

    def topics_for(self, text: str) -> list[str]:
        found = [key for key, rx in self.topics.items() if rx.search(text)]
        return found or ["other"]

    def to_item(self, post: dict, query: str, fetched_at: str) -> dict:
        rec = post["record"]
        text = rec["text"].strip()
        uri = post["uri"]
        return {
            "id": hashlib.sha256(uri.encode()).hexdigest(),
            "url": _web_url(uri) if self.store_url else None,
            "created_at": _to_utc_iso(rec.get("createdAt") or post["indexedAt"]),
            "fetched_at": fetched_at,
            "text": text,
            "lang": ",".join(rec.get("langs") or []) or None,
            "query": query,
            "kind": self.kind(post),
            "topics": json.dumps(self.topics_for(text)),
        }


# ------------------------------------------------------------------ helpers
def _linked_domains(post: dict) -> set[str]:
    """Domains from link facets, external embeds and quoted-with-media embeds."""
    urls: list[str] = []
    rec = post.get("record", {})
    for facet in rec.get("facets") or []:
        for feat in facet.get("features") or []:
            if feat.get("uri"):
                urls.append(feat["uri"])
    embed = rec.get("embed") or {}
    for e in (embed, embed.get("media") or {}):
        ext = e.get("external") or {}
        if ext.get("uri"):
            urls.append(ext["uri"])
    domains = set()
    for u in urls:
        host = (urlparse(u).hostname or "").lower()
        domains.add(host[4:] if host.startswith("www.") else host)
    return domains


def _web_url(uri: str) -> str:
    # at://<did>/app.bsky.feed.post/<rkey> -> https://bsky.app/profile/<did>/post/<rkey>
    # We use the DID form, not the handle, so we never even write the handle.
    did, _, rkey = uri.removeprefix("at://").split("/")
    return f"https://bsky.app/profile/{did}/post/{rkey}"


def _parse_ts(s: str) -> datetime:
    dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _to_utc_iso(s: str) -> str:
    return _parse_ts(s).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
