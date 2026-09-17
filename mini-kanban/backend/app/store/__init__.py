from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from app.models import (
    User, Board, BoardSummary, Column, Card, Participant, 
    BoardWithDetails, Invitation, UserRole
)
from app.auth import auth_create_user, users_db

# In-memory databases
boards_db: Dict[UUID, dict] = {}
columns_db: Dict[UUID, dict] = {}
cards_db: Dict[UUID, dict] = {}
participants_db: Dict[UUID, List[dict]] = {}
invitations_db: Dict[UUID, dict] = {}
board_participants: Dict[UUID, List[UUID]] = {}  # board_id -> [user_ids]


def create_user(email: str, name: str, password_hash: str) -> User:
    """Create a user using the auth module's function"""
    return auth_create_user(email, name, password_hash)


def get_user_by_email(email: str) -> Optional[User]:
    for user_data in users_db.values():
        if user_data["email"] == email:
            return User(**{k: v for k, v in user_data.items() if k != "password"})
    return None


def get_user_by_id(user_id: UUID) -> Optional[User]:
    if user_id in users_db:
        return User(**{k: v for k, v in users_db[user_id].items() if k != "password"})
    return None


def create_board(name: str, owner_id: UUID, owner_name: str) -> Board:
    board_id = uuid4()
    board = Board(
        id=board_id,
        name=name,
        ownerId=owner_id,
        ownerName=owner_name,
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow()
    )
    
    boards_db[board_id] = board.model_dump()
    board_participants[board_id] = [owner_id]  # Owner is automatically a participant
    
    # Create owner as participant
    create_participant(board_id, owner_id, owner_name, UserRole.OWNER)
    
    # Create default columns with correct order
    create_column(board_id, "To Do")
    create_column(board_id, "In Progress")
    create_column(board_id, "Done")
    
    return board


def get_board_by_id(board_id: UUID) -> Optional[Board]:
    if board_id in boards_db:
        return Board(**boards_db[board_id])
    return None


def get_user_boards(user_id: UUID) -> List[BoardSummary]:
    user_boards = []
    
    for board_id, participant_ids in board_participants.items():
        if user_id in participant_ids:
            board_data = boards_db[board_id]
            board = Board(**board_data)
            
            # Determine user's role
            role = UserRole.OWNER if board.ownerId == user_id else UserRole.PARTICIPANT
            
            # Get participant count
            participant_count = len(participant_ids)
            
            summary = BoardSummary(
                board=board,
                participantCount=participant_count,
                role=role
            )
            user_boards.append(summary)
    
    return user_boards


def update_board(board_id: UUID, name: str, owner_id: UUID) -> Optional[Board]:
    if board_id in boards_db:
        boards_db[board_id].update({
            "name": name,
            "updatedAt": datetime.utcnow()
        })
        return Board(**boards_db[board_id])
    return None


def delete_board(board_id: UUID) -> bool:
    if board_id in boards_db:
        del boards_db[board_id]
        if board_id in board_participants:
            del board_participants[board_id]
        
        # Delete related data
        columns_to_delete = [col_id for col_id, col_data in columns_db.items() 
                           if col_data["boardId"] == board_id]
        for col_id in columns_to_delete:
            del columns_db[col_id]
        
        cards_to_delete = [card_id for card_id, card_data in cards_db.items() 
                         if card_data["boardId"] == board_id]
        for card_id in cards_to_delete:
            del cards_db[card_id]
        
        if board_id in participants_db:
            del participants_db[board_id]
        
        return True
    return False


def create_column(board_id: UUID, name: str) -> Column:
    column_id = uuid4()
    column = Column(
        id=column_id,
        boardId=board_id,
        name=name,
        order=len(columns_db),  # Simple ordering
        createdAt=datetime.utcnow()
    )
    
    columns_db[column_id] = column.model_dump()
    return column


def get_columns_by_board(board_id: UUID) -> List[Column]:
    columns = []
    for column_data in columns_db.values():
        if column_data["boardId"] == board_id:
            columns.append(Column(**column_data))
    return sorted(columns, key=lambda x: x.order)


def update_column(column_id: UUID, name: Optional[str] = None, order: Optional[int] = None) -> Optional[Column]:
    if column_id in columns_db:
        if name is not None:
            columns_db[column_id]["name"] = name
        if order is not None:
            columns_db[column_id]["order"] = order
        return Column(**columns_db[column_id])
    return None


def delete_column(column_id: UUID) -> bool:
    if column_id in columns_db:
        del columns_db[column_id]
        return True
    return False


def reorder_columns(board_id: UUID, column_ids: List[UUID]) -> List[Column]:
    if board_id not in boards_db:
        return []
    
    # Update order for each column
    for i, column_id in enumerate(column_ids):
        if column_id in columns_db and columns_db[column_id]["boardId"] == board_id:
            columns_db[column_id]["order"] = i
    
    return get_columns_by_board(board_id)


