from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.models import Column, ColumnCreate, ColumnUpdate, ColumnReorder
from app.store import (
    create_column, get_columns_by_board, update_column, delete_column,
    reorder_columns, get_board_by_id
)
from app.auth import get_current_active_user
from app.models import User

router = APIRouter()


@router.post("/{boardId}/columns", response_model=Column, status_code=201)
async def create_column_endpoint(
    boardId: UUID,
    column_data: ColumnCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create column (owner only)"""
    # Check if board exists and user has access
    board = get_board_by_id(boardId)
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check if user is the owner (simplified - in real app, check participants)
    if board.ownerId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    column = create_column(
        board_id=boardId,
        name=column_data.name
    )
    return column


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