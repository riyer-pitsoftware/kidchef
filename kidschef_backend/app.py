"""HTTP server wiring for the KidsChef backend."""

from __future__ import annotations

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .contracts import SuggestRequest
from .repository import FavoritesStore, RecipeRepository, default_favorites_path
from .services import RecipeService


def create_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    *,
    base_dir: Path | None = None,
    service: RecipeService | None = None,
) -> ThreadingHTTPServer:
    base_dir = base_dir or Path.cwd()
    web_dir = base_dir / "web"
    if service is None:
        repository = RecipeRepository()
        favorites = FavoritesStore(default_favorites_path(base_dir))
        service = RecipeService(repository, favorites)
    handler_class = create_handler(service, web_dir=web_dir)
    return ThreadingHTTPServer((host, port), handler_class)


def create_handler(service: RecipeService, *, web_dir: Path) -> type[BaseHTTPRequestHandler]:
    class KidsChefHandler(BaseHTTPRequestHandler):
        server_version = "KidsChefHTTP/0.1"

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path in {"/", "/index.html"}:
                self._send_file(web_dir / "index.html")
                return

            if parsed.path in {"/app.js", "/styles.css"}:
                self._send_file(web_dir / parsed.path.lstrip("/"))
                return

            if parsed.path.startswith("/assets/"):
                relative = parsed.path[len("/assets/"):]
                if not relative:
                    self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
                    return
                assets_root = (web_dir / "assets").resolve()
                candidate = (assets_root / relative).resolve()
                try:
                    candidate.relative_to(assets_root)
                except ValueError:
                    self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
                    return
                self._send_file(candidate)
                return

            if parsed.path == "/api/health":
                self._send_json(HTTPStatus.OK, service.health_payload())
                return

            if parsed.path == "/api/bootstrap":
                self._send_json(HTTPStatus.OK, service.bootstrap_payload())
                return

            if parsed.path.startswith("/api/recipes/"):
                recipe_id = parsed.path.removeprefix("/api/recipes/").strip("/")
                if not recipe_id:
                    self._send_json(HTTPStatus.NOT_FOUND, {"error": "recipe_not_found"})
                    return
                payload = service.get_recipe(recipe_id)
                if payload is None:
                    self._send_json(HTTPStatus.NOT_FOUND, {"error": "recipe_not_found"})
                    return
                self._send_json(HTTPStatus.OK, payload)
                return

            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path in {"/api/recipes/suggest", "/api/recommendations"}:
                payload = SuggestRequest.from_payload(self._read_json())
                self._send_json(HTTPStatus.OK, service.suggest(payload))
                return

            if parsed.path == "/api/favorites/toggle":
                body = self._read_json()
                recipe_id = body.get("recipe_id") or body.get("recipeId")
                if not isinstance(recipe_id, str) or not recipe_id.strip():
                    self._send_json(HTTPStatus.BAD_REQUEST, {"error": "recipe_id_required"})
                    return
                payload = service.toggle_favorite(recipe_id.strip())
                if payload is None:
                    self._send_json(HTTPStatus.NOT_FOUND, {"error": "recipe_not_found"})
                    return
                self._send_json(HTTPStatus.OK, payload)
                return

            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

        def log_message(self, format: str, *args: object) -> None:
            return

        def _read_json(self) -> dict[str, object]:
            content_length = self.headers.get("Content-Length", "0")
            try:
                raw_length = int(content_length)
            except ValueError:
                raw_length = 0
            if raw_length <= 0:
                return {}
            raw_body = self.rfile.read(raw_length)
            try:
                payload = json.loads(raw_body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                return {}
            if not isinstance(payload, dict):
                return {}
            return payload

        def _send_json(self, status: HTTPStatus, payload: dict[str, object]) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status.value)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_file(self, path: Path) -> None:
            if not path.exists() or not path.is_file():
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
                return
            body = path.read_bytes()
            content_type, _ = mimetypes.guess_type(path.name)
            self.send_response(HTTPStatus.OK.value)
            self.send_header("Content-Type", content_type or "application/octet-stream")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return KidsChefHandler
