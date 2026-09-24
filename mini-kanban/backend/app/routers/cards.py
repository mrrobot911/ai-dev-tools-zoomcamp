from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session

from app.models import Card, CardCreate, CardUpdate, CardMove, CardMoveWithPath, User
from app.database_service import DatabaseService
from app.auth import get_current_active_user
from app.dependencies import get_db_session
from app.model_converter import ModelConverter

router = APIRouter()


@router.post("/{boardId}/cards", response_model=Card, status_code=201)
async def create_card_endpoint(
    boardId: UUID,
    card_data: CardCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """Create card"""
    service = DatabaseService(db)
    
    # Check if board exists and user has access
    board = service.get_board_by_id(str(boardId))
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check if column exists
    columns = service.get_columns_by_board(str(boardId))
    column_exists = any(c["id"] == str(card_data.columnId) for c in columns)
    if not column_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    # Get assignee info if provided
    assignee_name = None
    if card_data.assigneeId:
        assignee = service.get_user_by_id(str(card_data.assigneeId))
        if assignee:
            assignee_name = assignee.name
    
    card = service.create_card(
        board_id=str(boardId),
        column_id=str(card_data.columnId),
        title=card_data.title,
        creator_id=str(current_user.id),
        creator_name=current_user.name,
        description=card_data.description,
        assignee_id=str(card_data.assigneeId) if card_data.assigneeId else None,
        assignee_name=assignee_name
    )
    # Convert to API model
    return ModelConverter.to_card_model(card)


@router.delete("/{boardId}/cards/{cardId}")
async def delete_card_endpoint(
    boardId: UUID,
    cardId: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """Delete card (creator or owner only)"""
    service = DatabaseService(db)
    
    # Check if board exists and user has access
    board = service.get_board_by_id(str(boardId))
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check if card exists and belongs to this board
    cards = service.get_cards_by_board(str(boardId))
    card = None
    for c in cards:
        if str(c.id) == str(cardId):
            card = c
            break
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Check if user is creator or board owner
    if card.creator_id != str(current_user.id) and board.owner_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied (not creator or owner)"
        )
    
    success = service.delete_card(str(cardId))
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
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """Move card to different column"""
    service = DatabaseService(db)
    
    # Check if board exists and user has access
    board = service.get_board_by_id(str(boardId))
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check if card exists and belongs to this board
    cards = service.get_cards_by_board(str(boardId))
    card_exists = any(str(c.id) == str(move_data.cardId) for c in cards)
    if not card_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Check if target column exists
    columns = service.get_columns_by_board(str(boardId))
    target_column_exists = any(c["id"] == str(move_data.targetColumnId) for c in columns)
    if not target_column_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    moved_card = service.move_card(str(move_data.cardId), str(move_data.targetColumnId))
    if not moved_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Convert to API model
    return ModelConverter.to_card_model(moved_card)


@router.put("/{boardId}/cards/{cardId}/move", response_model=Card)
async def move_card_by_path_endpoint(
    boardId: UUID,
    cardId: UUID,
    move_data: CardMoveWithPath,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """Move card to different column (using card ID in path)"""
    service = DatabaseService(db)
    
    # Check if board exists and user has access
    board = service.get_board_by_id(str(boardId))
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check if card exists and belongs to this board
    cards = service.get_cards_by_board(str(boardId))
    card_exists = any(str(c.id) == str(cardId) for c in cards)
    if not card_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Check if target column exists
    columns = service.get_columns_by_board(str(boardId))
    target_column_exists = any(c["id"] == str(move_data.targetColumnId) for c in columns)
    if not target_column_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    moved_card = service.move_card(str(cardId), str(move_data.targetColumnId))
    if not moved_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Convert to API model
    return ModelConverter.to_card_model(moved_card)


@router.put("/{boardId}/cards/{cardId}", response_model=Card)
async def update_card_endpoint(
    boardId: UUID,
    cardId: UUID,
    card_data: CardUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """Update card"""
    service = DatabaseService(db)
    
    # Check if board exists and user has access
    board = service.get_board_by_id(str(boardId))
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check if card exists and belongs to this board
    cards = service.get_cards_by_board(str(boardId))
    card_exists = any(str(c.id) == str(cardId) for c in cards)
    if not card_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Check if target column exists (if columnId is provided)
    if card_data.columnId:
        columns = service.get_columns_by_board(str(boardId))
        target_column_exists = any(c["id"] == str(card_data.columnId) for c in columns)
        if not target_column_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Column not found"
            )
    
    # Get assignee info if provided
    assignee_name = None
    if card_data.assigneeId:
        assignee = service.get_user_by_id(str(card_data.assigneeId))
        if assignee:
            assignee_name = assignee.name
    
    updated_card = service.update_card(
        card_id=str(cardId),
        title=card_data.title,
        description=card_data.description,
        assignee_id=str(card_data.assigneeId) if card_data.assigneeId else None,
        assignee_name=assignee_name
    )
    
    if not updated_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Convert to API model
    return ModelConverter.to_card_model(updated_card)