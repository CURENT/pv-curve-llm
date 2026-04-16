"""
Session Service: manages the full lifecycle of a user session.

Responsibilities:
  - Create/retrieve sessions in both the in-memory cache and SQLite
  - Build WebSessionManager with the correct LLM config
  - Decode encrypted LLM config when restoring a session from DB
"""
import json
import uuid
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from web.backend.database import crud
from web.backend.services.agent_service import WebSessionManager
from web.backend.utils.cache import session_cache
from web.backend.core.security import encrypt_value, decrypt_value
from web.backend.core.config import get_settings


def _default_llm_config() -> dict:
    settings = get_settings()
    return {
        "provider": settings.default_llm_provider,
        "api_key": "",
        "ollama_url": settings.default_ollama_url,
        "ollama_model": settings.default_ollama_model,
    }


def get_or_create_session(db: DBSession, session_id: Optional[str] = None) -> str:
    """
    Return existing session_id or create a new one.
    Ensures the session exists in both the DB and in-memory cache.
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    # Ensure DB record exists
    db_session = crud.get_session(db, session_id)
    if not db_session:
        crud.create_session(db, session_id)

    # Ensure cache entry exists (without initializing the heavy agent yet)
    if session_cache.get(session_id) is None:
        session_cache.set(session_id, {
            "web_manager": None,
            "llm_config": _default_llm_config(),
        })

    return session_id


def get_web_manager(db: DBSession, session_id: str) -> WebSessionManager:
    """
    Return the WebSessionManager for a session, creating it lazily on first use.
    The manager is expensive to create (loads LLM + vector DB), so we cache it.
    """
    entry = session_cache.get(session_id)
    if entry is None:
        # Session expired from cache; restore from DB
        get_or_create_session(db, session_id)
        entry = session_cache.get(session_id)

    if entry["web_manager"] is not None:
        return entry["web_manager"]

    # Lazy init: build the WebSessionManager with stored LLM config
    settings = get_settings()
    llm_config = entry.get("llm_config") or _default_llm_config()

    # If config came from DB it's encrypted; decrypt it
    db_session = crud.get_session(db, session_id)
    if db_session and db_session.llm_config:
        raw = decrypt_value(db_session.llm_config, settings.encryption_key)
        if raw:
            try:
                llm_config = json.loads(raw)
            except json.JSONDecodeError:
                pass

    manager = WebSessionManager(
        provider=llm_config.get("provider", "ollama"),
        api_key=llm_config.get("api_key", ""),
        ollama_url=llm_config.get("ollama_url", ""),
        ollama_model=llm_config.get("ollama_model", ""),
    )
    entry["web_manager"] = manager
    entry["llm_config"] = llm_config
    session_cache.set(session_id, entry)
    return manager


def update_llm_config(db: DBSession, session_id: str, llm_config: dict) -> None:
    """
    Save new LLM config for a session.
    Encrypts the config and persists to DB.
    Forces re-creation of the WebSessionManager on next use.
    """
    settings = get_settings()
    encrypted = encrypt_value(json.dumps(llm_config), settings.encryption_key)
    crud.update_session_llm_config(db, session_id, encrypted)

    # Invalidate cached manager so it rebuilds with new LLM config
    entry = session_cache.get(session_id)
    if entry:
        entry["web_manager"] = None
        entry["llm_config"] = llm_config
        session_cache.set(session_id, entry)


def get_llm_config(db: DBSession, session_id: str) -> dict:
    """Return the (decrypted) LLM config for a session."""
    settings = get_settings()

    # Try cache first
    entry = session_cache.get(session_id)
    if entry and entry.get("llm_config"):
        return entry["llm_config"]

    # Fall back to DB
    db_session = crud.get_session(db, session_id)
    if db_session and db_session.llm_config:
        raw = decrypt_value(db_session.llm_config, settings.encryption_key)
        if raw:
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                pass

    return _default_llm_config()
