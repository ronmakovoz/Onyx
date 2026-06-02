#!/bin/bash
# Starts both backend and frontend in the background

echo "Starting VP CX Agent OS..."

# Kill any existing processes on these ports
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 8501/tcp 2>/dev/null || true

# Start FastAPI
uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!
echo "Backend started (PID $BACKEND_PID) on http://localhost:8000"

sleep 2

# Start Streamlit
streamlit run frontend/app.py --server.port 8501 --server.headless true &
FRONTEND_PID=$!
echo "Frontend started (PID $FRONTEND_PID) on http://localhost:8501"

echo ""
echo "App running at http://localhost:8501"
echo "API docs at   http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop."

wait
