# Web Deployment Sprint Plan (Budget-Optimized)
# PV Curve Agent - From CLI to Cloud-Based Web Application

## 🎯 Executive Summary

**Goal:** Transform CLI-based PV Curve Agent into an easy-to-use web application accessible from any browser, deployed on the cloud with minimal cost.

**Target Users:** 5-10 concurrent users initially, scalable to 500+ users in future
**Timeline:** 6 sprints (6 weeks) to production launch
**Estimated Monthly Cost:** $5-8/month (or $0 with free tiers)

---

## 📊 Quick Reference: What Changes vs Original Plan

| Aspect | Original Plan | Budget-Optimized Plan | Savings |
|--------|---------------|----------------------|---------|
| **Database** | PostgreSQL (RDS) | SQLite (file-based) | $30/month |
| **Caching** | Redis (ElastiCache) | In-memory (Python dict) | $15/month |
| **Deployment** | AWS ECS Fargate | Render/Railway | $43/month |
| **LLM Hosting** | Server-side (OpenAI/Ollama GPU) | User-provided | $50-320/month |
| **CDN** | CloudFront | Direct serving | $10/month |
| **Load Balancer** | AWS ALB | None (single server) | $20/month |
| **Monitoring** | CloudWatch + Sentry Paid | Sentry Free + UptimeRobot | $20/month |
| **Infrastructure** | Terraform/CDK | Manual setup | $0 (time saved) |
| **Timeline** | 8 sprints (8 weeks) | 6 sprints (6 weeks) | 2 weeks |
| **Total Cost** | $322-472/month | $5-8/month | **$314-464/month** |

### What's Deferred (Not Removed, Just Post-Launch)
- Advanced comparison dashboard → Basic comparison included
- Batch generation & parameter sweeps → Add when users request
- Advanced export formats (PDF, CSV, SVG) → PNG export included
- Job queue system (Celery) → FastAPI BackgroundTasks sufficient for now
- Parameter presets → Add when users request

---

### Key Decisions (Budget-Optimized)

✅ **SQLite** (not PostgreSQL) - $0 vs $30/month, migrate when 50+ users
✅ **No Redis** - In-memory caching sufficient for 5-10 users, add when 20+ users
✅ **Render/Railway** (not AWS ECS) - $7/month vs $50/month, simpler deployment
✅ **No CDN** - Direct serving sufficient for single-region users
✅ **No Load Balancer** - Single server sufficient for 5-10 users
✅ **User-provided LLM** - Users bring their own OpenAI key or local Ollama, $0 server cost
✅ **Free Monitoring** - Sentry + UptimeRobot free tiers
✅ **Simple CI/CD** - GitHub Actions with manual approval
✅ **No Infrastructure as Code** - Manual platform setup initially, add Terraform when scaling

### Deferred Features (Add Post-Launch Based on Demand)

⏸️ Advanced comparison dashboard (keep basic comparison)
⏸️ Batch generation and parameter sweeps
⏸️ Advanced export formats (PDF, CSV) - keep PNG only
⏸️ Job queue system (Celery + Redis)
⏸️ Parameter presets

---

## 📅 Sprint Breakdown at a Glance

| Sprint | Duration | Focus Area | Key Deliverables | Cost |
|--------|----------|------------|------------------|------|
| **1** | Week 1 | Backend API | FastAPI + WebSocket + SQLite + Auth | $0 |
| **2** | Week 2 | Frontend UI | React + Chat + Parameters + Plotly | $0 |
| **3** | Week 3 | Deployment | Docker + Render/Railway + LLM Config | $0-7/month |
| **4** | Week 4 | Features | History + Settings + Mobile Polish | $0 |
| **5** | Week 5 | DevOps | CI/CD + Monitoring + Optimization | $0 |
| **6** | Week 6 | Launch | Docs + Testing + Production Launch | $0 |

**Total Development Time:** 6 weeks
**Total Monthly Operating Cost:** $5-8/month (or $0 with free tiers)

### What You Get in 6 Weeks

✅ Modern React web interface with real-time chat
✅ All CLI features accessible through web UI
✅ Interactive PV curve visualization with Plotly.js
✅ Optional user authentication (guest or registered)
✅ Conversation history and basic comparison
✅ WebSocket streaming for real-time updates
✅ Deployed on cloud with automatic HTTPS
✅ User provides their own LLM (OpenAI API key or local Ollama)
✅ Mobile-responsive design
✅ Automated testing and deployment
✅ Basic monitoring and error tracking

---

## 💡 Concrete Example: User Journey

### CLI Experience (Current)
```bash
$ python main.py
Which model provider would you like to use? (openai or ollama): openai

Current Parameters:
  Grid: ieee39
  Bus ID: 5
  Power Factor: 0.95
  ...

Message: Generate PV curve for IEEE 118 bus 10

[Agent processes...]
PV curve generated for IEEE118 system (Bus 10)
Plot saved to generated/pv_curve_ieee118_20260314_143025.png
...
```

### Web Experience (After Sprint 6)

**Step 1: Access Website**
- User visits: `https://your-app.onrender.com` (or custom domain)
- Landing page with two options:
  - "Continue as Guest" button
  - "Login / Sign Up" button

