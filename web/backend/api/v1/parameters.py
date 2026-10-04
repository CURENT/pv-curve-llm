from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from web.backend.database.database import get_db
from web.backend.services import session_service
from web.backend.schemas.parameters import ParametersResponse, ParametersUpdateRequest
from agent.schemas.inputs import Inputs
from web.backend.database import crud

router = APIRouter()

def _load_manager_inputs(session_id: str, conversation_id: str | None, db: Session) -> Inputs:
    entry = session_service.session_cache.get(session_id)
    manager = entry.get("web_manager") if entry else None

    if conversation_id:
        saved = crud.get_conversation_parameters(db, conversation_id)
        current = Inputs(**saved) if saved else Inputs()
        if manager:
            manager.set_inputs(current)
        return current

    if manager:
        return manager.current_inputs
    return Inputs()


def _save(session_id: str, conversation_id: str | None, current: Inputs, db: Session):
    entry = session_service.session_cache.get(session_id)
    manager = entry.get("web_manager") if entry else None
    if manager:
        manager.set_inputs(current)
    if conversation_id:
        crud.set_conversation_parameters(db, conversation_id, current.model_dump())

@router.get("/parameters")
def get_parameters(session_id: str, conversation_id: str | None = None, db: Session = Depends(get_db)):
    session_service.get_or_create_session(db, session_id)
    current = _load_manager_inputs(session_id, conversation_id, db)
    return ParametersResponse(session_id=session_id, conversation_id=conversation_id, parameters=current)


@router.post("/parameters")
def update_parameters(body: ParametersUpdateRequest, db: Session = Depends(get_db)):
    session_service.get_or_create_session(db, body.session_id)
    current = _load_manager_inputs(body.session_id, body.conversation_id, db)

    updates = body.model_dump(exclude={"session_id", "conversation_id"}, exclude_none=True)
    if updates:
        current = Inputs(**{**current.model_dump(), **updates})

    _save(body.session_id, body.conversation_id, current, db)
    return ParametersResponse(session_id=body.session_id, conversation_id=body.conversation_id, parameters=current)


@router.post("/parameters/reset")
def reset_parameters(session_id: str, conversation_id: str | None = None, db: Session = Depends(get_db)):
    session_service.get_or_create_session(db, session_id)
    defaults = Inputs()
    _save(session_id, conversation_id, defaults, db)
    return ParametersResponse(session_id=session_id, conversation_id=conversation_id, parameters=defaults)