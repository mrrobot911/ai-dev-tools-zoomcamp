import pytest
import requests
import time
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.database import get_engine, reset_engine


@pytest.fixture(scope="session")
def postgres_engine():
    """Create a PostgreSQL engine for integration tests"""
    # Use the DATABASE_URL from environment (will be set by docker-compose)
    database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/minikanban")
    engine = create_engine(database_url)
    return engine


@pytest.fixture(scope="session")
def setup_database(postgres_engine):
    """Set up the database with migrations"""
    # Run migrations
    import subprocess
    import sys
    sys.path.append('/app')
    
    # Reset engine to use the PostgreSQL database
    reset_engine()
    
    # Run alembic upgrade
    result = subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        cwd="/app",
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        pytest.fail(f"Migration failed: {result.stderr}")
    
    yield
    
    # Clean up - drop all tables
    Base.metadata.drop_all(bind=postgres_engine)


@pytest.fixture
def wait_for_backend():
    """Wait for the backend service to be healthy"""
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    max_retries = 30
    retry_delay = 5
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{backend_url}/health", timeout=5)
            if response.status_code == 200:
                return
        except requests.exceptions.RequestException:
            pass
        
        if i < max_retries - 1:
            time.sleep(retry_delay)
    
    pytest.fail(f"Backend service at {backend_url} did not become healthy after {max_retries} retries")


@pytest.fixture
def api_client(wait_for_backend):
    """Create an API client for integration tests"""
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    class TestClient:
        def __init__(self, base_url):
            self.base_url = base_url
        
        def post(self, endpoint, json=None, headers=None):
            url = f"{self.base_url}{endpoint}"
            return requests.post(url, json=json, headers=headers)
        
        def get(self, endpoint, headers=None):
            url = f"{self.base_url}{endpoint}"
            return requests.get(url, headers=headers)
        
        def put(self, endpoint, json=None, headers=None):
            url = f"{self.base_url}{endpoint}"
            return requests.put(url, json=json, headers=headers)
        
        def delete(self, endpoint, headers=None):
            url = f"{self.base_url}{endpoint}"
            return requests.delete(url, headers=headers)
    
    return TestClient(backend_url)


def test_database_migrations_run_successfully(setup_database):
    """Test that database migrations run successfully"""
    # This test passes if setup_database fixture runs without error
    assert True


def test_user_registration_and_authentication_flow(api_client):
    """Test user registration and authentication flow"""
    # Register a new user with unique email
    import uuid
    user_data = {
        "email": f"test-{uuid.uuid4()}@example.com",
        "password": "testpass123",
        "name": "Test User"
    }
    
    response = api_client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert "token" in data
    assert data["user"]["email"] == user_data["email"]
    assert data["user"]["name"] == user_data["name"]
    
    # Login with the same user
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    response = api_client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "token" in data
    assert data["user"]["email"] == user_data["email"]
    
    # Get current user info
    headers = {"Authorization": f"Bearer {data['token']}"}
    response = api_client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    user = response.json()
    assert user["email"] == user_data["email"]
    assert user["name"] == user_data["name"]


def test_creating_board_with_default_columns(api_client):
    """Test creating a board with default columns"""
    # First register a user with unique email
    import uuid
    user_data = {
        "email": f"boarduser-{uuid.uuid4()}@example.com",
        "password": "boardpass123",
        "name": "Board User"
    }
    
    response = api_client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    token = response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a board
    board_data = {"name": "Test Board"}
    response = api_client.post("/boards", json=board_data, headers=headers)
    assert response.status_code == 201
    board = response.json()
    assert board["name"] == board_data["name"]
    assert "id" in board
    assert "ownerId" in board
    
    # Get board details to check columns
    board_id = board["id"]
    response = api_client.get(f"/boards/{board_id}", headers=headers)
    assert response.status_code == 200
    board_details = response.json()
    
    # Verify default columns exist
    columns = board_details["columns"]
    assert len(columns) == 3
    column_names = [col["name"] for col in columns]
    assert "To Do" in column_names
    assert "In Progress" in column_names
    assert "Done" in column_names
    
    # Verify column IDs are present
    for col in columns:
        assert "id" in col


def test_adding_cards_to_columns(api_client):
    """Test adding cards to columns"""
    # Register a user with unique email
    import uuid
    user_data = {
        "email": f"carduser-{uuid.uuid4()}@example.com",
        "password": "cardpass123",
        "name": "Card User"
    }
    
    response = api_client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    token = response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a board
    board_data = {"name": "Card Test Board"}
    response = api_client.post("/boards", json=board_data, headers=headers)
    assert response.status_code == 201
    board_id = response.json()["id"]
    
    # Get board details to get column IDs
    response = api_client.get(f"/boards/{board_id}", headers=headers)
    assert response.status_code == 200
    board = response.json()
    todo_column = next(col for col in board["columns"] if col["name"] == "To Do")
    
    # Add a card to the "To Do" column
    card_data = {
        "title": "Test Card",
        "columnId": todo_column["id"]
    }
    
    response = api_client.post(f"/boards/{board_id}/cards", json=card_data, headers=headers)
    assert response.status_code == 201
    card = response.json()
    assert card["title"] == card_data["title"]
    assert card["columnId"] == todo_column["id"]
    assert "id" in card
    
    # Verify the card appears in the board
    response = api_client.get(f"/boards/{board_id}", headers=headers)
    assert response.status_code == 200
    updated_board = response.json()
    cards_in_column = [c for c in updated_board["cards"] if c["columnId"] == todo_column["id"]]
    assert len(cards_in_column) == 1
    assert cards_in_column[0]["title"] == "Test Card"