**Step 2: Configure LLM (First Time)**
- User clicks "Continue as Guest"
- Prompted: "To use this app, you need to provide your own LLM:"
  - Option 1: "I have an OpenAI API key" → Enter key → Test connection → Save
  - Option 2: "I have Ollama running locally" → Enter URL (http://localhost:11434) → Test → Save
- Configuration saved (encrypted in database)

**Step 3: Chat Interface**
- Clean three-panel layout:
  - **Left**: Conversation list (collapsible on mobile)
  - **Center**: Chat messages with streaming responses
  - **Right**: Parameter controls (collapsible sidebar)
- Current parameters displayed in right panel
- Example prompts shown: "Generate PV curve for IEEE 39", "What is voltage stability?"

**Step 4: Generate PV Curve**
- User types: "Generate PV curve for IEEE 118 bus 10"
- Real-time updates stream in:
  - "🔄 Classifier: Analyzing your request..."
  - "🔄 Router: Routing to generation agent..."
  - "🔄 Generation: Running power flow simulation..."
  - "✅ PV curve generated!"
- Interactive Plotly plot appears in chat:
  - Hover to see exact values
  - Zoom and pan
  - Click "Export PNG" to download
- Results shown:
  - Load Margin: 523.4 MW
  - Nose Point Voltage: 0.82 pu
  - Convergence Steps: 187
- AI analysis: "The IEEE 118 system demonstrates robust voltage stability..."

**Step 5: Compare with Previous**
- User clicks "Compare with previous curve"
- Overlay plot shows both IEEE 39 and IEEE 118 curves
- Side-by-side metrics comparison

**Step 6: View History**
- User clicks "History" in navigation
- List of all past conversations
- Click any conversation to reload it in chat
- Search bar to find specific conversations

**Total Time: 2-3 minutes** from landing page to generated PV curve with analysis

---

## Sprint 1 Plan

**Sprint Goals (3/14 - 3/20)** Backend API & Core Web Infrastructure: Transform the CLI-based agent into a web-accessible API with FastAPI, implement WebSocket streaming for real-time updates, and establish the foundational web architecture under `/web` directory without modifying existing CLI functionality.

### Task 1: FastAPI Backend Setup & API Architecture

**Action Items:**
- Create `/web/backend/` directory structure with simple, modular organization:
  ```
  /web/backend/
    ├── api/          # API routes
    ├── services/     # Business logic (agent integration)
    ├── database/     # Database models and CRUD
    ├── core/         # Config and dependencies
    ├── tests/        # Test files
    └── main.py       # FastAPI app entry
  ```
- Initialize FastAPI application with CORS configuration for frontend communication
- Implement WebSocket endpoint (`/ws`) for real-time streaming of agent responses and PV curve generation progress
- Create REST API endpoints:
  - `POST /api/v1/chat` - Send user messages and receive agent responses
  - `GET /api/v1/parameters` - Retrieve current simulation parameters
  - `POST /api/v1/parameters` - Update simulation parameters
  - `POST /api/v1/generate` - Trigger PV curve generation
  - `GET /api/v1/systems` - List available IEEE test systems
- Integrate existing agent workflow (import from `../../agent/workflows/workflow.py`) as a service layer
- Implement simple in-memory session storage (Python dict with session cleanup) - sufficient for 5-10 users
- Add request/response Pydantic models for API validation
- Set up basic error handling middleware

**Deliverable:** A functional FastAPI backend running on `localhost:8000` with Swagger documentation at `/docs`, capable of executing the full agent workflow via HTTP/WebSocket and streaming real-time updates.

**Dependencies:** None

**Testing Strategy:**
- Create `/web/backend/tests/` directory
- Write pytest test cases for core API endpoints
- Test WebSocket connection and message streaming
- Test integration with existing agent workflow

---

### Task 2: Database Layer & Session Persistence (SQLite)

**Action Items:**
- Set up SQLAlchemy ORM with SQLite database (`/web/backend/web_app.db`)
- Design simple database schema:
  - `users` table: id, username, email, hashed_password, created_at, is_guest
  - `sessions` table: id, user_id, session_data (JSON), created_at, updated_at
  - `conversations` table: id, session_id, messages (JSON), parameters (JSON), timestamp
  - `pv_curves` table: id, session_id, grid, bus_id, parameters (JSON), results (JSON), plot_path, created_at
- Implement database models with SQLAlchemy
- Create simple database initialization script (no Alembic for now - add when migrating to PostgreSQL)
- Build session manager service that:
  - Creates new sessions for guest users (UUID-based)
  - Persists conversation history to database
  - Stores generated PV curve metadata and results
  - Retrieves historical sessions for logged-in users
- Implement basic CRUD operations
- **Migration Path Documented**: Add comments in code for future PostgreSQL migration (connection string change, add Alembic)

**Deliverable:** A working SQLite database (single file, no separate server needed) with all tables created, session persistence working, and ability to store/retrieve conversation history and PV curve results. **Cost: $0**

**Dependencies:** Task 1

**Testing Strategy:**
- Unit tests for database models
- Integration tests for session CRUD operations
- Test guest session creation and persistence

---

### Task 3: Authentication System (Optional Login)

**Action Items:**
- Implement simple JWT-based authentication system
- Create authentication endpoints:
  - `POST /api/v1/auth/register` - User registration
  - `POST /api/v1/auth/login` - User login (returns JWT token)
  - `POST /api/v1/auth/guest` - Create guest session (no registration)
  - `GET /api/v1/auth/me` - Get current user info
- Implement password hashing with bcrypt
- Add JWT token generation and validation middleware (using python-jose)
- Create authentication dependencies for protected routes
- Guest users: Limited history retention (7 days), no cross-device access
- Registered users: Unlimited history, cross-device access
- **Keep it simple**: No token refresh, no token blacklist initially (add when scaling)

**Deliverable:** A simple authentication system where users can optionally register/login or continue as guests, with JWT tokens for session management.

**Dependencies:** Task 2

**Testing Strategy:**
- Test user registration and login flows
- Verify JWT token generation and validation
- Test guest session creation

---

## Sprint 2 Plan

**Sprint Goals (3/21 - 3/27)** Frontend Web Application & Interactive UI: Build a modern, responsive React-based web interface with chat interface, interactive parameter controls, and real-time PV curve visualization using Plotly.js.

### Task 1: React Frontend Foundation & Project Setup

**Action Items:**
- Create `/web/frontend/` directory and initialize React + Vite project with TypeScript
- Set up simple project structure:
  ```
  /web/frontend/src/
    ├── components/   # Reusable UI components
    ├── pages/        # Main pages (Landing, Chat, History, Settings)
    ├── services/     # API client and WebSocket
    ├── hooks/        # Custom React hooks
    ├── store/        # Zustand store (simple global state)
    ├── types/        # TypeScript types
    └── utils/        # Helper functions
  ```
- Install essential dependencies only:
  - React Router (navigation)
  - Zustand (lightweight state management - simpler than Redux)
  - Tailwind CSS (styling)
  - Plotly.js (interactive charts)
  - Socket.io-client (WebSocket)
  - Axios (HTTP client)
- Implement simple API client service (`services/api.ts`)
- Create WebSocket manager for real-time agent streaming (`services/websocket.ts`)
- Set up basic routing:
  - `/` - Landing page with auth options
  - `/chat` - Main chat interface
  - `/history` - Simple conversation history list
  - `/settings` - User settings (LLM provider, API key)
- Implement authentication store with Zustand (simpler than Context API)

**Deliverable:** A working React application with routing, API integration, WebSocket connection, and authentication flow (login/register/guest).

**Dependencies:** Sprint 1

**Testing Strategy:**
- Manual testing of core flows (no extensive test suite initially)
- Test API client methods
- Test WebSocket connection handling

---

### Task 2: Chat Interface & Conversational UI

**Action Items:**
- Build main chat interface with simple two-panel layout:
  - Main panel: Chat conversation (full width on mobile)
  - Right panel: Parameter controls (collapsible sidebar)
- Implement chat message components:
  - User message bubbles
  - Agent response bubbles with markdown rendering (use `react-markdown`)
  - System messages (parameter updates, errors)
  - Simple loading indicator during agent processing
- Create message input component:
  - Text input with auto-resize (textarea)
  - Send button with loading state
  - Keyboard shortcuts (Enter to send, Shift+Enter for newline)
- Implement WebSocket streaming integration:
  - Connect to backend WebSocket on component mount
  - Stream agent responses in real-time as they're generated
  - Display progress updates during PV curve generation
  - Auto-reconnect on disconnect
- Add basic conversation management:
  - Create new conversation button
  - Load previous conversations from history
  - Auto-save conversations to backend
- Add example prompts as clickable buttons:
  - "Generate PV curve for IEEE 39"
  - "What is voltage stability?"
  - "Change grid to IEEE 118"

**Deliverable:** A functional chat interface with real-time streaming, message history, and intuitive UX that mirrors the CLI experience but with modern web UI.

**Dependencies:** Sprint 2, Task 1

**Testing Strategy:**
- Manual testing of message flows
- Test WebSocket streaming and reconnection
- Test conversation loading and saving

---

### Task 3: Interactive Parameter Controls & Basic Visualization

**Action Items:**
- Build parameter control panel component (right sidebar):
  - Grid system dropdown (IEEE 14/24/30/39/57/118/300)
  - Bus ID input with validation
  - Power factor slider with numeric input
  - Load type toggle (Inductive / Capacitive)
  - Step size input
  - Max scale slider
  - Voltage limit slider
  - Continuation mode toggle
  - Collapsible "Advanced" section: Contingency lines, Generator voltage setpoints (simple JSON input for now)
- Implement real-time parameter validation with visual feedback
- Add "Reset to defaults" button
- Create PV curve visualization component using Plotly.js:
  - Interactive plot with zoom, pan, hover tooltips
  - Clearly marked nose point
  - Upper and lower branch distinction (different colors)
  - Voltage limit line indicator
  - Simple PNG export button (using Plotly's built-in export)
  - Fullscreen mode
- Implement results display panel:
  - Load margin (MW)
  - Nose point voltage (pu)
  - Convergence steps count
  - System information (grid, bus, power factor)
  - Timestamp of generation
- **Defer to post-launch**: Advanced comparison dashboard, batch generation, parameter sweeps, advanced export formats

**Deliverable:** A clean UI with interactive parameter controls, real-time validation, and professional interactive PV curve visualizations with Plotly.js. Basic functionality only - no advanced comparison features yet.

**Dependencies:** Sprint 2, Task 2

**Testing Strategy:**
- Test parameter validation logic
- Test plot rendering with sample data
- Test plot interactivity (zoom, pan, hover)
- Test basic PNG export

---

## Sprint 3 Plan

**Sprint Goals (3/28 - 4/3)** Containerization & Simple Deployment: Containerize the application stack with Docker Compose and deploy to a simple, cost-effective platform (Render or Railway) for easy management and low cost.

### Task 1: Docker Containerization (Simple Single-Server Setup)

**Action Items:**
- Create `/web/Dockerfile` (single file for both frontend and backend):
  - Multi-stage build:
    - Stage 1: Build React frontend (Node.js)
    - Stage 2: Setup Python backend (Python 3.12)
    - Stage 3: Final image with nginx serving frontend + uvicorn running backend
  - Copy agent code from parent directory
  - Expose ports 80 (nginx) and 8000 (FastAPI)
  - Simple health check endpoint
- Create `/web/docker-compose.yml` for local development and production:
  - Single service running both frontend and backend
  - SQLite database (file volume mount)
  - Environment variable configuration
  - Volume mounts for:
    - SQLite database file
    - Generated PV curve plots
    - Agent vector database (read-only)
- Create `/web/.env.example` with required environment variables:
  ```
  JWT_SECRET=your-secret-key
  OPENAI_API_KEY=optional-system-key
  OLLAMA_BASE_URL=http://localhost:11434
  ```
- Create simple nginx configuration:
  - Serve React static files
  - Proxy `/api/*` and `/ws` to FastAPI backend
  - SPA routing (fallback to index.html)
- Implement graceful shutdown handling in backend

**Deliverable:** A simple, single-container application that can be launched locally with `docker-compose up` and deployed to any Docker-compatible platform. **Simplified architecture reduces complexity and cost.**

**Dependencies:** Sprint 2

**Testing Strategy:**
- Test local Docker Compose deployment
- Verify nginx routing to backend
- Test volume mounts for database and plots
- Test production build process

---

### Task 2: LLM Provider Selection & User API Key Support

**Action Items:**
- Implement LLM provider selection in backend:
  - Create `/web/backend/services/llm_service.py` with provider abstraction
  - Support three modes:
    1. **User's OpenAI API Key**: User provides their own key (stored encrypted in DB)
    2. **User's Local Ollama**: User runs Ollama on their own machine, provides URL
    3. **System OpenAI** (optional): Admin can configure system-wide key for guests
- Implement API key management endpoints:
  - `POST /api/v1/user/llm-config` - Save user's LLM configuration (API key or Ollama URL)
  - `GET /api/v1/user/llm-config` - Get current config (masked)
  - `DELETE /api/v1/user/llm-config` - Remove config
  - `POST /api/v1/user/llm-config/test` - Test API key or Ollama connection
- Encrypt user API keys in database using Fernet (cryptography library)
- Add LLM provider selection to frontend settings page:
  - Radio buttons: "My OpenAI API Key" / "My Local Ollama" / "System Default (if available)"
  - API key input with show/hide toggle
  - Ollama URL input (default: http://localhost:11434)
  - Test connection button
  - Save button
  - Clear instructions and warnings about key security
- Update agent service to use user's LLM configuration per session
- **Cost Benefit**: No server-side LLM costs - users bring their own compute

**Deliverable:** A flexible LLM provider system where users can use their own OpenAI API key or their own local Ollama instance, eliminating server-side LLM costs.

**Dependencies:** Sprint 3, Task 1

**Testing Strategy:**
- Test API key encryption and decryption
- Test API key validation
- Test Ollama connection validation
- Test provider switching in chat
- Verify user's LLM config is used correctly

---

### Task 3: Deploy to Render or Railway (Simple Cloud Deployment)

**Action Items:**
- Choose deployment platform:
  - **Render** (recommended): Simple, managed, good free tier
  - **Railway** (alternative): Developer-friendly, generous free tier
- Set up Render deployment (if chosen):
  - Create `render.yaml` blueprint file:
    ```yaml
    services:
      - type: web
        name: pv-curve-agent
        env: docker
        dockerfilePath: ./web/Dockerfile
        envVars:
          - key: JWT_SECRET
            generateValue: true
          - key: DATABASE_PATH
            value: /data/web_app.db
        disk:
          name: pv-curve-data
          mountPath: /data
          sizeGB: 10
    ```
  - Connect GitHub repository to Render
  - Configure environment variables in Render dashboard
  - Set up persistent disk for SQLite database and plots
  - Configure custom domain (optional)
  - Enable automatic HTTPS (free with Render)
- Or set up Railway deployment (if chosen):
  - Create `railway.json` or use Railway CLI
  - Connect GitHub repository
  - Configure environment variables
  - Set up volume for persistent storage
  - Enable automatic deployments on git push
- Create simple deployment script (`/web/scripts/deploy.sh`):
  - Build Docker image locally (for testing)
  - Push to platform (or auto-deploy via git push)
- Configure automatic deployments:
  - Deploy on push to `main` branch
  - Show deployment status in GitHub
- Set up basic monitoring:
  - Use platform's built-in monitoring (free)
  - Set up uptime monitoring (UptimeRobot free tier)
  - Configure email alerts for downtime

**Deliverable:** A live, publicly accessible web application deployed on Render or Railway with automatic HTTPS, persistent storage for database and plots, and automatic deployments on git push. **Cost: $0-20/month** (Render free tier or Hobby plan $7/month, Railway free tier or Hobby $5/month).

**Dependencies:** Sprint 3, Task 2

**Testing Strategy:**
- Test deployment process end-to-end
- Verify HTTPS and SSL certificate
- Test persistent storage (database and plots survive restart)
- Test automatic deployment on git push
- Verify application works on public URL
- Test with 5-10 concurrent users

---

## Sprint 4 Plan

**Sprint Goals (4/4 - 4/10)** History, Settings & User Experience: Implement conversation history browser, user profile and settings management, and polish the overall user experience.

### Task 1: Simple History Browser & Basic Comparison

**Action Items:**
- Build conversation history page (`/web/frontend/src/pages/History.tsx`):
  - Simple list view of past conversations:
    - Conversation title (auto-generated from first message)
    - Timestamp (created date)
    - Preview of last message (first 100 chars)
    - Number of PV curves generated
  - Basic search by title/content (client-side filtering)
  - Simple date sorting (newest first)
  - Click to load conversation in chat interface
  - Delete conversation button (with confirmation)
- Add basic comparison feature in chat:
  - "Compare with previous" button when viewing a PV curve
  - Simple overlay mode (show current + one previous curve on same plot)
  - Basic metrics comparison (load margin, nose point voltage)
  - No advanced multi-curve comparison dashboard (defer to post-launch)
- Backend endpoints:
  - `GET /api/v1/history` - List user's conversations (simple, no pagination initially)
  - `GET /api/v1/history/{id}` - Get specific conversation
  - `DELETE /api/v1/history/{id}` - Delete conversation
- **Deferred to post-launch**: Advanced comparison dashboard, multi-curve selection, PDF export, plot gallery

**Deliverable:** A simple history browser with search, and basic comparison feature (current vs previous curve). Keeps implementation simple while providing core functionality.

**Dependencies:** Sprint 3

**Testing Strategy:**
- Test history loading
- Test search functionality
- Test basic comparison overlay
- Test conversation deletion

---

### Task 2: User Profile & Settings Management

**Action Items:**
- Create simple settings page (`/web/frontend/src/pages/Settings.tsx`):
  - **LLM Configuration Section**:
    - Radio buttons: "My OpenAI API Key" / "My Local Ollama"
    - OpenAI API key input (password field with show/hide)
    - Ollama URL input (default: http://localhost:11434)
    - Test connection button with status indicator
    - Save button
    - Clear instructions: "Your API key is encrypted and stored securely. It's never shared."
  - **Profile Section** (for registered users):
    - Display username and email
    - Change password form (simple)
    - Delete account button (with confirmation)
  - **UI Preferences** (simple):
    - Theme toggle (light / dark)
    - No complex customization initially
- Implement backend endpoints:
  - `GET /api/v1/user/profile` - Get user profile
  - `PUT /api/v1/user/profile` - Update profile (username, email)
  - `POST /api/v1/user/change-password` - Change password
  - `DELETE /api/v1/user/account` - Delete account (cascade delete all data)
  - Already implemented in Task 2: LLM config endpoints
- Implement secure API key storage (encrypted in database using Fernet)
- Add simple usage statistics on profile:
  - Total conversations
  - Total PV curves generated
  - Account created date
- **Deferred to post-launch**: Parameter presets, advanced UI customization, notification preferences

**Deliverable:** Simple user profile and settings page with LLM provider configuration, basic profile management, and account deletion. Focus on essential features only.

**Dependencies:** Sprint 4, Task 1

**Testing Strategy:**
- Test profile update functionality
- Test password change
- Test API key encryption and storage
- Test account deletion

---

### Task 3: UI Polish & Mobile Responsiveness

**Action Items:**
- Polish the user interface:
  - Improve error messages and user guidance
  - Add helpful tooltips for parameters (explain what each parameter does)
  - Enhance loading states and progress indicators
  - Add empty states (no conversations yet, no PV curves yet)
  - Improve visual hierarchy and spacing
- Implement responsive design for mobile:
  - Mobile-first CSS with Tailwind
  - Collapsible parameter panel on mobile (drawer or bottom sheet)
  - Touch-friendly controls (larger buttons, swipe gestures)
  - Responsive plot sizing
  - Hamburger menu for navigation
- Add keyboard shortcuts:
  - `/` to focus message input
  - `Ctrl/Cmd + K` to create new conversation
  - `Esc` to close modals
- Improve accessibility:
  - Add ARIA labels for screen readers
  - Keyboard navigation support
  - Focus management in modals
  - Color contrast compliance (WCAG AA)
- Add helpful onboarding:
  - First-time user tutorial (simple 3-step overlay)
  - Example prompts prominently displayed
  - Inline help text for complex features
- Cross-browser testing:
  - Test on Chrome, Firefox, Safari, Edge
  - Fix any browser-specific issues
  - Verify WebSocket compatibility

**Deliverable:** A polished, mobile-responsive web application with good UX, accessibility features, keyboard shortcuts, and cross-browser compatibility.

**Dependencies:** Sprint 4, Task 2

**Testing Strategy:**
- Test on mobile devices (iOS Safari, Android Chrome)
- Test keyboard shortcuts
- Test accessibility with screen reader
- Cross-browser testing

---

## Sprint 5 Plan

**Sprint Goals (4/11 - 4/17)** CI/CD, Monitoring & Basic Optimization: Set up automated testing and deployment pipeline, implement basic monitoring with free tools, and optimize performance for current scale (5-10 users).

### Task 1: Basic Performance Optimization (No Redis)

**Action Items:**
- Backend optimizations:
  - Implement simple in-memory caching for:
    - IEEE system metadata (static data)
    - Recent agent responses (LRU cache, max 100 items)
  - Add response compression (gzip) in FastAPI
  - Add basic rate limiting using slowapi (simple, no Redis needed)
    - 100 requests per minute per IP
    - 20 PV curve generations per hour per user
  - Optimize SQLite queries:
    - Add indexes on frequently queried columns
    - Use connection pooling (SQLite supports this)
  - Use FastAPI BackgroundTasks for cleanup jobs (no Celery needed for 5-10 users)
- Frontend optimizations:
  - Enable Vite code splitting (automatic)
  - Lazy load heavy components (Plotly, History page)
  - Optimize bundle size (Vite does this by default)
  - Add simple image lazy loading for plot thumbnails
- WebSocket optimization:
  - Implement reconnection with exponential backoff
  - Add heartbeat/ping-pong for connection health
  - Simple connection pooling (FastAPI handles this)
- **No CDN needed**: Static files served directly from nginx (sufficient for 5-10 users)
- **No Redis needed**: In-memory caching sufficient for current scale
- **Scaling Path Documented**: Add comments in code for when to add Redis (20+ users) and CDN (global users)

**Deliverable:** A reasonably optimized application using simple in-memory caching, rate limiting, and frontend optimizations. Sufficient for 5-10 concurrent users. **Cost: $0** (no additional services).

**Dependencies:** Sprint 4

**Testing Strategy:**
- Simple load test with 10 concurrent users (using `ab` or `wrk`)
- Measure API response times
- Verify rate limiting works
- Test WebSocket connection stability

---

### Task 2: Basic Monitoring & Logging (Free Tier)

**Action Items:**
- Implement simple structured logging:
  - Use Python `logging` with JSON formatter (no need for structlog)
  - Log levels: INFO, WARNING, ERROR
  - Include request ID, user ID, session ID in logs
  - Log API requests/responses (sanitize passwords/API keys)
  - Log PV curve generation metrics (duration, convergence)
  - Write logs to stdout (captured by Render/Railway automatically)
- Set up free monitoring tools:
  - **Sentry Free Tier**: Error tracking for backend and frontend
    - 5,000 errors/month free
    - Captures unhandled exceptions
    - Source maps for frontend debugging
  - **UptimeRobot Free Tier**: Uptime monitoring
    - 50 monitors free
    - 5-minute check interval
    - Email alerts on downtime
  - **Platform Built-in Monitoring**: Use Render/Railway dashboards
    - CPU and memory usage
    - Request count and response times
    - Deployment history
- Implement basic health check endpoint:
  - `GET /api/v1/health` - Returns status, database connection, disk space
- Add simple error tracking:
  - Integrate Sentry SDK in backend and frontend
  - Capture unhandled exceptions
  - Add user context to error reports
- **No CloudWatch, No X-Ray, No custom dashboards** (add when moving to AWS)

**Deliverable:** Basic but functional monitoring using free tools (Sentry, UptimeRobot, platform built-in), sufficient for 5-10 users. **Cost: $0** (free tiers).

**Dependencies:** Sprint 5, Task 1

**Testing Strategy:**
- Test Sentry error capture
- Test uptime monitoring alerts
- Verify health check endpoint
- Test logging output

---

### Task 3: Simple CI/CD Pipeline

**Action Items:**
- Create GitHub Actions workflow (`.github/workflows/ci-cd.yml`):
  - **CI (runs on all branches and PRs)**:
    - Run backend tests (pytest)
    - Run linting (flake8 for Python, ESLint for TypeScript)
    - Build Docker image to verify build success
    - Report test results
  - **CD (runs on push to `main` branch)**:
    - Run full CI pipeline
    - Require manual approval (using GitHub Environments)
    - Deploy to Render/Railway (using platform CLI or API)
    - Run basic smoke test (check health endpoint)
    - Post deployment status to GitHub commit
- Keep it simple:
  - No separate staging environment initially (deploy directly to production with approval)
  - No complex blue-green deployment (Render/Railway handles this)
  - No automatic rollback (manual rollback via platform dashboard if needed)
- Create simple deployment script (`/web/scripts/deploy.sh`):
  - Build Docker image
  - Push to platform (or trigger via git push)
  - Basic deployment verification
- Add version tagging:
  - Manual version tags (v1.0.0, v1.1.0, etc.)
  - Tag releases in GitHub
- Create simple deployment documentation (`/web/docs/DEPLOYMENT.md`):
  - How to deploy manually
  - How to rollback
  - Environment variables reference
  - Basic troubleshooting

**Deliverable:** A simple CI/CD pipeline with GitHub Actions that runs tests on every push, requires manual approval for deployment, and deploys to production with basic smoke testing. **Cost: $0** (GitHub Actions free for public repos, 2000 minutes/month for private).

**Dependencies:** Sprint 5, Task 2

**Testing Strategy:**
- Test CI workflow on feature branch
- Test manual approval flow
- Test deployment to Render/Railway
- Verify smoke tests run correctly

---

## Sprint 6 Plan

**Sprint Goals (4/18 - 4/24)** Documentation, Testing & Production Launch: Create comprehensive documentation, conduct user testing, fix bugs, and execute production launch with post-launch monitoring.

### Task 1: User Documentation & Guides

**Action Items:**
- Create user documentation (`/web/docs/USER_GUIDE.md`):
  - **Getting Started**:
    - How to access the web application
    - Guest vs registered user (pros/cons)
    - How to configure LLM (OpenAI API key or local Ollama)
  - **Using the Chat Interface**:
    - How to ask questions
    - How to modify parameters
    - How to generate PV curves
    - Understanding the results
  - **Parameter Guide**:
    - Explanation of each parameter
    - Recommended values
    - How parameters affect results
  - **Interpreting PV Curves**:
    - What is a PV curve
    - Understanding the nose point
    - Load margin interpretation
    - Voltage stability assessment
  - **FAQ Section**:
    - Common questions and answers
    - Troubleshooting tips
    - How to get help
- Create API documentation (`/web/docs/API_REFERENCE.md`):
  - Supplement Swagger docs with examples
  - Authentication flow
  - WebSocket protocol
  - Error codes and handling
- Update main README.md:
  - Add web application section
  - Link to live demo
  - Installation instructions for web version
  - Link to user guide

**Deliverable:** Comprehensive user documentation with getting started guide, feature explanations, parameter reference, and FAQ.

**Dependencies:** Sprint 5

**Testing Strategy:**
- Have someone unfamiliar with the project follow the guide
- Verify all links work
- Check for clarity and completeness

---

### Task 2: User Acceptance Testing & Bug Fixes

**Action Items:**
- Conduct user acceptance testing:
  - Recruit 3-5 beta testers (power system engineers or students)
  - Provide test scenarios:
    - Guest user flow (no registration)
    - Registered user flow (signup, login)
    - Basic PV curve generation
    - Parameter modification
    - Multi-step queries
    - History browsing
    - LLM configuration (API key or Ollama)
  - Collect feedback via simple survey (Google Forms)
  - Track bugs in GitHub Issues
- Fix identified bugs:
  - Critical bugs: Fix immediately
  - High priority: Fix before launch
  - Medium/Low: Document for post-launch
- UI/UX improvements based on feedback:
  - Improve error messages
  - Enhance loading states
  - Fix any layout issues
  - Improve mobile experience if needed
- Security review:
  - Review authentication implementation
  - Check for common vulnerabilities (OWASP Top 10 basics)
  - Verify API key encryption
  - Test rate limiting
  - Ensure HTTPS enforcement
- Performance testing:
  - Test with 10 concurrent users
  - Verify response times are acceptable
  - Check for memory leaks (long-running sessions)

**Deliverable:** A tested, bug-free application with improvements based on real user feedback, basic security review completed, and performance verified for 5-10 concurrent users.

**Dependencies:** Sprint 6, Task 1

**Testing Strategy:**
- Conduct UAT with beta testers
- Track and resolve all critical bugs
- Perform basic security testing
- Load test with 10 concurrent users

---

### Task 3: Production Launch & Post-Launch Monitoring

**Action Items:**
- Pre-launch checklist:
  - [ ] All tests passing
  - [ ] Documentation complete
  - [ ] User guide published
  - [ ] Monitoring configured (Sentry, UptimeRobot)
  - [ ] HTTPS working
  - [ ] Database backups configured (Render/Railway automatic backups)
  - [ ] Environment variables configured
  - [ ] Beta testing completed
  - [ ] Critical bugs fixed
- Execute production launch:
  - Deploy to production via GitHub Actions (manual approval)
  - Verify deployment successful
  - Run smoke tests
  - Check all services healthy
- Post-launch monitoring (first 48 hours):
  - Monitor Sentry for errors
  - Check UptimeRobot for uptime
  - Monitor platform dashboard (CPU, memory, requests)
  - Watch for user-reported issues
  - Be ready for quick fixes
- Soft launch strategy:
  - Announce to small group first (internal team, beta testers)
  - Monitor for 24 hours
  - Fix any issues
  - Broader announcement
- Create support system:
  - Set up support email or GitHub Issues for support
  - Prepare response templates for common issues
  - Document common problems and solutions
- Post-launch communication:
  - Update GitHub README with live demo link
  - Announcement to relevant communities (if applicable)
  - Share with CURENT team

**Deliverable:** Successful production launch with live, publicly accessible web application, post-launch monitoring in place, and support system ready. Application running on Render/Railway with automatic HTTPS and backups.

**Dependencies:** Sprint 6, Task 2

**Testing Strategy:**
- Execute pre-launch checklist
- Run final smoke tests
- Monitor for first 48 hours
- Verify backup system works

---

## Post-Launch Roadmap (Sprint 7+)

### When to Scale Up (Triggers for Infrastructure Upgrade)

**Migrate from SQLite to PostgreSQL when:**
- Reaching 50+ total users OR 10+ concurrent users
- Database file size > 1GB
- Experiencing database lock contention
- Need for better concurrent write performance

**Add Redis when:**
- Reaching 20+ concurrent users
- Need for distributed session storage (multiple backend instances)
- Cache hit rate would significantly improve performance
- WebSocket scaling across multiple servers needed

**Migrate to AWS/GCP when:**
- Render/Railway limits reached (CPU, memory, or bandwidth)
- Need for auto-scaling (traffic spikes)
- Need for multi-region deployment
- Require more control over infrastructure
- Budget allows for $100+/month infrastructure costs

**Add CDN when:**
- Users are global (high latency from single region)
- Static asset bandwidth costs become significant
- Need for edge caching and DDoS protection

**Add Load Balancer when:**
- Running multiple backend instances
- Need for zero-downtime deployments
- Need for advanced routing (A/B testing, canary deployments)

---

## Removed Sprints (Deferred to Post-Launch)

The following sprints from the original plan are **deferred to post-launch** based on budget optimization:

### Sprint 7+ Features (Add When Needed)

**Deferred Features** (from original plan, add based on user demand):
- **Advanced Comparison Dashboard**: Multi-curve selection, side-by-side plots, synchronized zoom
- **Batch Generation**: Generate multiple PV curves in parallel
- **Parameter Sweeps**: Automated sensitivity analysis across parameter ranges
- **Advanced Export**: PDF reports, CSV data, SVG plots, batch export
- **Job Queue System**: Celery + Redis for background tasks
- **Parameter Presets**: Save and load parameter configurations
- **Advanced UI Customization**: Multiple themes, plot color schemes, layout options

**Infrastructure Upgrades** (when scaling triggers are met):
- **PostgreSQL Migration**: When SQLite limits are reached
- **Redis Addition**: When caching and distributed sessions are needed
- **AWS/GCP Migration**: When Render/Railway limits are reached
- **CDN Addition**: When global users need faster asset delivery
- **Load Balancer**: When running multiple backend instances

**Advanced Features** (future roadmap):
- Custom power system file upload (pandapower JSON/Excel)
- Advanced contingency analysis UI
- Parameter optimization recommendations (AI-suggested)
- Collaborative features (share conversations, team workspaces)
- Public API for programmatic access
- Mobile app (PWA or React Native)
- Multi-agent collaboration
- Fine-tuned models for power system domain
- Voice interface (speech-to-text)

---

## Simplified Sprint Summary (6 Sprints Total)

| Sprint | Focus | Key Deliverables | Cost Impact |
|--------|-------|------------------|-------------|
| **Sprint 1** | Backend API | FastAPI + WebSocket + SQLite + Auth | $0 |
| **Sprint 2** | Frontend UI | React + Chat + Parameters + Plotly | $0 |
| **Sprint 3** | Deployment | Docker + Render/Railway deployment | $0-20/month |
| **Sprint 4** | History & Settings | History browser + User settings + LLM config | $0 |
| **Sprint 5** | CI/CD & Monitoring | GitHub Actions + Sentry + UptimeRobot | $0 |
| **Sprint 6** | Launch | Documentation + Testing + Production launch | $0 |

**Total Timeline: 6 weeks** from start to production launch
**Total Monthly Cost: $10-25/month** (Render Hobby $7/month or Railway Hobby $5/month + domain ~$1/month + buffer)

---

## Removed Sprints (Deferred to Post-Launch)

The following content from the original plan is **deferred to post-launch** based on budget optimization:

**Phase 1: Feature Expansion**
- Custom power system file upload (pandapower JSON/Excel)
- Advanced contingency analysis UI
- Parameter optimization recommendations (AI-suggested optimal parameters)
- Collaborative features (share conversations, team workspaces)
- API for programmatic access (for researchers/developers)
- Mobile app (React Native or PWA)

**Phase 2: Scaling to Medium (500 users)**
- Migrate to Kubernetes (EKS) for better orchestration
- Implement auto-scaling with predictive scaling
- Add multi-region deployment for global users
- Upgrade to larger RDS instance or Aurora Serverless
- Implement CDN for global content delivery
- Add load balancing across regions

**Phase 3: Advanced AI Features**
- Multi-agent collaboration (multiple LLMs working together)
- Fine-tuned models for power system domain
- Predictive analytics (predict stability issues before generation)
- Automated report generation with insights
- Natural language to parameter conversion (more intelligent parsing)
- Voice interface (speech-to-text for queries)

**Phase 4: Enterprise Features**
- SSO integration (SAML, OAuth)
- Team management and permissions
- Admin dashboard for organization management
- Usage analytics per team/organization
- Custom branding for enterprise customers
- SLA guarantees and priority support
- On-premise deployment option

---

## Technical Architecture Summary

### Phase 1: Simple Single-Server Architecture (Current Plan)

```
┌─────────────────────────────────────────────────────────────┐
│                    Internet (HTTPS)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ (Automatic HTTPS via Render/Railway)
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
│  │  │  - Agent workflow integration                   │  │  │
│  │  │  - In-memory caching (simple dict)              │  │  │
│  │  └────────────────────┬────────────────────────────┘  │  │
│  │                       │                                 │  │
│  │  ┌────────────────────▼────────────────────────────┐  │  │
│  │  │         Agent Workflow (Imported)               │  │  │
│  │  │  - LangGraph nodes                              │  │  │
│  │  │  - Uses user's OpenAI key or Ollama             │  │  │
│  │  │  - Vector DB (read-only, bundled)               │  │  │
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
- Sentry (error tracking)
- UptimeRobot (uptime monitoring)
- GitHub Actions (CI/CD)

User's Local Machine (Optional):
- Ollama (if user chooses local LLM)
```

**Key Simplifications:**
- ✅ Single container (frontend + backend in one)
- ✅ No separate database server (SQLite file)
- ✅ No Redis (in-memory caching)
- ✅ No CDN (direct serving)
- ✅ No load balancer (single instance)
- ✅ No separate Ollama server (users run locally or use OpenAI)
- ✅ Automatic HTTPS (platform provides)
- ✅ Automatic backups (platform provides)

---

### Phase 2: Scaled Architecture (50+ Users, Future)

When scaling triggers are met, upgrade to:

```
┌─────────────────────────────────────────────────────────────┐
│                    Internet (HTTPS)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              Render/Railway (Upgraded)                       │
│                                                               │
│  ┌──────────────┐     ┌──────────────┐                      │
│  │   Frontend   │     │   Backend    │                      │
│  │   (Nginx)    │     │  (FastAPI)   │                      │
│  │   2 instances│     │  2-4 instances│                     │
│  └──────────────┘     └──────┬───────┘                      │
│                               │                               │
│  ┌────────────────────────────▼─────────────────────────┐   │
│  │         Managed PostgreSQL (Render/Railway)          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Upstash Redis (Managed, Serverless)          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

### Phase 3: Enterprise Architecture (500+ Users, Future)

When you need enterprise scale, migrate to AWS (full architecture from original plan).

---

### Technology Stack (Simplified)

**Frontend:**
- React 18 + Vite
- TypeScript
- Tailwind CSS
- Plotly.js (visualization)
- Socket.io-client (WebSocket)
- Zustand (lightweight state management)
- React Router (navigation)
- Axios (HTTP client)

**Backend:**
- FastAPI (Python 3.12)
- SQLAlchemy (ORM)
- SQLite (database - file-based)
- Pydantic (validation)
- JWT (authentication with python-jose)
- Socket.io (WebSocket)
- In-memory caching (Python dict with LRU)
- slowapi (rate limiting without Redis)

**Agent System (Existing - Reused):**
- LangGraph + LangChain
- OpenAI API (user's key) / Ollama (user's local)
- pandapower (power system simulation)
- Chroma (vector database for RAG)

**Infrastructure:**
- Render or Railway (managed platform)
- Docker (single container)
- Persistent disk (SQLite + plots)
- Automatic HTTPS (platform-provided)
- Automatic backups (platform-provided)

**DevOps:**
- Docker (single Dockerfile)
- Docker Compose (local development)
- GitHub Actions (CI/CD)
- No IaC initially (manual platform setup)

**Monitoring (Free Tier):**
- Sentry (error tracking)
- UptimeRobot (uptime monitoring)
- Platform built-in monitoring

---

## Engineering Principles & Constraints

### Hard Constraints

1. **No Modification to Existing CLI Code**: All web functionality must be built under `/web` directory without changing existing `agent/`, `cli.py`, or `main.py` files
2. **Feature Parity**: Web interface must support ALL features available in CLI:
   - All 11 agent workflow nodes
   - All input parameters (grid, bus_id, step_size, max_scale, power_factor, voltage_limit, capacitive, continuation, contingency_lines, gen_voltage_setpoints)
   - RAG-enhanced question answering
   - Multi-step planning and execution
   - Error handling and recovery
   - Session persistence
3. **Budget Constraint**: Initial deployment must cost $0-10/month, scalable to higher budgets when needed
4. **Simplicity First**: Keep architecture as simple as possible, add complexity only when scaling requires it
5. **User-Provided Compute**: Users provide their own LLM (OpenAI API key or local Ollama) to eliminate server-side LLM costs
6. **Real-time Experience**: WebSocket streaming for agent responses and PV curve generation progress

### Engineering Principles (Simplified)

1. **Keep It Simple**: Start with simplest solution that works, add complexity only when needed
2. **Separation of Concerns**: Clear separation between frontend, backend API, and agent logic (reuse existing)
3. **API-First Design**: Backend API should be usable independently (future mobile app, programmatic access)
4. **Stateless Where Possible**: Minimize server-side state, use SQLite for persistence
5. **Graceful Degradation**: Application should handle errors gracefully with clear user messages
6. **Basic Observability**: Simple logging and error tracking, expand when scaling
7. **Manual First, Automate Later**: Manual deployment initially, automate as confidence grows
8. **Test Core Paths**: Focus testing on critical user journeys, not 100% coverage
9. **Document As You Build**: Keep documentation simple and up-to-date
10. **Security Basics**: HTTPS, JWT, password hashing, rate limiting - no over-engineering

---

### Directory Structure (Simplified)

```
pv-curve-llm/
├── agent/                          # Existing CLI agent (DO NOT MODIFY)
│   ├── core.py
│   ├── workflows/
│   ├── nodes/
│   ├── state/
│   ├── schemas/
│   ├── pv_curve/
│   ├── utils/
│   ├── data/
│   ├── vector_db/
│   └── ...
├── main.py                         # Existing CLI entry point (DO NOT MODIFY)
├── cli.py                          # Existing CLI interface (DO NOT MODIFY)
│
├── web/                            # NEW: All web application code
│   │
│   ├── backend/                    # FastAPI backend (simplified)
│   │   ├── api/                    # API routes
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── chat.py         # Chat + WebSocket
│   │   │       ├── parameters.py   # Parameter CRUD
│   │   │       ├── auth.py         # Auth endpoints
│   │   │       ├── user.py         # User profile
│   │   │       └── history.py      # Conversation history
│   │   │
│   │   ├── services/               # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── agent_service.py    # Agent workflow integration
│   │   │   ├── llm_service.py      # LLM provider (OpenAI/Ollama)
│   │   │   ├── session_service.py  # Session management
│   │   │   └── auth_service.py     # Authentication logic
│   │   │
│   │   ├── database/               # Database layer
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # SQLAlchemy models
│   │   │   ├── database.py         # Database session
│   │   │   └── crud.py             # CRUD operations
│   │   │
│   │   ├── schemas/                # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── chat.py
│   │   │   ├── user.py
│   │   │   └── response.py
│   │   │
│   │   ├── core/                   # Core configuration
│   │   │   ├── __init__.py
│   │   │   ├── config.py           # Settings
│   │   │   ├── security.py         # JWT, password hashing
│   │   │   └── dependencies.py     # FastAPI dependencies
│   │   │
│   │   ├── utils/                  # Utilities
│   │   │   ├── __init__.py
│   │   │   ├── cache.py            # In-memory cache
│   │   │   └── helpers.py
│   │   │
│   │   ├── tests/                  # Backend tests
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py
│   │   │   └── test_api/
│   │   │
│   │   ├── main.py                 # FastAPI app entry
│   │   ├── requirements.txt        # Backend dependencies
│   │   └── .env.example
│   │
│   ├── frontend/                   # React frontend (simplified)
│   │   ├── public/
│   │   │   └── index.html
│   │   │
│   │   ├── src/
│   │   │   ├── components/         # UI components
│   │   │   │   ├── Chat/
│   │   │   │   ├── Parameters/
│   │   │   │   ├── Visualization/
│   │   │   │   ├── History/
│   │   │   │   ├── Auth/
│   │   │   │   └── Common/
│   │   │   │
│   │   │   ├── pages/              # Main pages
│   │   │   │   ├── Landing.tsx
│   │   │   │   ├── Chat.tsx
│   │   │   │   ├── History.tsx
│   │   │   │   └── Settings.tsx
│   │   │   │
│   │   │   ├── services/           # API client
│   │   │   │   ├── api.ts
│   │   │   │   └── websocket.ts
│   │   │   │
│   │   │   ├── hooks/              # Custom hooks
│   │   │   ├── store/              # Zustand store
│   │   │   ├── types/              # TypeScript types
│   │   │   ├── utils/              # Helpers
│   │   │   ├── App.tsx
│   │   │   └── main.tsx
│   │   │
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   ├── tsconfig.json
│   │   └── tailwind.config.js
│   │
│   ├── docs/                       # Documentation
│   │   ├── USER_GUIDE.md
│   │   ├── DEPLOYMENT.md
│   │   └── API_REFERENCE.md
│   │
│   ├── scripts/                    # Deployment scripts
│   │   └── deploy.sh
│   │
│   ├── Dockerfile                  # Single Dockerfile (frontend + backend)
│   ├── docker-compose.yml          # Local development
│   ├── nginx.conf                  # Nginx configuration
│   ├── render.yaml                 # Render deployment config (if using Render)
│   ├── .env.example                # Environment variables
│   └── README.md                   # Web app README
│
├── .github/
│   └── workflows/                  # CI/CD
│       └── ci-cd.yml               # Single workflow (CI + CD)
│
├── generated/                      # Existing: PV curve outputs (CLI)
├── requirements.txt                # Existing: CLI dependencies
└── README.md                       # Existing: Main README (update)
```

**Simplifications from Original Plan:**
- ✅ Single Dockerfile instead of separate frontend/backend
- ✅ No separate infrastructure/ directory (no IaC initially)
- ✅ Simpler backend structure (fewer services)
- ✅ Simpler frontend structure (fewer pages)
- ✅ Single CI/CD workflow instead of three
- ✅ No docker-compose.prod.yml (use same file)
- ✅ Fewer documentation files initially

---

## Cost Estimation (Budget-Optimized for 5-10 Users)

### Phase 1: Initial Launch (Current Plan)

| Service | Configuration | Estimated Cost |
|---------|--------------|----------------|
| **Render/Railway** | Hobby plan (512MB RAM, 0.5 CPU) | $5-7/month |
| **Domain Name** | Custom domain (optional) | $0-12/year (~$1/month) |
| **SQLite Database** | File-based, included in server storage | $0 |
| **Monitoring** | Sentry Free (5K errors/month) + UptimeRobot Free | $0 |
| **CI/CD** | GitHub Actions (free for public repos, 2000 min/month private) | $0 |
| **LLM Costs** | Users provide their own (OpenAI API key or local Ollama) | $0 |
| **Storage** | 10GB disk included with Render/Railway | $0 |

**Total Monthly Cost: $5-8/month** (or $0 if using free tiers)

**Free Tier Options:**
- **Render Free Tier**: 750 hours/month free (enough for 1 service running 24/7)
- **Railway Free Tier**: $5 credit/month (enough for small app)
- **Fly.io Free Tier**: 3 shared VMs free

**Recommended for Start: Render Free Tier → Upgrade to Hobby ($7/month) when traffic increases**

---

### Phase 2: Scaling to 50 Users (Future)

When you hit scaling triggers (20+ concurrent users, SQLite limitations), upgrade to:

| Service | Configuration | Estimated Cost |
|---------|--------------|----------------|
| **Render/Railway** | Standard plan (2GB RAM, 1 CPU) | $20-25/month |
| **Managed PostgreSQL** | Render/Railway add-on (1GB RAM) | $7-15/month |
| **Redis** | Upstash or Redis Cloud (100MB) | $0-10/month |
| **Monitoring** | Sentry Team (50K errors/month) | $0-26/month |
| **Storage** | Additional storage for plots | $5/month |

**Total Monthly Cost: $32-81/month**

---

### Phase 3: Scaling to 500 Users (Future)

When you need enterprise-grade infrastructure, migrate to AWS:

| Service | Configuration | Estimated Cost |
|---------|--------------|----------------|
| **AWS ECS Fargate** | 2-4 tasks (0.5 vCPU, 1GB RAM each) | $50-100/month |
| **RDS PostgreSQL** | db.t3.small (2 vCPU, 2GB RAM) | $30-50/month |
| **ElastiCache Redis** | cache.t3.small (2 vCPU, 2GB RAM) | $25-35/month |
| **S3 + CloudFront** | 500GB storage, 5TB transfer | $30-50/month |
| **ALB** | 1 load balancer, ~10M requests | $25-35/month |
| **Monitoring** | CloudWatch + Sentry Business | $30-50/month |

**Total Monthly Cost: $190-320/month**

---

### Cost Comparison: Budget vs Original Plan

| Approach | Initial Cost | 50 Users | 500 Users |
|----------|--------------|----------|-----------|
| **Budget-Optimized (This Plan)** | $0-8/month | $32-81/month | $190-320/month |
| **Original Full Plan** | $322-472/month | $322-472/month | $500-800/month |
| **Savings** | **$314-464/month** | **$241-440/month** | **$180-480/month** |

**Key Cost Savings:**
1. **No server-side LLM costs**: Users bring their own OpenAI API key or Ollama ($0 vs $50-200/month)
2. **Simple deployment**: Render/Railway vs AWS ECS ($7 vs $50/month)
3. **No Redis**: In-memory caching vs ElastiCache ($0 vs $15/month)
4. **SQLite**: File-based vs RDS PostgreSQL ($0 vs $30/month)
5. **No CDN**: Direct serving vs CloudFront ($0 vs $10/month)
6. **No Load Balancer**: Single server vs ALB ($0 vs $20/month)
7. **Free monitoring**: Free tiers vs paid monitoring ($0 vs $20/month)

---

## Risk Assessment & Mitigation (Simplified)

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **WebSocket connection instability** | High | Medium | Implement reconnection logic with exponential backoff, test thoroughly |
| **SQLite lock contention** | Medium | Low | Sufficient for 5-10 users, monitor and migrate to PostgreSQL if issues arise |
| **Platform limitations (Render/Railway)** | Medium | Low | Start with free/hobby tier, upgrade plan if needed, migration path to AWS documented |
| **User's Ollama connection issues** | Medium | Medium | Clear documentation, connection testing, fallback to OpenAI option |
| **PV curve generation timeout** | Medium | Low | Set reasonable timeouts (60s), show progress, clear error messages |

### Business Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Low user adoption** | High | Medium | User testing before launch, gather feedback, iterate quickly |
| **Users don't want to provide API keys** | Medium | Medium | Clear explanation of benefits (privacy, control), very easy setup process |
| **Platform costs increase** | Low | Low | Start with free tier, monitor usage, upgrade only when needed |

---

## Success Metrics (KPIs) - Simplified

### User Engagement (Track with free analytics)
- Total users (registered + guest)
- PV curves generated per week
- Active conversations per week
- User retention (returning users)

### Technical Performance (Monitor with free tools)
- Uptime (target: 99% with free tier)
- Error rate (target: <2%)
- Average PV curve generation time (target: <10s)
- WebSocket connection success rate (target: >95%)

### Cost Efficiency
- Monthly infrastructure cost (target: <$10 for 5-10 users)
- Cost per user (target: <$1/user/month)
- Server-side LLM cost (target: $0 - users provide their own)

---

## Launch Checklist (Simplified)

### Pre-Launch (Complete before Sprint 6, Task 3)
- [ ] All Sprint 1-5 tasks completed
- [ ] Core tests passing (backend + frontend critical paths)
- [ ] Basic security review completed (HTTPS, JWT, rate limiting, input validation)
- [ ] Simple performance testing (10 concurrent users)
- [ ] Documentation complete (user guide, deployment guide)
- [ ] Monitoring configured (Sentry, UptimeRobot)
- [ ] Platform backups enabled (automatic via Render/Railway)
- [ ] HTTPS working (automatic via platform)
- [ ] Error tracking (Sentry) configured
- [ ] Beta testing completed (3-5 users)
- [ ] Critical bugs fixed

### Launch Day
- [ ] Deploy to production (via GitHub Actions with manual approval)
- [ ] Run smoke tests (health check, login, generate PV curve)
- [ ] Verify services healthy (check platform dashboard)
- [ ] Monitoring active (Sentry, UptimeRobot)
- [ ] Update README with live demo link

### Post-Launch (First 48 Hours)
- [ ] Monitor Sentry for errors
- [ ] Check UptimeRobot for uptime
- [ ] Monitor platform dashboard (CPU, memory, requests)
- [ ] Watch for user-reported issues
- [ ] Be ready for quick fixes or rollback

---

## Key Technical Decisions & Rationale

### Why FastAPI?
- **Async Support**: Native async/await for WebSocket and concurrent operations
- **Type Safety**: Pydantic integration for request/response validation
- **Auto Documentation**: Swagger UI generated automatically
- **Performance**: One of the fastest Python frameworks
- **Simple**: Easy to learn, minimal boilerplate

### Why React + Vite?
- **Component-Based**: Reusable UI components, maintainable codebase
- **Performance**: Vite provides fast development and optimized builds
- **TypeScript**: Type safety for frontend
- **Ecosystem**: Rich library ecosystem
- **Simple**: Straightforward setup, no complex configuration

### Why SQLite (Initially)?
- **Zero Cost**: No separate database server needed
- **Zero Config**: Single file, no connection strings
- **Sufficient**: Handles 5-10 concurrent users easily
- **Easy Migration**: Can migrate to PostgreSQL later with minimal code changes
- **Simple Backups**: Just copy the database file

### Why Render/Railway over AWS?
- **Simplicity**: Deploy with git push, no infrastructure management
- **Cost**: $0-7/month vs $50+/month for AWS
- **Automatic HTTPS**: Free SSL certificates
- **Automatic Backups**: Platform handles backups
- **Easy Scaling**: Click to upgrade when needed
- **Migration Path**: Can move to AWS later if needed (Docker containers are portable)

### Why User-Provided LLM?
- **Zero Server Cost**: No OpenAI API bills or GPU server costs
- **User Control**: Users choose their preferred LLM and control costs
- **Privacy**: User's API key never leaves their control
- **Flexibility**: Users can use OpenAI, local Ollama, or any compatible API
- **Simple**: No complex LLM infrastructure to manage

### Why WebSocket over SSE or Polling?
- **Bi-directional**: Can send messages both ways
- **Real-time**: Lower latency than polling
- **Efficiency**: Single persistent connection
- **Good Libraries**: Socket.io provides robust implementation with fallbacks

### Why Plotly.js?
- **Interactivity**: Superior zoom, pan, hover capabilities
- **Professional**: Publication-quality plots
- **Export**: Built-in PNG export
- **Scientific**: Perfect for engineering/scientific visualization
- **No Backend Needed**: Pure JavaScript, no server-side rendering

---

## Conclusion

This **budget-optimized sprint plan** provides a practical roadmap to transform the PV Curve Agent from a CLI application to a production-ready, cloud-based web application with:

✅ **Feature Parity**: All CLI features available in web interface
✅ **Modern UI**: React-based interface with real-time WebSocket updates
✅ **Ultra-Low Cost**: $5-8/month (or $0 with free tiers) vs $322/month in original plan
✅ **Scalability**: Simple architecture now, clear upgrade path to 500+ users
✅ **Security**: HTTPS, JWT, password hashing, rate limiting, encrypted API keys
✅ **Monitoring**: Free tier monitoring (Sentry + UptimeRobot)
✅ **CI/CD**: Automated testing and deployment with GitHub Actions
✅ **Non-Invasive**: All web code under `/web`, existing CLI untouched
✅ **User-Provided LLM**: Zero server-side LLM costs, users bring their own compute

### Key Cost Savings vs Original Plan

- **$314-464/month saved** by using simple deployment platform
- **$50-200/month saved** by having users provide their own LLM
- **$15/month saved** by skipping Redis (in-memory caching)
- **$30/month saved** by using SQLite instead of PostgreSQL
- **$20/month saved** by skipping load balancer
- **$10/month saved** by skipping CDN

**Total Savings: ~$440-740/month** while maintaining core functionality

### Timeline & Next Steps

**Total Timeline: 6 sprints (6 weeks)** from backend API to production launch

**Immediate Next Steps:**
1. ✅ Review and approve this sprint plan
2. Set up development environment (`/web` directory structure)
3. Begin Sprint 1, Task 1: FastAPI Backend Setup
4. Create initial Docker setup for local development

**When to Scale Up:**
- Add Redis when reaching 20+ concurrent users
- Migrate to PostgreSQL when reaching 50+ users or SQLite shows limitations
- Migrate to AWS when Render/Railway limits are reached or need advanced features
- Add deferred features based on user demand and feedback

---

## 🚀 Getting Started with Sprint 1

Once you approve this plan, here's what we'll create first:

### Sprint 1, Task 1: Initial File Structure

```
web/
├── backend/
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── chat.py          # First endpoint: POST /api/v1/chat
│   │       └── parameters.py    # GET/POST /api/v1/parameters
│   ├── services/
│   │   └── agent_service.py     # Import and wrap existing agent workflow
│   ├── core/
│   │   ├── config.py            # Environment variables, settings
│   │   └── dependencies.py      # FastAPI dependencies
│   ├── main.py                  # FastAPI app initialization
│   ├── requirements.txt         # fastapi, uvicorn, sqlalchemy, etc.
│   └── .env.example
├── docker-compose.yml           # For local development
└── README.md                    # Web app README
```

### First Code We'll Write

**1. `/web/backend/main.py`** - FastAPI app with WebSocket:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

app = FastAPI(title="PV Curve Agent API")
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

# CORS for frontend
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# Health check
@app.get("/api/v1/health")
async def health():
    return {"status": "healthy"}

# Import routers
from api.v1 import chat, parameters
app.include_router(chat.router, prefix="/api/v1")
app.include_router(parameters.router, prefix="/api/v1")
```

**2. `/web/backend/services/agent_service.py`** - Wrap existing agent:
```python
import sys
from pathlib import Path

# Add parent directory to path to import existing agent
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from agent.core import create_graph, setup_dependencies
from agent.state.app_state import State

class AgentService:
    def __init__(self, provider: str = "openai"):
        self.llm, self.prompts, self.retriever = setup_dependencies(provider)
        self.graph = create_graph(provider)
    
    async def execute_turn(self, user_message: str, state: State):
        """Execute one turn of the agent workflow."""
        # Stream results from existing graph
        for node_name, state_update in self.graph.stream(...):
            yield node_name, state_update
```

**3. `/web/backend/api/v1/chat.py`** - Chat endpoint with WebSocket:
```python
from fastapi import APIRouter, WebSocket
from services.agent_service import AgentService

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    agent = AgentService(provider="openai")  # Will use user's key
    
    while True:
        message = await websocket.receive_text()
        
        # Stream agent responses back to frontend
        async for node_name, state_update in agent.execute_turn(message):
            await websocket.send_json({
                "type": "node_update",
                "node": node_name,
                "data": state_update
            })
```

This gives you a concrete picture of what we'll build. The key insight is we're **wrapping and reusing** your existing agent code, not rewriting it.

---

## Questions?

Before we begin implementation, do you have any questions about:
- The simplified architecture?
- The cost estimates ($5-8/month)?
- The timeline (6 weeks)?
- The deferred features?
- The scaling strategy?
- How user-provided LLM works?

**Ready to start?** Once you approve, I'll begin Sprint 1, Task 1 and create the initial `/web` directory structure with FastAPI backend setup. We'll build it step by step, and I'll explain the logic and thought process as we go (per your preferences).
