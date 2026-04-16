"""
Tests for the database CRUD layer.
Uses the in-memory DB from conftest.py fixtures.
"""
import pytest
from web.backend.database import crud


def test_create_and_get_session(db):
    session = crud.create_session(db, "session-db-001")
    assert session.id == "session-db-001"

    fetched = crud.get_session(db, "session-db-001")
    assert fetched is not None
    assert fetched.id == session.id


def test_create_conversation(db):
    crud.create_session(db, "session-db-002")
    conv = crud.create_conversation(db, "session-db-002", title="My First Chat")
    assert conv.title == "My First Chat"
    assert conv.session_id == "session-db-002"


def test_list_conversations(db):
    crud.create_session(db, "session-db-003")
    crud.create_conversation(db, "session-db-003", title="Conv A")
    crud.create_conversation(db, "session-db-003", title="Conv B")

    convs = crud.list_conversations(db, "session-db-003")
    titles = [c.title for c in convs]
    assert "Conv A" in titles
    assert "Conv B" in titles


def test_create_and_list_messages(db):
    crud.create_session(db, "session-db-004")
    conv = crud.create_conversation(db, "session-db-004")

    crud.create_message(db, conv.id, "user", "Hello!")
    crud.create_message(db, conv.id, "assistant", "Hi there!")

    msgs = crud.list_messages(db, conv.id)
    assert len(msgs) == 2
    assert msgs[0].role == "user"
    assert msgs[1].role == "assistant"


def test_create_pv_curve(db):
    crud.create_session(db, "session-db-005")
    conv = crud.create_conversation(db, "session-db-005")

    pvc = crud.create_pv_curve(
        db=db,
        conversation_id=conv.id,
        grid="ieee118",
        bus_id=10,
        parameters={"grid": "ieee118", "bus_id": 10},
        results={"load_margin": 2.5, "nose_point": 0.85},
        plot_path="/plots/test.png",
    )
    assert pvc.grid == "ieee118"
    assert pvc.bus_id == 10
    assert pvc.plot_path == "/plots/test.png"


def test_delete_conversation_cascades(db):
    crud.create_session(db, "session-db-006")
    conv = crud.create_conversation(db, "session-db-006")
    crud.create_message(db, conv.id, "user", "Test")
    crud.create_pv_curve(db, conv.id, "ieee39", 5)

    deleted = crud.delete_conversation(db, conv.id)
    assert deleted is True

    # Messages and PV curves should be gone
    msgs = crud.list_messages(db, conv.id)
    assert len(msgs) == 0


def test_update_session_llm_config(db):
    crud.create_session(db, "session-db-007")
    updated = crud.update_session_llm_config(db, "session-db-007", "encrypted-blob")
    assert updated.llm_config == "encrypted-blob"


def test_get_nonexistent_session(db):
    result = crud.get_session(db, "does-not-exist")
    assert result is None
