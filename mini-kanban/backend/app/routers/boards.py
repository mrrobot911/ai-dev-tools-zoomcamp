from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.models import Board, BoardCreate, BoardSummary, BoardWithDetails, User
from app.store import (
    create_board, get_user_boards, get_board_by_id, update_board, delete_board,
    get_participants_by_board, get_columns_by_board, get_cards_by_board
)
from app.auth import get_current_active_user

router = APIRouter()


@router.get("", response_model=List[BoardSummary])
async def list_user_boards(current_user: User = Depends(get_current_active_user)):
    """List user's boards"""
    return get_user_boards(current_user.id)


@router.post("", response_model=Board, status_code=201)
async def create_board_endpoint(
    board_data: BoardCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new board"""
    board = create_board(
        name=board_data.name,
        owner_id=current_user.id,
        owner_name=current_user.name
    )
    return board


@router.get("/{boardId}", response_model=BoardWithDetails)
async def get_board_details(
    boardId: UUID,
    current_user: User = Depends(get_current_active_user)
):
    """Get board details"""
    board = get_board_by_id(boardId)
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check if user has access to this board
    user_boards = get_user_boards(current_user.id)
    user_board_ids = [b.board.id for b in user_boards]
    
    if boardId not in user_board_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get board details
    participants = get_participants_by_board(boardId)
    columns = get_columns_by_board(boardId)
    cards = get_cards_by_board(boardId)
    
    # Determine user's role
    role = "owner" if board.ownerId == current_user.id else "participant"
    
    return BoardWithDetails(
        id=board.id,
        name=board.name,
        ownerId=board.ownerId,
        ownerName=board.ownerName,
        createdAt=board.createdAt,
        updatedAt=board.updatedAt,
        participants=participants,
        columns=columns,
        cards=cards,
        role=role
    )


@router.put("/{boardId}", response_model=Board)
async def update_board_endpoint(
    boardId: UUID,
    board_data: BoardCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Update board (owner only)"""
    board = get_board_by_id(boardId)
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check if user is the owner
    if board.ownerId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied (not owner)"
        )
    
    updated_board = update_board(
        board_id=boardId,
        name=board_data.name,
        owner_id=current_user.id
    )
    
    if not updated_board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    return updated_board


@router.delete("/{boardId}")
async def delete_board_endpoint(
    boardId: UUID,
    current_user: User = Depends(get_current_active_user)
):
    """Delete board (owner only)"""
    board = get_board_by_id(boardId)
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check if user is the owner
    if board.ownerId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied (not owner)"
        )
    
    success = delete_board(boardId)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    return {"message": "Board deleted successfully"}