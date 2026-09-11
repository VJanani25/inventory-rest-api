from __future__ import annotations

import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Item:
    id: int
    name: str
    category: str
    quantity: int
    reorder_level: int


class InventoryStore:
    def __init__(self, database_path: str | Path = "inventory.db"):
        self.database_path = str(database_path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL CHECK(length(trim(name)) BETWEEN 1 AND 120),
                    category TEXT NOT NULL CHECK(length(trim(category)) BETWEEN 1 AND 60),
                    quantity INTEGER NOT NULL CHECK(quantity >= 0),
                    reorder_level INTEGER NOT NULL CHECK(reorder_level >= 0)
                )
                """
            )

    @staticmethod
    def _validate_payload(payload: dict[str, object], partial: bool = False) -> dict[str, object]:
        allowed = {"name", "category", "quantity", "reorder_level"}
        unknown = set(payload) - allowed
        if unknown:
            raise ValueError(f"unknown fields: {', '.join(sorted(unknown))}")
        required = allowed if not partial else set(payload)
        if not partial and required - set(payload):
            raise ValueError(f"missing fields: {', '.join(sorted(required - set(payload)))}")
        clean: dict[str, object] = {}
        for field in ("name", "category"):
            if field not in payload:
                continue
            value = payload[field]
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} must be a non-empty string")
            clean[field] = value.strip()
        for field in ("quantity", "reorder_level"):
            if field not in payload:
                continue
            value = payload[field]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{field} must be a non-negative integer")
            clean[field] = value
        return clean

    @staticmethod
    def _row_to_item(row: sqlite3.Row) -> dict[str, object]:
        return asdict(Item(**dict(row)))

    def create_item(self, payload: dict[str, object]) -> dict[str, object]:
        clean = self._validate_payload(payload)
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO items(name, category, quantity, reorder_level) VALUES (?, ?, ?, ?)",
                (clean["name"], clean["category"], clean["quantity"], clean["reorder_level"]),
            )
            row = connection.execute("SELECT * FROM items WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return self._row_to_item(row)

    def list_items(self, category: str | None = None) -> list[dict[str, object]]:
        with self._connect() as connection:
            if category:
                rows = connection.execute(
                    "SELECT * FROM items WHERE category = ? ORDER BY id", (category.strip(),)
                ).fetchall()
            else:
                rows = connection.execute("SELECT * FROM items ORDER BY id").fetchall()
        return [self._row_to_item(row) for row in rows]

    def get_item(self, item_id: int) -> dict[str, object] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        return self._row_to_item(row) if row else None

    def update_item(self, item_id: int, payload: dict[str, object]) -> dict[str, object] | None:
        clean = self._validate_payload(payload, partial=True)
        if not clean:
            raise ValueError("at least one field is required")
        assignments = ", ".join(f"{field} = ?" for field in clean)
        values = list(clean.values()) + [item_id]
        with self._connect() as connection:
            cursor = connection.execute(f"UPDATE items SET {assignments} WHERE id = ?", values)
            if cursor.rowcount == 0:
                return None
            row = connection.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        return self._row_to_item(row)

    def delete_item(self, item_id: int) -> bool:
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM items WHERE id = ?", (item_id,))
        return cursor.rowcount > 0