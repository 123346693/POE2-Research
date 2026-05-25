from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


MetricMap = dict[str, float]


@dataclass(frozen=True)
class Build:
    id: str
    name: str
    game_version: str
    source: str
    player_class: str
    ascendancy: str
    main_skill: str
    damage_type: str
    tags: tuple[str, ...]
    budget: str
    trade_mode: str
    required_uniques: tuple[str, ...]
    defensive_layers: tuple[str, ...]
    metrics: MetricMap
    nerf_risk: str
    pros: tuple[str, ...] = field(default_factory=tuple)
    cons: tuple[str, ...] = field(default_factory=tuple)
    evidence: tuple[str, ...] = field(default_factory=tuple)
    notes: str = ""

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Build":
        return cls(
            id=str(raw["id"]),
            name=str(raw["name"]),
            game_version=str(raw.get("game_version", "unknown")),
            source=str(raw.get("source", "unknown")),
            player_class=str(raw.get("player_class", "")),
            ascendancy=str(raw.get("ascendancy", "")),
            main_skill=str(raw.get("main_skill", "")),
            damage_type=str(raw.get("damage_type", "")),
            tags=tuple(str(value).lower() for value in raw.get("tags", [])),
            budget=str(raw.get("budget", "medium")).lower(),
            trade_mode=str(raw.get("trade_mode", "either")).lower(),
            required_uniques=tuple(str(value) for value in raw.get("required_uniques", [])),
            defensive_layers=tuple(str(value) for value in raw.get("defensive_layers", [])),
            metrics={str(key): float(value) for key, value in raw.get("metrics", {}).items()},
            nerf_risk=str(raw.get("nerf_risk", "medium")).lower(),
            pros=tuple(str(value) for value in raw.get("pros", [])),
            cons=tuple(str(value) for value in raw.get("cons", [])),
            evidence=tuple(str(value) for value in raw.get("evidence", [])),
            notes=str(raw.get("notes", "")),
        )


@dataclass(frozen=True)
class UserProfile:
    player_class: str | None = None
    ascendancy: str | None = None
    playstyles: tuple[str, ...] = ("mapping",)
    budget: str = "medium"
    trade_mode: str = "either"
    hardcore: bool = False
    avoid_uniques: bool = False
    controller_friendly: bool = False
    min_survivability: float | None = None


@dataclass(frozen=True)
class ScoreResult:
    build: Build
    total: float
    strengths: tuple[str, ...]
    concerns: tuple[str, ...]
    component_scores: dict[str, float]
