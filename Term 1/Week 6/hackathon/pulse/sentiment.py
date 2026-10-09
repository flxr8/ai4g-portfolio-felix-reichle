"""Local sentiment inference with two pre-trained Hugging Face models.

Both models are downloaded once from the Hub and then run on our own CPU via
`transformers` + `torch`. No text ever leaves the machine for inference, and
no chat-model API is involved.

Each model gets the preprocessing its authors trained it with; feeding raw
text to a model trained on cleaned text measurably lowers accuracy.
"""
from __future__ import annotations

import logging
import re

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

log = logging.getLogger(__name__)

# GitHub's runners have 4 vCPUs; more threads than cores slows CPU inference.
torch.set_num_threads(min(4, torch.get_num_threads()))

LABELS = ("negative", "neutral", "positive")

# --- Model 1 preprocessing: re-implementation of `germansentiment`'s
# SentimentModel.clean_text (MIT, github.com/oliverguhr/german-sentiment-lib).
# We copy the ~10 lines instead of adding the package as a dependency.
_GS_CHARS = re.compile(r"[^A-Za-züöäÖÜÄß ]", re.MULTILINE)
_GS_URLS = re.compile(r"https*\S+", re.MULTILINE)
_GS_MENTIONS = re.compile(r"@\S+", re.MULTILINE)
_GS_DIGITS = {"0": " null", "1": " eins", "2": " zwei", "3": " drei", "4": " vier",
              "5": " fünf", "6": " sechs", "7": " sieben", "8": " acht", "9": " neun"}


def preprocess_germansentiment(text: str) -> str:
    text = text.replace("\n", " ")
    text = _GS_URLS.sub("", text)
    text = _GS_MENTIONS.sub("", text)
    for d, w in _GS_DIGITS.items():
        text = text.replace(d, w)
    text = _GS_CHARS.sub("", text)
    return " ".join(text.split()).strip().lower()


# --- Model 2 preprocessing: from the cardiffnlp model card. Mentions and
# links were masked to "@user" / "http" in the training tweets.
def preprocess_cardiff(text: str) -> str:
    out = []
    for t in text.split(" "):
        t = "@user" if t.startswith("@") and len(t) > 1 else t
        t = "http" if t.startswith("http") else t
        out.append(t)
    return " ".join(out)


PREPROCESSORS = {"germansentiment": preprocess_germansentiment, "cardiff": preprocess_cardiff}


class SentimentModel:
    def __init__(self, spec: dict):
        self.name = spec["name"]
        self.max_length = spec["max_length"]
        self.preprocess = PREPROCESSORS[spec["preprocess"]]
        log.info("Loading %s", self.name)
        self.tokenizer = AutoTokenizer.from_pretrained(
            spec["tokenizer"], revision=spec["tokenizer_revision"]
        )
        self.model = AutoModelForSequenceClassification.from_pretrained(
            spec["name"], revision=spec["revision"],
            # Without this, transformers looks for a safetensors conversion of
            # a .bin-only model and may download it from an unmerged Hub pull
            # request, i.e. weights from outside our pinned revision.
            use_safetensors=spec["use_safetensors"],
        )
        self.model.eval()
        # Map whatever the model calls its classes ("Positive", "LABEL_0", ...)
        # onto our three canonical labels once, up front.
        self.id2label = {int(i): _normalise(l) for i, l in self.model.config.id2label.items()}

    def predict(self, texts: list[str], batch_size: int) -> list[tuple[str, float]]:
        results: list[tuple[str, float]] = []
        for start in range(0, len(texts), batch_size):
            batch = [self.preprocess(t) for t in texts[start:start + batch_size]]
            enc = self.tokenizer(
                batch, padding=True, truncation=True,
                max_length=self.max_length, return_tensors="pt",
            )
            with torch.inference_mode():
                probs = torch.softmax(self.model(**enc).logits, dim=-1)
            score, idx = probs.max(dim=-1)
            results += [(self.id2label[i], round(s, 4)) for i, s in zip(idx.tolist(), score.tolist())]
        return results


def _normalise(label: str) -> str:
    l = label.strip().lower()
    for canon in LABELS:
        if l.startswith(canon[:3]):  # "neg", "neu", "pos"
            return canon
    raise ValueError(f"Unexpected model label {label!r}")
