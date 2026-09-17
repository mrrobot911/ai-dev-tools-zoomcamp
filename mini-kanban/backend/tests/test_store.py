import pytest
from datetime import datetime
from uuid import uuid4
from app.store import (
    create_user, get_user_by_email, get_user_by_id,
    create_board, get_board_by_id, get_user_boards, update_board, delete_board,
    create_column, get_columns_by_board, update_column, delete_column, reorder_columns,
    create_card, get_cards_by_board, get_card_by_id, update_card, delete_card, move_card,
    create_participant, get_participants_by_board, remove_participant,
    create_invitation, get_invitations_by_board, get_invitation_by_token, use_invitation,
    users_db, boards_db, columns_db, cards_db, participants_db, invitations_db, board_participants
)
from app.auth import get_password_hash
from app.models import UserRole


@pytest.fixture
def cleanup_dbs():
    """Clean up databases before each test"""
    users_db.clear()
    boards_db.clear()
    columns_db.clear()
    cards_db.clear()
    participants_db.clear()
    invitations_db.clear()
    board_participants.clear()


def test_create_user(cleanup_dbs):
    """Test creating a user"""
    user = create_user("test@example.com", "Test User", get_password_hash("password"))
    
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.id in users_db
    assert "password" in users_db[user.id]


def test_get_user_by_email(cleanup_dbs):
    """Test getting user by email"""
    # Create user
    create_user("test@example.com", "Test User", get_password_hash("password"))
    
    # Get user by email
    user = get_user_by_email("test@example.com")
    
    assert user is not None
    assert user.email == "test@example.com"
    assert user.name == "Test User"


def test_get_user_by_email_not_found(cleanup_dbs):
    """Test getting non-existent user by email"""
    user = get_user_by_email("nonexistent@example.com")
    assert user is None


def test_get_user_by_id(cleanup_dbs):
    """Test getting user by ID"""
    # Create user
    user = create_user("test@example.com", "Test User", get_password_hash("password"))
    
    # Get user by ID
    retrieved_user = get_user_by_id(user.id)
    
    assert retrieved_user is not None
    assert retrieved_user.id == user.id
    assert retrieved_user.email == "test@example.com"
    assert retrieved_user.name == "Test User"


def test_get_user_by_id_not_found(cleanup_dbs):
    """Test getting non-existent user by ID"""
    fake_id = uuid4()
    user = get_user_by_id(fake_id)
    assert user is None


def test_create_board(cleanup_dbs):
    """Test creating a board"""
    owner_id = uuid4()
    owner_name = "Test Owner"
    
    # Create user first
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    assert board.name == "Test Board"
    assert board.ownerId == user.id
    assert board.ownerName == owner_name
    assert board.id in boards_db
    
    # Check that owner is automatically added as participant
    assert board.id in board_participants
    assert user.id in board_participants[board.id]
    
    # Check that owner is added to participants_db
    assert board.id in participants_db
    assert len(participants_db[board.id]) == 1


def test_get_board_by_id(cleanup_dbs):
    """Test getting board by ID"""
    # Create user first
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    # Get board by ID
    retrieved_board = get_board_by_id(board.id)
    
    assert retrieved_board is not None
    assert retrieved_board.id == board.id
    assert retrieved_board.name == "Test Board"
    assert retrieved_board.ownerId == user.id
    assert retrieved_board.ownerName == owner_name


def test_get_board_by_id_not_found(cleanup_dbs):
    """Test getting non-existent board by ID"""
    fake_id = uuid4()
    board = get_board_by_id(fake_id)
    assert board is None


def test_get_user_boards(cleanup_dbs):
    """Test getting user's boards"""
    # Create user
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    # Create boards
    board1 = create_board("Board 1", user.id, user.name)
    board2 = create_board("Board 2", user.id, user.name)
    
    # Get user's boards
    user_boards = get_user_boards(user.id)
    
    assert len(user_boards) == 2
    assert board1.id in [b.board.id for b in user_boards]
    assert board2.id in [b.board.id for b in user_boards]


def test_get_user_boards_no_boards(cleanup_dbs):
    """Test getting user's boards when user has no boards"""
    # Create user
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    # Get user's boards
    user_boards = get_user_boards(user.id)
    
    assert len(user_boards) == 0


