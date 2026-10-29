"""Shared logic for the Invasive or Native? app and the evaluation script.

- `classify()` sends one photo to the Roboflow hosted model.
- `make_verdict()` turns the model output into what the user sees,
  using two safety rules (see THRESHOLDS below).
"""

from __future__ import annotations

import base64
import io
from dataclasses import dataclass

import requests
from PIL import Image, ImageOps

# --------------------------------------------------------------------------
# Safety rules. Change these numbers after testing on the held-out test set.
# --------------------------------------------------------------------------
UNSURE_BELOW = 0.70          # top confidence below this -> "Unsure, do not touch"
GIANT_HOGWEED_ALERT = 0.20   # giant hogweed score above this -> always warn

INVASIVE = {"giant_hogweed", "japanese_knotweed", "himalayan_balsam"}

SPECIES = {
    "giant_hogweed": {
        "name": "Giant hogweed",
        "latin": "Heracleum mantegazzianum",
        "dutch": "reuzenberenklauw",
        "tip": "Usually 2–5 m tall, with a thick stem covered in purple blotches "
               "and stiff hairs, and white flower heads that can be 50 cm across.",
        "action": "Do not touch it. The sap causes severe burns when the skin is "
                  "exposed to sunlight. Keep children and pets away.",
    },
    "japanese_knotweed": {
        "name": "Japanese knotweed",
        "latin": "Reynoutria japonica (incl. Bohemian knotweed)",
        "dutch": "Japanse duizendknoop",
        "tip": "Bamboo-like hollow stems with red speckles, broad leaves with a "
               "flat base, and zig-zag growth.",
        "action": "Do not cut, pull or mow it. Tiny pieces of root or stem grow "
                  "into new plants.",
    },
    "himalayan_balsam": {
        "name": "Himalayan balsam",
        "latin": "Impatiens glandulifera",
        "dutch": "reuzenbalsemien",
        "tip": "Pink to purple helmet-shaped flowers, reddish stems and leaves "
               "with finely toothed edges, often along water.",
        "action": "Do not touch ripe seed pods. They burst open and throw seeds "
                  "several metres.",
    },
    "common_hogweed": {
        "name": "Common hogweed",
        "latin": "Heracleum sphondylium",
        "dutch": "gewone berenklauw",
        "tip": "Usually under 2 m, with rough hairy leaves and smaller flower "
               "heads than giant hogweed.",
        "action": "Native and harmless to nature, but its sap can still irritate "
                  "skin in sunlight. Wear gloves if you handle it.",
    },
    "other_umbellifer": {
        "name": "Cow parsley or wild angelica",
        "latin": "Anthriscus sylvestris / Angelica sylvestris",
        "dutch": "fluitenkruid / gewone engelwortel",
        "tip": "Native plants with white flower umbels, much smaller than giant "
               "hogweed.",
        "action": "Native. No action needed. Some similar plants (such as "
                  "hemlock) are poisonous, so do not eat or handle plants you "
                  "cannot identify.",
    },
    "hedge_bindweed": {
        "name": "Hedge bindweed",
        "latin": "Calystegia sepium",
        "dutch": "haagwinde",
        "tip": "A climbing plant with heart- or arrow-shaped leaves and large "
               "white trumpet flowers. It twines around other plants.",
        "action": "Native. No action needed.",
    },
    "purple_loosestrife": {
        "name": "Purple loosestrife",
        "latin": "Lythrum salicaria",
        "dutch": "grote kattenstaart",
        "tip": "Tall spikes of purple-pink flowers, narrow leaves, often along "
               "ditches and water.",
        "action": "Native. No action needed.",
    },
}

REPORT_URL = "https://waarneming.nl"


@dataclass
class Verdict:
    kind: str            # "invasive" | "native" | "unsure"
    top_class: str | None
    top_confidence: float
    hogweed_alert: bool  # giant hogweed is a real possibility
    scores: list[tuple[str, float]]  # all classes, highest first


# --------------------------------------------------------------------------
# Image handling
# --------------------------------------------------------------------------
def prepare_image(data: bytes, max_side: int = 1024) -> Image.Image:
    """Open an uploaded photo, fix phone rotation and shrink it."""
    img = Image.open(io.BytesIO(data))
    img = ImageOps.exif_transpose(img).convert("RGB")
    img.thumbnail((max_side, max_side))
    return img


def to_base64_jpeg(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode("ascii")


# --------------------------------------------------------------------------
# Roboflow API
# --------------------------------------------------------------------------
API_URLS = ("https://serverless.roboflow.com", "https://classify.roboflow.com")


def parse_scores(resp: dict) -> list[tuple[str, float]]:
    """Return [(class, confidence), ...] sorted high to low.

    Handles both Roboflow formats: a list of {"class", "confidence"}
    (single-label) and a dict {class: {"confidence": x}} (multi-label).
    """
    preds = resp.get("predictions", resp)
    scores: list[tuple[str, float]] = []
    if isinstance(preds, list):
        for p in preds:
            if isinstance(p, dict) and "class" in p:
                scores.append((p["class"], float(p.get("confidence", 0))))
    elif isinstance(preds, dict):
        for cls, v in preds.items():
            conf = v.get("confidence", 0) if isinstance(v, dict) else v
            if isinstance(conf, (int, float)):
                scores.append((cls, float(conf)))
    # Ignore anything that is not one of our classes (e.g. a placeholder).
    scores = [(c, s) for c, s in scores if c in SPECIES]
    scores.sort(key=lambda cs: cs[1], reverse=True)
    return scores


def classify(img: Image.Image, model_id: str, api_key: str,
             timeout: float = 30) -> list[tuple[str, float]]:
    """Send one image to the hosted model. model_id looks like 'project/3'."""
    body = to_base64_jpeg(img)
    last_error: Exception | None = None
    for base in API_URLS:
        try:
            r = requests.post(
                f"{base}/{model_id}",
                params={"api_key": api_key},
                data=body,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=timeout,
            )
            if r.status_code == 404:
                last_error = RuntimeError(f"Model not found at {base}")
                continue
            r.raise_for_status()
            # An empty list is a valid answer: the model is not confident
            # about any class. make_verdict() then returns "unsure".
            return parse_scores(r.json())
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code in (401, 403):
                raise RuntimeError("The API key was refused. Check ROBOFLOW_API_KEY.") from e
            last_error = e
        except requests.RequestException as e:
            last_error = e
    raise RuntimeError(f"Could not reach the model: {last_error}")


# --------------------------------------------------------------------------
# Verdict
# --------------------------------------------------------------------------
def make_verdict(scores: list[tuple[str, float]]) -> Verdict:
    top_class, top_conf = scores[0] if scores else (None, 0.0)
    gh = dict(scores).get("giant_hogweed", 0.0)
    alert = gh >= GIANT_HOGWEED_ALERT

    if top_class is None or top_conf < UNSURE_BELOW:
        kind = "unsure"
    elif top_class in INVASIVE:
        kind = "invasive"
    elif alert:
        # Top answer is a native plant, but giant hogweed is still likely
        # enough that calling it "native" would be unsafe.
        kind = "unsure"
    else:
        kind = "native"
    return Verdict(kind, top_class, top_conf, alert, scores)
