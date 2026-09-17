from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.models import Card, User
from app.store import get_cards_by_board, get_board_by_id
from app.auth import get_current_active_user

router = APIRouter()


@router.get("/{boardId}/cards/search", response_model=List[Card])
async def search_cards_endpoint(
    boardId: UUID,
    query: str,
    current_user: User = Depends(get_current_active_user)
):
    """Search cards by title"""
    # Check if board exists and user has access
    board = get_board_by_id(boardId)
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Get all cards for the board
    cards = get_cards_by_board(boardId)
    
    # Filter cards by query (case-insensitive)
    query_lower = query.lower()
    matching_cards = [
        card for card in cards
        if query_lower in card.title.lower()
    ]
    
    return matching_cards


@router.get("/{boardId}/cards/filter", response_model=List[Card])
async def filter_cards_endpoint(
    boardId: UUID,
    assigneeId: UUID,
    current_user: User = Depends(get_current_active_user)
):
    """Filter cards by assignee"""
    # Check if board exists and user has access
    board = get_board_by_id(boardId)
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Get all cards for the board
    cards = get_cards_by_board(boardId)
    
    # Filter cards by assignee
    matching_cards = [
        card for card in cards
        if card.assigneeId == assigneeId
    ]
    
    return matching_cards