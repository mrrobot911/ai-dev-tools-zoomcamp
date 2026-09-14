import pytest
from uuid import uuid4
from app.auth import AuthService
from app.models import Session, SessionParticipant, Role, SessionStatus
from app.store import InMemoryStore


class TestAuthService:
    def setup_method(self):
        """Setup test data"""
        # Create a session using the store to ensure valid join code
        self.store = InMemoryStore()
        self.session = self.store.create_session(
            title="Test Session",
            description="Test Description",
            interviewer_name="Interviewer"
        )

    def test_validate_participant_success(self):
        """Test successful participant validation"""
        participant_id = self.session.participants[0].id
        participant = AuthService.validate_participant(self.session, participant_id)
        assert participant.id == participant_id
        assert participant.name == "Interviewer"

    def test_validate_participant_not_found(self):
        """Test participant validation with non-existent participant"""
        fake_id = uuid4()
        with pytest.raises(Exception) as exc_info:
            AuthService.validate_participant(self.session, fake_id)
        assert "Participant not found" in str(exc_info.value)

    def test_validate_interviewer_success(self):
        """Test successful interviewer validation"""
        interviewer_id = self.session.participants[0].id
        participant = AuthService.validate_interviewer(self.session, interviewer_id)
        assert participant.role == Role.interviewer

    def test_validate_interviewer_forbidden(self):
        """Test interviewer validation with candidate"""
        # Add a candidate to the session
        candidate_id = uuid4()
        self.session.participants.append(
            SessionParticipant(
                id=candidate_id,
                name="Candidate",
                role=Role.candidate
            )
        )
        
        with pytest.raises(Exception) as exc_info:
            AuthService.validate_interviewer(self.session, candidate_id)
        assert "Only interviewer can perform this action" in str(exc_info.value)

    def test_validate_active_session_success(self):
        """Test successful active session validation"""
        session = AuthService.validate_active_session(self.session)
        assert session.status == SessionStatus.active

    def test_validate_active_session_completed(self):
        """Test active session validation with completed session"""
        # Create a completed session using the store
        completed_session = self.store.create_session(
            title="Completed Session",
            description="Test Description",
            interviewer_name="Interviewer"
        )
        
        # Complete the session
        completed_session.status = SessionStatus.completed
        
        with pytest.raises(Exception) as exc_info:
            AuthService.validate_active_session(completed_session)
        assert "Session is not active" in str(exc_info.value)