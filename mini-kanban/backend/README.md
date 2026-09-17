# Mini Kanban Board Backend

A FastAPI backend for the Mini Kanban Board application that implements the OpenAPI specification with authentication, in-memory data storage, and comprehensive test coverage.

## Features

- **REST API**: Complete implementation of the OpenAPI specification
- **Authentication**: JWT-based authentication with hashed passwords
- **In-memory Storage**: Fast in-memory data persistence for development
- **Role-based Access**: Owner and participant roles with proper authorization
- **Comprehensive Testing**: Full test suite covering API endpoints, models, and business logic
- **Modular Architecture**: Clean separation of concerns with routers, models, store, and auth modules

## Architecture

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app with CORS and middleware
│   ├── models/              # Pydantic models from OpenAPI spec
│   │   └── __init__.py
│   ├── store/               # In-memory data persistence
│   │   └── __init__.py
│   ├── auth/                # Authentication and authorization
│   │   └── __init__.py
│   └── routers/             # API endpoint modules
│       ├── auth.py
│       ├── boards.py
│       ├── columns.py
│       ├── cards.py
│       ├── participants.py
│       ├── invitations.py
│       └── search.py
├── tests/                   # Comprehensive test suite
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_models.py
│   ├── test_store.py
│   └── test_auth.py
└── pyproject.toml           # Dependencies and project config
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user profile

### Boards
- `GET /boards` - List user's boards
- `POST /boards` - Create a new board
- `GET /boards/{boardId}` - Get board details
- `PUT /boards/{boardId}` - Update board (owner only)
- `DELETE /boards/{boardId}` - Delete board (owner only)

### Columns
- `POST /boards/{boardId}/columns` - Create column (owner only)
- `PUT /boards/{boardId}/columns/{columnId}` - Update column (owner only)
- `DELETE /boards/{boardId}/columns/{columnId}` - Delete column (owner only)
- `PUT /boards/{boardId}/columns/reorder` - Reorder columns (owner only)

### Cards
- `POST /boards/{boardId}/cards` - Create card
- `PUT /boards/{boardId}/cards/{cardId}` - Update card
- `DELETE /boards/{boardId}/cards/{cardId}` - Delete card (creator or owner only)
- `PUT /boards/{boardId}/cards/move` - Move card to different column

### Participants
- `DELETE /boards/{boardId}/participants/{userId}` - Remove participant (owner only)
- `POST /boards/{boardId}/leave` - Leave board (participant only)

### Invitations
- `POST /boards/{boardId}/invitations` - Create invitation (owner only)
- `GET /boards/{boardId}/invitations` - List invitations (owner only)
- `GET /invitations/{token}` - Get invitation by token (no auth required)

### Search
- `GET /boards/{boardId}/cards/search` - Search cards by title
- `GET /boards/{boardId}/cards/filter` - Filter cards by assignee

## Getting Started

### Prerequisites
- Python 3.8+
- uv package manager

### Installation

1. Clone the repository:
```bash
cd mini-kanban/backend
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
uv sync
```

### Running the Application

Start the development server:
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

- Interactive API documentation: `http://localhost:8000/docs`
- Alternative ReDoc documentation: `http://localhost:8000/redoc`

### Testing

Run the test suite:
```bash
uv run pytest tests/ -v
```

Run specific test files:
```bash
uv run pytest tests/test_api.py -v
uv run pytest tests/test_models.py -v
uv run pytest tests/test_store.py -v
uv run pytest tests/test_auth.py -v
```

Run tests with coverage:
```bash
uv run pytest tests/ --cov=app
```

## Data Seeding

The application automatically seeds initial data on startup:
- Test users: `test@example.com` and `admin@example.com`
- Test boards: "Test Board" and "Project Board"
- Test columns: "To Do", "In Progress", "Done"
- Test cards with sample tasks
- Test invitations

## Security Features

- **Password Hashing**: Uses bcrypt for secure password storage
- **JWT Authentication**: Stateless authentication with bearer tokens
- **Role-based Authorization**: Owner and participant roles with proper access control
- **Input Validation**: Comprehensive validation using Pydantic models
- **CORS Support**: Configurable CORS middleware for cross-origin requests

## Development

### Adding New Endpoints

1. Create new router in `app/routers/`
2. Add corresponding tests in `tests/`
3. Update main application in `app/main.py`

### Database Considerations

The current implementation uses in-memory storage for development. For production, you should:

1. Replace the in-memory store with a proper database (PostgreSQL, SQLite, etc.)
2. Add proper database migrations
3. Implement connection pooling
4. Add proper error handling for database operations

### Environment Variables

For production, consider adding environment variables for:
- `SECRET_KEY`: JWT secret key
- `DATABASE_URL`: Database connection string
- `CORS_ORIGINS`: Allowed CORS origins

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is part of the Mini Kanban Board application and follows the same license terms.