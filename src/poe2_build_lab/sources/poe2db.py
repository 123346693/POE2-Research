from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Poe2DbSnapshot:
    path: Path
    raw: dict[str, Any]

    @property
    def skills(self) -> list[dict[str, Any]]:
        value = self.raw.get("skills", [])
        return value if isinstance(value, list) else []

    @property
    def items(self) -> list[dict[str, Any]]:
        value = self.raw.get("items", [])
        return value if isinstance(value, list) else []

    @property
    def modifiers(self) -> list[dict[str, Any]]:
        value = self.raw.get("modifiers", [])
        return value if isinstance(value, list) else []


def load_poe2db_export(path: str | Path) -> Poe2DbSnapshot:
    """Load a normalized POE2DB export.

    This adapter intentionally starts with local exports. A live scraper should be
    added only after source terms, rate limits, and cache behavior are clear.
    """

    snapshot_path = Path(path)
    raw = json.loads(snapshot_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("POE2DB export must be a JSON object.")
    return Poe2DbSnapshot(path=snapshot_path, raw=raw)
