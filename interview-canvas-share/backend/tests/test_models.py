import pytest
from app.models import (
    Session, SessionParticipant, Role, SessionStatus,
    DiagramElement, ElementType, Note, NoteVisibility, EventType, SessionEvent,
    CreateSessionRequest, JoinSessionRequest, AddDiagramElementRequest,
    UpdateDiagramElementRequest, RemoveDiagramElementRequest, AddNoteRequest,
    UpdateNoteRequest, RemoveNoteRequest
)
from uuid import uuid4
import time


class TestModels:
    def test_session_creation(self):
        """Test Session model creation"""
        session = Session(
            title="Test Session",
            description="Test Description",
            joinCode="ABC123"
        )
        
        assert session.title == "Test Session"
        assert session.description == "Test Description"
        assert session.joinCode == "ABC123"
        assert session.status == SessionStatus.active
        assert len(session.participants) == 0

    def test_session_participant_creation(self):
        """Test SessionParticipant model creation"""
        participant = SessionParticipant(
            name="Test User",
            role=Role.interviewer
        )
        
        assert participant.name == "Test User"
        assert participant.role == Role.interviewer
        assert participant.joinedAt > 0

    def test_diagram_element_creation(self):
        """Test DiagramElement model creation"""
        element = DiagramElement(
            type=ElementType.box,
            x=100,
            y=100,
            width=200,
            height=100,
            label="Test Element"
        )
        
        assert element.type == ElementType.box
        assert element.x == 100
        assert element.y == 100
        assert element.width == 200
        assert element.height == 100
        assert element.label == "Test Element"

    def test_note_creation(self):
        """Test Note model creation"""
        note = Note(
            sessionId=uuid4(),
            authorId=uuid4(),
            authorName="Test User",
            content="Test Note Content",
            visibility=NoteVisibility.shared
        )
        
        assert note.authorName == "Test User"
        assert note.content == "Test Note Content"
        assert note.visibility == NoteVisibility.shared

    def test_session_event_creation(self):
        """Test SessionEvent model creation"""
        event = SessionEvent(
            sessionId=uuid4(),
            type=EventType.join,
            participantId=uuid4(),
            participantName="Test User"
        )
        
        assert event.type == EventType.join
        assert event.participantName == "Test User"

    def test_create_session_request_validation(self):
        """Test CreateSessionRequest validation"""
        request = CreateSessionRequest(
            title="Test Session",
            description="Test Description",
            interviewerName="Test Interviewer"
        )
        
        assert request.title == "Test Session"
        assert request.description == "Test Description"
        assert request.interviewerName == "Test Interviewer"

    def test_join_session_request_validation(self):
        """Test JoinSessionRequest validation"""
        request = JoinSessionRequest(
            joinCode="ABC123",
            candidateName="Test Candidate"
        )
        
        assert request.joinCode == "ABC123"
        assert request.candidateName == "Test Candidate"

    def test_add_diagram_element_request_validation(self):
        """Test AddDiagramElementRequest validation"""
        element = DiagramElement(
            type=ElementType.box,
            x=100,
            y=100,
            width=200,
            height=100
        )
        
        request = AddDiagramElementRequest(
            sessionId=uuid4(),
            element=element,
            actorId=uuid4()
        )
        
        assert request.element.type == ElementType.box
        assert request.actorId is not None

    def test_add_note_request_validation(self):
        """Test AddNoteRequest validation"""
        request = AddNoteRequest(
            sessionId=uuid4(),
            authorId=uuid4(),
            authorName="Test User",
            content="Test Note Content",
            visibility=NoteVisibility.shared
        )
        
        assert request.authorName == "Test User"
        assert request.content == "Test Note Content"
        assert request.visibility == NoteVisibility.shared

    def test_join_code_generation_format(self):
        """Test that join codes follow the required format"""
        from app.store import InMemoryStore
        
        store = InMemoryStore()
        
        # Generate several codes to check format
        codes = []
        for _ in range(10):
            code = store._generate_join_code()
            codes.append(code)
        
        # Check all codes match the pattern: 6 uppercase letters or digits
        import re
        pattern = r'^[A-Z0-9]{6}$'
        for code in codes:
            assert re.match(pattern, code), f"Code {code} doesn't match pattern {pattern}"

    def test_session_status_enum_values(self):
        """Test SessionStatus enum values"""
        assert SessionStatus.active == "active"
        assert SessionStatus.completed == "completed"

    def test_role_enum_values(self):
        """Test Role enum values"""
        assert Role.interviewer == "interviewer"
        assert Role.candidate == "candidate"

    def test_element_type_enum_values(self):
        """Test ElementType enum values"""
        assert ElementType.box == "box"
        assert ElementType.arrow == "arrow"
        assert ElementType.text == "text"

    def test_note_visibility_enum_values(self):
        """Test NoteVisibility enum values"""
        assert NoteVisibility.private == "private"
        assert NoteVisibility.shared == "shared"

    def test_event_type_enum_values(self):
        """Test EventType enum values"""
        assert EventType.join == "join"
        assert EventType.leave == "leave"
        assert EventType.element_add == "element-add"
        assert EventType.element_update == "element-update"
        assert EventType.element_remove == "element-remove"
        assert EventType.note_add == "note-add"
        assert EventType.note_update == "note-update"
        assert EventType.note_remove == "note-remove"
        assert EventType.session_complete == "session-complete"