from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .service import InventoryStore


class InventoryHandler(BaseHTTPRequestHandler):
    store: InventoryStore

    def _send(self, status: int, payload: object) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 20_000:
            raise ValueError("request body is too large")
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError as error:
            raise ValueError("request body must be valid JSON") from error
        if not isinstance(payload, dict):
            raise ValueError("request body must be a JSON object")
        return payload

    def _route(self) -> tuple[str, int | None]:
        path = urlparse(self.path).path.rstrip("/") or "/"
        pieces = path.split("/")
        item_id = None
        if len(pieces) == 3 and pieces[1] == "items":
            try:
                item_id = int(pieces[2])
            except ValueError:
                raise ValueError("item id must be an integer")
        return path, item_id

    def do_GET(self) -> None:
        try:
            path, item_id = self._route()
            if path == "/health":
                return self._send(200, {"status": "ok"})
            if path == "/items":
                category = parse_qs(urlparse(self.path).query).get("category", [None])[0]
                return self._send(200, self.store.list_items(category))
            if item_id is not None:
                item = self.store.get_item(item_id)
                return self._send(200, item) if item else self._send(404, {"error": "item not found"})
            self._send(404, {"error": "route not found"})
        except ValueError as error:
            self._send(400, {"error": str(error)})

    def do_POST(self) -> None:
        if urlparse(self.path).path.rstrip("/") != "/items":
            return self._send(404, {"error": "route not found"})
        try:
            self._send(201, self.store.create_item(self._read_json()))
        except (ValueError, TypeError) as error:
            self._send(400, {"error": str(error)})

    def do_PATCH(self) -> None:
        try:
            path, item_id = self._route()
            if item_id is None or not path.startswith("/items/"):
                return self._send(404, {"error": "route not found"})
            item = self.store.update_item(item_id, self._read_json())
            self._send(200, item) if item else self._send(404, {"error": "item not found"})
        except (ValueError, TypeError) as error:
            self._send(400, {"error": str(error)})

    def do_DELETE(self) -> None:
        try:
            path, item_id = self._route()
            if item_id is None or not path.startswith("/items/"):
                return self._send(404, {"error": "route not found"})
            self._send(204, {}) if self.store.delete_item(item_id) else self._send(404, {"error": "item not found"})
        except ValueError as error:
            self._send(400, {"error": str(error)})

    def log_message(self, format: str, *args: object) -> None:
        return


def create_server(host: str = "127.0.0.1", port: int = 8000, database_path: str = "inventory.db") -> ThreadingHTTPServer:
    InventoryHandler.store = InventoryStore(database_path)
    return ThreadingHTTPServer((host, port), InventoryHandler)