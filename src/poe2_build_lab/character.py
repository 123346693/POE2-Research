from __future__ import annotations

import json
from pathlib import Path

from .market import PriceBook
from .models import CharacterSnapshot, UpgradeRecommendation


IMPORTANT_SLOTS = ("weapon", "body_armour", "helmet", "gloves", "boots", "amulet", "ring", "belt")


def load_character(path: str | Path) -> CharacterSnapshot:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Character snapshot must be a JSON object.")
    return CharacterSnapshot.from_dict(raw)


def diagnose_character(
    character: CharacterSnapshot,
    prices: PriceBook,
    budget_divines: float,
) -> list[UpgradeRecommendation]:
    recommendations: list[UpgradeRecommendation] = []

    recommendations.extend(_defensive_recommendations(character, prices, budget_divines))
    recommendations.extend(_damage_recommendations(character, prices, budget_divines))
    recommendations.extend(_missing_slot_recommendations(character, prices, budget_divines))

    affordable = [item for item in recommendations if item.estimated_cost_divines <= budget_divines]
    affordable.sort(key=lambda item: (item.priority, -item.confidence, -item.estimated_damage_gain_pct), reverse=False)
    return affordable


def _defensive_recommendations(
    character: CharacterSnapshot,
    prices: PriceBook,
    budget_divines: float,
) -> list[UpgradeRecommendation]:
    recommendations: list[UpgradeRecommendation] = []
    elemental_resists = [
        character.resistances.get("fire", 0.0),
        character.resistances.get("cold", 0.0),
        character.resistances.get("lightning", 0.0),
    ]
    if elemental_resists and min(elemental_resists) < 75:
        quote = prices.estimate("resistance rare boots", character.league, min(2.0, budget_divines))
        recommendations.append(
            UpgradeRecommendation(
                priority=1,
                slot="boots/gloves/ring",
                title="Cap elemental resistances before buying damage.",
                reason="Uncapped elemental resistance is usually the fastest way to turn a good build into repeated deaths.",
                estimated_cost_divines=quote.median_divines,
                estimated_survival_gain_pct=18.0,
                confidence=max(0.55, quote.confidence),
            )
        )

    if (character.life or 0) < 2500 and (character.energy_shield or 0) < 1500:
        quote = prices.estimate("life energy shield rare body armour", character.league, min(5.0, budget_divines))
        recommendations.append(
            UpgradeRecommendation(
                priority=2,
                slot="body_armour",
                title="Upgrade the main defensive chest slot.",
                reason="The snapshot has a low primary effective health pool for endgame mapping or bossing.",
                estimated_cost_divines=quote.median_divines,
                estimated_survival_gain_pct=12.0,
                confidence=max(0.45, quote.confidence),
            )
        )

    return recommendations


def _damage_recommendations(
    character: CharacterSnapshot,
    prices: PriceBook,
    budget_divines: float,
) -> list[UpgradeRecommendation]:
    weapon = _find_slot(character, "weapon")
    if weapon is None:
        return []

    weak_weapon_terms = ("low dps", "campaign", "missing +levels", "missing attack speed", "missing spell damage")
    if any(term in mod.lower() for mod in weapon.mods for term in weak_weapon_terms):
        quote = prices.estimate(f"{character.main_skill} weapon", character.league, min(0.6 * budget_divines, budget_divines))
        return [
            UpgradeRecommendation(
                priority=1,
                slot="weapon",
                title="Buy or craft a proper main-skill weapon.",
                reason="The weapon carries the largest damage multiplier for most attack and spell archetypes.",
                estimated_cost_divines=quote.median_divines,
                estimated_damage_gain_pct=25.0,
                confidence=max(0.5, quote.confidence),
            )
        ]
    return []


def _missing_slot_recommendations(
    character: CharacterSnapshot,
    prices: PriceBook,
    budget_divines: float,
) -> list[UpgradeRecommendation]:
    present = {item.slot for item in character.items}
    missing = [slot for slot in IMPORTANT_SLOTS if slot not in present]
    if not missing:
        return []
    slot = missing[0]
    quote = prices.estimate(f"starter rare {slot}", character.league, min(1.0, budget_divines))
    return [
        UpgradeRecommendation(
            priority=3,
            slot=slot,
            title=f"Fill missing or untracked {slot}.",
            reason="A missing core slot makes the snapshot too incomplete for high-confidence optimization.",
            estimated_cost_divines=quote.median_divines,
            estimated_damage_gain_pct=4.0,
            estimated_survival_gain_pct=4.0,
            confidence=max(0.3, quote.confidence),
        )
    ]


def _find_slot(character: CharacterSnapshot, slot: str):
    for item in character.items:
        if item.slot == slot:
            return item
    return None
