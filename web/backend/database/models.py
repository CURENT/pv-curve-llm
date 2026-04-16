from sqlalchemy import Column, Text, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from web.backend.database.database import Base


class UserSession(Base):
    """
    Represents a browser session. Uses UUID as primary key.
    llm_config stores encrypted JSON: {"provider": "openai", "api_key": "...", "ollama_url": "..."}
    """
    __tablename__ = "sessions"

    id = Column(Text, primary_key=True)
    llm_config = Column(Text, nullable=True)   # Encrypted JSON
    created_at = Column(DateTime, server_default=func.now())


class Conversation(Base):
    """
    A single chat session (user opens a new chat = new conversation).
    Title is auto-generated from the first message.
    """
    __tablename__ = "conversations"

    id = Column(Text, primary_key=True)
    session_id = Column(Text, ForeignKey("sessions.id"), nullable=False)
    title = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class Message(Base):
    """
    One message inside a conversation.
    role is either 'user' or 'assistant'.
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Text, ForeignKey("conversations.id"), nullable=False)
    role = Column(Text, nullable=False)    # 'user' | 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())


class PVCurve(Base):
    """
    A generated PV curve result linked to a conversation.
    parameters and results are stored as JSON strings.
    """
    __tablename__ = "pv_curves"

    id = Column(Text, primary_key=True)
    conversation_id = Column(Text, ForeignKey("conversations.id"), nullable=False)
    grid = Column(Text, nullable=False)
    bus_id = Column(Integer, nullable=False)
    parameters = Column(Text, nullable=True)   # JSON of Inputs
    results = Column(Text, nullable=True)      # JSON of generation results
    plot_path = Column(Text, nullable=True)    # Path to PNG file
    created_at = Column(DateTime, server_default=func.now())
