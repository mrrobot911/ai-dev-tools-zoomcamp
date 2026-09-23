from datetime import datetime
from typing import List, Dict, Any
from uuid import UUID

from app.models.database import User, Board, BoardColumn, Card, BoardParticipant, Invitation
from app.models import (
    User as UserModel, Board as BoardModel, Column as ColumnModel, Card as CardModel,
    Participant as ParticipantModel, Invitation as InvitationModel, BoardSummary, BoardWithDetails, UserRole
)

class ModelConverter:
    @staticmethod
    def to_user_model(db_user: User) -> UserModel:
        """Convert database User to API User model"""
        return UserModel(
            id=UUID(db_user.id),
            email=db_user.email,
            name=db_user.name,
            createdAt=db_user.created_at
        )
    
    @staticmethod
    def to_board_model(db_board: Board) -> BoardModel:
        """Convert database Board to API Board model"""
        return BoardModel(
            id=db_board.id if isinstance(db_board.id, UUID) else UUID(str(db_board.id)),
            name=db_board.name,
            ownerId=db_board.owner_id if isinstance(db_board.owner_id, UUID) else UUID(str(db_board.owner_id)),
            ownerName=db_board.owner.name,  # This should work through relationship
            createdAt=db_board.created_at,
            updatedAt=db_board.updated_at
        )
    
    @staticmethod
    def to_column_model(db_column: BoardColumn) -> ColumnModel:
        """Convert database BoardColumn to API Column model"""
        return ColumnModel(
            id=UUID(db_column.id),
            boardId=UUID(db_column.board_id),
            name=db_column.name,
            order=db_column.order,
            createdAt=db_column.created_at
        )
    
    @staticmethod
    def to_card_model(db_card: Card) -> CardModel:
        """Convert database Card to API Card model"""
        return CardModel(
            id=UUID(db_card.id),
            boardId=UUID(db_card.board_id),
            columnId=UUID(db_card.column_id),
            title=db_card.title,
            description=db_card.description,
            creatorId=UUID(db_card.creator_id),
            creatorName=db_card.creator_name,
            assigneeId=UUID(db_card.assignee_id) if db_card.assignee_id else None,
            assigneeName=db_card.assignee_name,
            createdAt=db_card.created_at,
            updatedAt=db_card.updated_at
        )
    
    @staticmethod
    def to_participant_model(db_participant: BoardParticipant) -> ParticipantModel:
        """Convert database BoardParticipant to API Participant model"""
        return ParticipantModel(
            userId=UUID(db_participant.user_id),
            email=db_participant.user.email,  # This should work through relationship
            name=db_participant.user.name,
            role=UserRole(db_participant.role),
            joinedAt=db_participant.joined_at
        )
    
    @staticmethod
    def to_invitation_model(db_invitation: Invitation) -> InvitationModel:
        """Convert database Invitation to API Invitation model"""
        return InvitationModel(
            id=UUID(db_invitation.id),
            boardId=UUID(db_invitation.board_id),
            boardName=db_invitation.board_name,
            token=db_invitation.token,
            used=db_invitation.used,
            createdAt=db_invitation.created_at,
            createdBy=UUID(db_invitation.created_by)
        )
    
    @staticmethod
    def to_board_summary(board_data: Dict[str, Any]) -> BoardSummary:
        """Convert board data to BoardSummary"""
        board = board_data["board"]
        return BoardSummary(
            board=board,
            participantCount=board_data["participantCount"],
            role=board_data["role"]
        )
    
    @staticmethod
    def to_board_with_details(
        db_board: Board,
        participants: List[BoardParticipant],
        columns: List[BoardColumn],
        cards: List[Card],
        role: str
    ) -> BoardWithDetails:
        """Convert database data to BoardWithDetails"""
        return BoardWithDetails(
            id=UUID(db_board.id),
            name=db_board.name,
            ownerId=UUID(db_board.owner_id),
            ownerName=db_board.owner.name,
            createdAt=db_board.created_at,
            updatedAt=db_board.updated_at,
            participants=[ModelConverter.to_participant_model(p) for p in participants],
            columns=[ModelConverter.to_column_model(c) for c in columns],
            cards=[ModelConverter.to_card_model(ca) for ca in cards],
            role=UserRole(role)
        )