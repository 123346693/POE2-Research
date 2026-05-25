import unittest

from poe2_build_lab.web import AlphaState, DEFAULT_BUILDS, DEFAULT_PRICES, handle_diagnose, handle_recommend


class WebApiTest(unittest.TestCase):
    def test_recommend_endpoint_returns_results(self) -> None:
        state = AlphaState(DEFAULT_BUILDS, DEFAULT_PRICES)

        response = handle_recommend(
            state,
            {
                "ascendancy": "Invoker",
                "playstyles": "mapping",
                "budget_divines": 5,
            },
        )

        self.assertGreaterEqual(len(response["results"]), 1)
        self.assertEqual(response["results"][0].build.ascendancy, "Invoker")

    def test_diagnose_endpoint_returns_upgrades(self) -> None:
        state = AlphaState(DEFAULT_BUILDS, DEFAULT_PRICES)
        character = {
            "name": "test",
            "level": 80,
            "league": "Standard",
            "player_class": "Monk",
            "ascendancy": "Invoker",
            "main_skill": "Tempest Flurry",
            "life": 2000,
            "energy_shield": 500,
            "spirit": 100,
            "resistances": {"fire": 75, "cold": 60, "lightning": 75},
            "defensive_layers": ["evasion"],
            "items": [{"slot": "weapon", "name": "weak staff", "mods": ["low dps"]}],
        }

        response = handle_diagnose(state, {"character": character, "budget_divines": 20})

        self.assertGreaterEqual(len(response["recommendations"]), 1)


if __name__ == "__main__":
    unittest.main()
