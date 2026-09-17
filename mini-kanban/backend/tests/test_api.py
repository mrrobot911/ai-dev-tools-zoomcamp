import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def cleanup_dbs():
    """Clean up all databases before each test"""
    from app.store import (
        users_db, boards_db, columns_db, cards_db, 
        participants_db, invitations_db, board_participants
    )
    from app.auth import users_db as auth_users_db
    
    # Store original state
    original_state = {
        'users_db': dict(users_db),
        'boards_db': dict(boards_db),
        'columns_db': dict(columns_db),
        'cards_db': dict(cards_db),
        'participants_db': dict(participants_db),
        'invitations_db': dict(invitations_db),
        'board_participants': dict(board_participants),
        'auth_users_db': dict(auth_users_db)
    }
    
    # Clear all databases
    users_db.clear()
    boards_db.clear()
    columns_db.clear()
    cards_db.clear()
    participants_db.clear()
    invitations_db.clear()
    board_participants.clear()
    auth_users_db.clear()
    
    yield
    
    # Restore original state
    users_db.update(original_state['users_db'])
    boards_db.update(original_state['boards_db'])
    columns_db.update(original_state['columns_db'])
    cards_db.update(original_state['cards_db'])
    participants_db.update(original_state['participants_db'])
    invitations_db.update(original_state['invitations_db'])
    board_participants.update(original_state['board_participants'])
    auth_users_db.update(original_state['auth_users_db'])


@pytest.fixture
def test_user():
    """Create a test user"""
    return {
        "email": "test@example.com",
        "password": "testpass123",
        "name": "Test User"
    }


@pytest.fixture
def test_user2():
    """Create another test user"""
    return {
        "email": "test2@example.com",
        "password": "testpass123",
        "name": "Test User 2"
    }


@pytest.fixture
def auth_token(test_user, cleanup_dbs):
    """Get authentication token for test user"""
    response = client.post("/auth/register", json=test_user)
    assert response.status_code == 201
    return response.json()["token"]


@pytest.fixture
def auth_token2(test_user2, cleanup_dbs):
    """Get authentication token for second test user"""
    response = client.post("/auth/register", json=test_user2)
    assert response.status_code == 201
    return response.json()["token"]


@pytest.fixture
def headers(auth_token):
    """Headers with authentication token"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def headers2(auth_token2):
    """Headers with second user's authentication token"""
    return {"Authorization": f"Bearer {auth_token2}"}


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Mini Kanban Board API"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_user_registration(test_user):
    """Test user registration"""
    response = client.post("/auth/register", json=test_user)
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert "token" in data
    assert data["user"]["email"] == test_user["email"]
    assert data["user"]["name"] == test_user["name"]


def test_user_registration_duplicate(test_user):
    """Test user registration with duplicate email"""
    # Register user first time
    client.post("/auth/register", json=test_user)
    
    # Try to register same user again
    response = client.post("/auth/register", json=test_user)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_user_login(test_user):
    """Test user login"""
    # Register user first
    client.post("/auth/register", json=test_user)
    
    # Login
    login_data = {"email": test_user["email"], "password": test_user["password"]}
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "token" in data
    assert data["user"]["email"] == test_user["email"]


def test_user_login_invalid_credentials(test_user):
    """Test user login with invalid credentials"""
    # Register user first
    client.post("/auth/register", json=test_user)
    
    # Login with wrong password
    login_data = {"email": test_user["email"], "password": "wrongpassword"}
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_get_current_user(headers):
    """Test get current user endpoint"""
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    user = response.json()
    assert "email" in user
    assert "name" in user
    assert "id" in user


def test_get_current_user_invalid_token():
    """Test get current user with invalid token"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 401


def test_create_board(headers, test_user):
    """Test creating a board"""
    board_data = {"name": "Test Board"}
    response = client.post("/boards", json=board_data, headers=headers)
    assert response.status_code == 201
    board = response.json()
    assert board["name"] == "Test Board"
    assert "id" in board
    assert "ownerId" in board
    assert "ownerName" in board


def test_list_user_boards(headers):
    """Test listing user's boards"""
    # Create a board first
    board_data = {"name": "Test Board"}
    client.post("/boards", json=board_data, headers=headers)
    
    # List boards
    response = client.get("/boards", headers=headers)
    assert response.status_code == 200
    boards = response.json()
    assert len(boards) == 1
    assert boards[0]["board"]["name"] == "Test Board"


def test_get_board_details(headers):
    """Test getting board details"""
    # Create a board first
    board_data = {"name": "Test Board"}
    create_response = client.post("/boards", json=board_data, headers=headers)
    board_id = create_response.json()["id"]
    
    # Get board details
    response = client.get(f"/boards/{board_id}", headers=headers)
    assert response.status_code == 200
    board = response.json()
    assert board["name"] == "Test Board"
    assert "columns" in board
    assert "cards" in board
    # Should have 3 default columns
    assert len(board["columns"]) == 3
    column_names = [col["name"] for col in board["columns"]]
    assert "To Do" in column_names
    assert "In Progress" in column_names
    assert "Done" in column_names
    assert "participants" in board


