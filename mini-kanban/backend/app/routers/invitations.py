from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.models import Invitation, InvitationCreate, User
from app.store import (
    create_invitation, get_invitations_by_board, get_invitation_by_token,
    use_invitation, get_board_by_id, get_user_by_id
)
from app.auth import get_current_active_user

router = APIRouter()


@router.post("/{boardId}/invitations", response_model=Invitation, status_code=201)
async def create_invitation_endpoint(
    boardId: UUID,
    invitation_data: InvitationCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create invitation (owner only)"""
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
            detail="Access denied"
        )
    
    invitation = create_invitation(
        board_id=boardId,
        board_name=board.name,
        created_by=current_user.id
    )
    return invitation


@router.get("/{boardId}/invitations", response_model=List[Invitation])
async def list_invitations_endpoint(
    boardId: UUID,
    current_user: User = Depends(get_current_active_user)
):
    """List invitations (owner only)"""
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
            detail="Access denied"
        )
    
    invitations = get_invitations_by_board(boardId)
    return invitations


@router.get("/invitations/{token}", response_model=Invitation)
async def get_invitation_by_token_endpoint(token: str):
    """Get invitation by token (no auth required)"""
    invitation = get_invitation_by_token(token)
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or already used"
        )
    return invitation