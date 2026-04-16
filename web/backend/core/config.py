from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from functools import lru_cache
import secrets


def _bootstrap_encryption_key(env_file: str = ".env") -> str:
    """
    Generate a random encryption key and append it to the .env file so it
    persists across restarts.  Called only when ENCRYPTION_KEY is unset.
    """
    key = secrets.token_hex(32)
    with open(env_file, "a") as f:
        f.write(f"\n# Auto-generated encryption key — do not lose this\nENCRYPTION_KEY={key}\n")
    print(f"[security] No ENCRYPTION_KEY found — generated and saved to {env_file}")
    return key


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "PV Curve Agent API"
    debug: bool = False

    # Database
    database_path: str = "web_app.db"

    # Security
    encryption_key: str = ""
    jwt_secret: str = secrets.token_hex(32)

    @model_validator(mode="after")
    def ensure_encryption_key(self) -> "Settings":
        if not self.encryption_key:
            self.encryption_key = _bootstrap_encryption_key()
        return self

    # Plots output directory
    plots_path: str = "plots"

    # CORS origins allowed to talk to this backend
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # Session TTL in seconds (30 minutes)
    session_ttl_seconds: int = 1800

    # Default LLM provider
    default_llm_provider: str = "ollama"
    default_ollama_url: str = "http://localhost:11434"
    default_ollama_model: str = "llama3.1:8b"


@lru_cache
def get_settings() -> Settings:
    return Settings()