def test_get_board_not_found(headers):
    """Test getting non-existent board"""
    import uuid
    fake_board_id = uuid.uuid4()
    response = client.get(f"/boards/{fake_board_id}", headers=headers)
    assert response.status_code == 404


def test_update_board(headers):
    """Test updating a board"""
    # Create a board first
    board_data = {"name": "Test Board"}
    create_response = client.post("/boards", json=board_data, headers=headers)
    board_id = create_response.json()["id"]
    
    # Update board
    update_data = {"name": "Updated Board"}
    response = client.put(f"/boards/{board_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    board = response.json()
    assert board["name"] == "Updated Board"


def test_update_board_not_owner(headers, headers2, test_user, test_user2):
    """Test updating board when not the owner"""
    # User 1 creates a board
    board_data = {"name": "Test Board"}
    create_response = client.post("/boards", json=board_data, headers=headers)
    board_id = create_response.json()["id"]
    
    # User 2 tries to update the board
    update_data = {"name": "Updated Board"}
    response = client.put(f"/boards/{board_id}", json=update_data, headers=headers2)
    assert response.status_code == 403


def test_delete_board(headers):
    """Test deleting a board"""
    # Create a board first
    board_data = {"name": "Test Board"}
    create_response = client.post("/boards", json=board_data, headers=headers)
    board_id = create_response.json()["id"]
    
    # Delete board
    response = client.delete(f"/boards/{board_id}", headers=headers)
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]


def test_create_column(headers):
    """Test creating a column"""
    # Create a board first
    board_data = {"name": "Test Board"}
    create_response = client.post("/boards", json=board_data, headers=headers)
    board_id = create_response.json()["id"]
    
    # Create column
    column_data = {"name": "To Do"}
    response = client.post(f"/boards/{board_id}/columns", json=column_data, headers=headers)
    assert response.status_code == 201
    column = response.json()
    assert column["name"] == "To Do"
    assert "id" in column


def test_create_column_not_owner(headers, headers2, test_user, test_user2):
    """Test creating column when not the owner"""
    # User 1 creates a board
    board_data = {"name": "Test Board"}
    create_response = client.post("/boards", json=board_data, headers=headers)
    board_id = create_response.json()["id"]
    
    # User 2 tries to create a column
    column_data = {"name": "To Do"}
    response = client.post(f"/boards/{board_id}/columns", json=column_data, headers=headers2)
    assert response.status_code == 403


def test_create_card(headers):
    """Test creating a card"""
    # Create a board first
    board_data = {"name": "Test Board"}
    create_response = client.post("/boards", json=board_data, headers=headers)
    board_id = create_response.json()["id"]
    
    # Create a column
    column_data = {"name": "To Do"}
    column_response = client.post(f"/boards/{board_id}/columns", json=column_data, headers=headers)
    column_id = column_response.json()["id"]
    
    # Create card
    card_data = {"title": "Test Card", "columnId": str(column_id)}
    response = client.post(f"/boards/{board_id}/cards", json=card_data, headers=headers)
    assert response.status_code == 201
    card = response.json()
    assert card["title"] == "Test Card"
    assert card["columnId"] == column_id


