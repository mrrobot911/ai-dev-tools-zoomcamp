from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from app.models import (
    User, Board, BoardSummary, Column, Card, Participant, 
    BoardWithDetails, Invitation, UserRole
)
from app.auth import get_password_hash
from app.database_service import DatabaseService
from app.model_converter import ModelConverter


def create_user(email: str, name: str, password_hash: str) -> User:
    """Create a user using the database service"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        user = service.create_user(email, name, password_hash)
        return ModelConverter.to_user_model(user)
    finally:
        db.close()


def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email from database"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        user = service.get_user_by_email(email)
        if user:
            return ModelConverter.to_user_model(user)
        return None
    finally:
        db.close()


def get_user_by_id(user_id: UUID) -> Optional[User]:
    """Get user by ID from database"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        user = service.get_user_by_id(str(user_id))
        if user:
            return ModelConverter.to_user_model(user)
        return None
    finally:
        db.close()


def create_board(name: str, owner_id: UUID, owner_name: str) -> Board:
    """Create a board using the database service"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        board = service.create_board(name, str(owner_id), owner_name)
        return board
    finally:
        db.close()


def get_board_by_id(board_id: UUID) -> Optional[Board]:
    """Get board by ID from database"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        board = service.get_board_by_id(str(board_id))
        if board:
            return ModelConverter.to_board_model(board)
        return None
    finally:
        db.close()


def get_user_boards(user_id: UUID) -> List[BoardSummary]:
    """Get user's boards from database"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        user_boards_data = service.get_user_boards(str(user_id))
        board_summaries = []
        for board_data in user_boards_data:
            board_summaries.append(ModelConverter.to_board_summary(board_data))
        return board_summaries
    finally:
        db.close()


def update_board(board_id: UUID, name: str, owner_id: UUID) -> Optional[Board]:
    """Update board using database service"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        board = service.update_board(str(board_id), name, str(owner_id))
        if board:
            # The service already returns a BoardModel, so just return it
            return board
        return None
    finally:
        db.close()


def delete_board(board_id: UUID) -> bool:
    """Delete board from database"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        success = service.delete_board(str(board_id))
        return success
    finally:
        db.close()


def create_column(board_id: UUID, name: str) -> Column:
    """Create column using database service"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        column = service.create_column(str(board_id), name)
        return ModelConverter.to_column_model(column)
    finally:
        db.close()


def get_columns_by_board(board_id: UUID) -> List[Column]:
    """Get columns by board from database"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        columns_data = service.get_columns_by_board(str(board_id))
        columns = []
        for col_data in columns_data:
            # Convert dict data to Column model
            columns.append(Column(
                id=UUID(col_data["id"]),
                boardId=UUID(col_data["boardId"]),
                name=col_data["name"],
                order=col_data["order"],
                createdAt=col_data["createdAt"]
            ))
        return sorted(columns, key=lambda x: x.order)
    finally:
        db.close()


def update_column(column_id: UUID, name: Optional[str] = None, order: Optional[int] = None) -> Optional[Column]:
    """Update column using database service"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        column = service.update_column(str(column_id), name, order)
        if column:
            return ModelConverter.to_column_model(column)
        return None
    finally:
        db.close()


def delete_column(column_id: UUID) -> bool:
    """Delete column from database"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        success = service.delete_column(str(column_id))
        return success
    finally:
        db.close()


def reorder_columns(board_id: UUID, column_ids: List[UUID]) -> List[Column]:
    """Reorder columns using database service"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        reordered_columns = service.reorder_columns(str(board_id), [str(cid) for cid in column_ids])
        columns = []
        for col_data in reordered_columns:
            columns.append(Column(
                id=UUID(col_data["id"]),
                boardId=UUID(col_data["boardId"]),
                name=col_data["name"],
                order=col_data["order"],
                createdAt=col_data["createdAt"]
            ))
        return columns
    finally:
        db.close()


