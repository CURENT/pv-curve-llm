"""
Tests for chat-related functionality.

WebSocket tests use TestClient's websocket_connect context manager.
The full agent streaming is NOT tested here (requires LLM) — 
we only test the protocol and session/conversation management.
"""
import json
import pytest


def test_websocket_session_assignment(client):
    """
    Connecting without a session_id should receive a generated session_id back.
    """
    with client.websocket_connect("/ws") as ws:
        msg = ws.receive_json()
        assert msg["type"] == "session"
        assert "session_id" in msg
        assert len(msg["session_id"]) > 0


def test_websocket_session_persistence(client):
    """
    Connecting with an existing session_id should get that same id echoed back.
    """
    session_id = "test-session-ws-001"
    with client.websocket_connect(f"/ws?session_id={session_id}") as ws:
        msg = ws.receive_json()
        assert msg["type"] == "session"
        assert msg["session_id"] == session_id


def test_websocket_ping_pong(client):
    """Server replies to ping with pong."""
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()  # skip session message
        ws.send_json({"type": "ping"})
        msg = ws.receive_json()
        assert msg["type"] == "pong"


def test_websocket_invalid_json(client):
    """Sending non-JSON text returns an error."""
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()  # skip session message
        ws.send_text("this is not json")
        msg = ws.receive_json()
        assert msg["type"] == "error"


def test_websocket_missing_content(client):
    """Sending a message type without content returns an error."""
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()
        ws.send_json({"type": "message", "content": ""})
        msg = ws.receive_json()
        assert msg["type"] == "error"


def test_conversation_created_on_message(client):
    """
    When a user sends the first message in a new conversation, the server
    should respond with conversation_created before streaming agent updates.
    This test sends a message and checks we get conversation_created back.
    Note: the agent will then fail (no real LLM) but the conversation record is created.
    """
    with client.websocket_connect("/ws") as ws:
        session_msg = ws.receive_json()
        session_id = session_msg["session_id"]

        ws.send_json({
            "type": "message",
            "content": "hello",
        })

        # First response after a user message should be conversation_created.
        # (starlette TestClient WebSocket has no timeout arg on receive_json)
        responses = []
        for _ in range(10):
            try:
                msg = ws.receive_json()   # no timeout — blocks until message arrives
                responses.append(msg)
                if msg["type"] in ("conversation_created", "error", "complete"):
                    break
            except Exception:
                break

        types = [m["type"] for m in responses]
        assert "conversation_created" in types, f"Expected conversation_created, got: {types}"
