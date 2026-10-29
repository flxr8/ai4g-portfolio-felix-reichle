"""Test the model on the held-out test photos (the ones NOT uploaded to Roboflow).

Usage:
    python evaluate.py path/to/dataset/test

The test folder must contain one sub-folder per class, e.g.
test/giant_hogweed/*.jpg. Needs ROBOFLOW_API_KEY and ROBOFLOW_MODEL_ID as
environment variables or in .streamlit/secrets.toml.

Writes results.csv and prints:
  - accuracy per species and a confusion matrix
  - results at app level (Invasive / Native / Unsure), using the same
    safety rules as the app
"""

import csv
import os
import sys
import time
import tomllib
from collections import Counter
from pathlib import Path

import plantid


def setting(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    secrets = Path(__file__).parent / ".streamlit" / "secrets.toml"
    if secrets.exists():
        value = tomllib.loads(secrets.read_text()).get(name)
        if value:
            return value
    sys.exit(f"Missing {name}. Set it as an environment variable or in {secrets}.")


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    test_dir = Path(sys.argv[1])
    api_key, model_id = setting("ROBOFLOW_API_KEY"), setting("ROBOFLOW_MODEL_ID")

    photos = sorted(p for p in test_dir.glob("*/*")
                    if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})
    if not photos:
        sys.exit(f"No photos found in {test_dir}/<class>/")
    print(f"Testing {len(photos)} photos with model {model_id} …\n")

    rows = []
    for i, path in enumerate(photos, 1):
        truth = path.parent.name
        scores = plantid.classify(plantid.prepare_image(path.read_bytes()),
                                  model_id, api_key)
        v = plantid.make_verdict(scores)
        predicted = v.top_class or "none"   # "none" = model gave no answer
        rows.append({
            "file": f"{truth}/{path.name}",
            "true_class": truth,
            "predicted_class": predicted,
            "confidence": round(v.top_confidence, 4),
            "giant_hogweed_score": round(dict(scores).get("giant_hogweed", 0), 4),
            "true_status": "invasive" if truth in plantid.INVASIVE else "native",
            "app_verdict": v.kind,
            "hogweed_alert": v.hogweed_alert,
        })
        print(f"[{i:>3}/{len(photos)}] {truth:<18} -> {predicted:<18} "
              f"{v.top_confidence:5.0%}  {v.kind}")
        time.sleep(0.1)

    out = Path("results.csv")
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    # ---- species level -------------------------------------------------
    classes = sorted({r["true_class"] for r in rows} | {r["predicted_class"] for r in rows})
    correct = sum(r["true_class"] == r["predicted_class"] for r in rows)
    print(f"\nSpecies accuracy: {correct}/{len(rows)} = {correct/len(rows):.1%}\n")
    print("Per species:")
    for c in sorted({r["true_class"] for r in rows}):
        rs = [r for r in rows if r["true_class"] == c]
        ok = sum(r["predicted_class"] == c for r in rs)
        print(f"  {c:<18} {ok:>3}/{len(rs):<3} {ok/len(rs):6.0%}")

    cm = Counter((r["true_class"], r["predicted_class"]) for r in rows)
    short = {c: c[:6] for c in classes}
    print("\nConfusion matrix (rows = true, columns = predicted):")
    print(" " * 20 + " ".join(f"{short[c]:>6}" for c in classes))
    for t in sorted({r["true_class"] for r in rows}):
        print(f"  {t:<18}" + " ".join(f"{cm[(t, p)]:>6}" for p in classes))

    # ---- app level ------------------------------------------------------
    inv = [r for r in rows if r["true_status"] == "invasive"]
    nat = [r for r in rows if r["true_status"] == "native"]
    def count(rs, kind):
        return sum(r["app_verdict"] == kind for r in rs)
    print("\nApp verdicts (with safety rules):")
    print(f"  Invasive plants ({len(inv)}): invasive {count(inv,'invasive')}, "
          f"unsure {count(inv,'unsure')}, NATIVE {count(inv,'native')}  <- dangerous")
    print(f"  Native plants   ({len(nat)}): native {count(nat,'native')}, "
          f"unsure {count(nat,'unsure')}, invasive {count(nat,'invasive')}  <- false alarm")
    gh = [r for r in rows if r["true_class"] == "giant_hogweed"]
    if gh:
        warned = sum(r["app_verdict"] != "native" for r in gh)
        print(f"  Giant hogweed warned about: {warned}/{len(gh)}")
    print(f"\nSaved every prediction to {out.resolve()}")


if __name__ == "__main__":
    main()
