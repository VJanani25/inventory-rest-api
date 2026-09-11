# Inventory REST API

A small, production-minded inventory service built with Python's standard library and SQLite. It demonstrates RESTful CRUD, input validation, persistence, filtering, clean error responses, and tests without hiding the core behavior behind a framework.

## What it solves

Small teams often need a reliable inventory endpoint before they need a large platform. This service tracks stock items, supports category filtering, and exposes a minimal HTTP API that is easy to run locally and explain in an interview.

## Features

- `GET /health`
- `GET /items`
- `GET /items?category=hardware`
- `GET /items/{id}`
- `POST /items`
- `PATCH /items/{id}`
- `DELETE /items/{id}`
- SQLite persistence
- Validation for names, quantities, and reorder levels
- JSON error responses
- Unit tests for the service layer

## Technology

- Python 3.10+
- `http.server`
- SQLite via `sqlite3`
- `dataclasses`
- `pytest` for tests

The standard-library implementation keeps the API behavior visible. A production version could move the handler to FastAPI, add authentication, and use PostgreSQL.

## Run

```bash
cd inventory-rest-api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python scripts/run_server.py
```

The server listens on `http://127.0.0.1:8000` and stores data in `inventory.db`.

## Example requests

```bash
curl http://127.0.0.1:8000/health

curl -X POST http://127.0.0.1:8000/items \
  -H 'Content-Type: application/json' \
  -d '{"name":"USB-C adapter","category":"hardware","quantity":12,"reorder_level":4}'

curl 'http://127.0.0.1:8000/items?category=hardware'
```

Example response:

```json
{
  "id": 1,
  "name": "USB-C adapter",
  "category": "hardware",
  "quantity": 12,
  "reorder_level": 4
}
```

## Test

```bash
PYTHONPATH=src python -m pytest
```

## Architecture

```text
HTTP request
   │
   ▼
JSON request handler
   │
   ▼
InventoryStore validation + SQLite queries
   │
   ▼
JSON response
```

## Future improvements

- Authentication and role-based permissions
- PostgreSQL adapter and migrations
- Pagination and optimistic concurrency
- OpenAPI documentation
- Docker deployment and CI

## Resume bullet

Built a Python REST API with SQLite persistence, validated CRUD operations, category filtering, structured JSON errors, and automated service-layer tests.

## Author

Janani Varadharajan