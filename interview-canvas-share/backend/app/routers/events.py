from fastapi import APIRouter, HTTPException, status, Path
from typing import Optional
from uuid import UUID
from app.models import ServiceResult, SessionEvent
from app.store import store


router = APIRouter(prefix="/sessions/{sessionId}/events", tags=["Events"])


@router.get("/", response_model=ServiceResult)
async def get_events(session_id: UUID = Path(..., description="Session ID")):
    """Get session events"""
    try:
        session = store.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        events = store.get_events(session_id)
        return ServiceResult(data=events)
    except HTTPException:
        raise
    except Exception as e:
        return ServiceResult(error=str(e))