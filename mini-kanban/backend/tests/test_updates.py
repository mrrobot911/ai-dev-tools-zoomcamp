import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
import os

# Override database URL for tests
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Run migrations for test database
import subprocess
import sys
sys.path.append('/home/kelwin/Документы/ai-dev-tools-zoomcamp/mini-kanban/backend')
subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', 'head'], cwd='/home/kelwin/Документы/ai-dev-tools-zoomcamp/mini-kanban/backend')

client = TestClient(app)

@pytest.fixture
def cleanup_dbs():
    """Clean up all databases before each test"""
    # Clear the test database by dropping and recreating tables
    from app.database import Base, engine
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    # Recreate all tables
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Clean up again after test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@pytest.fixture
def test_user():
    """Create a test user"""
    return {
        "email": f"test-{uuid4()}@example.com",
        "password": "testpass123",
        "name": "Test User"
    }

@pytest.fixture
def auth_token(test_user, cleanup_dbs):
    """Get authentication token for test user"""
    response = client.post("/auth/register", json=test_user)
    assert response.status_code == 201
    return response.json()["token"]

@pytest.fixture
def headers(auth_token):
    """Headers with authentication token"""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def test_board(auth_token, cleanup_dbs):
    """Create a test board"""
    response = client.post("/boards", json={"name": "Test Board"}, headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 201
    return response.json()

def test_get_updates_with_changes(test_board, auth_token):
    """Test that updates endpoint returns changes after 'since' timestamp"""
    # Create a change after the current time
    from app.database import get_db
    from app.database_service import DatabaseService
    from datetime import datetime, timezone
    
    with get_db() as db:
        service = DatabaseService(db)
    
        # Get a timestamp before making changes
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
        # Wait a bit to ensure different timestamps
        import time
        time.sleep(1)
    
        # Create a new card
        columns = service.get_columns_by_board(test_board["id"])
        column_id = columns[0]["id"] if columns else None
    
        if column_id:
            card = service.create_card(
                test_board["id"], column_id, "New Card",
                test_board["ownerId"], test_board["ownerName"]
            )
    
            # Get updates with the timestamp before the change
            response = client.get(
                f"/api/boards/{test_board['id']}/updates?since={timestamp}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
    
            assert response.status_code == 200
            data = response.json()
    
            # Should have at least one change
            assert len(data) > 0
            
            # Check that the change is for the new card
            card_changes = [change for change in data if change["entity_type"] == "card"]
            assert len(card_changes) > 0
            assert card_changes[0]["entity_id"] == card.id
            assert card_changes[0]["action"] == "updated"

def test_get_updates_empty_on_timeout(test_board, auth_token):
    """Test that updates endpoint returns empty list on timeout"""
    # Use a recent timestamp to ensure no changes exist
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Mock the sleep to make tests faster
    with patch('asyncio.sleep', return_value=None):
        response = client.get(
            f"/api/boards/{test_board['id']}/updates?since={timestamp}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        # Should return empty list after timeout
        assert data == []

def test_get_updates_immediate_when_changes_exist(test_board, auth_token):
    """Test that updates endpoint returns immediately when changes exist"""
    # Create a change first
    from app.database import get_db
    from app.database_service import DatabaseService
    from datetime import datetime, timezone
    
    with get_db() as db:
        service = DatabaseService(db)
    
        # Get a timestamp before making changes
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
        columns = service.get_columns_by_board(test_board["id"])
        column_id = columns[0]["id"] if columns else None
    
        if column_id:
            card = service.create_card(
                test_board["id"], column_id, "Test Card",
                test_board["ownerId"], test_board["ownerName"]
            )
    
            # Get updates with the timestamp before the change
            response = client.get(
                f"/api/boards/{test_board['id']}/updates?since={timestamp}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
    
            assert response.status_code == 200
            data = response.json()
    
            # Should return changes immediately
            assert len(data) > 0

def test_get_updates_requires_authentication(test_board):
    """Test that updates endpoint requires authentication"""
    response = client.get(f"/api/boards/{test_board['id']}/updates?since=2026-01-01T00:00:00Z")
    
    assert response.status_code == 401

def test_get_updates_forbidden_for_non_participant(test_board, auth_token):
    """Test that updates endpoint returns 403 if user not a board participant"""
    # Create another user who is not a participant
    from app.database import get_db
    from app.database_service import DatabaseService
    
    with get_db() as db:
        service = DatabaseService(db)
        other_user = service.create_user("other@example.com", "Other User", "hashed_password")
        
        # Try to get updates with the other user's token
        from app.auth import create_access_token
        other_token = create_access_token(data={"sub": str(other_user.id)})
        
        response = client.get(
            f"/api/boards/{test_board['id']}/updates?since=2026-01-01T00:00:00Z",
            headers={"Authorization": f"Bearer {other_token}"}
        )
        
        assert response.status_code == 403

def test_get_updates_invalid_timestamp_format(test_board, auth_token):
    """Test that updates endpoint returns 400 for invalid timestamp format"""
    response = client.get(
        f"/api/boards/{test_board['id']}/updates?since=invalid-timestamp",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 400
    assert "Invalid timestamp format" in response.json()["detail"]

def test_get_updates_board_not_found(auth_token):
    """Test that updates endpoint returns 404 for non-existent board"""
    non_existent_board_id = str(uuid4())
    
    response = client.get(
        f"/boards/{non_existent_board_id}/updates?since=2026-01-01T00:00:00Z",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 404
    assert "Not Found" in response.json()["detail"]

def test_get_updates_multiple_entity_types(test_board, auth_token):
    """Test that updates endpoint returns changes for all entity types"""
    from app.database import get_db
    from app.database_service import DatabaseService
    from datetime import datetime, timezone
    
    with get_db() as db:
        service = DatabaseService(db)
    
        # Get a timestamp before making changes
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
        # Update board
        service.update_board(test_board["id"], "Updated Board Name", test_board["ownerId"])
    
        # Create column
        column = service.create_column(test_board["id"], "New Column")
    
        # Create card
        card = service.create_card(
            test_board["id"], str(column.id), "New Card",
            test_board["ownerId"], test_board["ownerName"]
        )
    
        # Get updates
        response = client.get(
            f"/api/boards/{test_board['id']}/updates?since={timestamp}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
        assert response.status_code == 200
        data = response.json()
    
        # Should have changes for different entity types
        entity_types = {change["entity_type"] for change in data}
        assert "board" in entity_types
        assert "column" in entity_types
        assert "card" in entity_types

def test_get_updates_sorted_by_timestamp(test_board, auth_token):
    """Test that updates are sorted by timestamp"""
    from app.database import get_db
    from app.database_service import DatabaseService
    
    with get_db() as db:
        service = DatabaseService(db)
        
        # Create changes with different timestamps
        import time
        time.sleep(1)  # Ensure different timestamps
        
        # Update board
        service.update_board(test_board["id"], "First Update", test_board["ownerId"])
        time.sleep(1)
        
        # Create column
        column = service.create_column(test_board["id"], "Column Update")
        time.sleep(1)
        
        # Create card
        card = service.create_card(
            test_board["id"], str(column.id), "Card Update",
            test_board["ownerId"], test_board["ownerName"]
        )
        
        # Get updates
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        response = client.get(
            f"/api/boards/{test_board['id']}/updates?since={timestamp}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that changes are sorted by timestamp
        timestamps = [change["timestamp"] for change in data]
        assert timestamps == sorted(timestamps)