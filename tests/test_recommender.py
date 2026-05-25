import unittest

from poe2_build_lab.models import Build, UserProfile
from poe2_build_lab.recommender import recommend


class RecommenderTest(unittest.TestCase):
    def test_budget_and_playstyle_affect_ranking(self) -> None:
        builds = [
            Build(
                id="cheap-mapper",
                name="Cheap Mapper",
                game_version="test",
                source="test",
                player_class="Mercenary",
                ascendancy="Gemling Legionnaire",
                main_skill="Grenade",
                damage_type="fire",
                tags=("mapping", "starter"),
                budget="low",
                trade_mode="either",
                required_uniques=(),
                defensive_layers=("armour",),
                metrics={
                    "damage": 65,
                    "clear_speed": 90,
                    "survivability": 65,
                    "cost_efficiency": 95,
                    "patch_stability": 75,
                    "ssf_viability": 80,
                    "ease_of_play": 80,
                    "data_confidence": 70,
                },
                nerf_risk="low",
            ),
            Build(
                id="expensive-bosser",
                name="Expensive Bosser",
                game_version="test",
                source="test",
                player_class="Monk",
                ascendancy="Invoker",
                main_skill="Lightning Strike",
                damage_type="lightning",
                tags=("bossing",),
                budget="high",
                trade_mode="trade",
                required_uniques=("Rare Unique",),
                defensive_layers=("evasion",),
                metrics={
                    "damage": 95,
                    "clear_speed": 70,
                    "survivability": 70,
                    "cost_efficiency": 45,
                    "patch_stability": 60,
                    "ssf_viability": 20,
                    "ease_of_play": 55,
                    "data_confidence": 70,
                },
                nerf_risk="medium",
            ),
        ]

        profile = UserProfile(playstyles=("mapping", "starter"), budget="low", trade_mode="ssf")
        result = recommend(builds, profile, top=1)

        self.assertEqual(result[0].build.id, "cheap-mapper")


if __name__ == "__main__":
    unittest.main()
