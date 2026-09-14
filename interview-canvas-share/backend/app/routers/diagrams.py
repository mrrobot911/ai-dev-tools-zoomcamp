from fastapi import APIRouter, HTTPException, status, Path
from typing import Optional
from uuid import UUID
from app.models import (
    ServiceResult, ServiceError, DiagramElement, DiagramState,
    AddDiagramElementRequest, UpdateDiagramElementRequest, RemoveDiagramElementRequest
)
from app.store import store
from app.auth import auth_service


router = APIRouter(prefix="/sessions/{session_id}/diagram", tags=["Diagrams"])


@router.get("/", response_model=ServiceResult)
async def get_diagram_state(session_id: UUID = Path(..., description="Session ID")):
    """Get diagram state"""
    try:
        session = store.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        diagram_state = store.get_diagram_state(session_id)
        return ServiceResult(data=diagram_state)
    except HTTPException:
        raise
    except Exception as e:
        return ServiceResult(error=str(e))


@router.post("/", response_model=ServiceResult, status_code=status.HTTP_201_CREATED)
async def add_diagram_element(
    request: AddDiagramElementRequest,
    session_id: UUID = Path(..., description="Session ID")
):
    """Add diagram element"""
    try:
        session = store.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Validate session is active
        auth_service.validate_active_session(session)
        
        element = store.add_diagram_element(
            session_id=session_id,
            element=request.element,
            actor_id=request.actorId
        )
        
        if not element:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add element"
            )
        
        return ServiceResult(data=element)
    except HTTPException:
        raise
    except Exception as e:
        return ServiceResult(error=str(e))


@router.put("/", response_model=ServiceResult)
async def update_diagram_element(
    request: UpdateDiagramElementRequest,
    session_id: UUID = Path(..., description="Session ID")
):
    """Update diagram element"""
    try:
        session = store.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Validate session is active
        auth_service.validate_active_session(session)
        
        element = store.update_diagram_element(
            session_id=session_id,
            element_id=request.elementId,
            updates=request.updates,
            actor_id=request.actorId
        )
        
        if not element:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Element not found"
            )
        
        return ServiceResult(data=element)
    except HTTPException:
        raise
    except Exception as e:
        return ServiceResult(error=str(e))


@router.delete("/", response_model=ServiceResult)
async def remove_diagram_element(
    request: RemoveDiagramElementRequest,
    session_id: UUID = Path(..., description="Session ID")
):
    """Remove diagram element"""
    try:
        session = store.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Validate session is active
        auth_service.validate_active_session(session)
        
        result = store.remove_diagram_element(
            session_id=session_id,
            element_id=request.elementId,
            actor_id=request.actorId
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Element not found"
            )
        
        return ServiceResult(data=result)
    except HTTPException:
        raise
    except Exception as e:
        return ServiceResult(error=str(e))