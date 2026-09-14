from fastapi import APIRouter, HTTPException, status, Path, Query
from typing import Optional
from uuid import UUID
from app.models import (
    ServiceResult, ServiceError, Note, NoteVisibility,
    AddNoteRequest, UpdateNoteRequest, RemoveNoteRequest
)
from app.store import store
from app.auth import auth_service


router = APIRouter(prefix="/sessions/{sessionId}/notes", tags=["Notes"])


@router.get("/", response_model=ServiceResult)
async def get_notes(
    participant_id: UUID = Query(..., description="Participant ID"),
    session_id: UUID = Path(..., description="Session ID")
):
    """Get notes for a session"""
    try:
        session = store.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Validate participant exists in session
        auth_service.validate_participant(session, participant_id)
        
        notes = store.get_notes(session_id, participant_id)
        return ServiceResult(data=notes)
    except HTTPException:
        raise
    except Exception as e:
        return ServiceResult(error=str(e))


@router.post("/", response_model=ServiceResult, status_code=status.HTTP_201_CREATED)
async def add_note(
    request: AddNoteRequest,
    session_id: UUID = Path(..., description="Session ID")
):
    """Add a new note"""
    try:
        session = store.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Validate participant exists in session
        auth_service.validate_participant(session, request.authorId)
        
        note = store.add_note(
            session_id=session_id,
            author_id=request.authorId,
            author_name=request.authorName,
            content=request.content,
            visibility=request.visibility
        )
        
        if not note:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add note"
            )
        
        return ServiceResult(data=note)
    except HTTPException:
        raise
    except Exception as e:
        return ServiceResult(error=str(e))


@router.patch("/{note_id}", response_model=ServiceResult)
async def update_note(
    request: UpdateNoteRequest,
    note_id: UUID = Path(..., description="Note ID")
):
    """Update a note"""
    try:
        note = store.update_note(
            note_id=note_id,
            updates=request.updates,
            actor_id=request.actorId
        )
        
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        
        return ServiceResult(data=note)
    except HTTPException:
        raise
    except Exception as e:
        return ServiceResult(error=str(e))


@router.delete("/{note_id}", response_model=ServiceResult)
async def remove_note(
    request: RemoveNoteRequest,
    note_id: UUID = Path(..., description="Note ID")
):
    """Delete a note"""
    try:
        result = store.remove_note(
            note_id=note_id,
            actor_id=request.actorId
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        
        return ServiceResult(data=result)
    except HTTPException:
        raise
    except Exception as e:
        return ServiceResult(error=str(e))