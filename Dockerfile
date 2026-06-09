# Onyx CX Agent OS — Next.js frontend + FastAPI backend in one container
# (Hugging Face Spaces exposes a single port; Next serves on 7860 and
# proxies /api/* to uvicorn on 8000 via next.config.js rewrites.)

FROM node:20-slim

# Python runtime for the FastAPI backend + agents
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps (cached layer)
COPY api/requirements.txt api/requirements.txt
RUN python3 -m venv /venv && /venv/bin/pip install --no-cache-dir -r api/requirements.txt

# Node deps (cached layer)
COPY web/package.json web/package-lock.json web/
RUN cd web && npm ci

# App source
COPY . .

# Build the Next.js production bundle
RUN cd web && npm run build

ENV NODE_ENV=production
EXPOSE 7860

# Start FastAPI (internal :8000), then Next.js on the public port
CMD ["bash", "-c", "/venv/bin/python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 & cd web && npx next start -p 7860 -H 0.0.0.0"]
