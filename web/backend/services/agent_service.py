"""
Agent Service: wraps the existing CLI SessionManager for web use.

Key challenge: SessionManager.execute_turn_streaming() is a synchronous
generator. FastAPI is async. We run the blocking generator in a thread pool
(via asyncio.to_thread / run_in_executor) and convert it into an async
generator that the WebSocket handler can await.
"""
import asyncio
import json
from typing import AsyncGenerator, Optional

from agent.session import SessionManager
from agent.schemas.inputs import Inputs
from web.backend.services.llm_service import build_llm
from web.backend.core.config import get_settings


def _extract_ai_text(state_update: dict) -> str:
    """Pull the last AIMessage content out of a node state update."""
    messages = state_update.get("messages", [])
    if not messages:
        return ""
    last = messages[-1]
    # LangChain AIMessage has .content attribute; dicts have "content" key
    if hasattr(last, "content"):
        return last.content
    if isinstance(last, dict):
        return last.get("content", "")
    return str(last)


def _extract_results(state_update: dict) -> Optional[dict]:
    """Return results dict if this node update contains PV curve results."""
    results = state_update.get("results")
    if not results:
        return None
    # Convert Pydantic models / numpy arrays to plain dicts for JSON
    try:
        return json.loads(json.dumps(results, default=str))
    except Exception:
        return None


class WebSessionManager:
    """
    Holds one user's agent state for the duration of their browser session.
    Created once per session_id and kept in the session cache.
    """

    def __init__(self, provider: str, api_key: str = "", ollama_url: str = "", ollama_model: str = ""):
        settings = get_settings()
        llm = build_llm(provider, api_key=api_key, ollama_url=ollama_url, ollama_model=ollama_model)

        from agent.core import setup_dependencies
        from agent.workflows.workflow import create_workflow
        from agent.pv_curve.pv_curve import generate_pv_curve
        from agent.prompts import get_prompts
        from agent.vector import retriever as make_retriever
        import os

        # Point PV curve output at the configured plots directory
        os.environ["PV_CURVE_OUTPUT_DIR"] = settings.plots_path
        os.makedirs(settings.plots_path, exist_ok=True)

        prompts = get_prompts()
        retriever = make_retriever()
        workflow = create_workflow(llm, prompts, retriever, generate_pv_curve)

        self.session_manager = SessionManager(workflow, provider, llm._model_name)
        self.current_inputs = Inputs()

    def set_inputs(self, inputs: Inputs) -> None:
        """Update parameters in BOTH the REST surface and the live agent state."""
        self.current_inputs = inputs
        self.session_manager.state["inputs"] = inputs

    async def execute_streaming(self, user_input: str) -> AsyncGenerator[dict, None]:
        """
        Async generator that yields WebSocket-friendly dicts for each node update.

        Example yielded values:
          {"type": "node_update", "node": "classifier", "content": "..."}
          {"type": "result", "results": {...}, "plot_path": "..."}
          {"type": "complete"}
        """
        loop = asyncio.get_event_loop()
        queue: asyncio.Queue = asyncio.Queue()

        def run_agent():
            """Runs synchronous generator in a background thread, pushes to queue."""
            try:
                for node_name, state_update in self.session_manager.execute_turn_streaming(user_input):
                    # Push each update; loop.call_soon_threadsafe is thread-safe
                    asyncio.run_coroutine_threadsafe(
                        queue.put(("update", node_name, state_update)), loop
                    ).result()
            except Exception as exc:
                asyncio.run_coroutine_threadsafe(
                    queue.put(("error", str(exc), {})), loop
                ).result()
            finally:
                asyncio.run_coroutine_threadsafe(
                    queue.put(("done", None, None)), loop
                ).result()

        # Start agent in background thread
        thread_future = loop.run_in_executor(None, run_agent)

        # Consume queue as async generator
        while True:
            kind, node_name, state_update = await queue.get()

            if kind == "done":
                break

            if kind == "error":
                yield {"type": "error", "content": node_name}
                break

            # kind == "update"
            text = _extract_ai_text(state_update)
            results = _extract_results(state_update)

            msg = {"type": "node_update", "node": node_name, "content": text}

            # Attach results if this is a generation/analysis node
            if results:
                msg["results"] = results
                plot_path = state_update.get("results", {}).get("plot_path", "")
                if plot_path:
                    msg["plot_path"] = plot_path

            # Keep both copies in sync so the next turn's graph sees the latest inputs
            if "inputs" in state_update:
                self.set_inputs(state_update["inputs"])

            yield msg

        await thread_future  # Ensure thread completed cleanly
        yield {"type": "complete"}

    def get_state(self) -> dict:
        return self.session_manager.get_state()
