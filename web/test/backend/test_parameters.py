"""
Tests for parameter REST endpoints.
These don't need a real LLM — they only touch the parameter cache logic.
"""
import pytest
from web.backend.utils.cache import session_cache

SESSION_ID = "test-session-params-001"


def test_health(client):
    """Sanity check: server is up."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_get_parameters_default(client):
    """Getting parameters for a new session returns defaults."""
    response = client.get(f"/api/v1/parameters?session_id={SESSION_ID}")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == SESSION_ID
    params = data["parameters"]
    # Check defaults from agent/schemas/inputs.py
    assert params["grid"] == "ieee39"
    assert params["bus_id"] == 5
    assert params["power_factor"] == 0.95
    assert params["capacitive"] is False


def test_update_parameters(client):
    """Updating specific parameters leaves others unchanged."""
    response = client.post("/api/v1/parameters", json={
        "session_id": SESSION_ID,
        "grid": "ieee118",
        "bus_id": 10,
    })
    assert response.status_code == 200
    params = response.json()["parameters"]
    assert params["grid"] == "ieee118"
    assert params["bus_id"] == 10
    # Unchanged fields keep their default
    assert params["power_factor"] == 0.95


def test_reset_parameters(client):
    """Reset restores all defaults."""
    response = client.post(f"/api/v1/parameters/reset?session_id={SESSION_ID}")
    assert response.status_code == 200
    params = response.json()["parameters"]
    assert params["grid"] == "ieee39"
    assert params["bus_id"] == 5


def test_invalid_grid(client):
    """Invalid grid name is rejected by Pydantic validation."""
    response = client.post("/api/v1/parameters", json={
        "session_id": SESSION_ID,
        "grid": "ieee999",   # Not a valid GridSystem value
    })
    assert response.status_code == 422  # Unprocessable Entity


def test_update_power_factor_out_of_range(client):
    """power_factor must be between 0 and 1."""
    response = client.post("/api/v1/parameters", json={
        "session_id": SESSION_ID,
        "power_factor": 1.5,
    })
    assert response.status_code == 422