def test_update_board(cleanup_dbs):
    """Test updating a board"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    # Update board
    updated_board = update_board(board.id, "Updated Board Name", user.id)
    
    assert updated_board is not None
    assert updated_board.id == board.id
    assert updated_board.name == "Updated Board Name"
    assert updated_board.ownerId == user.id
    assert updated_board.ownerName == owner_name


def test_update_board_not_found(cleanup_dbs):
    """Test updating non-existent board"""
    fake_id = uuid4()
    board = update_board(fake_id, "Updated Name", fake_id)
    assert board is None


def test_delete_board(cleanup_dbs):
    """Test deleting a board"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    # Delete board
    deleted = delete_board(board.id)
    
    assert deleted is True
    assert board.id not in boards_db
    assert board.id not in participants_db
    assert board.id not in board_participants


def test_delete_board_not_found(cleanup_dbs):
    """Test deleting non-existent board"""
    fake_id = uuid4()
    board = delete_board(fake_id)
    assert board is False


def test_create_column(cleanup_dbs):
    """Test creating a column"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))

    board = create_board("Test Board", user.id, user.name)
    
    # Board should have 3 default columns
    default_columns = get_columns_by_board(board.id)
    assert len(default_columns) == 3
    
    # Create a new column
    column = create_column(board.id, "To Do")
    
    assert column.name == "To Do"
    assert column.boardId == board.id
    assert column.id in columns_db
    # New column should have order 3 (after the 3 default columns)
    assert column.order == 3


def test_get_columns_by_board(cleanup_dbs):
    """Test getting columns by board"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))

    board = create_board("Test Board", user.id, user.name)
    
    # Board should have 3 default columns
    columns = get_columns_by_board(board.id)
    assert len(columns) == 3
    
    # Create additional columns
    column1 = create_column(board.id, "To Do")
    column2 = create_column(board.id, "In Progress")
    
    # Get columns by board again
    all_columns = get_columns_by_board(board.id)
    assert len(all_columns) == 5  # 3 default + 2 new
    assert column1.id in [c.id for c in all_columns]
    assert column2.id in [c.id for c in all_columns]


def test_get_columns_by_board_no_columns(cleanup_dbs):
    """Test getting columns for board with no columns"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))

    board = create_board("Test Board", user.id, user.name)
    
    # Board should have 3 default columns, not 0
    columns = get_columns_by_board(board.id)
    assert len(columns) == 3


def test_update_column(cleanup_dbs):
    """Test updating a column"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    column = create_column(board.id, "To Do")
    
    # Update column
    updated_column = update_column(column.id, "Updated Name", 5)
    
    assert updated_column is not None
    assert updated_column.id == column.id
    assert updated_column.name == "Updated Name"
    assert updated_column.order == 5


def test_update_column_not_found(cleanup_dbs):
    """Test updating non-existent column"""
    fake_id = uuid4()
    column = update_column(fake_id, "Updated Name", 5)
    assert column is None


def test_delete_column(cleanup_dbs):
    """Test deleting a column"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    column = create_column(board.id, "To Do")
    
    # Delete column
    deleted = delete_column(column.id)
    
    assert deleted is True
    assert column.id not in columns_db


def test_delete_column_not_found(cleanup_dbs):
    """Test deleting non-existent column"""
    fake_id = uuid4()
    column = delete_column(fake_id)
    assert column is False


def test_reorder_columns(cleanup_dbs):
    """Test reordering columns"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))

    board = create_board("Test Board", user.id, user.name)
    
    # Board should have 3 default columns
    default_columns = get_columns_by_board(board.id)
    assert len(default_columns) == 3
    
    # Create additional columns
    column1 = create_column(board.id, "To Do")
    column2 = create_column(board.id, "In Progress")
    
    # Reorder columns - put the new ones first
    reordered_columns = reorder_columns(board.id, [column2.id, column1.id] + [c.id for c in default_columns])
    
    assert len(reordered_columns) == 5  # 3 default + 2 new
    assert reordered_columns[0].id == column2.id
    assert reordered_columns[1].id == column1.id
    # Default columns should follow in their original order
    assert reordered_columns[2].id == default_columns[0].id
    assert reordered_columns[3].id == default_columns[1].id
    assert reordered_columns[4].id == default_columns[2].id
    assert reordered_columns[0].id == column2.id
    assert reordered_columns[0].order == 0
    assert reordered_columns[1].id == column1.id
    assert reordered_columns[1].order == 1


