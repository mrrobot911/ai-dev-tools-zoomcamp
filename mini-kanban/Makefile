.PHONY: help install install-backend install-dev install-frontend test test-backend test-frontend run run-backend run-frontend build clean lint lint-backend lint-frontend format format-backend format-frontend dev dev-backend dev-frontend

# Default target
help:
	@echo "Mini Kanban Board - Development Commands"
	@echo "========================================"
	@echo ""
	@echo "Installation:"
	@echo "  install           - Install all dependencies for both frontend and backend"
	@echo "  install-backend   - Install backend dependencies with uv"
	@echo "  install-frontend  - Install frontend dependencies with npm"
	@echo "  install-dev       - Install development dependencies only"
	@echo ""
	@echo "Development:"
	@echo "  dev               - Start both frontend and backend in development mode"
	@echo "  dev-backend       - Start backend only"
	@echo "  dev-frontend      - Start frontend only"
	@echo "  run               - Run the application in production mode"
	@echo "  run-backend       - Run backend in production mode"
	@echo "  run-frontend      - Run frontend in production mode"
	@echo ""
	@echo "Testing:"
	@echo "  test              - Run all tests (backend and frontend)"
	@echo "  test-backend      - Run backend tests with pytest"
	@echo "  test-frontend     - Run frontend tests with vitest"
	@echo ""
	@echo "Building:"
	@echo "  build             - Build frontend for production"
	@echo "  build-backend     - Build backend package"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint              - Run linters for both frontend and backend"
	@echo "  lint-backend      - Run Python linter (flake8)"
	@echo "  lint-frontend     - Run ESLint for frontend"
	@echo "  format            - Format code for both frontend and backend"
	@echo "  format-backend    - Format Python code (black, isort)"
	@echo "  format-frontend   - Format TypeScript/JavaScript code (prettier)"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean             - Clean build artifacts and cache"
	@echo "  clean-backend     - Clean Python cache and build artifacts"
	@echo "  clean-frontend    - Clean Node.js build artifacts and cache"

# Installation targets
install:
	@echo "Installing all dependencies..."
	@$(MAKE) install-backend
	@$(MAKE) install-frontend
	@echo "All dependencies installed successfully!"

install-backend:
	@echo "Installing backend dependencies..."
	cd backend && uv sync

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

install-dev:
	@echo "Installing development dependencies..."
	cd backend && uv sync --dev
	cd frontend && npm install

# Development targets
dev:
	@echo "Starting both frontend and backend in development mode..."
	@$(MAKE) dev-backend &
	@$(MAKE) dev-frontend
	@wait

dev-backend:
	@echo "Starting backend in development mode..."
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "Starting frontend in development mode..."
	cd frontend && npm run dev

# Production targets
run:
	@echo "Starting application in production mode..."
	@$(MAKE) run-backend &
	@$(MAKE) run-frontend
	@wait

run-backend:
	@echo "Starting backend in production mode..."
	cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

run-frontend:
	@echo "Starting frontend in production mode..."
	cd frontend && npm run preview

# Testing targets
test:
	@echo "Running all tests..."
	@$(MAKE) test-backend
	@$(MAKE) test-frontend
	@echo "All tests completed!"

test-backend:
	@echo "Running backend tests..."
	cd backend && uv run pytest

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm test

# Building targets
build:
	@echo "Building frontend for production..."
	cd frontend && npm run build

build-backend:
	@echo "Building backend package..."
	cd backend && uv build

# Code quality targets
lint:
	@echo "Running linters..."
	@$(MAKE) lint-backend
	@$(MAKE) lint-frontend
	@echo "Linting completed!"

lint-backend:
	@echo "Running Python linter..."
	cd backend && uv run flake8 app/ tests/

lint-frontend:
	@echo "Running ESLint for frontend..."
	cd frontend && npm run lint

format:
	@echo "Formatting code..."
	@$(MAKE) format-backend
	@$(MAKE) format-frontend
	@echo "Code formatting completed!"

format-backend:
	@echo "Formatting Python code..."
	cd backend && uv run black app/ tests/
	cd backend && uv run isort app/ tests/

format-frontend:
	@echo "Formatting frontend code..."
	cd frontend && npx prettier --write .

# Cleaning targets
clean:
	@echo "Cleaning build artifacts..."
	@$(MAKE) clean-backend
	@$(MAKE) clean-frontend
	@echo "Cleaning completed!"

clean-backend:
	@echo "Cleaning backend artifacts..."
	cd backend && rm -rf .pytest_cache/
	cd backend && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	cd backend && find . -type f -name "*.pyc" -delete
	cd backend && rm -rf build/ dist/ *.egg-info/

clean-frontend:
	@echo "Cleaning frontend artifacts..."
	cd frontend && rm -rf node_modules/.cache/
	cd frontend && rm -rf dist/ build/
	cd frontend && npm run clean 2>/dev/null || true