from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session

from app.models import Card, User
from app.database_service import DatabaseService
from app.auth import get_current_active_user
from app.dependencies import get_db_session
from app.model_converter import ModelConverter

router = APIRouter()


@router.get("/{boardId}/cards/search", response_model=List[Card])
async def search_cards_endpoint(
    boardId: UUID,
    query: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """Search cards by title"""
    service = DatabaseService(db)
    
    # Check if board exists and user has access
    board = service.get_board_by_id(str(boardId))
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Get all cards for the board
    cards = service.get_cards_by_board(str(boardId))
    
    # Filter cards by query (case-insensitive)
    query_lower = query.lower()
    matching_cards = [
        card for card in cards
        if query_lower in card.title.lower()
    ]
    
    # Convert to API models
    return [ModelConverter.to_card_model(card) for card in matching_cards]


@router.get("/{boardId}/cards/filter", response_model=List[Card])
async def filter_cards_endpoint(
    boardId: UUID,
    assigneeId: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """Filter cards by assignee"""
    service = DatabaseService(db)
    
    # Check if board exists and user has access
    board = service.get_board_by_id(str(boardId))
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Get all cards for the board
    cards = service.get_cards_by_board(str(boardId))
    
    # Filter cards by assignee
    matching_cards = [
        card for card in cards
        if card.assignee_id == str(assigneeId)
    ]
    
    # Convert to API models
    return [ModelConverter.to_card_model(card) for card in matching_cards]