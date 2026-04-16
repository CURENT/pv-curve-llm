# ── Stage 1: Build React frontend ─────────────────────────────────────────────
FROM node:20-alpine AS frontend

WORKDIR /build
COPY web/frontend/package.json web/frontend/package-lock.json ./
RUN npm ci --prefer-offline
COPY web/frontend/ .
RUN npm run build

# ── Stage 2: Runtime — Python + Nginx + Uvicorn ───────────────────────────────
FROM python:3.12-slim

# Install Nginx (reverse proxy + static file server)
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx && \
    rm -rf /var/lib/apt/lists/*

# /app is the working directory — matches `uvicorn web.backend.main:app`
# run instructions in the project README (imports resolve from here)
WORKDIR /app

# Install Python deps in one layer (agent deps + backend deps)
COPY requirements.txt ./
COPY web/backend/requirements.txt ./web-requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r web-requirements.txt

# Copy application code
COPY agent/ agent/
COPY web/backend/ web/backend/

# Copy built frontend static files (served by Nginx)
COPY --from=frontend /build/dist /app/web/frontend/dist

# Nginx site config (overwrites the Debian default)
COPY web/nginx.conf /etc/nginx/sites-available/default

# Startup script
COPY web/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
