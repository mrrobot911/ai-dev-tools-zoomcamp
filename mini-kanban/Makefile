.PHONY: help test-integration test-e2e test-all clean build

# Default target
help:
	@echo "Available targets:"
	@echo "  test-integration    - Run integration tests in Docker"
	@echo "  test-e2e           - Run Playwright end-to-end tests locally"
	@echo "  test-all           - Run all tests (integration + e2e)"
	@echo "  clean             - Clean up Docker containers and volumes"
	@echo "  build             - Build Docker images"

# Test targets
test-integration:
	@echo "Running integration tests..."
	docker-compose exec backend uv run pytest tests/integration/ -v
	@echo "Integration tests completed"

test-e2e:
	@echo "Running end-to-end tests..."
	cd e2e && npm install && npx playwright test
	@echo "End-to-end tests completed"

test-all: test-integration test-e2e
	@echo "All tests completed"

# Docker targets
build:
	@echo "Building Docker images..."
	docker-compose build

# Clean up
clean:
	@echo "Cleaning up Docker containers and volumes..."
	docker-compose down -v --remove-orphans
	docker system prune -f

# Development helpers
dev-up:
	@echo "Starting services in development mode..."
	docker-compose up -d postgres backend

dev-down:
	@echo "Stopping development services..."
	docker-compose down

logs:
	@echo "Showing logs..."
	docker-compose logs -f

# Run tests locally (without Docker)
test-integration-local:
	@echo "Running integration tests locally..."
	cd backend && DATABASE_URL=postgresql://user:***@localhost:5432/minikanban BACKEND_URL=http://localhost:8000 uv run pytest tests/integration/ -v --tb=short

test-e2e-local:
	@echo "Running end-to-end tests locally..."
	cd e2e && npm install && npx playwright test

# Check if services are healthy
health-check:
	@echo "Checking service health..."
	docker-compose ps
	@echo "Checking backend health..."
	curl http://localhost:8000/health || echo "Backend not healthy"

# Install dependencies
install-deps:
	@echo "Installing dependencies..."
	cd backend && uv sync
	cd e2e && npm install

# Run specific test scenarios
break-it-integration:
	@echo "Running integration tests with 'break it on purpose' approach..."
	docker-compose exec backend uv run pytest tests/integration/ -v
	@echo "Integration tests completed - check for intentional failures"

break-it-e2e:
	@echo "Running end-to-end tests with 'break it on purpose' approach..."
	cd e2e && npm install && npx playwright test
	@echo "End-to-end tests completed - check for intentional failures"