from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal


LLMProvider = Literal["openai", "ollama"]


class LLMConfigRequest(BaseModel):
    """Save or update LLM configuration for a session."""
    session_id: str
    provider: LLMProvider
    api_key: Optional[str] = None        # OpenAI key (only sent when provider=openai)
    ollama_url: Optional[str] = None     # Ollama base URL (only when provider=ollama)
    ollama_model: Optional[str] = None   # Ollama model name


class LLMConfigResponse(BaseModel):
    """Masked LLM config returned to the browser (never expose the raw key)."""
    session_id: str
    provider: LLMProvider
    api_key_set: bool = False
    api_key_masked: Optional[str] = None
    ollama_url: Optional[str] = None
    ollama_model: Optional[str] = None


class LLMTestResponse(BaseModel):
    """Result of testing LLM connectivity."""
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
