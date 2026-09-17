import pytest
from datetime import datetime
from uuid import uuid4
from app.models import (
    User, Board, BoardSummary, Column, Card, Participant,
    BoardWithDetails, Invitation, UserRole, UserCreate, UserLogin,
    BoardCreate, ColumnCreate, ColumnUpdate, CardCreate, CardUpdate,
    CardMove, ColumnReorder, InvitationCreate, Error
)


def test_user_creation():
    """Test User model creation"""
    user = User(
        id=uuid4(),
        email="test@example.com",
        name="Test User",
        createdAt=datetime.utcnow()
    )
    
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert isinstance(user.id, type(uuid4()))
    assert isinstance(user.createdAt, datetime)


def test_user_creation_with_defaults():
    """Test User model creation with default values"""
    # This should fail because email and name are required fields
    with pytest.raises(Exception):
        User()


def test_board_creation():
    """Test Board model creation"""
    board = Board(
        id=uuid4(),
        name="Test Board",
        ownerId=uuid4(),
        ownerName="Test Owner",
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow()
    )
    
    assert board.name == "Test Board"
    assert board.ownerId is not None
    assert board.ownerName == "Test Owner"
    assert isinstance(board.id, type(uuid4()))


def test_board_summary_creation():
    """Test BoardSummary model creation"""
    board = Board(
        id=uuid4(),
        name="Test Board",
        ownerId=uuid4(),
        ownerName="Test Owner",
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow()
    )
    
    summary = BoardSummary(
        board=board,
        participantCount=3,
        role=UserRole.OWNER
    )
    
    assert summary.board.name == "Test Board"
    assert summary.participantCount == 3
    assert summary.role == UserRole.OWNER


def test_column_creation():
    """Test Column model creation"""
    column = Column(
        id=uuid4(),
        boardId=uuid4(),
        name="To Do",
        order=0,
        createdAt=datetime.utcnow()
    )
    
    assert column.name == "To Do"
    assert column.order == 0
    assert isinstance(column.id, type(uuid4()))


def test_card_creation():
    """Test Card model creation"""
    card = Card(
        id=uuid4(),
        boardId=uuid4(),
        columnId=uuid4(),
        title="Test Card",
        description="Test description",
        creatorId=uuid4(),
        creatorName="Test Creator",
        assigneeId=uuid4(),
        assigneeName="Test Assignee",
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow()
    )
    
    assert card.title == "Test Card"
    assert card.description == "Test description"
    assert card.creatorName == "Test Creator"
    assert card.assigneeName == "Test Assignee"


def test_participant_creation():
    """Test Participant model creation"""
    participant = Participant(
        userId=uuid4(),
        email="test@example.com",
        name="Test Participant",
        role=UserRole.PARTICIPANT,
        joinedAt=datetime.utcnow()
    )
    
    assert participant.email == "test@example.com"
    assert participant.name == "Test Participant"
    assert participant.role == UserRole.PARTICIPANT


def test_board_with_details_creation():
    """Test BoardWithDetails model creation"""
    board = Board(
        id=uuid4(),
        name="Test Board",
        ownerId=uuid4(),
        ownerName="Test Owner",
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow()
    )
    
    participants = []
    columns = []
    cards = []
    
    board_with_details = BoardWithDetails(
        id=board.id,
        name=board.name,
        ownerId=board.ownerId,
        ownerName=board.ownerName,
        createdAt=board.createdAt,
        updatedAt=board.updatedAt,
        participants=participants,
        columns=columns,
        cards=cards,
        role=UserRole.OWNER
    )
    
    assert board_with_details.name == "Test Board"
    assert board_with_details.participants == []
    assert board_with_details.columns == []
    assert board_with_details.cards == []


def test_invitation_creation():
    """Test Invitation model creation"""
    invitation = Invitation(
        id=uuid4(),
        boardId=uuid4(),
        boardName="Test Board",
        token="test-token-123",
        used=False,
        createdAt=datetime.utcnow(),
        createdBy=uuid4()
    )
    
    assert invitation.boardName == "Test Board"
    assert invitation.token == "test-token-123"
    assert invitation.used is False


def test_user_create_validation():
    """Test UserCreate model validation"""
    user_data = UserCreate(
        email="test@example.com",
        password="testpass123",
        name="Test User"
    )
    
    assert user_data.email == "test@example.com"
    assert user_data.password == "testpass123"
    assert user_data.name == "Test User"
    assert user_data.invitationToken is None


def test_user_login_validation():
    """Test UserLogin model validation"""
    login_data = UserLogin(
        email="test@example.com",
        password="testpass123"
    )
    
    assert login_data.email == "test@example.com"
    assert login_data.password == "testpass123"


def test_board_create_validation():
    """Test BoardCreate model validation"""
    board_data = BoardCreate(name="Test Board")
    
    assert board_data.name == "Test Board"


def test_column_create_validation():
    """Test ColumnCreate model validation"""
    column_data = ColumnCreate(name="To Do")
    
    assert column_data.name == "To Do"


def test_column_update_validation():
    """Test ColumnUpdate model validation"""
    update_data = ColumnUpdate(name="Updated Name", order=1)
    
    assert update_data.name == "Updated Name"
    assert update_data.order == 1


def test_card_create_validation():
    """Test CardCreate model validation"""
    from uuid import uuid4
    
    card_data = CardCreate(
        title="Test Card",
        columnId=uuid4(),
        description="Test description",
        assigneeId=uuid4()
    )
    
    assert card_data.title == "Test Card"
    assert card_data.columnId is not None
    assert card_data.description == "Test description"
    assert card_data.assigneeId is not None


def test_card_update_validation():
    """Test CardUpdate model validation"""
    update_data = CardUpdate(
        title="Updated Title",
        description="Updated description",
        assigneeId=uuid4()
    )
    
    assert update_data.title == "Updated Title"
    assert update_data.description == "Updated description"
    assert update_data.assigneeId is not None


def test_card_move_validation():
    """Test CardMove model validation"""
    move_data = CardMove(
        cardId=uuid4(),
        targetColumnId=uuid4()
    )
    
    assert move_data.cardId is not None
    assert move_data.targetColumnId is not None


def test_column_reorder_validation():
    """Test ColumnReorder model validation"""
    reorder_data = ColumnReorder(
        columnIds=[uuid4(), uuid4(), uuid4()]
    )
    
    assert len(reorder_data.columnIds) == 3


def test_invitation_create_validation():
    """Test InvitationCreate model validation"""
    invite_data = InvitationCreate()
    
    assert invite_data is not None  # Empty model is valid


def test_error_model():
    """Test Error model"""
    error = Error(
        message="Test error message",
        status=400
    )
    
    assert error.message == "Test error message"
    assert error.status == 400


def test_user_role_enum():
    """Test UserRole enum values"""
    assert UserRole.OWNER == "owner"
    assert UserRole.PARTICIPANT == "participant"


def test_email_format_validation():
    """Test email format validation"""
    # Valid emails
    valid_emails = [
        "test@example.com",
        "user.name@domain.co.uk",
        "user+tag@domain.com"
    ]
    
    for email in valid_emails:
        user = User(email=email, name="Test User")
        assert user.email == email
    
    # Invalid emails would be caught by Pydantic validation
    # This is just to show the model accepts valid formats


if __name__ == "__main__":
    pytest.main([__file__])