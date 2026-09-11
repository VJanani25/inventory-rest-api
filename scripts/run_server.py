from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from inventory_api.server import create_server


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    with create_server(host, port) as server:
        print(f"Inventory API listening on http://{host}:{port}")
        server.serve_forever()