from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote


TRADE2_ROOT = "https://www.pathofexile.com/trade2"


@dataclass(frozen=True)
class TradeSearchPlan:
    league: str
    query_name: str
    item_category: str
    min_price_divines: float | None = None
    max_price_divines: float | None = None
    required_stats: tuple[str, ...] = ()

    def browser_url(self) -> str:
        return f"{TRADE2_ROOT}/search/poe2/{quote(self.league)}"


def build_manual_trade_plan(
    league: str,
    query_name: str,
    item_category: str,
    max_price_divines: float | None,
    required_stats: tuple[str, ...] = (),
) -> TradeSearchPlan:
    return TradeSearchPlan(
        league=league,
        query_name=query_name,
        item_category=item_category,
        max_price_divines=max_price_divines,
        required_stats=required_stats,
    )
