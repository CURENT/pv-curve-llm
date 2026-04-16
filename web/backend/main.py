"""
PV Curve Agent - FastAPI Backend

Run with:
    cd pv-curve-llm
    uvicorn web.backend.main:app --reload --host 0.0.0.0 --port 8000

Swagger docs available at:  http://localhost:8000/docs
"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from web.backend.core.config import get_settings
from web.backend.database.database import init_db
from web.backend.utils.cache import session_cache

# Import routers
from web.backend.api.v1.chat import router as chat_router
from web.backend.api.v1.parameters import router as parameters_router
from web.backend.api.v1.settings import router as settings_router
from web.backend.api.v1.history import router as history_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    settings = get_settings()

    # Create DB tables if they don't exist yet
    init_db()

    # Create plots directory
    os.makedirs(settings.plots_path, exist_ok=True)

    # Background task: evict expired sessions every 10 minutes
    async def evict_loop():
        while True:
            await asyncio.sleep(600)
            removed = session_cache.evict_expired()
            if removed:
                print(f"[cache] Evicted {removed} expired session(s)")

    task = asyncio.create_task(evict_loop())

    yield

    task.cancel()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="REST + WebSocket API wrapping the PV Curve LangGraph Agent",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS — allow the Vite dev server (and production origin) to call the API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount API routers under /api/v1
    app.include_router(parameters_router, prefix="/api/v1", tags=["parameters"])
    app.include_router(settings_router, prefix="/api/v1", tags=["settings"])
    app.include_router(history_router, prefix="/api/v1", tags=["history"])

    # WebSocket router (no /api/v1 prefix — ws://localhost:8000/ws)
    app.include_router(chat_router, tags=["chat"])

    # Serve generated PV curve PNG files at /plots/<filename>
    if os.path.isdir(settings.plots_path):
        app.mount("/plots", StaticFiles(directory=settings.plots_path), name="plots")

    @app.get("/health", tags=["health"])
    def health():
        return {
            "status": "ok",
            "active_sessions": len(session_cache),
        }

    return app


app = create_app()
