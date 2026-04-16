from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from web.backend.database.database import get_db
from web.backend.services import session_service
from web.backend.services.llm_service import test_llm_connection
from web.backend.schemas.settings import (
    LLMConfigRequest,
    LLMConfigResponse,
    LLMTestResponse,
)
from web.backend.core.security import mask_api_key

router = APIRouter()


@router.post("/settings/llm", response_model=LLMConfigResponse)
def save_llm_config(body: LLMConfigRequest, db: Session = Depends(get_db)):
    """Save (and encrypt) the user's LLM configuration."""
    session_service.get_or_create_session(db, body.session_id)

    config = {
        "provider": body.provider,
        "api_key": body.api_key or "",
        "ollama_url": body.ollama_url or "",
        "ollama_model": body.ollama_model or "",
    }
    session_service.update_llm_config(db, body.session_id, config)

    return LLMConfigResponse(
        session_id=body.session_id,
        provider=body.provider,
        api_key_set=bool(body.api_key),
        api_key_masked=mask_api_key(body.api_key) if body.api_key else None,
        ollama_url=body.ollama_url,
        ollama_model=body.ollama_model,
    )


@router.get("/settings/llm", response_model=LLMConfigResponse)
def get_llm_config(session_id: str, db: Session = Depends(get_db)):
    """Return the current LLM config (with API key masked)."""
    session_service.get_or_create_session(db, session_id)
    config = session_service.get_llm_config(db, session_id)

    api_key = config.get("api_key", "")
    return LLMConfigResponse(
        session_id=session_id,
        provider=config.get("provider", "ollama"),
        api_key_set=bool(api_key),
        api_key_masked=mask_api_key(api_key) if api_key else None,
        ollama_url=config.get("ollama_url", ""),
        ollama_model=config.get("ollama_model", ""),
    )


@router.post("/settings/llm/test", response_model=LLMTestResponse)
def test_llm(body: LLMConfigRequest, db: Session = Depends(get_db)):
    """
    Test whether the provided LLM config actually works.
    This makes a real (small) API call, so it may take a few seconds.
    """
    result = test_llm_connection(
        provider=body.provider,
        api_key=body.api_key or "",
        ollama_url=body.ollama_url or "",
    )
    return LLMTestResponse(**result)
