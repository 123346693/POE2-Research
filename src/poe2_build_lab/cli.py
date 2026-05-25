from __future__ import annotations

import argparse
from pathlib import Path

from .data_loader import load_builds
from .models import ScoreResult, UserProfile
from .recommender import recommend


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = PROJECT_ROOT / "data" / "sample" / "builds.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="poe2-build-lab")
    subparsers = parser.add_subparsers(dest="command", required=True)

    recommend_parser = subparsers.add_parser("recommend", help="Rank POE2 builds for a requirement profile.")
    recommend_parser.add_argument("--data", default=str(DEFAULT_DATA), help="Path to build database JSON.")
    recommend_parser.add_argument("--class", dest="player_class", help="Preferred class.")
    recommend_parser.add_argument("--ascendancy", help="Preferred ascendancy.")
    recommend_parser.add_argument(
        "--playstyle",
        action="append",
        default=[],
        help="Playstyle tag. Can be repeated. Examples: mapping, bossing, starter, hardcore.",
    )
    recommend_parser.add_argument("--budget", default="medium", help="starter, low, medium, high, mirror.")
    recommend_parser.add_argument("--trade-mode", default="either", choices=["either", "trade", "ssf"])
    recommend_parser.add_argument("--ssf", action="store_true", help="Shortcut for --trade-mode ssf.")
    recommend_parser.add_argument("--hardcore", action="store_true", help="Prefer HC-safe builds.")
    recommend_parser.add_argument("--avoid-uniques", action="store_true", help="Penalize required uniques.")
    recommend_parser.add_argument("--controller-friendly", action="store_true", help="Prefer controller tags.")
    recommend_parser.add_argument("--min-survivability", type=float, help="Minimum survivability metric.")
    recommend_parser.add_argument("--top", type=int, default=3, help="Number of recommendations.")

    args = parser.parse_args(argv)

    if args.command == "recommend":
        playstyles = _parse_playstyles(args.playstyle)
        trade_mode = "ssf" if args.ssf else args.trade_mode
        profile = UserProfile(
            player_class=args.player_class,
            ascendancy=args.ascendancy,
            playstyles=playstyles,
            budget=args.budget.lower(),
            trade_mode=trade_mode,
            hardcore=args.hardcore,
            avoid_uniques=args.avoid_uniques,
            controller_friendly=args.controller_friendly,
            min_survivability=args.min_survivability,
        )
        results = recommend(load_builds(args.data), profile, top=args.top)
        _print_results(results, profile)
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


def _parse_playstyles(values: list[str]) -> tuple[str, ...]:
    parsed: list[str] = []
    for value in values:
        parsed.extend(part.strip().lower() for part in value.split(",") if part.strip())
    return tuple(parsed or ["mapping"])


def _print_results(results: list[ScoreResult], profile: UserProfile) -> None:
    print("POE2 Build Lab recommendations")
    print(
        "Profile: "
        f"class={profile.player_class or 'any'}, "
        f"ascendancy={profile.ascendancy or 'any'}, "
        f"playstyle={','.join(profile.playstyles)}, "
        f"budget={profile.budget}, "
        f"trade_mode={profile.trade_mode}, "
        f"hardcore={profile.hardcore}"
    )
    print()

    for index, result in enumerate(results, start=1):
        build = result.build
        print(f"{index}. {build.name} [{result.total:.2f}]")
        print(f"   {build.player_class} / {build.ascendancy} / {build.main_skill} / {build.damage_type}")
        print(f"   Version: {build.game_version} | Source: {build.source} | Budget: {build.budget}")
        print(f"   Defensive layers: {', '.join(build.defensive_layers) or 'unknown'}")
        if build.required_uniques:
            print(f"   Required uniques: {', '.join(build.required_uniques)}")
        print(f"   Strengths: {_join(result.strengths)}")
        print(f"   Concerns: {_join(result.concerns)}")
        print(f"   Pros: {_join(build.pros)}")
        print(f"   Cons: {_join(build.cons)}")
        print()


def _join(values: tuple[str, ...]) -> str:
    return "; ".join(values) if values else "none"


if __name__ == "__main__":
    raise SystemExit(main())
