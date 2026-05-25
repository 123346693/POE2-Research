from __future__ import annotations

import json
from pathlib import Path

from .models import PriceQuote


class PriceBook:
    def __init__(self, quotes: list[PriceQuote]) -> None:
        self._quotes = {(quote.league.lower(), quote.query.lower()): quote for quote in quotes}

    @classmethod
    def from_file(cls, path: str | Path) -> "PriceBook":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        rows = raw.get("quotes", raw) if isinstance(raw, dict) else raw
        if not isinstance(rows, list):
            raise ValueError("Price data must be a list or an object with a 'quotes' list.")
        return cls([PriceQuote.from_dict(row) for row in rows])

    def find(self, query: str, league: str) -> PriceQuote | None:
        return self._quotes.get((league.lower(), query.lower()))

    def estimate(self, query: str, league: str, fallback_divines: float) -> PriceQuote:
        return self.find(query, league) or PriceQuote(
            query=query,
            league=league,
            median_divines=fallback_divines,
            sample_size=0,
            source="fallback",
            captured_at="unknown",
            confidence=0.15,
        )
