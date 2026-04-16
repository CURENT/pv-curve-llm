# Web Deployment Sprint Plan (Simple & Practical)
# PV Curve Agent - From CLI to Cloud-Based Web Application

**Target Users:** 5-10 concurrent users initially, scalable to 500+ in future
**Estimated Monthly Cost:** $0-7/month
**Timeline:** 3 sprints (3 weeks) to production launch

---

## 🎯 Executive Summary

**Goal:** Transform CLI-based PV Curve Agent into an easy-to-use web application accessible from any browser, deployed on the cloud with minimal cost.

### Key Approach
- **Minimum Viable Product**: Get it working first, add features later
- **Reuse Existing Agent**: Wrap existing code, don't rewrite
- **Simple Architecture**: Single container, SQLite, no complex infrastructure
- **User-Provided LLM**: Users bring their own OpenAI API key or local Ollama ($0 server cost)

### What You Get in 3 Weeks

✅ Web interface with real-time chat (WebSocket streaming)
✅ All CLI features accessible through web UI
✅ Interactive PV curve visualization (Plotly.js)
✅ Save and load conversation history
✅ Mobile-responsive design
✅ Deployed on cloud with automatic HTTPS
✅ Cost: $0-7/month

### What's Deferred (Add Later)

⏸️ User accounts/login (everyone is guest for now)
⏸️ Advanced comparison dashboard (just show one curve at a time)
⏸️ Batch generation and parameter sweeps
⏸️ Advanced export formats (just PNG)
⏸️ CI/CD automation (manual deploy initially)
⏸️ Advanced monitoring (just basic error tracking)

---

## Sprint 1 Plan

**Sprint Goals (Week 1)** Backend API & Database: Create FastAPI backend that wraps existing agent workflow, implement WebSocket for real-time streaming, and set up SQLite database for conversation persistence.

### Task 1: FastAPI Backend Setup & Agent Integration

**Action Items:**
- Create `/web/backend/` directory structure:
  ```
  /web/backend/
    ├── api/v1/          # API endpoints
    ├── services/        # Agent service wrapper
    ├── database/        # SQLite models
    ├── core/            # Config
    └── main.py          # FastAPI app
  ```
- Initialize FastAPI application with CORS configuration
- Implement WebSocket endpoint (`/ws`) for real-time chat streaming
- Create agent service wrapper (`services/agent_service.py`):
  - Import existing agent workflow from `../../agent/workflows/workflow.py`
  - Wrap `create_graph()` and `setup_dependencies()`
  - Stream agent responses through WebSocket
- Create basic REST API endpoints:
  - `POST /api/v1/chat` - Send message, get response
  - `GET /api/v1/parameters` - Get current parameters
  - `POST /api/v1/parameters` - Update parameters
  - `GET /api/v1/health` - Health check
- Implement simple in-memory session storage (Python dict)
- Add Pydantic models for request/response validation
- Set up basic error handling

**Deliverable:** A functional FastAPI backend running on `localhost:8000` with Swagger docs at `/docs`, capable of executing full agent workflow via WebSocket with real-time streaming.

**Dependencies:** None

---

### Task 2: SQLite Database & Persistence

**Action Items:**
- Set up SQLAlchemy ORM with SQLite (`/web/backend/web_app.db`)
- Design simple database schema (4 tables):
  - `sessions`: id, llm_config (encrypted), created_at
  - `conversations`: id, session_id, title, created_at
  - `messages`: id, conversation_id, role, content, timestamp
  - `pv_curves`: id, conversation_id, grid, bus_id, parameters (JSON), results (JSON), plot_path, created_at
- Implement SQLAlchemy models in `database/models.py`
- Create database initialization script
- Build CRUD operations:
  - Save/load conversations
  - Store PV curve results
  - Retrieve conversation history
- Implement session manager:
  - Create guest sessions (UUID-based)
  - Persist conversations to database
  - Load previous conversations

**Deliverable:** Working SQLite database with conversation persistence. Users can save/load chat history. **Cost: $0**

**Dependencies:** Task 1

---

### Task 3: LLM Configuration & Encryption

