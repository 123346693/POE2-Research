from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Build


def load_builds(path: str | Path) -> list[Build]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, list):
        rows: list[dict[str, Any]] = raw
    elif isinstance(raw, dict) and isinstance(raw.get("builds"), list):
        rows = raw["builds"]
    else:
        raise ValueError("Build data must be a list or an object with a 'builds' list.")

    builds = [Build.from_dict(row) for row in rows]
    if not builds:
        raise ValueError("Build data did not contain any build candidates.")
    return builds
