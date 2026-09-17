from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.models import Card, CardCreate, CardUpdate, CardMove, User
from app.store import (
    create_card, get_cards_by_board, get_card_by_id, update_card, delete_card,
    move_card, get_board_by_id, get_columns_by_board, get_user_by_id
)
from app.auth import get_current_active_user

router = APIRouter()


@router.post("/{boardId}/cards", response_model=Card, status_code=201)
async def create_card_endpoint(
    boardId: UUID,
    card_data: CardCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create card"""
    # Check if board exists and user has access
    board = get_board_by_id(boardId)
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check if column exists
    columns = get_columns_by_board(boardId)
    column_exists = any(c.id == card_data.columnId for c in columns)
    if not column_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    # Get assignee info if provided
    assignee_name = None
    if card_data.assigneeId:
        assignee = get_user_by_id(card_data.assigneeId)
        if assignee:
            assignee_name = assignee.name
    
    card = create_card(
        board_id=boardId,
        column_id=card_data.columnId,
        title=card_data.title,
        creator_id=current_user.id,
        creator_name=current_user.name,
        description=card_data.description,
        assignee_id=card_data.assigneeId,
        assignee_name=assignee_name
    )
    return card


@router.put("/{boardId}/cards/{cardId}", response_model=Card)
async def update_card_endpoint(
    boardId: UUID,
    cardId: UUID,
    card_data: CardUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update card"""
    # Check if board exists and user has access
    board = get_board_by_id(boardId)
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check if card exists and belongs to this board
    cards = get_cards_by_board(boardId)
    card_exists = any(c.id == cardId for c in cards)
    if not card_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Get assignee info if provided
    assignee_name = None
    if card_data.assigneeId:
        assignee = get_user_by_id(card_data.assigneeId)
        if assignee:
            assignee_name = assignee.name
    
    updated_card = update_card(
        card_id=cardId,
        title=card_data.title,
        description=card_data.description,
        assignee_id=card_data.assigneeId,
        assignee_name=assignee_name
    )
    
    if not updated_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    return updated_card


@router.delete("/{boardId}/cards/{cardId}")
async def delete_card_endpoint(
    boardId: UUID,
    cardId: UUID,
    current_user: User = Depends(get_current_active_user)
):
    """Delete card (creator or owner only)"""
    # Check if board exists and user has access
    board = get_board_by_id(boardId)
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check if card exists and belongs to this board
    cards = get_cards_by_board(boardId)
    card = None
    for c in cards:
        if c.id == cardId:
            card = c
            break
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Check if user is creator or board owner
    if card.creatorId != current_user.id and board.ownerId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied (not creator or owner)"
        )
    
    success = delete_card(cardId)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    return {"message": "Card deleted"}


@router.put("/{boardId}/cards/move", response_model=Card)
async def move_card_endpoint(
    boardId: UUID,
    move_data: CardMove,
    current_user: User = Depends(get_current_active_user)
):
    """Move card to different column"""
    # Check if board exists and user has access
    board = get_board_by_id(boardId)
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check if card exists and belongs to this board
    cards = get_cards_by_board(boardId)
    card_exists = any(c.id == move_data.cardId for c in cards)
    if not card_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Check if target column exists
    columns = get_columns_by_board(boardId)
    target_column_exists = any(c.id == move_data.targetColumnId for c in columns)
    if not target_column_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    moved_card = move_card(move_data.cardId, move_data.targetColumnId)
    if not moved_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    return moved_card