def test_reorder_columns_not_found(cleanup_dbs):
    """Test reordering columns for non-existent board"""
    fake_id = uuid4()
    fake_column_id = uuid4()
    columns = reorder_columns(fake_id, [fake_column_id])
    assert len(columns) == 0


def test_create_card(cleanup_dbs):
    """Test creating a card"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    # Create column
    column = create_column(board.id, "To Do")
    
    # Create card
    card = create_card(board.id, column.id, "Test Card", user.id, user.name)
    
    assert card.title == "Test Card"
    assert card.boardId == board.id
    assert card.columnId == column.id
    assert card.creatorId == user.id
    assert card.creatorName == user.name
    assert card.id in cards_db


def test_get_cards_by_board(cleanup_dbs):
    """Test getting cards by board"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    # Create column and cards
    column = create_column(board.id, "To Do")
    card1 = create_card(board.id, column.id, "Card 1", user.id, user.name)
    card2 = create_card(board.id, column.id, "Card 2", user.id, user.name)
    
    # Get cards by board
    cards = get_cards_by_board(board.id)
    
    assert len(cards) == 2
    assert card1.id in [c.id for c in cards]
    assert card2.id in [c.id for c in cards]


def test_get_card_by_id(cleanup_dbs):
    """Test getting card by ID"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    # Create column and card
    column = create_column(board.id, "To Do")
    card = create_card(board.id, column.id, "Test Card", user.id, user.name)
    
    # Get card by ID
    retrieved_card = get_card_by_id(card.id)
    
    assert retrieved_card is not None
    assert retrieved_card.id == card.id
    assert retrieved_card.title == "Test Card"
    assert retrieved_card.boardId == board.id
    assert retrieved_card.columnId == column.id


def test_get_card_by_id_not_found(cleanup_dbs):
    """Test getting non-existent card by ID"""
    fake_id = uuid4()
    card = get_card_by_id(fake_id)
    assert card is None


def test_update_card(cleanup_dbs):
    """Test updating a card"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    # Create column and card
    column = create_column(board.id, "To Do")
    card = create_card(board.id, column.id, "Test Card", user.id, user.name)
    
    # Update card
    updated_card = update_card(card.id, "Updated Card", "Updated description", user.id, user.name)
    
    assert updated_card is not None
    assert updated_card.id == card.id
    assert updated_card.title == "Updated Card"
    assert updated_card.description == "Updated description"
    assert updated_card.assigneeId == user.id
    assert updated_card.assigneeName == user.name


def test_update_card_not_found(cleanup_dbs):
    """Test updating non-existent card"""
    fake_id = uuid4()
    card = update_card(fake_id, "Updated Title", "Updated description", fake_id, "Updated User")
    assert card is None


def test_delete_card(cleanup_dbs):
    """Test deleting a card"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    # Create column and card
    column = create_column(board.id, "To Do")
    card = create_card(board.id, column.id, "Test Card", user.id, user.name)
    
    # Delete card
    deleted = delete_card(card.id)
    
    assert deleted is True
    assert card.id not in cards_db


def test_delete_card_not_found(cleanup_dbs):
    """Test deleting non-existent card"""
    fake_id = uuid4()
    card = delete_card(fake_id)
    assert card is False


def test_move_card(cleanup_dbs):
    """Test moving a card"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    # Create columns
    column1 = create_column(board.id, "To Do")
    column2 = create_column(board.id, "In Progress")
    
    # Create card
    card = create_card(board.id, column1.id, "Test Card", user.id, user.name)
    
    # Move card
    moved_card = move_card(card.id, column2.id)
    
    assert moved_card is not None
    assert moved_card.id == card.id
    assert moved_card.columnId == column2.id


def test_move_card_not_found(cleanup_dbs):
    """Test moving non-existent card"""
    fake_id = uuid4()
    fake_column_id = uuid4()
    card = move_card(fake_id, fake_column_id)
    assert card is None


