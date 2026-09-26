# Stage 1: Frontend build
FROM node:20-alpine as frontend-builder

WORKDIR /app

# VITE_API_URL is baked at build time; default '' = same-origin (backend serves /app/static)
ARG VITE_API_URL=""
ENV VITE_API_URL=$VITE_API_URL

# Copy only package files first for better layer caching
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies
RUN npm install

# Copy remaining frontend files and build
COPY frontend/ .
RUN npm run build

# Stage 2: Backend runtime
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY backend/pyproject.toml backend/uv.lock backend/README.md ./
COPY backend/alembic.ini ./
COPY backend/alembic/ ./alembic/

# Install Python dependencies
RUN pip install --no-cache-dir uv && uv sync

# Copy backend application code
COPY backend/ .

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/dist /app/static

# Expose port
EXPOSE 8000

# Default command: Render injects $PORT (default 10000); locally falls back to 8000.
# Migrate on start because Render uses this CMD directly (compose override is local-only).
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]