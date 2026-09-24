# Mini Kanban Board

## Description
A collaborative Kanban board application with real-time updates via Long Polling.
Users can create boards with columns (To Do, In Progress, Done), manage cards 
with drag-and-drop, invite participants via single-use links, and see changes 
from other users in real-time.

## Tech Stack
- Frontend: React + TypeScript + @dnd-kit
- Backend: FastAPI + SQLAlchemy
- Database: SQLite
- Real-time: Long Polling over REST API
- API Contract: OpenAPI

## Prerequisites
- Python 3.8+
- Node.js 18+
- uv (Python package manager)

## Project Structure
```
mini-kanban/
├── AGENTS.md                    # Project instructions
├── Makefile                     # Build and development commands
├── openapi.yaml                 # API specification
├── docs/
│   └── spec.md                  # Product specification
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── database.py         # Database configuration
│   │   ├── database_service.py # Database operations
│   │   ├── models/              # SQLAlchemy models
│   │   ├── routers/             # API endpoints
│   │   └── auth/               # Authentication logic
│   ├── pyproject.toml          # Python dependencies
│   ├── tests/                  # Backend tests
│   └── README.md               # Backend documentation
├── frontend/
│   ├── src/                    # React source code
│   ├── package.json            # Node.js dependencies
│   ├── vite.config.ts          # Vite configuration
│   └── tests/                  # Frontend tests
└── docs/
    └── spec.md                 # Product specification
```

## Installation

### Backend
```bash
# Install backend dependencies
make install-backend
# or
cd backend && uv sync
```

### Frontend
```bash
# Install frontend dependencies
make install-frontend
# or
cd frontend && npm install
```

## Running the Application

### Option 1: Using Makefile (recommended)
```bash
# Start both frontend and backend in development mode
make dev

# Start backend only
make dev-backend

# Start frontend only
make dev-frontend

# Run in production mode
make run

# Run backend in production mode
make run-backend

# Run frontend in production mode
make run-frontend
```

### Option 2: Manual commands
```bash
# Backend (port 8000)
cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend development (port 5174 or 5173)
cd frontend && npm run dev

# Production commands
# Frontend production (port 4173)
cd frontend && npm run preview
cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Frontend (dev):** http://localhost:5174 (or 5173 if available)  
**Frontend (prod):** http://localhost:4173  
**Backend:** http://localhost:8000  
**API docs:** http://localhost:8000/docs

## Running Tests
```bash
# Run all tests
make test

# Run backend tests only
make test-backend
# or
cd backend && uv run pytest

# Run frontend tests only
make test-frontend
# or
cd frontend && npm test
```

## Real-time Features
The application uses Long Polling (GET /api/boards/{board_id}/updates?since=...) 
for real-time updates. Open the same board in two browser tabs to see changes 
propagate between them within 1-3 seconds.

## Database
SQLite database is created automatically on first backend startup. 
Seed data (test user, sample board) is also created automatically.

**Default credentials:**
- Email: test@example.com
- Password: password

To reset the database: Delete the `backend/mini_kanban.db` file

## Default Credentials
The application creates test data automatically:
- **Test User**: test@example.com / password
- **Admin User**: admin@example.com / admin

## Key Features
- **Boards**: Create and manage multiple Kanban boards
- **Columns**: Default columns (To Do, In Progress, Done) with custom naming
- **Cards**: Create, edit, and delete cards with titles, descriptions, and assignees
- **Drag & Drop**: Move cards between columns using @dnd-kit
- **Collaboration**: Real-time updates via long polling
- **Invitations**: Generate single-use invitation links for new participants
- **Search & Filter**: Search cards by title and filter by assignee
- **Permissions**: Owner vs participant roles with different access levels
- **Real-time Sync**: Changes propagate to all connected users within 1-3 seconds

## Development Commands
```bash
# Code quality
make lint           # Run linters for both frontend and backend
make format         # Format code for both frontend and backend

# Building
make build         # Build frontend for production
make build-backend # Build backend package

# Maintenance
make clean         # Clean build artifacts
```

## API Endpoints
- Authentication: `/auth/*`
- Boards: `/boards/*`
- Real-time updates: `/api/boards/{board_id}/updates?since={timestamp}`

## MVP Limits
- Maximum 10 boards per user
- Maximum 10 participants per board
- Maximum 10 columns per board
- Minimum 3 columns per board
- Maximum 100 cards per column