from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class ChatMessage(BaseModel):
    """A single message in a conversation."""
    id: Optional[int] = None
    role: str           # 'user' | 'assistant'
    content: str
    timestamp: Optional[datetime] = None


class ConversationSummary(BaseModel):
    """Lightweight conversation info for the history list."""
    id: str
    session_id: str
    title: Optional[str] = None
    created_at: Optional[datetime] = None


class ConversationDetail(ConversationSummary):
    """Full conversation with all messages."""
    messages: list[ChatMessage] = []


class WebSocketIncoming(BaseModel):
    """Message sent from browser → backend over WebSocket."""
    type: str                    # 'message' | 'ping'
    content: Optional[str] = None
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None


class StreamUpdate(BaseModel):
    """
    One streaming chunk sent from backend → browser.
    type:
      - 'node_update'  → agent node finished, partial content available
      - 'result'       → PV curve result with data and plot path
      - 'complete'     → whole turn finished
      - 'error'        → something went wrong
      - 'pong'         → response to ping
    """
    type: str
    node: Optional[str] = None
    content: Optional[str] = None
    results: Optional[dict[str, Any]] = None
    plot_path: Optional[str] = None
    conversation_id: Optional[str] = None
