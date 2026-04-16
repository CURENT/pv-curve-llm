"""
Shared fixtures for all backend tests.

Uses an in-memory SQLite database so tests are isolated and fast.
Sets required env vars before importing the app so Settings picks them up.
"""
import os
import pytest

# Set test environment BEFORE importing anything that reads Settings
os.environ.setdefault("DATABASE_PATH", ":memory:")
os.environ.setdefault("ENCRYPTION_KEY", "test-encryption-key-12345")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret")
os.environ.setdefault("PLOTS_PATH", "/tmp/test_pv_plots")
os.environ.setdefault("DEFAULT_LLM_PROVIDER", "ollama")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from web.backend.database.database import Base, get_db
from web.backend.database import models  # noqa: F401 — must import to register ORM classes
from web.backend.main import app


# StaticPool forces all operations to share ONE connection, so tables created
# by create_all are visible to every subsequent query in the same process.
_test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSession = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)


def override_get_db():
    db = _TestSession()
    try:
        yield db
    finally:
        db.close()


# Create all tables in the test engine (models must be imported first)
Base.metadata.create_all(bind=_test_engine)

# Override DB dependency in the app so all routes use the test DB
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db():
    """Provide a clean DB session for direct CRUD tests."""
    session = _TestSession()
    yield session
    session.close()
