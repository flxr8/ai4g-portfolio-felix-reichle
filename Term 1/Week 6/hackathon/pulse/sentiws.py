"""Word-list baseline using SentiWS v2.0 (Remus, Quasthoff & Heyer, LREC 2010).

Why a baseline: it shows how much the transformers actually add over simply
counting positive and negative words. If a model can't beat this, it isn't
earning its 500 MB.

Licence: SentiWS is CC BY-NC-SA 3.0 (attribution, non-commercial, share-alike).
University coursework is non-commercial. To stay clear of redistribution
questions we do NOT commit the lexicon; it is downloaded on first use into
eval/sentiws/ (git-ignored) from the University of Leipzig.
"""
from __future__ import annotations

import io
import re
import urllib.request
import zipfile

from .config import EVAL_DIR

URL = "https://downloads.wortschatz-leipzig.de/etc/SentiWS/SentiWS_v2.0.zip"
CACHE = EVAL_DIR / "sentiws"

# Thresholds were fixed before looking at the evaluation set (not tuned on it).
# SentiWS weights are small (most |w| < 0.3), so a single clearly polar word
# should be enough to tip a short post.
POS_THRESHOLD = 0.1
NEG_THRESHOLD = -0.1
NEGATIONS = {"nicht", "kein", "keine", "keinen", "keinem", "keiner", "nie", "niemals", "ohne"}
TOKEN_RE = re.compile(r"[a-zäöüß]+", re.IGNORECASE)


def _ensure_downloaded() -> None:
    if (CACHE / "SentiWS_v2.0_Negative.txt").exists():
        return
    CACHE.mkdir(parents=True, exist_ok=True)
    data = urllib.request.urlopen(URL, timeout=60).read()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for name in z.namelist():
            if name.endswith(".txt"):  # flat archive; take files by base name only
                (CACHE / name.rsplit("/", 1)[-1]).write_bytes(z.read(name))


def load_lexicon() -> dict[str, float]:
    _ensure_downloaded()
    lex: dict[str, float] = {}
    for fname in ("SentiWS_v2.0_Positive.txt", "SentiWS_v2.0_Negative.txt"):
        for line in (CACHE / fname).read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            base = parts[0].split("|")[0]
            weight = float(parts[1])
            forms = [base] + (parts[2].split(",") if len(parts) > 2 and parts[2] else [])
            for form in forms:
                lex[form.lower()] = weight
    return lex


def score(text: str, lex: dict[str, float]) -> float:
    total, flip_left = 0.0, 0
    for tok in TOKEN_RE.findall(text.lower()):
        if tok in NEGATIONS:
            flip_left = 3  # "nicht gut", "nicht wirklich gut": flip the next 3 tokens
            continue
        w = lex.get(tok, 0.0)
        total += -w if flip_left else w
        flip_left = max(flip_left - 1, 0)
    return total


def label(text: str, lex: dict[str, float]) -> tuple[str, float]:
    s = score(text, lex)
    if s >= POS_THRESHOLD:
        return "positive", round(s, 4)
    if s <= NEG_THRESHOLD:
        return "negative", round(s, 4)
    return "neutral", round(s, 4)
