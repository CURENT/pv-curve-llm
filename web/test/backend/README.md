# Backend Tests

Tests for the FastAPI backend located in `web/backend/`.

## Running Tests

From the project root:

```bash
cd pv-curve-llm
source /path/to/venv/bin/activate
python -m pytest web/test/backend/ -v
```

## Test Files

- **`conftest.py`** - Pytest fixtures, test database setup with in-memory SQLite
- **`test_security.py`** - Encryption/decryption and API key masking tests
- **`test_database.py`** - SQLAlchemy CRUD operation tests
- **`test_parameters.py`** - Parameter REST endpoint tests
- **`test_chat.py`** - WebSocket protocol and integration tests

## Test Coverage

- ✅ Configuration and security utilities
- ✅ Database models and CRUD operations
- ✅ REST API endpoints (parameters, settings, history)
- ✅ WebSocket chat protocol
- ✅ Session management
- ✅ Integration test with real agent workflow

**Total: 26 tests**

## Notes

- Tests use an isolated in-memory SQLite database (via `StaticPool`)
- No real LLM calls are made (except in the integration test which uses the actual agent)
- All tests are independent and can run in parallel
