# PV Curve Agent — Frontend (Sprint 2)

React + Vite + TypeScript web interface for the PV Curve LangGraph agent.

## Quick Start

```bash
# 1. Install dependencies (first time only)
npm install

# 2. Start dev server  (hot reload, proxies to backend at :8000)
npm run dev
# → Opens at http://localhost:5173

# 3. Build for production
npm run build
```

## Running the Full Stack

You need to start the FastAPI backend first:

```bash
# From pv-curve-llm/ root
uvicorn web.backend.main:app --reload --host 0.0.0.0 --port 8000
```

Then the frontend dev server:

```bash
cd web/frontend
npm run dev
```

Open **http://localhost:5173** — Vite automatically proxies:
- `/api/*` → `http://localhost:8000`
- `/ws`   → `ws://localhost:8000`
- `/plots/*` → `http://localhost:8000`

## Project Structure

```
src/
├── components/
│   ├── Chat/           # MessageBubble, MessageInput, ChatInterface
│   ├── Parameters/     # ParameterPanel (all 8 controls + validation)
│   ├── Visualization/  # PVCurvePlot (Plotly.js interactive chart)
│   └── Common/         # Header, Loading, Modal
├── pages/
│   ├── Chat.tsx         # Main chat + sidebar layout
│   ├── History.tsx      # Conversation history browser
│   └── Settings.tsx     # LLM configuration + theme
├── services/
│   ├── api.ts           # Axios REST client for all backend endpoints
│   └── websocket.ts     # WebSocket singleton with auto-reconnect
├── store/
│   └── appStore.ts      # Zustand global state (persists session + theme)
├── types/
│   └── index.ts         # TypeScript interfaces (mirrors backend schemas)
└── utils/
    └── helpers.ts       # formatGrid, debounce, formatDateTime
```

## Key Design Decisions

1. **Single WebSocket** — one persistent connection per browser session; auto-reconnects with exponential back-off.
2. **Optimistic UI** — user message bubble appears immediately before server confirms.
3. **Streaming responses** — each agent node update appends text to the same assistant bubble.
4. **Draft state in ParameterPanel** — edits are local until "Apply" is clicked; prevents spamming the API.
5. **Zustand persist** — only `sessionId`, `llmConfig`, and `isDark` are persisted to `localStorage`; messages are session-only.
