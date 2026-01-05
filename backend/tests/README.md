# Backend Testing

This directory contains contract-level tests for the API endpoints.

## Setup

1. Install test dependencies:
```bash
poetry install
```

2. Run all tests:
```bash
poetry run pytest
```

3. Run tests with verbose output:
```bash
poetry run pytest -v
```

4. Run a specific test file:
```bash
poetry run pytest tests/test_users.py
```

5. Run a specific test:
```bash
poetry run pytest tests/test_users.py::test_get_all_users_with_auth
```

## Test Structure

- `conftest.py`: Contains pytest fixtures for test database, client, and authentication
- `test_users.py`: Contract-level tests for the `/api/users` endpoint

## How It Works

The tests use an **in-memory SQLite database** that is created fresh for each test and destroyed afterward. This ensures:

- Tests don't modify your development database
- Tests are isolated from each other
- Tests run quickly (in-memory is fast)

The test database is set up using FastAPI's `dependency_overrides` feature, which replaces the real `get_db` dependency with one that uses the test database.

## Writing Contract-Level Tests

Contract-level tests verify:
- **Status codes** (200, 201, 404, 401, etc.)
- **Response format** (JSON structure, required fields)
- **Error messages** (when things go wrong)
- **Authentication/Authorization** (who can access what)

They do **not** test implementation details - they test the API contract from the client's perspective.

