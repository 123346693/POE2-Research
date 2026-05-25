from __future__ import annotations

from collections.abc import Iterable

from .models import Build, ScoreResult, UserProfile
from .scoring import score_build


def recommend(builds: Iterable[Build], profile: UserProfile, top: int = 3) -> list[ScoreResult]:
    scored = [score_build(build, profile) for build in builds]
    scored.sort(key=lambda result: result.total, reverse=True)
    return scored[: max(1, top)]
