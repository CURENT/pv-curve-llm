from typing import Any
from web.backend.core.config import get_settings


def build_llm(provider: str, api_key: str = "", ollama_url: str = "", ollama_model: str = "") -> Any:
    """
    Build a LangChain LLM object from provider config.
    We import here (not at module level) so the module loads fast even when
    langchain isn't installed in the test environment.
    """
    settings = get_settings()

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_key,
        )
        llm._model_name = "gpt-4o-mini"
        return llm

    # Default: Ollama
    from langchain_ollama import ChatOllama
    url = ollama_url or settings.default_ollama_url
    model = ollama_model or settings.default_ollama_model
    llm = ChatOllama(model=model, base_url=url)
    llm._model_name = model
    return llm


def test_llm_connection(provider: str, api_key: str = "", ollama_url: str = "") -> dict:
    """
    Test whether the LLM config actually works.
    Returns {"success": True} or {"success": False, "error": "..."}.
    """
    try:
        llm = build_llm(provider, api_key=api_key, ollama_url=ollama_url)
        # A tiny prompt to verify connectivity
        response = llm.invoke("Reply with the single word: OK")
        return {"success": True, "response": str(response.content)[:50]}
    except Exception as exc:
        return {"success": False, "error": str(exc)}
