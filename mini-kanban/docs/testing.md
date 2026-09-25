# Testing Guide for Mini Kanban Board

This document explains how to run different types of tests for the Mini Kanban Board application, including unit tests, integration tests, and end-to-end tests.

## Overview

The Mini Kanban Board application uses a comprehensive testing strategy:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test interactions between components using Docker services
- **End-to-End Tests**: Test the complete user workflow using Playwright

## Test Structure

### Backend Tests
- **Location**: `backend/tests/`
- **Unit Tests**: `test_api.py` - Tests individual API endpoints
- **Integration Tests**: `tests/integration/test_integration.py` - Tests full workflows with PostgreSQL

### Frontend Tests
- **Location**: `frontend/` (using Vitest)
- **Unit Tests**: Tests for React components and utilities
- **Component Tests**: Tests for UI components

### End-to-End Tests
- **Location**: `e2e/`
- **Playwright Tests**: `tests/e2e.spec.ts` - Full user workflow tests

## Running Tests

### Prerequisites

1. Ensure Docker and Docker Compose are installed
2. Install dependencies:
   ```bash
   make install-deps
   ```

### Unit Tests

#### Backend Unit Tests
```bash
cd backend
uv run pytest tests/ -v
```

#### Frontend Unit Tests
```bash
cd frontend
npm test
```

### Integration Tests

#### Using Docker (Recommended)
```bash
make test-integration
```

#### Running Locally
```bash
make test-integration-local
```

The integration tests:
- Use PostgreSQL database from docker-compose
- Test database migrations
- Test user registration and authentication
- Test board creation with default columns
- Test card operations and column movements
- Include a health check fixture that waits for the backend service

### End-to-End Tests

#### Locally (Recommended)
```bash
make test-e2e
```

#### Running Locally
```bash
make test-e2e-local
```

The end-to-end tests:
- Launch the frontend application locally
- Test user registration and login
- Test board creation
- Test card creation and drag-and-drop functionality
- Test card movement between columns
- Verify UI state updates

**Note**: End-to-end tests are designed to run locally against http://localhost:8000, not in Docker containers.

### Running All Tests
```bash
make test-all
```

## Test Configuration

### Docker Compose Services
The `docker-compose.yml` file includes:
- `postgres`: PostgreSQL database service
- `backend`: FastAPI backend service

**Note**: Test and e2e services have been removed. Integration tests now run directly via `docker-compose exec backend`, and e2e tests run locally.

### Environment Variables
Tests use environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `BACKEND_URL`: Backend service URL
- `FRONTEND_URL`: Frontend service URL

**Note**: `.env.test` file has been removed. Integration tests use environment variables from the Docker service.

## "Break It On Purpose" Approach

Following the course methodology, we implement a "break it on purpose" testing strategy:

### Integration Tests
```bash
make break-it-integration
```

This approach:
- Intentionally introduces bugs in the test scenarios
- Verifies that tests catch these failures
- Ensures robust error handling
- Validates the testing framework itself

### End-to-End Tests
```bash
make break-it-e2e
```

This includes:
- Testing invalid user inputs
- Testing edge cases in drag-and-drop
- Testing authentication failures
- Testing network error scenarios

## Test Coverage

### Backend Integration Tests Coverage
- Database migration validation
- User authentication flows
- Board CRUD operations
- Column management
- Card operations
- Permission handling
- Search and filtering

### End-to-End Tests Coverage
- Complete user registration workflow
- Board creation and management
- Card creation and editing
- Drag-and-drop functionality
- Column transitions
- Error handling scenarios
- Authentication state management

## Debugging Tests

### Integration Tests Debugging
1. Check Docker logs:
   ```bash
   make logs
   ```

2. Run tests with verbose output:
   ```bash
   docker-compose exec backend uv run pytest tests/integration/ -v --tb=long
   ```

3. Check database connection:
   ```bash
   make health-check
   ```

4. Run specific test:
   ```bash
   docker-compose exec backend uv run pytest tests/integration/test_integration.py::test_database_migrations_run_successfully -v
   ```

### End-to-End Tests Debugging
1. Run tests headed mode:
   ```bash
   cd e2e && npx playwright test --headed
   ```

2. Run tests in debug mode:
   ```bash
   cd e2e && npx playwright test --debug
   ```

3. View Playwright traces:
   ```bash
   npx playwright show-trace trace.zip
   ```

4. Run specific test:
   ```bash
   cd e2e && npx playwright test tests/e2e.spec.ts --grep "User registration"
   ```

## Continuous Integration

The tests are designed to run in CI/CD environments:

1. **Integration Tests**: Run in Docker containers using `docker-compose exec backend`
2. **E2E Tests**: Run locally in headless mode using Playwright
3. **Parallel Execution**: Tests can run in parallel for faster execution

### CI Configuration Example
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Start services
        run: docker-compose up -d postgres backend
      - name: Wait for services
        run: sleep 15
      - name: Run integration tests
        run: make test-integration

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Start services
        run: docker-compose up -d postgres backend
      - name: Wait for services
        run: sleep 15
      - name: Run e2e tests
        run: make test-e2e
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Data Cleanup**: Tests should clean up after themselves
3. **Realistic Data**: Use realistic test data
4. **Error Handling**: Test both success and failure scenarios
5. **Performance**: Consider test execution time
6. **Documentation**: Keep tests well-documented

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Ensure PostgreSQL is running
   - Check database URL configuration
   - Verify database credentials

2. **Backend Service Not Ready**
   - Use `make health-check` to verify service status
   - Check backend logs with `make logs`

3. **Frontend Not Loading**
   - Ensure backend is running on port 8000
   - Check frontend development server
   - Verify CORS configuration

4. **Test Failures**
   - Check test logs for detailed error messages
   - Verify test data is properly cleaned up
   - Ensure dependencies are installed

### Getting Help

If you encounter issues with tests:
1. Check the troubleshooting section
2. Review the test documentation
3. Run tests locally with verbose output
4. Check Docker service logs
5. Verify environment variables are set correctly