def test_update_card(headers):
    """Test updating a card"""
    # Create a board and card first
    board_data = {"name": "Test Board"}
    create_response = client.post("/boards", json=board_data, headers=headers)
    board_id = create_response.json()["id"]
    
    column_data = {"name": "To Do"}
    column_response = client.post(f"/boards/{board_id}/columns", json=column_data, headers=headers)
    column_id = column_response.json()["id"]
    
    card_data = {"title": "Test Card", "columnId": str(column_id)}
    card_response = client.post(f"/boards/{board_id}/cards", json=card_data, headers=headers)
    card_id = card_response.json()["id"]
    
    # Update card
    update_data = {"title": "Updated Card"}
    response = client.put(f"/boards/{board_id}/cards/{card_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    card = response.json()
    assert card["title"] == "Updated Card"


def test_delete_card(headers):
    """Test deleting a card"""
    # Create a board and card first
    board_data = {"name": "Test Board"}
    create_response = client.post("/boards", json=board_data, headers=headers)
    board_id = create_response.json()["id"]
    
    column_data = {"name": "To Do"}
    column_response = client.post(f"/boards/{board_id}/columns", json=column_data, headers=headers)
    column_id = column_response.json()["id"]
    
    card_data = {"title": "Test Card", "columnId": str(column_id)}
    card_response = client.post(f"/boards/{board_id}/cards", json=card_data, headers=headers)
    card_id = card_response.json()["id"]
    
    # Delete card
    response = client.delete(f"/boards/{board_id}/cards/{card_id}", headers=headers)
    assert response.status_code == 200
    assert "deleted" in response.json()["message"]


def test_search_cards(headers):
    """Test searching cards"""
    # Create a board and cards first
    board_data = {"name": "Test Board"}
    create_response = client.post("/boards", json=board_data, headers=headers)
    board_id = create_response.json()["id"]
    
    column_data = {"name": "To Do"}
    column_response = client.post(f"/boards/{board_id}/columns", json=column_data, headers=headers)
    column_id = column_response.json()["id"]
    
    # Create multiple cards
    card1_data = {"title": "Important Task", "columnId": str(column_id)}
    card2_data = {"title": "Regular Task", "columnId": str(column_id)}
    client.post(f"/boards/{board_id}/cards", json=card1_data, headers=headers)
    client.post(f"/boards/{board_id}/cards", json=card2_data, headers=headers)
    
    # Search for "important"
    response = client.get(f"/boards/{board_id}/cards/search?query=important", headers=headers)
    assert response.status_code == 200
    cards = response.json()
    assert len(cards) == 1
    assert cards[0]["title"] == "Important Task"


def test_filter_cards(headers):
    """Test filtering cards by assignee"""
    # Create users and board
    user1_data = {"email": "user1@example.com", "password": "pass123", "name": "User 1"}
    user2_data = {"email": "user2@example.com", "password": "pass123", "name": "User 2"}
    
    # Register users
    user1_response = client.post("/auth/register", json=user1_data)
    user2_response = client.post("/auth/register", json=user2_data)
    user1_id = user1_response.json()["user"]["id"]
    user2_id = user2_response.json()["user"]["id"]
    
    # Create board
    board_data = {"name": "Test Board"}
    board_response = client.post("/boards", json=board_data, headers=headers)
    board_id = board_response.json()["id"]
    
    # Create column
    column_data = {"name": "To Do"}
    column_response = client.post(f"/boards/{board_id}/columns", json=column_data, headers=headers)
    column_id = column_response.json()["id"]
    
    # Create cards with different assignees
    card1_data = {"title": "Task 1", "columnId": str(column_id), "assigneeId": str(user1_id)}
    card2_data = {"title": "Task 2", "columnId": str(column_id), "assigneeId": str(user2_id)}
    card3_data = {"title": "Task 3", "columnId": str(column_id)}  # No assignee
    
    client.post(f"/boards/{board_id}/cards", json=card1_data, headers=headers)
    client.post(f"/boards/{board_id}/cards", json=card2_data, headers=headers)
    client.post(f"/boards/{board_id}/cards", json=card3_data, headers=headers)
    
    # Filter by user1
    response = client.get(f"/boards/{board_id}/cards/filter?assigneeId={user1_id}", headers=headers)
    assert response.status_code == 200
    cards = response.json()
    assert len(cards) == 1
    assert cards[0]["title"] == "Task 1"


def test_create_invitation(headers):
    """Test creating an invitation"""
    # Create a board first
    board_data = {"name": "Test Board"}
    create_response = client.post("/boards", json=board_data, headers=headers)
    board_id = create_response.json()["id"]
    
    # Create invitation
    response = client.post(f"/boards/{board_id}/invitations", headers=headers, json={})
    assert response.status_code == 201
    invitation = response.json()
    assert "token" in invitation
    assert not invitation["used"]


def test_list_invitations(headers):
    """Test listing invitations"""
    # Create a board first
    board_data = {"name": "Test Board"}
    create_response = client.post("/boards", json=board_data, headers=headers)
    board_id = create_response.json()["id"]
    
    # Create an invitation
    client.post(f"/boards/{board_id}/invitations", headers=headers, json={})
    
    # List invitations
    response = client.get(f"/boards/{board_id}/invitations", headers=headers)
    assert response.status_code == 200
    invitations = response.json()
    assert len(invitations) == 1
    assert "token" in invitations[0]


def test_get_invitation_by_token(auth_token):
    """Test getting invitation by token"""
    # Create a board and invitation first
    board_data = {"name": "Test Board"}
    create_response = client.post("/boards", json=board_data, headers={"Authorization": f"Bearer {auth_token}"})
    board_id = create_response.json()["id"]
    
    invitation_response = client.post(f"/boards/{board_id}/invitations", headers={"Authorization": f"Bearer {auth_token}"}, json={})
    token = invitation_response.json()["token"]
    
    # Get invitation by token (no auth required)
    response = client.get(f"/boards/invitations/{token}")
    assert response.status_code == 200
    invitation = response.json()
    assert invitation["token"] == token


def test_leave_board(headers, headers2, test_user, test_user2):
    """Test leaving a board"""
    # User 1 creates a board
    board_data = {"name": "Test Board"}
    create_response = client.post("/boards", json=board_data, headers=headers)
    board_id = create_response.json()["id"]
    
    # User 2 cannot leave if they're not a participant (should be 404)
    response = client.post(f"/boards/{board_id}/leave", headers=headers2)
    assert response.status_code == 404


def test_move_card_valid(headers, test_user):
    """Test moving a card to a different column"""
    # Create a board first
    board_data = {"name": "Test Board"}
    create_response = client.post("/boards", json=board_data, headers=headers)
    board_id = create_response.json()["id"]
    
    # Get columns (should have 3 default columns)
    columns_response = client.get(f"/boards/{board_id}", headers=headers)
    columns = columns_response.json()["columns"]
    todo_column = next(col for col in columns if col["name"] == "To Do")
    progress_column = next(col for col in columns if col["name"] == "In Progress")
    
    # Create a card in "To Do"
    card_data = {
        "title": "Test Card",
        "columnId": todo_column["id"]
    }
    card_response = client.post(f"/boards/{board_id}/cards", json=card_data, headers=headers)
    card = card_response.json()
    
    # Move card to "In Progress"
    move_data = {
        "cardId": card["id"],
        "targetColumnId": progress_column["id"]
    }
    move_response = client.put(f"/boards/{board_id}/cards/move", json=move_data, headers=headers)
    assert move_response.status_code == 200
    moved_card = move_response.json()
    assert moved_card["id"] == card["id"]
    assert moved_card["columnId"] == progress_column["id"]


def test_move_card_invalid_card_id(headers, test_user):
    """Test moving a card with invalid card_id"""
    # Create a board first
    board_data = {"name": "Test Board"}
    create_response = client.post("/boards", json=board_data, headers=headers)
    board_id = create_response.json()["id"]
    
    # Get columns
    columns_response = client.get(f"/boards/{board_id}", headers=headers)
    columns = columns_response.json()["columns"]
    progress_column = next(col for col in columns if col["name"] == "In Progress")
    
    # Try to move non-existent card
    fake_card_id = str(uuid4())
    move_data = {
        "cardId": fake_card_id,  # Non-existent card ID
        "targetColumnId": progress_column["id"]
    }
    move_response = client.put(f"/boards/{board_id}/cards/{fake_card_id}/move", json=move_data, headers=headers)
    assert move_response.status_code == 404


def test_move_card_invalid_board_id(headers, test_user):
    """Test moving a card with invalid board_id"""
    # Create a board first to get a valid column ID
    board_data = {"name": "Test Board"}
    create_response = client.post("/boards", json=board_data, headers=headers)
    board_id = create_response.json()["id"]
    
    # Get columns
    columns_response = client.get(f"/boards/{board_id}", headers=headers)
    columns = columns_response.json()["columns"]
    todo_column = next(col for col in columns if col["name"] == "To Do")
    progress_column = next(col for col in columns if col["name"] == "In Progress")
    
    # Create a card
    card_data = {
        "title": "Test Card",
        "columnId": todo_column["id"]
    }
    card_response = client.post(f"/boards/{board_id}/cards", json=card_data, headers=headers)
    card = card_response.json()
    
    # Try to move to non-existent board
    fake_board_id = str(uuid4())
    move_data = {
        "cardId": card["id"],
        "targetColumnId": progress_column["id"]
    }
    move_response = client.put(f"/boards/{fake_board_id}/cards/move", json=move_data, headers=headers)
    assert move_response.status_code == 404


def test_move_card_same_column(headers, test_user):
    """Test moving a card to the same column (should still work)"""
    # Create a board first
    board_data = {"name": "Test Board"}
    create_response = client.post("/boards", json=board_data, headers=headers)
    board_id = create_response.json()["id"]
    
    # Get columns
    columns_response = client.get(f"/boards/{board_id}", headers=headers)
    columns = columns_response.json()["columns"]
    todo_column = next(col for col in columns if col["name"] == "To Do")
    
    # Create a card in "To Do"
    card_data = {
        "title": "Test Card",
        "columnId": todo_column["id"]
    }
    card_response = client.post(f"/boards/{board_id}/cards", json=card_data, headers=headers)
    card = card_response.json()
    
    # Move card to the same column
    move_data = {
        "cardId": card["id"],
        "targetColumnId": todo_column["id"]
    }
    move_response = client.put(f"/boards/{board_id}/cards/move", json=move_data, headers=headers)
    assert move_response.status_code == 200
    moved_card = move_response.json()
    assert moved_card["id"] == card["id"]
    assert moved_card["columnId"] == todo_column["id"]


if __name__ == "__main__":
    pytest.main([__file__])