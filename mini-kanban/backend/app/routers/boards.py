from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session

from app.models import Board, BoardCreate, BoardSummary, BoardWithDetails, User
from app.database_service import DatabaseService
from app.auth import get_current_active_user
from app.dependencies import get_db_session
from app.model_converter import ModelConverter

router = APIRouter()


@router.get("", response_model=List[BoardSummary])
async def list_user_boards(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """List user's boards"""
    service = DatabaseService(db)
    return service.get_user_boards(current_user.id)


@router.post("", response_model=Board, status_code=201)
async def create_board_endpoint(
    board_data: BoardCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """Create a new board"""
    service = DatabaseService(db)
    board = service.create_board(
        name=board_data.name,
        owner_id=current_user.id,
        owner_name=current_user.name
    )
    return board


@router.get("/{boardId}", response_model=BoardWithDetails)
async def get_board_details(
    boardId: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """Get board details"""
    service = DatabaseService(db)
    board = service.get_board_by_id(str(boardId))
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check if user has access to this board
    user_boards = service.get_user_boards(current_user.id)
    user_board_ids = [b["board"].id for b in user_boards]
    
    if boardId not in user_board_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get board details
    participants = service.get_participants_by_board(str(boardId))
    columns = service.get_columns_by_board(str(boardId))
    cards = service.get_cards_by_board(str(boardId))
    
    # Convert database objects to API models
    participants_models = []
    for participant in participants:
        # Create a BoardParticipant object for conversion with user data
        from app.models.database import BoardParticipant, User
        db_participant = BoardParticipant(
            id=participant["id"],
            user_id=participant["userId"],
            role=participant["role"],
            joined_at=participant["joinedAt"]
        )
        # Create a User object and attach it to the participant
        if participant.get("email") and participant.get("name"):
            db_participant.user = User(
                id=participant["userId"],
                email=participant["email"],
                name=participant["name"]
            )
        else:
            # Fallback for missing user data
            db_participant.user = User(
                id=participant["userId"],
                email="unknown@example.com",
                name="Unknown"
            )
        participants_models.append(ModelConverter.to_participant_model(db_participant))
    
    columns_models = []
    for column in columns:
        # Create a BoardColumn object for conversion
        from app.models.database import BoardColumn
        db_column = BoardColumn(
            id=column["id"],
            board_id=column["boardId"],
            name=column["name"],
            order=column["order"],
            created_at=column["createdAt"]
        )
        columns_models.append(ModelConverter.to_column_model(db_column))
    
    cards_models = [ModelConverter.to_card_model(card) for card in cards]
    
    # Determine user's role and get owner name
    owner_name = None
    for participant in participants:
        if participant["role"] == "owner":
            owner_name = participant["name"]
            break
    
    # Since we checked access, owner should exist
    if owner_name is None:
        owner_name = "Unknown"
    
    role = "owner" if board.owner_id == str(current_user.id) else "participant"
    
    return BoardWithDetails(
        id=board.id,
        name=board.name,
        ownerId=board.owner_id,
        ownerName=owner_name,
        createdAt=board.created_at,
        updatedAt=board.updated_at,
        participants=participants_models,
        columns=columns_models,
        cards=cards_models,
        role=role
    )


@router.put("/{boardId}", response_model=Board)
async def update_board_endpoint(
    boardId: UUID,
    board_data: BoardCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """Update board (owner only)"""
    service = DatabaseService(db)
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
    
    updated_board = service.update_board(
        board_id=str(boardId),
        name=board_data.name,
        owner_id=current_user.id
    )
    
    if not updated_board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Convert to API model (already done in service)
    return updated_board


@router.delete("/{boardId}")
async def delete_board_endpoint(
    boardId: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """Delete board (owner only)"""
    service = DatabaseService(db)
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
    
    success = service.delete_board(str(boardId))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    return {"message": "Board deleted successfully"}