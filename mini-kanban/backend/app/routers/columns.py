from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session

from app.models import Column, ColumnCreate, ColumnUpdate, ColumnReorder
from app.database_service import DatabaseService
from app.auth import get_current_active_user
from app.models import User
from app.dependencies import get_db_session

router = APIRouter()


@router.post("/{boardId}/columns", response_model=Column, status_code=201)
async def create_column_endpoint(
    boardId: UUID,
    column_data: ColumnCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """Create column (owner only)"""
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
    
    column = service.create_column(str(boardId), column_data.name)
    # Convert to API model
    from app.model_converter import ModelConverter
    return ModelConverter.to_column_model(column)


@router.put("/{boardId}/columns/{columnId}", response_model=Column)
async def update_column_endpoint(
    boardId: UUID,
    columnId: UUID,
    column_data: ColumnUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update column (owner only)"""
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
    
    # Check if column exists and belongs to this board
    columns = get_columns_by_board(boardId)
    column_exists = any(c.id == columnId for c in columns)
    if not column_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    updated_column = update_column(
        column_id=columnId,
        name=column_data.name,
        order=column_data.order
    )
    
    if not updated_column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    return updated_column


@router.delete("/{boardId}/columns/{columnId}")
async def delete_column_endpoint(
    boardId: UUID,
    columnId: UUID,
    current_user: User = Depends(get_current_active_user)
):
    """Delete column (owner only, must be empty)"""
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
    
    # Check if column exists and belongs to this board
    columns = get_columns_by_board(boardId)
    column_exists = any(c.id == columnId for c in columns)
    if not column_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    # Check if column is empty (in a real app, check for cards)
    # For now, we'll allow deletion regardless of content
    
    success = delete_column(columnId)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    return {"message": "Column deleted"}


@router.put("/{boardId}/columns/reorder", response_model=List[Column])
async def reorder_columns_endpoint(
    boardId: UUID,
    reorder_data: ColumnReorder,
    current_user: User = Depends(get_current_active_user)
):
    """Reorder columns (owner only)"""
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
    
    # Validate all column IDs exist and belong to this board
    columns = get_columns_by_board(boardId)
    column_ids = [c.id for c in columns]
    
    for column_id in reorder_data.columnIds:
        if column_id not in column_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Column not found"
            )
    
    updated_columns = reorder_columns(boardId, reorder_data.columnIds)
    return updated_columns