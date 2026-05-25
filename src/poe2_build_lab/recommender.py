from __future__ import annotations

from collections.abc import Iterable

from .models import Build, ScoreResult, UserProfile
from .scoring import score_build


def recommend(builds: Iterable[Build], profile: UserProfile, top: int = 3) -> list[ScoreResult]:
    candidates = list(builds)
    filtered = _hard_filter(candidates, profile)
    scored = [score_build(build, profile) for build in filtered]
    scored.sort(key=lambda result: result.total, reverse=True)
    return scored[: max(1, top)]


def _hard_filter(builds: list[Build], profile: UserProfile) -> list[Build]:
    filtered = builds
    if profile.player_class:
        class_matches = [build for build in filtered if build.player_class.lower() == profile.player_class.lower()]
        if class_matches:
            filtered = class_matches
    if profile.ascendancy:
        ascendancy_matches = [build for build in filtered if build.ascendancy.lower() == profile.ascendancy.lower()]
        if ascendancy_matches:
            filtered = ascendancy_matches
    return filtered
