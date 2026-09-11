import tempfile
from pathlib import Path

import pytest

from inventory_api.service import InventoryStore


@pytest.fixture
def store():
    with tempfile.TemporaryDirectory() as directory:
        yield InventoryStore(Path(directory) / "test.db")


def test_create_and_filter_items(store):
    created = store.create_item({"name": "Keyboard", "category": "hardware", "quantity": 5, "reorder_level": 2})
    assert created["id"] == 1
    assert store.list_items("hardware")[0]["name"] == "Keyboard"
    assert store.list_items("software") == []


def test_update_and_delete_items(store):
    created = store.create_item({"name": "Mouse", "category": "hardware", "quantity": 2, "reorder_level": 1})
    updated = store.update_item(created["id"], {"quantity": 7})
    assert updated["quantity"] == 7
    assert store.delete_item(created["id"]) is True
    assert store.get_item(created["id"]) is None


def test_validation_rejects_bad_payload(store):
    with pytest.raises(ValueError):
        store.create_item({"name": "", "category": "hardware", "quantity": -1, "reorder_level": 0})
    with pytest.raises(ValueError):
        store.update_item(1, {})