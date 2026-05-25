from __future__ import annotations

from pathlib import Path

from ..data_loader import load_builds
from ..models import Build


def load_local_build_database(path: str | Path) -> list[Build]:
    return load_builds(path)
