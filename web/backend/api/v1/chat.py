"""
WebSocket endpoint for real-time agent chat.

Connection flow:
  1. Client opens ws://localhost:8000/ws?session_id=<uuid>
     (If session_id is omitted, a new one is generated and returned first)
  2. Client sends: {"type": "message", "content": "...", "conversation_id": "..."}
  3. Server streams back node_update events, then complete
  4. Connection stays open for the whole browser session
"""
import asyncio
import json
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from web.backend.database.database import get_db
from web.backend.database import crud
from web.backend.services import session_service
from web.backend.schemas.chat import WebSocketIncoming

router = APIRouter()


@router.websocket("/ws")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str = "",
    db: Session = Depends(get_db),
):
    await websocket.accept()

    # Ensure session exists; generate one if not provided
    session_id = session_service.get_or_create_session(db, session_id or None)

    # Send the session_id back immediately so the browser can persist it
    await websocket.send_json({"type": "session", "session_id": session_id})

    try:
        while True:
            raw = await websocket.receive_text()

            # --- Parse incoming message ---
            try:
                data = json.loads(raw)
                incoming = WebSocketIncoming(**data)
            except Exception:
                await websocket.send_json({"type": "error", "content": "Invalid message format"})
                continue

            if incoming.type == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            if incoming.type != "message" or not incoming.content:
                await websocket.send_json({"type": "error", "content": "Expected type='message' with content"})
                continue

            user_text = incoming.content.strip()

            # --- Ensure conversation record exists ---
            conversation_id = incoming.conversation_id
            if not conversation_id:
                # Auto-generate title from first 60 chars of user message
                title = user_text[:60] + ("..." if len(user_text) > 60 else "")
                conv = crud.create_conversation(db, session_id, title=title)
                conversation_id = conv.id
                # Tell browser the conversation_id so it can track history
                await websocket.send_json({
                    "type": "conversation_created",
                    "conversation_id": conversation_id,
                    "title": title,
                })

            # Persist user message
            crud.create_message(db, conversation_id, role="user", content=user_text)

            # --- Get (or lazily create) the agent manager ---
            # Run in thread so the blocking LLM/vector-DB initialization
            # does NOT hold the event loop (which would prevent send_json flushes)
            manager = await asyncio.to_thread(session_service.get_web_manager, db, session_id)

            # --- Stream agent responses ---
            assistant_chunks: list[str] = []
            final_results: dict = {}
            plot_path: str = ""

            async for update in manager.execute_streaming(user_text):
                update["conversation_id"] = conversation_id
                await websocket.send_json(update)

                if update["type"] == "node_update" and update.get("content"):
                    assistant_chunks.append(update["content"])
                if update.get("results"):
                    final_results = update["results"]
                if update.get("plot_path"):
                    plot_path = update["plot_path"]

            # --- Persist assistant response ---
            assistant_text = "\n\n".join(c for c in assistant_chunks if c).strip()
            if assistant_text:
                crud.create_message(db, conversation_id, role="assistant", content=assistant_text)

            # --- Persist PV curve if generated ---
            if final_results:
                state = manager.get_state()
                inputs_obj = state.get("inputs")
                crud.create_pv_curve(
                    db=db,
                    conversation_id=conversation_id,
                    grid=getattr(inputs_obj, "grid", ""),
                    bus_id=getattr(inputs_obj, "bus_id", 0),
                    parameters=inputs_obj.model_dump() if inputs_obj else None,
                    results=final_results,
                    plot_path=plot_path,
                )

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        try:
            await websocket.send_json({"type": "error", "content": str(exc)})
        except Exception:
            pass
