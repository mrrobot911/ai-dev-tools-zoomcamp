from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status
from ..models import Session, SessionParticipant, Role


class AuthService:
    @staticmethod
    def validate_participant(session: Session, participant_id: UUID) -> SessionParticipant:
        """Validate that participant exists in session and return participant info"""
        for participant in session.participants:
            if participant.id == participant_id:
                return participant
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found in session"
        )

    @staticmethod
    def validate_interviewer(session: Session, participant_id: UUID) -> SessionParticipant:
        """Validate that participant is interviewer in session"""
        participant = AuthService.validate_participant(session, participant_id)
        if participant.role != Role.interviewer:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only interviewer can perform this action"
            )
        return participant

    @staticmethod
    def validate_active_session(session: Session) -> Session:
        """Validate that session is active"""
        if session.status != "active":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Session is not active"
            )
        return session


auth_service = AuthService()