def create_card(board_id: UUID, column_id: UUID, title: str, creator_id: UUID, 
                creator_name: str, description: Optional[str] = None, 
                assignee_id: Optional[UUID] = None, assignee_name: Optional[str] = None) -> Card:
    """Create card using database service"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        card = service.create_card(
            str(board_id), str(column_id), title, str(creator_id), 
            creator_name, description, str(assignee_id) if assignee_id else None, 
            assignee_name
        )
        return ModelConverter.to_card_model(card)
    finally:
        db.close()


def get_cards_by_board(board_id: UUID) -> List[Card]:
    """Get cards by board from database"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        cards = service.get_cards_by_board(str(board_id))
        card_list = []
        for card in cards:
            card_list.append(ModelConverter.to_card_model(card))
        return sorted(card_list, key=lambda x: x.createdAt)
    finally:
        db.close()


def get_card_by_id(card_id: UUID) -> Optional[Card]:
    """Get card by ID from database"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        card = service.get_card_by_id(str(card_id))
        if card:
            return ModelConverter.to_card_model(card)
        return None
    finally:
        db.close()


def update_card(card_id: UUID, title: Optional[str] = None, description: Optional[str] = None, 
                assignee_id: Optional[UUID] = None, assignee_name: Optional[str] = None) -> Optional[Card]:
    """Update card using database service"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        card = service.update_card(
            str(card_id), title, description, 
            str(assignee_id) if assignee_id else None, assignee_name
        )
        if card:
            return ModelConverter.to_card_model(card)
        return None
    finally:
        db.close()


def delete_card(card_id: UUID) -> bool:
    """Delete card from database"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        success = service.delete_card(str(card_id))
        return success
    finally:
        db.close()


def move_card(card_id: UUID, target_column_id: UUID) -> Optional[Card]:
    """Move card to different column using database service"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        card = service.move_card(str(card_id), str(target_column_id))
        if card:
            return ModelConverter.to_card_model(card)
        return None
    finally:
        db.close()


def create_participant(board_id: UUID, user_id: UUID, user_name: str, role: UserRole) -> Participant:
    """Create participant using database service"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        participant = service.create_participant(str(board_id), str(user_id), user_name, role)
        return ModelConverter.to_participant_model(participant)
    finally:
        db.close()


def get_participants_by_board(board_id: UUID) -> List[Participant]:
    """Get participants by board from database"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        participants_data = service.get_participants_by_board(str(board_id))
        participants = []
        for p_data in participants_data:
            # Convert dict data to Participant model
            participants.append(Participant(
                userId=UUID(p_data["userId"]),
                email=p_data["email"],
                name=p_data["name"],
                role=p_data["role"],
                joinedAt=p_data["joinedAt"]
            ))
        return participants
    finally:
        db.close()


def remove_participant(board_id: UUID, user_id: UUID) -> bool:
    """Remove participant from database"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        success = service.remove_participant(str(board_id), str(user_id))
        return success
    finally:
        db.close()


def create_invitation(board_id: UUID, board_name: str, created_by: UUID) -> Invitation:
    """Create invitation using database service"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        invitation = service.create_invitation(str(board_id), board_name, str(created_by))
        return ModelConverter.to_invitation_model(invitation)
    finally:
        db.close()


def get_invitations_by_board(board_id: UUID) -> List[Invitation]:
    """Get invitations by board from database"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        invitations = service.get_invitations_by_board(str(board_id))
        invitation_list = []
        for inv in invitations:
            invitation_list.append(ModelConverter.to_invitation_model(inv))
        return invitation_list
    finally:
        db.close()


def get_invitation_by_token(token: str) -> Optional[Invitation]:
    """Get invitation by token from database"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        invitation = service.get_invitation_by_token(token)
        if invitation:
            return ModelConverter.to_invitation_model(invitation)
        return None
    finally:
        db.close()


def use_invitation(invitation_id: UUID) -> bool:
    """Use invitation from database"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        success = service.use_invitation(str(invitation_id))
        return success
    finally:
        db.close()


def seed_data():
    """Create some initial data for testing"""
    from app.database import get_session
    db = get_session()
    try:
        service = DatabaseService(db)
        service.seed_data()
    finally:
        db.close()