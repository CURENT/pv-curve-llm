#!/bin/sh
set -e

# Ensure persistent data directories exist at startup
mkdir -p /data/plots

# Start Uvicorn in the background (bound to localhost — Nginx is the public face)
uvicorn web.backend.main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --log-level info &
UVICORN_PID=$!

# Trap SIGTERM/INT so both processes are cleaned up on container stop
trap 'kill $UVICORN_PID 2>/dev/null; exit 0' TERM INT

# Nginx runs in the foreground (keeps the container alive)
nginx -g 'daemon off;'

# If Nginx exits for any reason, kill Uvicorn too
kill $UVICORN_PID 2>/dev/null
