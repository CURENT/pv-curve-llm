from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from web.backend.database.database import get_db
from web.backend.services import session_service
from web.backend.schemas.parameters import ParametersResponse, ParametersUpdateRequest
from agent.schemas.inputs import Inputs

router = APIRouter()


@router.get("/parameters", response_model=ParametersResponse)
def get_parameters(session_id: str, db: Session = Depends(get_db)):
    """Return the current parameter state for a session."""
    session_service.get_or_create_session(db, session_id)
    entry = session_service.session_cache.get(session_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Session not found")

    manager = entry.get("web_manager")
    if manager:
        current = manager.current_inputs
    else:
        current = Inputs()

    return ParametersResponse(session_id=session_id, parameters=current)


@router.post("/parameters", response_model=ParametersResponse)
def update_parameters(body: ParametersUpdateRequest, db: Session = Depends(get_db)):
    """Apply partial parameter updates to the session's current inputs."""
    session_service.get_or_create_session(db, body.session_id)
    entry = session_service.session_cache.get(body.session_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Session not found")

    manager = entry.get("web_manager")
    if manager is None:
        # Manager not yet created — just update cache without spinning up agent
        current = Inputs()
    else:
        current = manager.current_inputs

    # Only update fields that were explicitly provided (non-None)
    updates = body.model_dump(exclude={"session_id"}, exclude_none=True)
    if updates:
        # Reconstruct via Inputs(**merged) so field validators run properly.
        # model_copy(update=...) skips validators in Pydantic v2.
        merged = {**current.model_dump(), **updates}
        try:
            current = Inputs(**merged)
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=exc.errors())
        if manager:
            manager.set_inputs(current)

    return ParametersResponse(session_id=body.session_id, parameters=current)


@router.post("/parameters/reset", response_model=ParametersResponse)
def reset_parameters(session_id: str, db: Session = Depends(get_db)):
    """Reset parameters to defaults."""
    session_service.get_or_create_session(db, session_id)
    entry = session_service.session_cache.get(session_id)

    defaults = Inputs()
    if entry and entry.get("web_manager"):
        entry["web_manager"].set_inputs(defaults)

    return ParametersResponse(session_id=session_id, parameters=defaults)
