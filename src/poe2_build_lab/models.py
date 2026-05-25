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
    estimated_cost_divines: float | None
    required_uniques: tuple[str, ...]
    key_items: tuple[str, ...]
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
            estimated_cost_divines=_optional_float(raw.get("estimated_cost_divines")),
            required_uniques=tuple(str(value) for value in raw.get("required_uniques", [])),
            key_items=tuple(str(value) for value in raw.get("key_items", [])),
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
    budget_divines: float | None = None
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


@dataclass(frozen=True)
class EquippedItem:
    slot: str
    name: str
    base_type: str = ""
    rarity: str = "rare"
    item_level: int | None = None
    price_paid_divines: float | None = None
    mods: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "EquippedItem":
        return cls(
            slot=str(raw["slot"]),
            name=str(raw.get("name", "")),
            base_type=str(raw.get("base_type", "")),
            rarity=str(raw.get("rarity", "rare")),
            item_level=_optional_int(raw.get("item_level")),
            price_paid_divines=_optional_float(raw.get("price_paid_divines")),
            mods=tuple(str(value) for value in raw.get("mods", [])),
        )


@dataclass(frozen=True)
class CharacterSnapshot:
    name: str
    level: int
    league: str
    player_class: str
    ascendancy: str
    main_skill: str
    life: int | None
    energy_shield: int | None
    spirit: int | None
    resistances: dict[str, float]
    defensive_layers: tuple[str, ...]
    items: tuple[EquippedItem, ...]
    notes: str = ""

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "CharacterSnapshot":
        return cls(
            name=str(raw.get("name", "unknown")),
            level=int(raw.get("level", 1)),
            league=str(raw.get("league", "unknown")),
            player_class=str(raw.get("player_class", "")),
            ascendancy=str(raw.get("ascendancy", "")),
            main_skill=str(raw.get("main_skill", "")),
            life=_optional_int(raw.get("life")),
            energy_shield=_optional_int(raw.get("energy_shield")),
            spirit=_optional_int(raw.get("spirit")),
            resistances={str(key): float(value) for key, value in raw.get("resistances", {}).items()},
            defensive_layers=tuple(str(value) for value in raw.get("defensive_layers", [])),
            items=tuple(EquippedItem.from_dict(value) for value in raw.get("items", [])),
            notes=str(raw.get("notes", "")),
        )


@dataclass(frozen=True)
class PriceQuote:
    query: str
    league: str
    median_divines: float
    low_divines: float | None = None
    high_divines: float | None = None
    sample_size: int = 0
    source: str = "unknown"
    captured_at: str = "unknown"
    confidence: float = 0.0

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "PriceQuote":
        return cls(
            query=str(raw["query"]),
            league=str(raw.get("league", "unknown")),
            median_divines=float(raw.get("median_divines", 0.0)),
            low_divines=_optional_float(raw.get("low_divines")),
            high_divines=_optional_float(raw.get("high_divines")),
            sample_size=int(raw.get("sample_size", 0)),
            source=str(raw.get("source", "unknown")),
            captured_at=str(raw.get("captured_at", "unknown")),
            confidence=float(raw.get("confidence", 0.0)),
        )


@dataclass(frozen=True)
class UpgradeRecommendation:
    priority: int
    slot: str
    title: str
    reason: str
    estimated_cost_divines: float
    estimated_damage_gain_pct: float = 0.0
    estimated_survival_gain_pct: float = 0.0
    confidence: float = 0.0


def _optional_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(value)