def test_moving_cards_between_columns(api_client):
    """Test moving cards between columns"""
    # Register a user with unique email
    import uuid
    user_data = {
        "email": f"moveuser-{uuid.uuid4()}@example.com",
        "password": "movepass123",
        "name": "Move User"
    }
    
    response = api_client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    token = response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a board
    board_data = {"name": "Move Test Board"}
    response = api_client.post("/boards", json=board_data, headers=headers)
    assert response.status_code == 201
    board_id = response.json()["id"]
    
    # Get board details to get column IDs
    response = api_client.get(f"/boards/{board_id}", headers=headers)
    assert response.status_code == 200
    board = response.json()
    todo_column = next(col for col in board["columns"] if col["name"] == "To Do")
    progress_column = next(col for col in board["columns"] if col["name"] == "In Progress")
    
    # Add a card to the "To Do" column
    card_data = {
        "title": "Test Card to Move",
        "columnId": todo_column["id"]
    }
    
    response = api_client.post(f"/boards/{board_id}/cards", json=card_data, headers=headers)
    assert response.status_code == 201
    card = response.json()
    card_id = card["id"]
    
    # Move the card to "In Progress"
    move_data = {
        "cardId": card_id,
        "targetColumnId": progress_column["id"]
    }
    
    response = api_client.put(f"/boards/{board_id}/cards/move", json=move_data, headers=headers)
    assert response.status_code == 200
    moved_card = response.json()
    assert moved_card["id"] == card_id
    assert moved_card["columnId"] == progress_column["id"]
    
    # Verify the card has moved
    response = api_client.get(f"/boards/{board_id}", headers=headers)
    assert response.status_code == 200
    updated_board = response.json()
    
    # Check card is no longer in "To Do"
    todo_cards = [c for c in updated_board["cards"] if c["columnId"] == todo_column["id"]]
    assert len(todo_cards) == 0
    
    # Check card is now in "In Progress"
    progress_cards = [c for c in updated_board["cards"] if c["columnId"] == progress_column["id"]]
    assert len(progress_cards) == 1
    assert progress_cards[0]["id"] == card_id
    assert progress_cards[0]["title"] == "Test Card to Move"


def test_end_to_end_workflow(api_client):
    """Test a complete end-to-end workflow"""
    # Register a user with unique email
    import uuid
    user_data = {
        "email": f"workflowuser-{uuid.uuid4()}@example.com",
        "password": "workflowpass123",
        "name": "Workflow User"
    }
    
    response = api_client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    token = response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a board
    board_data = {"name": "Workflow Test Board"}
    response = api_client.post("/boards", json=board_data, headers=headers)
    assert response.status_code == 201
    board_id = response.json()["id"]
    
    # Get board details
    response = api_client.get(f"/boards/{board_id}", headers=headers)
    assert response.status_code == 200
    board = response.json()
    
    # Verify default columns
    todo_column = next(col for col in board["columns"] if col["name"] == "To Do")
    progress_column = next(col for col in board["columns"] if col["name"] == "In Progress")
    done_column = next(col for col in board["columns"] if col["name"] == "Done")
    
    # Add multiple cards to "To Do"
    card1_data = {"title": "Task 1", "columnId": todo_column["id"]}
    card2_data = {"title": "Task 2", "columnId": todo_column["id"]}
    
    response1 = api_client.post(f"/boards/{board_id}/cards", json=card1_data, headers=headers)
    response2 = api_client.post(f"/boards/{board_id}/cards", json=card2_data, headers=headers)
    
    assert response1.status_code == 201
    assert response2.status_code == 201
    card1_id = response1.json()["id"]
    card2_id = response2.json()["id"]
    
    # Move card1 to "In Progress"
    move_data1 = {"cardId": card1_id, "targetColumnId": progress_column["id"]}
    response = api_client.put(f"/boards/{board_id}/cards/move", json=move_data1, headers=headers)
    assert response.status_code == 200
    
    # Move card1 to "Done"
    move_data2 = {"cardId": card1_id, "targetColumnId": done_column["id"]}
    response = api_client.put(f"/boards/{board_id}/cards/move", json=move_data2, headers=headers)
    assert response.status_code == 200
    
    # Move card2 to "In Progress"
    move_data3 = {"cardId": card2_id, "targetColumnId": progress_column["id"]}
    response = api_client.put(f"/boards/{board_id}/cards/move", json=move_data3, headers=headers)
    assert response.status_code == 200
    
    # Verify final state
    response = api_client.get(f"/boards/{board_id}", headers=headers)
    assert response.status_code == 200
    final_board = response.json()
    
    # Count cards in each column
    todo_cards = [c for c in final_board["cards"] if c["columnId"] == todo_column["id"]]
    progress_cards = [c for c in final_board["cards"] if c["columnId"] == progress_column["id"]]
    done_cards = [c for c in final_board["cards"] if c["columnId"] == done_column["id"]]
    
    assert len(todo_cards) == 0
    assert len(progress_cards) == 1
    assert len(done_cards) == 1
    assert progress_cards[0]["id"] == card2_id
    assert done_cards[0]["id"] == card1_id