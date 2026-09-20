from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session

from app.models import Invitation, InvitationCreate, User
from app.database_service import DatabaseService
from app.auth import get_current_active_user
from app.dependencies import get_db_session
from app.model_converter import ModelConverter

router = APIRouter()


@router.post("/{boardId}/invitations", response_model=Invitation, status_code=201)
async def create_invitation_endpoint(
    boardId: UUID,
    invitation_data: InvitationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """Create invitation (owner only)"""
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
            detail="Access denied"
        )
    
    invitation = service.create_invitation(
        board_id=str(boardId),
        board_name=board.name,
        created_by=str(current_user.id)
    )
    # Convert to API model
    return ModelConverter.to_invitation_model(invitation)


@router.get("/{boardId}/invitations", response_model=List[Invitation])
async def list_invitations_endpoint(
    boardId: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """List invitations (owner only)"""
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
            detail="Access denied"
        )
    
    invitations = service.get_invitations_by_board(str(boardId))
    # Convert to API models
    return [ModelConverter.to_invitation_model(invitation) for invitation in invitations]


@router.get("/invitations/{token}", response_model=Invitation)
async def get_invitation_by_token_endpoint(token: str, db: Session = Depends(get_db_session)):
    """Get invitation by token (no auth required)"""
    service = DatabaseService(db)
    
    invitation = service.get_invitation_by_token(token)
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or already used"
        )
    
    # Convert to API model
    return ModelConverter.to_invitation_model(invitation)