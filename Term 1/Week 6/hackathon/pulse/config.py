"""Paths and config loading.

All paths are resolved relative to the project folder (the parent of this
package), not the current working directory. That way `python -m pulse.x`
behaves the same whether it is started locally, from the repo root, or by the
GitHub Actions runner.
"""
from __future__ import annotations

import logging
from pathlib import Path

import yaml

PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_DIR / "config.yaml"
DATA_DIR = PROJECT_DIR / "data"
DB_PATH = DATA_DIR / "pulse.db"
EVAL_DIR = PROJECT_DIR / "eval"


def load_config(path: Path = CONFIG_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def setup_logging() -> None:
    # Timestamps in the log make it possible to line up a GitHub Actions log
    # with the `runs` table when debugging.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    # The HTTP clients log every request at INFO, which buries our own lines.
    for noisy in ("httpx", "httpx2", "httpcore", "huggingface_hub", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
