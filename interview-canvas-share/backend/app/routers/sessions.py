from fastapi import APIRouter, HTTPException, status
from typing import Optional
from uuid import UUID
from app.models import (
    ServiceResult, ServiceError, CreateSessionRequest, JoinSessionRequest,
    Session, SessionStatus
)
from app.store import store


router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("/", response_model=ServiceResult)
async def create_session(request: CreateSessionRequest):
    """Create a new interview session"""
    try:
        session = store.create_session(
            title=request.title,
            description=request.description,
            interviewer_name=request.interviewerName
        )
        
        return ServiceResult(
            data={
                "session": session,
                "participant": session.participants[0]  # The interviewer who created it
            }
        )
    except Exception as e:
        return ServiceResult(error=str(e))


@router.post("/join", response_model=ServiceResult)
async def join_session(request: JoinSessionRequest):
    """Join an existing session"""
    try:
        session = store.join_session(
            join_code=request.joinCode,
            candidate_name=request.candidateName
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Find the participant who just joined
        participant = None
        for p in session.participants:
            if p.name == request.candidateName:
                participant = p
                break
        
        return ServiceResult(
            data={
                "session": session,
                "participant": participant
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        return ServiceResult(error=str(e))


@router.get("/{session_id}", response_model=ServiceResult)
async def get_session(session_id: UUID):
    """Get session details"""
    try:
        session = store.get_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return ServiceResult(data=session)
    except HTTPException:
        raise
    except Exception as e:
        return ServiceResult(error=str(e))


@router.patch("/{session_id}", response_model=ServiceResult)
async def complete_session(session_id: UUID):
    """Complete a session"""
    try:
        session = store.complete_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return ServiceResult(data=session)
    except HTTPException:
        raise
    except Exception as e:
        return ServiceResult(error=str(e))