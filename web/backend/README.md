# PV Curve Agent — FastAPI Backend

REST + WebSocket API that wraps the existing CLI agent for web access.

## Quick Start

```bash
# From the project root (pv-curve-llm/)
cp web/backend/.env.example web/backend/.env
# Edit .env and fill in ENCRYPTION_KEY and JWT_SECRET

# Install dependencies (uses the project's shared venv)
pip install -r requirements.txt          # agent deps
pip install -r web/backend/requirements.txt

# Run the backend
uvicorn web.backend.main:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000/docs** to see the Swagger UI with all endpoints.

---

## Docker (Full Stack — Local)

Run the backend + React frontend together in a single container:

```bash
# From the project root (pv-curve-llm/)
cp web/backend/.env.example web/backend/.env
# Edit web/backend/.env — set ENCRYPTION_KEY (JWT_SECRET is auto-generated)

docker compose -f web/docker-compose.yml up --build
```

Browse to **http://localhost:8080**.

- `DATABASE_PATH` and `PLOTS_PATH` are overridden inside the container to `/data/web_app.db` and `/data/plots`, backed by a named Docker volume (`pv_data`).
- All other env vars are read from `web/backend/.env`.

---

## Deploying to Render

1. Push this repository to GitHub.
2. Go to [render.com](https://render.com) → **New → Blueprint** → connect your repo.
3. Render detects `render.yaml` at the repo root — click **Apply** to provision the service and disk.
4. Set `ENCRYPTION_KEY` in the Render dashboard → **Environment** if it wasn't auto-generated (the blueprint uses `generateValue: true` for both secrets).
5. Trigger a deploy — the app will be live at `https://<app>.onrender.com`.

**Verify the deployment:**

```bash
# Health check
curl https://<app>.onrender.com/health
# → {"status":"ok","active_sessions":0}

# WebSocket (connection indicator in the header should turn green)
# wss://<app>.onrender.com/ws

# Generate a PV curve to confirm end-to-end flow
```

> **Free tier note:** Render Free spins down after ~15 minutes of inactivity (cold start ~30s). Upgrade to Starter ($7/month) for always-on.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_PATH` | `web_app.db` | SQLite file path |
| `ENCRYPTION_KEY` | *(required)* | Secret key for encrypting API keys in DB |
| `JWT_SECRET` | *(auto-generated)* | Secret for future JWT auth |
| `PLOTS_PATH` | `plots` | Directory where PV curve PNGs are saved |
| `DEFAULT_LLM_PROVIDER` | `ollama` | `openai` or `ollama` |
| `DEFAULT_OLLAMA_URL` | `http://localhost:11434` | Ollama base URL |
| `DEFAULT_OLLAMA_MODEL` | `llama3.1:8b` | Ollama model name |

Generate keys:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## API Reference

### WebSocket — `/ws`

Connect: `ws://localhost:8000/ws?session_id=<uuid>`  
(Omit `session_id` to get a new one assigned)

**Client → Server:**
```json
{"type": "message", "content": "Generate PV curve for IEEE 118 bus 10"}
{"type": "ping"}
```

**Server → Client (streaming):**
```json
{"type": "session",             "session_id": "uuid"}
{"type": "conversation_created","conversation_id": "uuid", "title": "..."}
{"type": "node_update",         "node": "classifier", "content": "..."}
{"type": "node_update",         "node": "generation", "content": "...", "results": {...}, "plot_path": "..."}
{"type": "complete"}
{"type": "error",               "content": "error message"}
{"type": "pong"}
```

---

### REST Endpoints

#### Parameters
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/parameters?session_id=` | Get current parameters |
| `POST` | `/api/v1/parameters` | Update parameters (partial) |
| `POST` | `/api/v1/parameters/reset?session_id=` | Reset to defaults |

#### Settings (LLM Configuration)
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/settings/llm` | Save LLM config (encrypted) |
| `GET` | `/api/v1/settings/llm?session_id=` | Get config (key masked) |
| `POST` | `/api/v1/settings/llm/test` | Test LLM connectivity |

#### Conversation History
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/conversations?session_id=` | List all conversations |
| `GET` | `/api/v1/conversations/{id}` | Get conversation + messages |
| `DELETE` | `/api/v1/conversations/{id}` | Delete conversation |

#### Misc
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check + active session count |

---

## Architecture

```
web/backend/
├── main.py              # FastAPI app entry point, lifespan, routes
├── core/
│   ├── config.py        # Pydantic Settings (reads .env)
│   └── security.py      # Fernet encryption, API key masking
├── database/
│   ├── database.py      # SQLAlchemy engine + get_db dependency
│   ├── models.py        # ORM: UserSession, Conversation, Message, PVCurve
│   └── crud.py          # CRUD operations
├── services/
│   ├── agent_service.py # Wraps agent SessionManager for async streaming
│   ├── llm_service.py   # Builds LLM objects (OpenAI / Ollama)
│   └── session_service.py  # Bridges in-memory cache ↔ database
├── api/v1/
│   ├── chat.py          # WebSocket endpoint /ws
│   ├── parameters.py    # GET/POST /api/v1/parameters
│   ├── settings.py      # GET/POST /api/v1/settings/llm
│   └── history.py       # GET/DELETE /api/v1/conversations
├── schemas/
│   ├── chat.py          # Pydantic models for WebSocket messages
│   ├── parameters.py    # Request/response models for parameters
│   └── settings.py      # LLM config request/response models
└── utils/
    └── cache.py         # In-memory session cache with TTL

Tests are located in:
web/test/backend/
├── conftest.py       # Pytest fixtures, test DB override
├── test_chat.py      # WebSocket protocol tests
├── test_parameters.py# Parameter endpoint tests
├── test_database.py  # CRUD unit tests
└── test_security.py  # Encryption unit tests
```

---

## Running Tests

```bash
cd pv-curve-llm
python -m pytest web/test/backend/ -v
```

Tests use an isolated in-memory SQLite database and do NOT touch your real `web_app.db`.

---

## Generated Plots

PV curve PNG files are saved to `PLOTS_PATH` (default: `plots/`).  
They are served at `http://localhost:8000/plots/<filename>`.

Example: `/plots/pv_curve_ieee118_20260315_123456.png`
