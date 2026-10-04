import json
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from web.backend.database.models import UserSession, Conversation, Message, PVCurve


# ---------------------------------------------------------------------------
# Session CRUD
# ---------------------------------------------------------------------------

def create_session(db: Session, session_id: str) -> UserSession:
    record = UserSession(id=session_id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_session(db: Session, session_id: str) -> Optional[UserSession]:
    return db.query(UserSession).filter(UserSession.id == session_id).first()


def update_session_llm_config(db: Session, session_id: str, encrypted_config: str) -> Optional[UserSession]:
    record = get_session(db, session_id)
    if not record:
        return None
    record.llm_config = encrypted_config
    db.commit()
    db.refresh(record)
    return record


# ---------------------------------------------------------------------------
# Conversation CRUD
# ---------------------------------------------------------------------------

def create_conversation(db: Session, session_id: str, title: Optional[str] = None) -> Conversation:
    record = Conversation(
        id=str(uuid.uuid4()),
        session_id=session_id,
        title=title,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_conversation(db: Session, conversation_id: str) -> Optional[Conversation]:
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def list_conversations(db: Session, session_id: str) -> list[Conversation]:
    return (
        db.query(Conversation)
        .filter(Conversation.session_id == session_id)
        .order_by(Conversation.created_at.desc())
        .all()
    )


def delete_conversation(db: Session, conversation_id: str) -> bool:
    record = get_conversation(db, conversation_id)
    if not record:
        return False
    # Delete dependent messages and pv_curves first (no cascade configured)
    db.query(Message).filter(Message.conversation_id == conversation_id).delete()
    db.query(PVCurve).filter(PVCurve.conversation_id == conversation_id).delete()
    db.delete(record)
    db.commit()
    return True


def update_conversation_title(db: Session, conversation_id: str, title: str) -> Optional[Conversation]:
    record = get_conversation(db, conversation_id)
    if not record:
        return None
    record.title = title
    db.commit()
    db.refresh(record)
    return record

def get_conversation_parameters(db: Session, conversation_id: str) -> Optional[dict]:
    conv = get_conversation(db, conversation_id)
    if not conv or not conv.parameters:
        return None
    return json.loads(conv.parameters)
def set_conversation_parameters(db: Session, conversation_id: str, params: dict) -> None:
    conv = get_conversation(db, conversation_id)
    if not conv:
        return
    conv.parameters = json.dumps(params)
    db.commit()

# ---------------------------------------------------------------------------
# Message CRUD
# ---------------------------------------------------------------------------

def create_message(
    db: Session,
    conversation_id: str,
    role: str,
    content: str,
) -> Message:
    record = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_messages(db: Session, conversation_id: str) -> list[Message]:
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.timestamp.asc())
        .all()
    )


# ---------------------------------------------------------------------------
# PV Curve CRUD
# ---------------------------------------------------------------------------

def create_pv_curve(
    db: Session,
    conversation_id: str,
    grid: str,
    bus_id: int,
    parameters: Optional[dict] = None,
    results: Optional[dict] = None,
    plot_path: Optional[str] = None,
) -> PVCurve:
    record = PVCurve(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        grid=grid,
        bus_id=bus_id,
        parameters=json.dumps(parameters) if parameters else None,
        results=json.dumps(results) if results else None,
        plot_path=plot_path,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_pv_curves_by_session(db: Session, session_id: str) -> list[PVCurve]:
    """All plots for a session, newest first."""
    return (
        db.query(PVCurve)
        .join(Conversation, PVCurve.conversation_id == Conversation.id)
        .filter(Conversation.session_id == session_id)
        .order_by(PVCurve.created_at.desc())
        .all()
    )