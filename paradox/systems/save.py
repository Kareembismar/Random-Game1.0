"""Persistence: %APPDATA%/paradox/save.json.

A corrupt, missing, or unwritable save file must never crash the game — every
path in here degrades to defaults instead of raising. The schema grows in
Phase 2C (loop bests, pace data); unknown keys are preserved, missing keys
are filled from DEFAULTS, so old files stay compatible.
"""

import json
import os
from datetime import date
from pathlib import Path

DEFAULTS = {
    "best_score": 0,
    "deepest_loop": 0,
    "total_runs": 0,
    "top_scores": [],  # [{"score": int, "loop": int, "date": "YYYY-MM-DD"}]
}
TOP_SCORES_KEPT = 5

_data: dict | None = None


def path() -> Path:
    appdata = os.getenv("APPDATA")
    base = Path(appdata) if appdata else Path.cwd()
    return base / "paradox" / "save.json"


def load() -> dict:
    """Read the save file (or regenerate defaults). Also primes get()."""
    global _data
    try:
        raw = json.loads(path().read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("save root is not an object")
        _data = {**DEFAULTS, **raw}
        _data["top_scores"] = [
            s for s in _data.get("top_scores", [])
            if isinstance(s, dict) and isinstance(s.get("score"), int)
        ]
    except (OSError, ValueError):
        _data = dict(DEFAULTS)
    return _data


def get() -> dict:
    return _data if _data is not None else load()


def write() -> None:
    try:
        p = path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(get(), indent=2), encoding="utf-8")
    except OSError:
        pass  # a read-only disk should never take the game down


def record_run(score: int, loop: int) -> bool:
    """Fold a finished (or abandoned) run into the records and persist.

    Returns True if this run set a new best score.
    """
    d = get()
    d["total_runs"] += 1
    new_best = score > d["best_score"]
    if new_best:
        d["best_score"] = score
    d["deepest_loop"] = max(d["deepest_loop"], loop)
    d["top_scores"].append({"score": score, "loop": loop, "date": date.today().isoformat()})
    d["top_scores"] = sorted(d["top_scores"], key=lambda s: s["score"], reverse=True)[:TOP_SCORES_KEPT]
    write()
    return new_best