def create_card(board_id: UUID, column_id: UUID, title: str, creator_id: UUID, 
                creator_name: str, description: Optional[str] = None, 
                assignee_id: Optional[UUID] = None, assignee_name: Optional[str] = None) -> Card:
    card_id = uuid4()
    card = Card(
        id=card_id,
        boardId=board_id,
        columnId=column_id,
        title=title,
        description=description,
        creatorId=creator_id,
        creatorName=creator_name,
        assigneeId=assignee_id,
        assigneeName=assignee_name,
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow()
    )
    
    cards_db[card_id] = card.model_dump()
    return card


def get_cards_by_board(board_id: UUID) -> List[Card]:
    cards = []
    for card_data in cards_db.values():
        if card_data["boardId"] == board_id:
            cards.append(Card(**card_data))
    return sorted(cards, key=lambda x: x.createdAt)


def get_card_by_id(card_id: UUID) -> Optional[Card]:
    if card_id in cards_db:
        return Card(**cards_db[card_id])
    return None


def update_card(card_id: UUID, title: Optional[str] = None, description: Optional[str] = None, 
                assignee_id: Optional[UUID] = None, assignee_name: Optional[str] = None) -> Optional[Card]:
    if card_id in cards_db:
        if title is not None:
            cards_db[card_id]["title"] = title
        if description is not None:
            cards_db[card_id]["description"] = description
        if assignee_id is not None:
            cards_db[card_id]["assigneeId"] = assignee_id
        if assignee_name is not None:
            cards_db[card_id]["assigneeName"] = assignee_name
        cards_db[card_id]["updatedAt"] = datetime.utcnow()
        return Card(**cards_db[card_id])
    return None


def delete_card(card_id: UUID) -> bool:
    if card_id in cards_db:
        del cards_db[card_id]
        return True
    return False


def move_card(card_id: UUID, target_column_id: UUID) -> Optional[Card]:
    if card_id in cards_db:
        cards_db[card_id]["columnId"] = target_column_id
        cards_db[card_id]["updatedAt"] = datetime.utcnow()
        return Card(**cards_db[card_id])
    return None


def create_participant(board_id: UUID, user_id: UUID, user_name: str, role: UserRole) -> Participant:
    # Check if user exists in users_db
    if user_id not in users_db:
        raise ValueError(f"User {user_id} not found in database")
    
    participant = Participant(
        userId=user_id,
        email=users_db[user_id]["email"],
        name=user_name,
        role=role,
        joinedAt=datetime.utcnow()
    )
    
    if board_id not in participants_db:
        participants_db[board_id] = []
    
    participants_db[board_id].append(participant.model_dump())
    
    # Add to board participants list
    if board_id not in board_participants:
        board_participants[board_id] = []
    board_participants[board_id].append(user_id)
    
    return participant


def get_participants_by_board(board_id: UUID) -> List[Participant]:
    if board_id in participants_db:
        return [Participant(**p) for p in participants_db[board_id]]
    return []


def remove_participant(board_id: UUID, user_id: UUID) -> bool:
    if board_id in participants_db:
        # Remove participant from the list
        original_count = len(participants_db[board_id])
        participants_db[board_id] = [p for p in participants_db[board_id] if p["userId"] != user_id]
        return len(participants_db[board_id]) < original_count
    return False


def create_invitation(board_id: UUID, board_name: str, created_by: UUID) -> Invitation:
    import secrets
    token = secrets.token_urlsafe(32)
    
    invitation = Invitation(
        id=uuid4(),
        boardId=board_id,
        boardName=board_name,
        token=token,
        used=False,
        createdAt=datetime.utcnow(),
        createdBy=created_by
    )
    
    invitations_db[invitation.id] = invitation.model_dump()
    return invitation


def get_invitations_by_board(board_id: UUID) -> List[Invitation]:
    invitations = []
    for inv_data in invitations_db.values():
        if inv_data["boardId"] == board_id and not inv_data["used"]:
            invitations.append(Invitation(**inv_data))
    return invitations


def get_invitation_by_token(token: str) -> Optional[Invitation]:
    for inv_data in invitations_db.values():
        if inv_data["token"] == token and not inv_data["used"]:
            return Invitation(**inv_data)
    return None


def use_invitation(invitation_id: UUID) -> bool:
    if invitation_id in invitations_db:
        invitations_db[invitation_id]["used"] = True
        return True
    return False


def seed_data():
    """Create some initial data for testing"""
    from app.auth import get_password_hash
    
    # Create test users
    user1 = create_user("test@example.com", "Test User", get_password_hash("password"))
    user2 = create_user("admin@example.com", "Admin User", get_password_hash("admin"))
    
    # Create test boards
    board1 = create_board("Test Board", user1.id, user1.name)
    board2 = create_board("Project Board", user1.id, user1.name)
    
    # Create test columns for board1
    col1 = create_column(board1.id, "To Do")
    col2 = create_column(board1.id, "In Progress")
    col3 = create_column(board1.id, "Done")
    
    # Create test cards
    card1 = create_card(board1.id, col1.id, "Task 1", user1.id, user1.name, "Description 1")
    card2 = create_card(board1.id, col1.id, "Task 2", user1.id, user1.name, "Description 2")
    card3 = create_card(board1.id, col2.id, "Task 3", user1.id, user1.name, "Description 3")
    
    # Create invitation
    create_invitation(board1.id, board1.name, user1.id)
    
    print("Data seeded successfully!")