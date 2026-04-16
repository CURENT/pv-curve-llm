from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from web.backend.database.database import get_db
from web.backend.database import crud
from web.backend.schemas.chat import ConversationSummary, ConversationDetail, ChatMessage

router = APIRouter()


@router.get("/conversations", response_model=list[ConversationSummary])
def list_conversations(session_id: str, db: Session = Depends(get_db)):
    """Return all conversations for a session, newest first."""
    convs = crud.list_conversations(db, session_id)
    return [
        ConversationSummary(
            id=c.id,
            session_id=c.session_id,
            title=c.title,
            created_at=c.created_at,
        )
        for c in convs
    ]


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Return a conversation with all its messages."""
    conv = crud.get_conversation(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = crud.list_messages(db, conversation_id)
    return ConversationDetail(
        id=conv.id,
        session_id=conv.session_id,
        title=conv.title,
        created_at=conv.created_at,
        messages=[
            ChatMessage(
                id=m.id,
                role=m.role,
                content=m.content,
                timestamp=m.timestamp,
            )
            for m in messages
        ],
    )


@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Delete a conversation and all its messages."""
    deleted = crud.delete_conversation(db, conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"deleted": True, "conversation_id": conversation_id}
