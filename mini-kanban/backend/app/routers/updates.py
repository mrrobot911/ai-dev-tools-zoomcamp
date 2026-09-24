from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from sqlalchemy import and_

from app.auth import get_current_active_user
from app.database import get_session
from app.database_service import DatabaseService
from app.models.database import User
from app.models.database import Board, BoardColumn, Card, BoardParticipant

router = APIRouter()

@router.get("/api/boards/{board_id}/updates")
async def get_board_updates(
    board_id: str,
    since: str = Query(..., description="ISO 8601 timestamp"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
) -> List[dict]:
    """
    Poll for board updates using long polling.
    
    Returns changes to the board since the given timestamp.
    If no changes are available, holds the request open for up to 30 seconds.
    """
    # Convert since timestamp to datetime
    try:
        since_datetime = datetime.fromisoformat(since.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format")
    
    # Check if user is a participant of this board
    service = DatabaseService(db)
    board = service.get_board_by_id(board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    # Check if user is a participant
    is_participant = db.query(BoardParticipant).filter(
        and_(
            BoardParticipant.board_id == board_id,
            BoardParticipant.user_id == str(current_user.id)
        )
    ).first()
    
    if not is_participant:
        raise HTTPException(status_code=403, detail="Not a participant of this board")
    
    # Check for existing changes immediately
    changes = _get_board_changes(db, board_id, since_datetime)
    if changes:
        return changes
    
    # No changes found, wait up to 30 seconds checking every second
    import asyncio
    max_wait_time = 30
    check_interval = 1
    
    for _ in range(max_wait_time):
        # Check for changes
        changes = _get_board_changes(db, board_id, since_datetime)
        if changes:
            return changes
        
        # Wait for 1 second before checking again
        await asyncio.sleep(check_interval)
    
    # Timeout reached, return empty list
    return []

def _get_board_changes(db: Session, board_id: str, since: datetime) -> List[dict]:
    """
    Get all changes to a board since the given timestamp.
    Returns a list of BoardEvent objects.
    """
    changes = []
    
    # Get board updates
    board_updates = db.query(Board).filter(
        and_(Board.id == board_id, Board.updated_at > since)
    ).all()
    
    for board in board_updates:
        changes.append({
            "entity_type": "board",
            "action": "updated",
            "entity_id": board.id,
            "timestamp": board.updated_at.isoformat(),
            "payload": {
                "id": board.id,
                "name": board.name,
                "ownerId": board.owner_id,
                "ownerName": board.owner.name if board.owner else None,
                "createdAt": board.created_at.isoformat(),
                "updatedAt": board.updated_at.isoformat()
            }
        })
    
    # Get column updates
    column_updates = db.query(BoardColumn).filter(
        and_(BoardColumn.board_id == board_id, BoardColumn.updated_at > since)
    ).all()
    
    for column in column_updates:
        # Check if it was deleted by checking if it still exists
        column_exists = db.query(BoardColumn).filter(BoardColumn.id == column.id).first()
        
        action = "deleted" if not column_exists else "updated"
        payload = None if action == "deleted" else {
            "id": column.id,
            "boardId": column.board_id,
            "name": column.name,
            "order": column.order,
            "createdAt": column.created_at.isoformat()
        }
        
        changes.append({
            "entity_type": "column",
            "action": action,
            "entity_id": column.id,
            "timestamp": column.updated_at.isoformat(),
            "payload": payload
        })
    
    # Get card updates
    card_updates = db.query(Card).filter(
        and_(Card.board_id == board_id, Card.updated_at > since)
    ).all()
    
    for card in card_updates:
        # Check if it was deleted by checking if it still exists
        card_exists = db.query(Card).filter(Card.id == card.id).first()
        
        action = "deleted" if not card_exists else "updated"
        payload = None if action == "deleted" else {
            "id": card.id,
            "boardId": card.board_id,
            "columnId": card.column_id,
            "title": card.title,
            "description": card.description,
            "creatorId": card.creator_id,
            "creatorName": card.creator_name,
            "assigneeId": card.assignee_id,
            "assigneeName": card.assignee_name,
            "createdAt": card.created_at.isoformat(),
            "updatedAt": card.updated_at.isoformat()
        }
        
        changes.append({
            "entity_type": "card",
            "action": action,
            "entity_id": card.id,
            "timestamp": card.updated_at.isoformat(),
            "payload": payload
        })
    
    # Get participant updates (joins)
    # For joins: check for new participants since the timestamp
    new_participants = db.query(BoardParticipant).join(
        User, BoardParticipant.user_id == User.id
    ).filter(
        and_(BoardParticipant.board_id == board_id, BoardParticipant.joined_at > since)
    ).all()
    
    for participant in new_participants:
        changes.append({
            "entity_type": "participant",
            "action": "created",
            "entity_id": participant.id,
            "timestamp": participant.joined_at.isoformat(),
            "payload": {
                "userId": participant.user_id,
                "email": participant.user.email if participant.user else "unknown@example.com",
                "name": participant.user.name if participant.user else "Unknown",
                "role": participant.role,
                "joinedAt": participant.joined_at.isoformat()
            }
        })
    
    # For leaves: check for participants who were removed
    # This is harder to track without a deleted_at field, so we'll skip for now
    
    # Sort changes by timestamp
    changes.sort(key=lambda x: x["timestamp"])
    
    return changes