from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.models import User
from app.store import (
    get_board_by_id, remove_participant, get_participants_by_board,
    get_user_by_id, board_participants
)
from app.auth import get_current_active_user

router = APIRouter()


@router.delete("/{boardId}/participants/{userId}")
async def remove_participant_endpoint(
    boardId: UUID,
    userId: UUID,
    current_user: User = Depends(get_current_active_user)
):
    """Remove participant (owner only)"""
    # Check if board exists and user has access
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
    
    # Check if trying to remove the owner
    if userId == board.ownerId:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot remove board owner"
        )
    
    # Check if user is a participant
    if boardId not in board_participants or userId not in board_participants[boardId]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in board"
        )
    
    success = remove_participant(boardId, userId)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in board"
        )
    
    return {"message": "Participant removed"}


@router.post("/{boardId}/leave")
async def leave_board_endpoint(
    boardId: UUID,
    current_user: User = Depends(get_current_active_user)
):
    """Leave board"""
    # Check if board exists and user has access
    board = get_board_by_id(boardId)
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check if user is the owner (cannot leave if owner)
    if board.ownerId == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot leave (only participant, not owner)"
        )
    
    # Check if user is a participant
    if boardId not in board_participants or current_user.id not in board_participants[boardId]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found or not a participant"
        )
    
    success = remove_participant(boardId, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found or not a participant"
        )
    
    return {"message": "Left board successfully"}