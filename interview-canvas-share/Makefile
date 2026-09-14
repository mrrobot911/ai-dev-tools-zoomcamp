# Makefile for Interview Canvas Share Application
# Full-stack development with FastAPI backend and React frontend

.PHONY: help install install-deps install-backend install-frontend start start-backend start-frontend stop restart build build-backend build-frontend test test-backend test-frontend lint lint-backend lint-frontend clean format format-backend format-frontend docs dev-setup

# Default target
help:
	@echo "Available commands:"
	@echo "  install-deps     - Install all dependencies for both backend and frontend"
	@echo "  install-backend  - Install backend dependencies using uv"
	@echo "  install-frontend - Install frontend dependencies using npm"
	@echo "  start           - Start both backend and frontend in development mode"
	@echo "  start-backend   - Start FastAPI backend server"
	@echo "  start-frontend  - Start React frontend development server"
	@echo "  stop            - Stop all running services"
	@echo "  restart         - Restart all services"
	@echo "  build           - Build both backend and frontend for production"
	@echo "  build-backend   - Build backend for production"
	@echo "  build-frontend  - Build frontend for production"
	@echo "  test            - Run all tests"
	@echo "  test-backend    - Run backend tests"
	@echo "  test-frontend   - Run frontend tests"
	@echo "  lint            - Run linting for both backend and frontend"
	@echo "  lint-backend    - Run backend linting"
	@echo "  lint-frontend   - Run frontend linting"
	@echo "  format          - Format code for both backend and frontend"
	@echo "  format-backend  - Format backend code"
	@echo "  format-frontend - Format frontend code"
	@echo "  clean           - Clean build artifacts and cache"
	@echo "  docs            - Generate API documentation"
	@echo "  dev-setup       - Initial development setup"

# Development setup
dev-setup:
	@echo "Setting up development environment..."
	@make install-deps
	@echo "Development environment setup complete!"

# Installation
install-deps: install-backend install-frontend

install-backend:
	@echo "Installing backend dependencies..."
	cd backend && uv sync
	@echo "Backend dependencies installed successfully!"

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Frontend dependencies installed successfully!"

# Starting services
start: start-backend start-frontend

start-backend:
	@echo "Starting FastAPI backend server..."
	cd backend && uv run python app/main.py

start-frontend:
	@echo "Starting React frontend development server..."
	cd frontend && npm run dev

stop:
	@echo "Stopping all services..."
	@pkill -f "uvicorn" || true
	@pkill -f "vite" || true
	@echo "All services stopped."

restart: stop start

# Building
build: build-backend build-frontend

build-backend:
	@echo "Building backend..."
	cd backend && uv build
	@echo "Backend built successfully!"

build-frontend:
	@echo "Building frontend..."
	cd frontend && npm run build
	@echo "Frontend built successfully!"

# Testing
test: test-backend test-frontend

test-backend:
	@echo "Running backend tests..."
	cd backend && uv run pytest

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm test

# Linting
lint: lint-backend lint-frontend

lint-backend:
	@echo "Running backend linting..."
	cd backend && uv run ruff check app/

lint-frontend:
	@echo "Running frontend linting..."
	cd frontend && npm run lint

# Formatting
format: format-backend format-frontend

format-backend:
	@echo "Formatting backend code..."
	cd backend && uv run ruff format app/

format-frontend:
	@echo "Formatting frontend code..."
	cd frontend && npm run format

# Cleaning
clean:
	@echo "Cleaning build artifacts and cache..."
	cd backend && rm -rf __pycache__ .pytest_cache .venv
	cd frontend && rm -rf node_modules dist .vite
	@echo "Cleaned successfully!"

# Documentation
docs:
	@echo "Generating API documentation..."
	cd backend && uv run python -c "from app.main import app; print('API docs available at: http://localhost:8000/docs')"
	@echo "API documentation generated!"

# Utility targets
check-deps:
	@echo "Checking dependencies..."
	@which uv > /dev/null || echo "❌ uv not found. Please install uv."
	@which npm > /dev/null || echo "❌ npm not found. Please install Node.js."
	@echo "Dependency check complete."

status:
	@echo "Service status:"
	@pgrep -f "uvicorn" && echo "✅ Backend running" || echo "❌ Backend not running"
	@pgrep -f "vite" && echo "✅ Frontend running" || echo "❌ Frontend not running"