**Action Items:**
- Create LLM configuration endpoints:
  - `POST /api/v1/settings/llm` - Save user's LLM config (API key or Ollama URL)
  - `GET /api/v1/settings/llm` - Get current config (masked)
  - `POST /api/v1/settings/llm/test` - Test connection
- Implement API key encryption using Fernet (cryptography library)
- Update agent service to use user's LLM configuration:
  - If user provides OpenAI key, use it
  - If user provides Ollama URL, connect to it
  - Store encrypted in database per session
- Add LLM provider abstraction in `services/llm_service.py`
- Implement connection testing (validate API key or Ollama URL)

**Deliverable:** Backend can use user-provided OpenAI API key or Ollama URL, stored encrypted in database. **Cost: $0** (no server-side LLM costs).

**Dependencies:** Task 2

---

## Sprint 2 Plan

**Sprint Goals (Week 2)** Frontend Web Application: Build React-based web interface with chat, parameter controls, and interactive PV curve visualization using Plotly.js.

### Task 1: React Foundation & Chat Interface

**Action Items:**
- Create `/web/frontend/` and initialize React + Vite + TypeScript project
- Set up project structure:
  ```
  /web/frontend/src/
    ├── components/      # UI components
    ├── pages/           # Main pages
    ├── services/        # API + WebSocket
    ├── store/           # Zustand state
    └── types/           # TypeScript types
  ```
- Install core dependencies:
  - React Router (navigation)
  - Zustand (state management)
  - Tailwind CSS (styling)
  - Socket.io-client (WebSocket)
  - Axios (HTTP client)
- Build chat interface components:
  - `ChatInterface.tsx` - Main chat container
  - `MessageBubble.tsx` - User and agent messages
  - `MessageInput.tsx` - Text input with send button
- Implement WebSocket service (`services/websocket.ts`):
  - Connect to backend `/ws`
  - Send user messages
  - Receive and display streaming responses
  - Auto-reconnect on disconnect
- Implement API client (`services/api.ts`) for REST endpoints
- Set up routing:
  - `/chat` - Main chat page
  - `/history` - Conversation list (simple)
  - `/settings` - LLM configuration

**Deliverable:** Working React app on `localhost:5173` with functional chat interface, WebSocket streaming, and navigation between pages.

**Dependencies:** Sprint 1

---

### Task 2: Parameter Controls & Visualization

**Action Items:**
- Build parameter control panel (`components/Parameters/ParameterPanel.tsx`):
  - Grid system dropdown (IEEE 14/24/30/39/57/118/300)
  - Bus ID input with validation
  - Power factor slider (0.0-1.0) with numeric input
  - Load type toggle (Inductive/Capacitive)
  - Step size input (0.001-0.1)
  - Max scale slider (1.0-10.0)
  - Voltage limit slider (0.0-1.0)
  - Continuation toggle
  - Reset to defaults button
- Implement real-time parameter validation
- Connect parameter controls to backend API
- Create PV curve visualization component (`components/Visualization/PVCurvePlot.tsx`):
  - Integrate Plotly.js for interactive charts
  - Display voltage vs load curve
  - Mark nose point clearly
  - Color-code upper/lower branches
  - Show voltage limit line
  - Add hover tooltips (exact values)
  - Zoom and pan controls
  - Export PNG button (Plotly built-in)
- Display results panel:
  - Load margin (MW)
  - Nose point voltage (pu)
  - Convergence steps
  - System info (grid, bus, power factor)
  - Timestamp

**Deliverable:** Complete parameter controls with validation, and professional interactive PV curve plots with Plotly.js.

**Dependencies:** Sprint 2, Task 1

---

### Task 3: History & Settings Pages

**Action Items:**
- Build conversation history page (`pages/History.tsx`):
  - Simple list of past conversations
  - Show: title, timestamp, preview
  - Click to load conversation in chat
  - Delete button (with confirmation)
  - Basic client-side search/filter
