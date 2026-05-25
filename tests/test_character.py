import unittest

from poe2_build_lab.character import diagnose_character
from poe2_build_lab.market import PriceBook
from poe2_build_lab.models import CharacterSnapshot, EquippedItem, PriceQuote


class CharacterDiagnosisTest(unittest.TestCase):
    def test_diagnosis_prioritizes_weapon_and_resists(self) -> None:
        character = CharacterSnapshot(
            name="test",
            level=80,
            league="Standard",
            player_class="Monk",
            ascendancy="Invoker",
            main_skill="Tempest Flurry",
            life=2000,
            energy_shield=500,
            spirit=100,
            resistances={"fire": 75, "cold": 60, "lightning": 75},
            defensive_layers=("evasion",),
            items=(
                EquippedItem(
                    slot="weapon",
                    name="weak staff",
                    mods=("low dps", "missing attack speed"),
                ),
            ),
        )
        prices = PriceBook(
            [
                PriceQuote(query="resistance rare boots", league="Standard", median_divines=1.0, confidence=0.5),
                PriceQuote(query="Tempest Flurry weapon", league="Standard", median_divines=5.0, confidence=0.5),
            ]
        )

        recommendations = diagnose_character(character, prices, budget_divines=10)

        titles = [item.title for item in recommendations]
        self.assertIn("Cap elemental resistances before buying damage.", titles)
        self.assertIn("Buy or craft a proper main-skill weapon.", titles)


if __name__ == "__main__":
    unittest.main()
