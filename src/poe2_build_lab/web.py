from __future__ import annotations

import argparse
import json
import mimetypes
import sys
from dataclasses import asdict, is_dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from .character import diagnose_character
from .data_loader import load_builds
from .market import PriceBook
from .models import CharacterSnapshot, UserProfile
from .recommender import recommend


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = PROJECT_ROOT / "web"
STATIC_ROOT = WEB_ROOT / "static"
DEFAULT_BUILDS = PROJECT_ROOT / "data" / "sample" / "builds.json"
DEFAULT_PRICES = PROJECT_ROOT / "data" / "sample" / "prices.json"
DEFAULT_CHARACTER = PROJECT_ROOT / "data" / "sample" / "character.json"
DEFAULT_ASCENDANCIES = PROJECT_ROOT / "data" / "knowledge" / "ascendancies.json"


class AlphaState:
    def __init__(self, builds_path: Path, prices_path: Path) -> None:
        self.builds_path = builds_path
        self.prices_path = prices_path
        self.reload()

    def reload(self) -> None:
        self.builds = load_builds(self.builds_path)
        self.prices = PriceBook.from_file(self.prices_path)


def create_handler(state: AlphaState):
    class AlphaHandler(BaseHTTPRequestHandler):
        server_version = "POE2BuildLabAlpha/0.1"

        def do_GET(self) -> None:
            path = unquote(self.path.split("?", 1)[0])
            if path == "/":
                self._send_file(WEB_ROOT / "index.html")
                return
            if path == "/api/state":
                self._send_json(load_alpha_state(state))
                return
            if path == "/api/sample-character":
                self._send_json(_read_json(DEFAULT_CHARACTER))
                return
            if path.startswith("/static/"):
                self._send_file(STATIC_ROOT / path.removeprefix("/static/"))
                return
            self._send_error(404, "Not found")

        def do_POST(self) -> None:
            try:
                payload = self._read_body()
                if self.path == "/api/recommend":
                    self._send_json(handle_recommend(state, payload))
                    return
                if self.path == "/api/diagnose":
                    self._send_json(handle_diagnose(state, payload))
                    return
                self._send_error(404, "Not found")
            except Exception as exc:  # noqa: BLE001 - keep Alpha API debuggable.
                self._send_error(400, str(exc))

        def log_message(self, format: str, *args: Any) -> None:
            return

        def _read_body(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8") if length else "{}"
            value = json.loads(body)
            if not isinstance(value, dict):
                raise ValueError("Request body must be a JSON object.")
            return value

        def _send_file(self, path: Path) -> None:
            resolved = path.resolve()
            if not str(resolved).startswith(str(WEB_ROOT.resolve())) or not resolved.exists() or not resolved.is_file():
                self._send_error(404, "Not found")
                return
            content_type = mimetypes.guess_type(str(resolved))[0] or "application/octet-stream"
            data = resolved.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _send_json(self, payload: Any, status: int = 200) -> None:
            data = json.dumps(to_jsonable(payload), ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _send_error(self, status: int, message: str) -> None:
            self._send_json({"error": message}, status=status)

    return AlphaHandler


def handle_recommend(state: AlphaState, payload: dict[str, Any]) -> dict[str, Any]:
    profile = UserProfile(
        player_class=_blank_to_none(payload.get("player_class")),
        ascendancy=_blank_to_none(payload.get("ascendancy")),
        playstyles=_parse_playstyles(payload.get("playstyles")),
        budget=str(payload.get("budget") or "medium").lower(),
        budget_divines=_optional_float(payload.get("budget_divines")),
        trade_mode=str(payload.get("trade_mode") or "either").lower(),
        hardcore=bool(payload.get("hardcore", False)),
        avoid_uniques=bool(payload.get("avoid_uniques", False)),
        controller_friendly=bool(payload.get("controller_friendly", False)),
        min_survivability=_optional_float(payload.get("min_survivability")),
    )
    top = int(payload.get("top") or 5)
    results = recommend(state.builds, profile, top=top)
    return {
        "profile": profile,
        "results": results,
        "warning": "Alpha uses seed data until live POE2DB/trade snapshots are connected.",
    }


def handle_diagnose(state: AlphaState, payload: dict[str, Any]) -> dict[str, Any]:
    character_raw = payload.get("character")
    if isinstance(character_raw, str):
        character_raw = json.loads(character_raw)
    if not isinstance(character_raw, dict):
        raise ValueError("Provide a character JSON object.")

    character = CharacterSnapshot.from_dict(character_raw)
    budget = _optional_float(payload.get("budget_divines"))
    if budget is None:
        raise ValueError("budget_divines is required.")
    return {
        "character": character,
        "recommendations": diagnose_character(character, state.prices, budget),
        "warning": "Alpha estimates are rule-based and price-snapshot based.",
    }


def load_alpha_state(state: AlphaState) -> dict[str, Any]:
    ascendancies = _read_json(DEFAULT_ASCENDANCIES)
    return {
        "build_count": len(state.builds),
        "builds_path": str(state.builds_path),
        "prices_path": str(state.prices_path),
        "ascendancies": ascendancies,
        "sample_character": _read_json(DEFAULT_CHARACTER),
    }


def to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return to_jsonable(asdict(value))
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    return value


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_playstyles(value: Any) -> tuple[str, ...]:
    if isinstance(value, list):
        parts = value
    elif isinstance(value, str):
        parts = value.split(",")
    else:
        parts = ["mapping"]
    parsed = tuple(str(part).strip().lower() for part in parts if str(part).strip())
    return parsed or ("mapping",)


def _optional_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def _blank_to_none(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def run(host: str = "127.0.0.1", port: int = 8765) -> None:
    state = AlphaState(DEFAULT_BUILDS, DEFAULT_PRICES)
    server = ThreadingHTTPServer((host, port), create_handler(state))
    try:
        print(f"POE2 Build Lab Alpha running at http://{host}:{port}", flush=True)
    except (OSError, RuntimeError):
        sys.stdout = None
    server.serve_forever()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="poe2-build-lab-alpha")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    run(args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