- Build settings page (`pages/Settings.tsx`):
  - LLM configuration section:
    - Radio buttons: "OpenAI API Key" / "Local Ollama"
    - API key input (password field with show/hide)
    - Ollama URL input (default: http://localhost:11434)
    - Test connection button with status indicator
    - Save button
    - Clear instructions and security notice
  - Theme toggle (light/dark)
- Connect to backend settings API
- Implement encrypted API key storage
- Add loading states and error handling

**Deliverable:** Working history browser and settings page where users can configure their LLM provider.

**Dependencies:** Sprint 2, Task 2

---

## Sprint 3 Plan

**Sprint Goals (Week 3)** Deployment & Polish: Containerize application with Docker, deploy to Render/Railway, and polish UI for mobile responsiveness and production readiness.

### Task 1: Docker Containerization

**Action Items:**
- Create single `Dockerfile` (multi-stage build):
  - Stage 1: Build React frontend with Node.js
  - Stage 2: Setup Python backend
  - Stage 3: Final image with Nginx + FastAPI
    - Nginx serves React static files
    - Nginx proxies `/api/*` and `/ws` to FastAPI
    - Uvicorn runs FastAPI on port 8000
- Create `nginx.conf`:
  - Serve React from `/usr/share/nginx/html`
  - Proxy `/api/*` to `http://localhost:8000`
  - Proxy `/ws` to WebSocket backend
  - SPA routing (fallback to index.html)
- Create `docker-compose.yml` for local development:
  - Single service (web app)
  - Volume mounts:
    - SQLite database file
    - Generated PV curve plots
    - Agent vector database (read-only)
  - Environment variables
  - Port mapping (80:80)
- Create `.env.example` with required variables:
  ```
  JWT_SECRET=your-secret-key-here
  DATABASE_PATH=/data/web_app.db
  PLOTS_PATH=/data/plots
  ```
- Test full stack locally with `docker-compose up`

**Deliverable:** Fully containerized application running in single Docker container, tested locally with docker-compose. **Cost: $0**

**Dependencies:** Sprint 2

---

### Task 2: Deploy to Render or Railway

**Action Items:**
- Choose deployment platform (Render recommended)
- Create `render.yaml` deployment configuration:
  ```yaml
  services:
    - type: web
      name: pv-curve-agent
      env: docker
      dockerfilePath: ./web/Dockerfile
      envVars:
        - key: JWT_SECRET
          generateValue: true
      disk:
        name: pv-curve-data
        mountPath: /data
        sizeGB: 10
  ```
- Push code to GitHub repository
- Connect Render to GitHub repo
- Configure environment variables in Render dashboard
- Enable persistent disk for SQLite database and plots
- Deploy application (automatic on git push)
- Verify deployment:
  - Check health endpoint
  - Test WebSocket connection
  - Generate test PV curve
  - Verify HTTPS working (automatic with Render)
- Set up custom domain (optional)
- Configure automatic deployments on push to `main` branch

**Deliverable:** Live, publicly accessible web application at `https://your-app.onrender.com` with automatic HTTPS, persistent storage, and automatic deployments. **Cost: $0-7/month** (free tier or Hobby plan).

**Dependencies:** Sprint 3, Task 1

---

### Task 3: Mobile Polish & Production Readiness

**Action Items:**
- Implement responsive design for mobile:
  - Collapsible parameter panel (drawer on mobile)
  - Touch-friendly controls (larger buttons, tap targets)
  - Responsive plot sizing
  - Mobile-optimized chat layout
  - Hamburger menu for navigation
- Add helpful UI elements:
  - Loading indicators during agent processing
  - Error messages with clear guidance
  - Empty states (no conversations yet, no curves yet)
  - Tooltips for parameters (explain what each does)
  - Example prompts as clickable buttons
- Implement keyboard shortcuts:
  - Enter to send message
  - Shift+Enter for newline
  - Esc to close modals
- Add basic accessibility:
  - ARIA labels for screen readers
  - Keyboard navigation
  - Color contrast (WCAG AA)
- Cross-browser testing:
  - Test on Chrome, Firefox, Safari, Edge
  - Fix browser-specific issues
  - Verify WebSocket compatibility
- Set up basic monitoring:
  - Integrate Sentry free tier for error tracking
  - Set up UptimeRobot free tier for uptime monitoring
  - Configure email alerts for downtime
- Write basic documentation:
  - User guide (how to use the web app)
  - How to configure LLM (API key or Ollama)
  - Deployment guide (for future updates)
- Final testing:
  - Test with 5-10 concurrent users
  - Verify all features work on production
  - Test on mobile devices

**Deliverable:** Production-ready web application with mobile-responsive design, basic monitoring, and documentation. Ready for users.

**Dependencies:** Sprint 3, Task 2

---

## Technical Architecture

### Simple Single-Container Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Internet (HTTPS)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ (Automatic HTTPS via Render)
                         │
┌────────────────────────▼────────────────────────────────────┐
│              Render/Railway Platform                         │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Single Docker Container                        │  │
│  │                                                         │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │              Nginx (Port 80)                     │  │  │
│  │  │  - Serves React static files                     │  │  │
│  │  │  - Proxies /api/* to FastAPI                     │  │  │
│  │  │  - Proxies /ws to WebSocket                      │  │  │
│  │  └────────────────────┬────────────────────────────┘  │  │
│  │                       │                                 │  │
│  │  ┌────────────────────▼────────────────────────────┐  │  │
│  │  │         FastAPI Backend (Port 8000)             │  │  │
│  │  │  - REST API endpoints                           │  │  │
│  │  │  - WebSocket streaming                          │  │  │
│  │  │  - In-memory caching (Python dict)              │  │  │
│  │  └────────────────────┬────────────────────────────┘  │  │
│  │                       │                                 │  │
│  │  ┌────────────────────▼────────────────────────────┐  │  │
│  │  │         Agent Service (Wrapper)                 │  │  │
│  │  │  - Imports ../../agent/workflows/               │  │  │
│  │  │  - Uses user's OpenAI key or Ollama             │  │  │
│  │  └────────────────────┬────────────────────────────┘  │  │
│  │                       │                                 │  │
│  │  ┌────────────────────▼────────────────────────────┐  │  │
│  │  │    Existing Agent Workflow (Reused)             │  │  │
│  │  │  - LangGraph nodes (11 nodes)                   │  │  │
│  │  │  - pandapower (PV curve generation)             │  │  │
│  │  │  - Chroma vector DB (RAG)                       │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │                                                         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Persistent Disk (10GB)                         │  │
│  │  - SQLite database (web_app.db)                       │  │
│  │  - Generated PV curve plots (PNG files)               │  │
│  │  - Agent vector database (copied from ../agent/)      │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
└───────────────────────────────────────────────────────────────┘

External Services (Free Tier):
- Sentry (error tracking) - $0
- UptimeRobot (uptime monitoring) - $0
- GitHub (code hosting + Actions) - $0

User's Machine (Optional):
- Ollama (if user chooses local LLM) - $0
```

---

## Technology Stack

**Frontend:**
- React 18 + Vite
- TypeScript
- Tailwind CSS
- Plotly.js (visualization)
- Socket.io-client (WebSocket)
- Zustand (state management)
- React Router (navigation)
- Axios (HTTP client)

**Backend:**
- FastAPI (Python 3.12)
- SQLAlchemy (ORM)
- SQLite (database)
- Pydantic (validation)
- python-jose (JWT)
- cryptography (API key encryption)
- Socket.io (WebSocket)
- slowapi (rate limiting)

**Agent System (Existing - Reused):**
- LangGraph + LangChain
- OpenAI API (user's key) / Ollama (user's local)
- pandapower (power system simulation)
- Chroma (vector database for RAG)

**Infrastructure:**
- Render or Railway (managed platform)
- Docker (single container)
- Nginx (reverse proxy)
- Persistent disk (SQLite + plots)

**Monitoring (Free):**
- Sentry (error tracking)
- UptimeRobot (uptime monitoring)
- Platform built-in monitoring

---

## Complete Directory Structure

```
pv-curve-llm/
├── agent/                           # Existing CLI agent (DON'T TOUCH)
│   ├── core.py
│   ├── workflows/
│   │   └── workflow.py              # ← We import this!
│   ├── nodes/                       # All 11 agent nodes
│   │   ├── classify.py
│   │   ├── route.py
│   │   ├── planner.py
│   │   ├── question_general.py
│   │   ├── question_parameter.py
│   │   ├── parameter.py
│   │   ├── generation.py
│   │   ├── error_handler.py
│   │   ├── summary.py
│   │   ├── step_controller.py
│   │   └── advance_step.py
│   ├── state/
│   │   └── app_state.py
│   ├── schemas/
│   │   ├── inputs.py                # Parameter validation
│   │   ├── classifier.py
│   │   ├── planner.py
│   │   └── ...
│   ├── pv_curve/
│   │   └── pv_curve.py              # PV curve generation
│   ├── utils/
│   │   ├── display.py
│   │   └── common_utils.py
│   ├── vector_db/                   # RAG database
│   │   └── chroma.sqlite3
│   ├── data/                        # Training documents
│   ├── prompts.py
│   └── session.py
│
├── cli.py                           # Existing CLI (DON'T TOUCH)
├── main.py                          # Existing CLI entry (DON'T TOUCH)
├── requirements.txt                 # Existing CLI dependencies
│
└── web/                             # NEW: All web code (~25 files)
    │
    ├── backend/                     # FastAPI backend (12 files)
    │   │
    │   ├── api/
    │   │   ├── __init__.py
    │   │   └── v1/
    │   │       ├── __init__.py
    │   │       ├── chat.py          # POST /api/v1/chat + WebSocket /ws
    │   │       ├── parameters.py    # GET/POST /api/v1/parameters
    │   │       ├── history.py       # GET/DELETE /api/v1/history
    │   │       └── settings.py      # POST/GET /api/v1/settings/llm
    │   │
    │   ├── services/
    │   │   ├── __init__.py
    │   │   ├── agent_service.py     # Wraps ../../agent/workflows/workflow.py
    │   │   └── llm_service.py       # LLM provider abstraction
    │   │
    │   ├── database/
    │   │   ├── __init__.py
    │   │   ├── models.py            # SQLAlchemy models (4 tables)
    │   │   ├── database.py          # DB connection and session
    │   │   └── crud.py              # CRUD operations
    │   │
    │   ├── schemas/
    │   │   ├── __init__.py
    │   │   ├── chat.py              # Chat request/response models
    │   │   ├── parameters.py        # Parameter models
    │   │   └── settings.py          # Settings models
    │   │
    │   ├── core/
    │   │   ├── __init__.py
    │   │   ├── config.py            # Environment variables, settings
    │   │   └── security.py          # JWT, password hash, encryption
    │   │
    │   ├── utils/
    │   │   ├── __init__.py
    │   │   └── cache.py             # Simple in-memory cache
    │   │
    │   ├── tests/                   # Basic tests
    │   │   ├── __init__.py
    │   │   ├── conftest.py
    │   │   ├── test_chat.py
    │   │   └── test_parameters.py
    │   │
    │   ├── main.py                  # FastAPI app entry point
    │   ├── requirements.txt         # Backend dependencies
    │   └── .env.example             # Environment template
    │
    ├── frontend/                    # React frontend (13 files)
    │   │
    │   ├── public/
    │   │   └── index.html
    │   │
    │   ├── src/
    │   │   │
    │   │   ├── components/
    │   │   │   ├── Chat/
    │   │   │   │   ├── ChatInterface.tsx    # Main chat container
    │   │   │   │   ├── MessageBubble.tsx    # User/agent messages
    │   │   │   │   └── MessageInput.tsx     # Text input + send
    │   │   │   │
    │   │   │   ├── Parameters/
    │   │   │   │   └── ParameterPanel.tsx   # All parameter controls
    │   │   │   │
    │   │   │   ├── Visualization/
    │   │   │   │   └── PVCurvePlot.tsx      # Plotly chart
    │   │   │   │
    │   │   │   └── Common/
    │   │   │       ├── Button.tsx
    │   │   │       ├── Loading.tsx
    │   │   │       └── Header.tsx
    │   │   │
    │   │   ├── pages/
    │   │   │   ├── Chat.tsx         # Main chat page
    │   │   │   ├── History.tsx      # Conversation list
    │   │   │   └── Settings.tsx     # LLM configuration
    │   │   │
    │   │   ├── services/
    │   │   │   ├── api.ts           # Axios HTTP client
    │   │   │   └── websocket.ts     # Socket.io WebSocket
    │   │   │
    │   │   ├── store/
    │   │   │   └── appStore.ts      # Zustand global state
    │   │   │
    │   │   ├── types/
    │   │   │   └── index.ts         # TypeScript interfaces
    │   │   │
    │   │   ├── utils/
    │   │   │   └── helpers.ts       # Helper functions
    │   │   │
    │   │   ├── App.tsx              # Root component + routing
    │   │   ├── main.tsx             # Entry point
    │   │   └── index.css            # Tailwind imports
    │   │
    │   ├── package.json
    │   ├── vite.config.ts
    │   ├── tsconfig.json
    │   ├── tailwind.config.js
    │   └── postcss.config.js
    │
    ├── Dockerfile                   # Multi-stage (React + Python + Nginx)
    ├── docker-compose.yml           # Local development
    ├── nginx.conf                   # Nginx reverse proxy config
    ├── render.yaml                  # Render deployment config
    ├── .env.example                 # Environment variables template
    ├── .gitignore                   # Ignore .env, *.db, node_modules, etc.
    └── README.md                    # Web app documentation
```

**Total New Files:** ~25 files
**Lines of Code:** ~2,000-3,000 (mostly boilerplate and UI)

---

## Key Files Explained

### Backend Files (Python)

| File | Purpose | Lines |
|------|---------|-------|
| `main.py` | FastAPI app initialization, CORS, WebSocket setup | ~50 |
| `agent_service.py` | Wraps existing agent workflow, bridges web ↔ CLI agent | ~100 |
| `llm_service.py` | LLM provider abstraction (OpenAI/Ollama) | ~80 |
| `models.py` | SQLAlchemy database models (4 tables) | ~100 |
| `database.py` | SQLite connection and session management | ~30 |
| `crud.py` | Database CRUD operations | ~150 |
| `chat.py` | WebSocket endpoint + chat API | ~100 |
| `parameters.py` | Parameter GET/POST endpoints | ~50 |
| `history.py` | Conversation list/get/delete endpoints | ~60 |
| `settings.py` | LLM configuration endpoints | ~70 |
| `config.py` | Environment variables and settings | ~40 |
| `security.py` | JWT, password hashing, API key encryption | ~80 |

**Total Backend:** ~910 lines

### Frontend Files (React/TypeScript)

| File | Purpose | Lines |
|------|---------|-------|
| `App.tsx` | Root component with React Router | ~80 |
| `ChatInterface.tsx` | Main chat UI container | ~150 |
| `MessageBubble.tsx` | Individual message display | ~60 |
| `MessageInput.tsx` | Text input with send button | ~80 |
| `ParameterPanel.tsx` | All parameter controls (grid, bus, sliders, etc.) | ~250 |
| `PVCurvePlot.tsx` | Plotly.js interactive chart | ~120 |
| `Chat.tsx` (page) | Chat page layout | ~50 |
| `History.tsx` (page) | Conversation list page | ~100 |
| `Settings.tsx` (page) | LLM configuration page | ~120 |
| `api.ts` | Axios HTTP client for backend | ~100 |
| `websocket.ts` | Socket.io WebSocket manager | ~120 |
| `appStore.ts` | Zustand global state store | ~80 |

**Total Frontend:** ~1,310 lines

### Config Files

| File | Purpose | Lines |
|------|---------|-------|
| `Dockerfile` | Multi-stage build (React + Python + Nginx) | ~60 |
| `docker-compose.yml` | Local development setup | ~30 |
| `nginx.conf` | Reverse proxy configuration | ~40 |
| `render.yaml` | Render deployment config | ~20 |

**Total Config:** ~150 lines

**Grand Total:** ~2,370 lines of new code (manageable!)

---

## Database Schema

### SQLite Tables (4 tables)

```sql
-- Store user sessions
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,              -- UUID
    llm_config TEXT,                  -- Encrypted (API key or Ollama URL)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Store conversations
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,              -- UUID
    session_id TEXT,                  -- Foreign key to sessions
    title TEXT,                       -- Auto-generated from first message
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

-- Store messages in conversations
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT,             -- Foreign key to conversations
    role TEXT,                        -- 'user' or 'assistant'
    content TEXT,                     -- Message text
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

-- Store generated PV curves
CREATE TABLE pv_curves (
    id TEXT PRIMARY KEY,              -- UUID
    conversation_id TEXT,             -- Foreign key to conversations
    grid TEXT,                        -- e.g., 'ieee118'
    bus_id INTEGER,
    parameters TEXT,                  -- JSON (all input parameters)
    results TEXT,                     -- JSON (load_margin, nose_point, etc.)
    plot_path TEXT,                   -- Path to PNG file
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

-- Indexes for performance
CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_pv_curves_conversation ON pv_curves(conversation_id);
```

**Simple and efficient** - no complex relationships, just basic foreign keys.

---

## Data Flow Example

### User Request: "Generate PV curve for IEEE 118 bus 10"

```
1. User types in browser
   ↓
2. React (MessageInput.tsx)
   → websocket.ts.send(message)
   ↓
3. Backend WebSocket (chat.py) receives
   → agent_service.execute_turn(message)
   ↓
4. agent_service.py
   → Imports ../../agent/workflows/workflow.py
   → graph = create_graph(provider="openai", user_api_key="user's key")
   → graph.stream(message)
   ↓
5. Existing Agent Workflow executes (unchanged code)
   → Classifier node: "This is a generation request"
   → Router node: "Route to generation"
   → Generation node:
       → Calls ../../agent/pv_curve/pv_curve.py
       → pandapower runs power flow simulation
       → Generates plot with matplotlib
       → Returns results
   ↓
6. Results stream back through WebSocket
   → Each node update sent to frontend
   ↓
7. React (ChatInterface.tsx) receives updates
   → Displays "Classifier processing..."
   → Displays "Generation processing..."
   → PVCurvePlot.tsx renders Plotly chart
   ↓
8. User sees:
   - Real-time progress updates
   - Interactive plot (zoom, pan, hover)
   - Results (load margin, nose point)
   - AI analysis text
   ↓
9. Backend saves to SQLite
   → conversations table (message)
   → pv_curves table (results + plot path)
```

**Key Insight:** We're just adding HTTP/WebSocket wrapper. Agent logic is 100% reused!

---

## Dependencies

### Backend (`web/backend/requirements.txt`)

```txt
# Web framework
fastapi==0.110.0
uvicorn[standard]==0.27.0
python-socketio==5.11.0

# Database
sqlalchemy==2.0.27
alembic==1.13.1

# Validation
pydantic==2.6.1
pydantic-settings==2.1.0

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
cryptography==42.0.2

# Utilities
python-multipart==0.0.9
python-dotenv==1.0.1

# Rate limiting
slowapi==0.1.9

# Monitoring
sentry-sdk[fastapi]==1.40.0

# NOTE: Agent dependencies (langchain, langgraph, pandapower, etc.)
# are already installed from parent requirements.txt
# We import them from ../../agent/
```

### Frontend (`web/frontend/package.json`)

```json
{
  "name": "pv-curve-web",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.22.0",
    "zustand": "^4.5.0",
    "axios": "^1.6.7",
    "socket.io-client": "^4.7.4",
    "plotly.js": "^2.29.1",
    "react-plotly.js": "^2.6.0",
    "react-markdown": "^9.0.1"
  },
  "devDependencies": {
    "@types/react": "^18.2.55",
    "@types/react-dom": "^18.2.19",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.1.0",
    "tailwindcss": "^3.4.1",
    "postcss": "^8.4.35",
    "autoprefixer": "^10.4.17"
  }
}
```

**Total Dependencies:** ~20 packages (minimal, no bloat)

---

## Cost Breakdown

### Phase 1: Initial Launch (5-10 users)

| Service | Configuration | Cost |
|---------|--------------|------|
| **Render Free Tier** | 750 hours/month (enough for 24/7) | $0 |
| **OR Render Hobby** | 512MB RAM, 0.5 CPU, 10GB disk | $7/month |
| **SQLite** | File-based, included in disk | $0 |
| **Monitoring** | Sentry Free (5K errors) + UptimeRobot Free | $0 |
| **CI/CD** | GitHub Actions (free for public repos) | $0 |
| **LLM** | User-provided (OpenAI key or Ollama) | $0 |
| **Domain** | Optional custom domain | $0-12/year |

**Total: $0-7/month**

**User's LLM Cost (their side):**
- OpenAI API: ~$0.01-0.10 per PV curve generation
- Local Ollama: $0 (runs on their machine)

### Phase 2: Scaling to 50 Users (Future)

| Service | Cost |
|---------|------|
| Render Standard (2GB RAM, 1 CPU) | $25/month |
| Managed PostgreSQL | $7-15/month |
| Redis (Upstash free tier) | $0 |

**Total: $32-40/month**

### Phase 3: Scaling to 500 Users (Future)

Migrate to AWS with full infrastructure: $190-320/month

---

## Engineering Principles

### Hard Constraints

1. **No Modification to Existing CLI Code**: All web functionality under `/web` directory
2. **Feature Parity**: Web interface must support ALL CLI features
3. **Budget Constraint**: $0-10/month initially
4. **Simplicity First**: Simplest solution that works
5. **User-Provided LLM**: Users bring their own compute

### Key Principles

1. **Make it work first** - Don't worry about perfect code
2. **Reuse existing agent** - Import and wrap, don't rewrite
3. **Keep it simple** - Single container, single database file
4. **Deploy early** - Get it online by week 3
5. **Iterate based on feedback** - Add features users actually want
6. **Document scaling triggers** - Know when to upgrade each component

---

## Scaling Triggers (When to Upgrade)

### Add PostgreSQL
- ✅ When: 50+ total users OR 10+ concurrent users
- ✅ When: Database file size > 1GB
- ✅ When: Experiencing SQLite lock contention
- **Action:** Migrate to Render/Railway managed PostgreSQL ($7-15/month)

### Add Redis
- ✅ When: 20+ concurrent users
- ✅ When: Need distributed session storage (multiple backend instances)
- ✅ When: Cache hit rate would significantly improve performance
- **Action:** Add Upstash Redis free tier, then upgrade

### Upgrade Hosting Plan
- ✅ When: CPU/memory consistently >80%
- ✅ When: Response times >2 seconds
- ✅ When: Platform limits reached
- **Action:** Upgrade Render/Railway plan ($7 → $25/month)

### Migrate to AWS
- ✅ When: Need auto-scaling (traffic spikes)
- ✅ When: Need multi-region deployment
- ✅ When: Render/Railway limits reached
- ✅ When: Budget allows $100+/month
- **Action:** Follow detailed plan in `WEB_DEPLOYMENT_SPRINT_PLAN.md`

---

## What Gets Deferred (Post-Launch)

### Features to Add When Users Request

⏸️ **User Accounts/Login** - Everyone is guest initially (simpler)
⏸️ **Advanced Comparison** - Multi-curve side-by-side (just one curve for now)
⏸️ **Batch Generation** - Generate multiple curves in parallel
⏸️ **Parameter Sweeps** - Automated sensitivity analysis
⏸️ **Advanced Export** - PDF/CSV/SVG (just PNG for now)
⏸️ **Parameter Presets** - Save/load parameter configurations
⏸️ **Search in History** - Just list conversations for now
⏸️ **Advanced Monitoring** - CloudWatch dashboards (just Sentry for now)

### Infrastructure to Add When Scaling

⏸️ **PostgreSQL** - When SQLite is too slow (50+ users)
⏸️ **Redis** - When need caching/distributed sessions (20+ users)
⏸️ **CDN** - When have global users (high latency)
⏸️ **Load Balancer** - When need multiple backend instances
⏸️ **AWS Migration** - When need enterprise features
⏸️ **CI/CD Automation** - Full auto-deploy (manual initially)

---

## Next Steps

1. **Review and approve this simplified plan**
2. **I'll create the initial `/web` directory structure**
3. **We'll build Sprint 1 step-by-step** (I'll explain each file as we create it)
4. **You'll have a working website in 3 weeks**

Ready to start Sprint 1? 🚀
