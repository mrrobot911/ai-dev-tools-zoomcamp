from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session

from app.models import User
from app.database_service import DatabaseService
from app.auth import get_current_active_user
from app.dependencies import get_db_session
from app.model_converter import ModelConverter

router = APIRouter()


@router.delete("/{boardId}/participants/{userId}")
async def remove_participant_endpoint(
    boardId: UUID,
    userId: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """Remove participant (owner only)"""
    service = DatabaseService(db)
    
    # Check if board exists and user has access
    board = service.get_board_by_id(str(boardId))
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check if user is the owner
    if board.owner_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied (not owner)"
        )
    
    # Check if trying to remove the owner
    if str(userId) == board.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot remove board owner"
        )
    
    # Check if user is a participant
    participants = service.get_participants_by_board(str(boardId))
    user_is_participant = any(p["userId"] == str(userId) for p in participants)
    if not user_is_participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in board"
        )
    
    success = service.remove_participant(str(boardId), str(userId))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in board"
        )
    
    return {"message": "Participant removed"}


@router.post("/{boardId}/leave")
async def leave_board_endpoint(
    boardId: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """Leave board"""
    service = DatabaseService(db)
    
    # Check if board exists and user has access
    board = service.get_board_by_id(str(boardId))
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check if user is the owner (cannot leave if owner)
    if board.owner_id == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot leave (only participant, not owner)"
        )
    
    # Check if user is a participant
    participants = service.get_participants_by_board(str(boardId))
    user_is_participant = any(p["userId"] == str(current_user.id) for p in participants)
    if not user_is_participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found or not a participant"
        )
    
    success = service.remove_participant(str(boardId), str(current_user.id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found or not a participant"
        )
    
    return {"message": "Left board successfully"}