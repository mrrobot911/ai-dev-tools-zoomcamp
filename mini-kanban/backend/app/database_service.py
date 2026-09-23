from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.database import User, Board, BoardColumn, Card, BoardParticipant, Invitation
from app.models import UserRole, Board as BoardModel
from app.model_converter import ModelConverter

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, email: str, name: str, password_hash: str) -> User:
        """Create a user in the database or return existing user"""
        from app.database import create_tables
        create_tables()
        
        # Check if user already exists
        existing_user = self.get_user_by_email(email)
        if existing_user:
            return existing_user
        
        user_id = str(uuid4())
        user = User(
            id=user_id,
            email=email,
            name=name,
            password_hash=password_hash,
            created_at=datetime.utcnow()
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        from app.database import create_tables
        create_tables()
        
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create_board(self, name: str, owner_id: str, owner_name: str) -> BoardModel:
        from uuid import uuid4
        from app.model_converter import ModelConverter
        
        board = Board(
            id=str(uuid4()),
            name=name,
            owner_id=str(owner_id),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(board)
        self.db.flush()  # Get the board ID
        
        # Create owner as participant
        self.create_participant(board.id, str(owner_id), owner_name, UserRole.OWNER)
        
        # Create default columns with correct order
        self.create_column(board.id, "To Do", 0)
        self.create_column(board.id, "In Progress", 1)
        self.create_column(board.id, "Done", 2)
        
        # Refresh to load all fields including relationships
        self.db.refresh(board)
        
        # Convert to API model
        return ModelConverter.to_board_model(board)
    
    def get_board_by_id(self, board_id: str) -> Optional[Board]:
        return self.db.query(Board).filter(Board.id == board_id).first()
    
    def get_user_boards(self, user_id: str) -> List[Dict[str, Any]]:
        from app.model_converter import ModelConverter
        user_boards = []
        
        # Get all boards where user is a participant
        participant_boards = self.db.query(Board).join(
            BoardParticipant, Board.id == BoardParticipant.board_id
        ).filter(BoardParticipant.user_id == str(user_id)).all()
        
        for board in participant_boards:
            # Get participant count
            participant_count = self.db.query(BoardParticipant).filter(
                BoardParticipant.board_id == board.id
            ).count()
            
            # Determine user's role
            participant = self.db.query(BoardParticipant).filter(
                and_(
                    BoardParticipant.board_id == board.id,
                    BoardParticipant.user_id == str(user_id)
                )
            ).first()
            role = participant.role if participant else UserRole.PARTICIPANT
            
            user_boards.append({
                "board": ModelConverter.to_board_model(board),
                "participantCount": participant_count,
                "role": role
            })
        
        return user_boards
    
    def update_board(self, board_id: str, name: str, owner_id: str) -> Optional[BoardModel]:
        board = self.get_board_by_id(board_id)
        if board:
            board.name = name
            board.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(board)
            return ModelConverter.to_board_model(board)
        return None
    
    def delete_board(self, board_id: str) -> bool:
        board = self.get_board_by_id(board_id)
        if board:
            # SQLAlchemy will cascade delete due to relationships
            self.db.delete(board)
            self.db.commit()
            return True
        return False
    
    def create_column(self, board_id: str, name: str, order: int = None) -> BoardColumn:
        if order is None:
            # Get max order and add 1
            max_order_result = self.db.query(func.max(BoardColumn.order)).filter(
                BoardColumn.board_id == board_id
            ).scalar()
            order = (max_order_result + 1) if max_order_result is not None else 0
        
        column = BoardColumn(
            id=str(uuid4()),
            board_id=board_id,
            name=name,
            order=order,
            created_at=datetime.utcnow()
        )
        self.db.add(column)
        self.db.commit()
        self.db.refresh(column)
        return column
    
    def get_columns_by_board(self, board_id: str) -> List[Dict[str, Any]]:
        columns = self.db.query(BoardColumn).filter(
            BoardColumn.board_id == board_id
        ).order_by(BoardColumn.order).all()
        
        result = []
        for column in columns:
            result.append({
                "id": column.id,
                "boardId": column.board_id,
                "name": column.name,
                "order": column.order,
                "createdAt": column.created_at
            })
        
        return result
    
    def update_column(self, column_id: str, name: Optional[str] = None, order: Optional[int] = None) -> Optional[BoardColumn]:
        column = self.db.query(BoardColumn).filter(BoardColumn.id == column_id).first()
        if column:
            if name is not None:
                column.name = name
            if order is not None:
                column.order = order
            self.db.commit()
            self.db.refresh(column)
            return column
        return None
    
    def delete_column(self, column_id: str) -> bool:
        column = self.db.query(BoardColumn).filter(BoardColumn.id == column_id).first()
        if column:
            self.db.delete(column)
            self.db.commit()
            return True
        return False
    
    def reorder_columns(self, board_id: str, column_ids: List[str]) -> List[BoardColumn]:
        if self.db.query(Board).filter(Board.id == board_id).first():
            for i, column_id in enumerate(column_ids):
                column = self.db.query(BoardColumn).filter(
                    and_(
                        BoardColumn.id == column_id,
                        BoardColumn.board_id == board_id
                    )
                ).first()
                if column:
                    column.order = i
            
            self.db.commit()
            return self.get_columns_by_board(board_id)
        return []
    
    def create_card(self, board_id: str, column_id: str, title: str, creator_id: str, 
                   creator_name: str, description: Optional[str] = None, 
                   assignee_id: Optional[str] = None, assignee_name: Optional[str] = None) -> Card:
        card = Card(
            id=str(uuid4()),
            board_id=board_id,
            column_id=column_id,
            title=title,
            description=description,
            creator_id=creator_id,
            creator_name=creator_name,
            assignee_id=assignee_id,
            assignee_name=assignee_name,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(card)
        self.db.commit()
        self.db.refresh(card)
        return card
    
    def get_cards_by_board(self, board_id: str) -> List[Card]:
        return self.db.query(Card).filter(
            Card.board_id == board_id
        ).order_by(Card.created_at).all()
    
    def get_card_by_id(self, card_id: str) -> Optional[Card]:
        return self.db.query(Card).filter(Card.id == card_id).first()
    
    def update_card(self, card_id: str, title: Optional[str] = None, description: Optional[str] = None, 
                   assignee_id: Optional[str] = None, assignee_name: Optional[str] = None) -> Optional[Card]:
        card = self.db.query(Card).filter(Card.id == card_id).first()
        if card:
            if title is not None:
                card.title = title
            if description is not None:
                card.description = description
            if assignee_id is not None:
                card.assignee_id = assignee_id
            if assignee_name is not None:
                card.assignee_name = assignee_name
            card.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(card)
            return card
        return None
    
    def delete_card(self, card_id: str) -> bool:
        card = self.db.query(Card).filter(Card.id == card_id).first()
        if card:
            self.db.delete(card)
            self.db.commit()
            return True
        return False
    
    def move_card(self, card_id: str, target_column_id: str) -> Optional[Card]:
        card = self.db.query(Card).filter(Card.id == card_id).first()
        if card:
            card.column_id = target_column_id
            card.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(card)
            return card
        return None
    
    def create_participant(self, board_id: str, user_id: str, user_name: str, role: UserRole) -> BoardParticipant:
        # Check if user exists
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found in database")
        
        # Check if user is already a participant
        existing = self.db.query(BoardParticipant).filter(
            and_(
                BoardParticipant.board_id == board_id,
                BoardParticipant.user_id == user_id
            )
        ).first()
        
        if existing:
            return existing
        
        participant = BoardParticipant(
            id=str(uuid4()),
            board_id=board_id,
            user_id=user_id,
            role=role,
            joined_at=datetime.utcnow()
        )
        self.db.add(participant)
        self.db.commit()
        self.db.refresh(participant)
        return participant
    
    def get_participants_by_board(self, board_id: str) -> List[Dict[str, Any]]:
        participants = self.db.query(BoardParticipant).filter(
            BoardParticipant.board_id == board_id
        ).all()
        
        result = []
        for participant in participants:
            # Get user details
            user = self.db.query(User).filter(User.id == participant.user_id).first()
            result.append({
                "id": participant.id,
                "userId": participant.user_id,
                "email": user.email if user else "unknown@example.com",
                "name": user.name if user else "Unknown",
                "role": participant.role,
                "joinedAt": participant.joined_at
            })
        
        return result
    
    def remove_participant(self, board_id: str, user_id: str) -> bool:
        participant = self.db.query(BoardParticipant).filter(
            and_(
                BoardParticipant.board_id == board_id,
                BoardParticipant.user_id == user_id
            )
        ).first()
        if participant:
            self.db.delete(participant)
            self.db.commit()
            return True
        return False
    
    def create_invitation(self, board_id: str, board_name: str, created_by: str) -> Invitation:
        import secrets
        token = secrets.token_urlsafe(32)
        
        invitation = Invitation(
            id=str(uuid4()),
            board_id=board_id,
            board_name=board_name,
            token=token,
            used=False,
            created_at=datetime.utcnow(),
            created_by=created_by
        )
        self.db.add(invitation)
        self.db.commit()
        self.db.refresh(invitation)
        return invitation
    
    def get_invitations_by_board(self, board_id: str) -> List[Invitation]:
        return self.db.query(Invitation).filter(
            and_(
                Invitation.board_id == board_id,
                Invitation.used == False
            )
        ).all()
    
    def get_invitation_by_token(self, token: str) -> Optional[Invitation]:
        return self.db.query(Invitation).filter(
            and_(
                Invitation.token == token,
                Invitation.used == False
            )
        ).first()
    
    def use_invitation(self, invitation_id: str) -> bool:
        invitation = self.db.query(Invitation).filter(Invitation.id == invitation_id).first()
        if invitation:
            invitation.used = True
            self.db.commit()
            return True
        return False
    
    def seed_data(self):
        """Create some initial data for testing"""
        from app.auth import get_password_hash
        
        # Create test users
        user1 = self.create_user("test@example.com", "Test User", get_password_hash("password"))
        user2 = self.create_user("admin@example.com", "Admin User", get_password_hash("admin"))
        
        # Create test boards
        board1 = self.create_board("Test Board", user1.id, user1.name)
        board2 = self.create_board("Project Board", user1.id, user1.name)
        
        # Create test columns for board1
        col1 = self.create_column(board1.id, "To Do")
        col2 = self.create_column(board1.id, "In Progress")
        col3 = self.create_column(board1.id, "Done")
        
        # Create test cards
        card1 = self.create_card(board1.id, col1.id, "Task 1", user1.id, user1.name, "Description 1")
        card2 = self.create_card(board1.id, col1.id, "Task 2", user1.id, user1.name, "Description 2")
        card3 = self.create_card(board1.id, col2.id, "Task 3", user1.id, user1.name, "Description 3")
        
        # Create invitation
        self.create_invitation(board1.id, board1.name, user1.id)
        
        print("Data seeded successfully!")