def test_create_participant(cleanup_dbs):
    """Test creating a participant"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    # Create participant
    participant = create_participant(board.id, user.id, user.name, UserRole.PARTICIPANT)
    
    assert participant.userId == user.id
    assert participant.email == f"owner_{owner_id}@test.com"
    assert participant.name == user.name
    assert participant.role == UserRole.PARTICIPANT
    assert participant.model_dump() in participants_db[board.id]


def test_get_participants_by_board(cleanup_dbs):
    """Test getting participants by board"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    # Create participants - first user already exists, second one needs to be created
    # Owner is already added as participant by create_board, so we only need to add the second user
    user2_id = uuid4()
    # Create the user using the auth module directly to get the specific ID
    from app.auth import auth_create_user
    user2 = auth_create_user(f"user2_{user2_id}@test.com", "Another User", get_password_hash("password"), user2_id)
    participant2 = create_participant(board.id, user2_id, "Another User", UserRole.PARTICIPANT)
    
    # Get participants by board
    participants = get_participants_by_board(board.id)
    
    assert len(participants) == 2
    # Owner should be there
    assert any(p.userId == user.id for p in participants)
    assert any(p.role == UserRole.OWNER for p in participants)
    # Second user should be there
    assert any(p.userId == user2_id for p in participants)
    assert any(p.role == UserRole.PARTICIPANT for p in participants)


def test_get_participants_by_board_no_participants(cleanup_dbs):
    """Test getting participants for board with no participants"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    # Get participants by board
    participants = get_participants_by_board(board.id)
    
    # Owner should be automatically added as participant
    assert len(participants) == 1
    assert participants[0].userId == user.id
    assert participants[0].role == UserRole.OWNER


def test_remove_participant(cleanup_dbs):
    """Test removing a participant"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    # Create participant
    participant = create_participant(board.id, user.id, user.name, UserRole.PARTICIPANT)
    
    # Remove participant
    removed = remove_participant(board.id, user.id)
    
    assert removed is True
    assert not any(p["userId"] == user.id for p in participants_db[board.id])


def test_remove_participant_not_found(cleanup_dbs):
    """Test removing non-existent participant"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    fake_id = uuid4()
    participant = remove_participant(board.id, fake_id)
    assert participant is False


def test_create_invitation(cleanup_dbs):
    """Test creating an invitation"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    # Create invitation
    invitation = create_invitation(board.id, board.name, user.id)
    
    assert invitation.boardId == board.id
    assert invitation.boardName == board.name
    assert invitation.createdBy == user.id
    assert invitation.used == False
    assert invitation.id in invitations_db


def test_get_invitations_by_board(cleanup_dbs):
    """Test getting invitations by board"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    # Create invitations
    invitation1 = create_invitation(board.id, board.name, user.id)
    invitation2 = create_invitation(board.id, board.name, user.id)
    
    # Get invitations by board
    invitations = get_invitations_by_board(board.id)
    
    assert len(invitations) == 2
    assert invitation1.id in [i.id for i in invitations]
    assert invitation2.id in [i.id for i in invitations]


def test_get_invitations_by_board_no_invitations(cleanup_dbs):
    """Test getting invitations for board with no invitations"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    # Get invitations by board
    invitations = get_invitations_by_board(board.id)
    
    assert len(invitations) == 0


def test_get_invitation_by_token(cleanup_dbs):
    """Test getting invitation by token"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    # Create invitation
    invitation = create_invitation(board.id, board.name, user.id)
    
    # Get invitation by token
    retrieved_invitation = get_invitation_by_token(invitation.token)
    
    assert retrieved_invitation is not None
    assert retrieved_invitation.id == invitation.id
    assert retrieved_invitation.boardId == board.id
    assert retrieved_invitation.boardName == board.name
    assert retrieved_invitation.createdBy == user.id


def test_get_invitation_by_token_not_found(cleanup_dbs):
    """Test getting non-existent invitation by token"""
    fake_token = "fake-token"
    invitation = get_invitation_by_token(fake_token)
    assert invitation is None


def test_use_invitation(cleanup_dbs):
    """Test using an invitation"""
    # Create user and board
    owner_id = uuid4()
    owner_name = "Test Owner"
    user = create_user(f"owner_{owner_id}@test.com", owner_name, get_password_hash("password"))
    
    board = create_board("Test Board", user.id, user.name)
    
    # Create invitation
    invitation = create_invitation(board.id, board.name, user.id)
    
    # Use invitation
    used = use_invitation(invitation.id)
    
    assert used is True
    assert invitation.id in invitations_db
    # Check that the invitation is marked as used
    assert invitations_db[invitation.id]["used"] == True


def test_use_invitation_not_found(cleanup_dbs):
    """Test using non-existent invitation"""
    fake_id = uuid4()
    invitation = use_invitation(fake_id)
    assert invitation is False