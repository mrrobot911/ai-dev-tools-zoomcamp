import pytest
from uuid import uuid4
from app.store import InMemoryStore
from app.models import (
    Session, SessionParticipant, Role, SessionStatus,
    DiagramElement, ElementType, Note, NoteVisibility, EventType, SessionEvent
)


class TestInMemoryStore:
    def setup_method(self):
        """Setup test store"""
        self.store = InMemoryStore()
        
        # Create a test session using the store
        self.session = self.store.create_session(
            title="Test Session",
            description="Test Description",
            interviewer_name="Test Interviewer"
        )
        
        # Add a test participant
        self.participant_id = uuid4()
        self.session.participants.append(
            SessionParticipant(
                id=self.participant_id,
                name="Test User",
                role=Role.interviewer
            )
        )

    def test_create_session(self):
        """Test creating a new session"""
        session = self.store.create_session(
            title="Test Session",
            description="Test Description",
            interviewer_name="Test Interviewer"
        )
        
        assert session.title == "Test Session"
        assert session.description == "Test Description"
        assert session.participants[0].name == "Test Interviewer"
        assert session.participants[0].role == Role.interviewer
        assert len(session.participants) == 1
        assert session.status == SessionStatus.active

    def test_get_session(self):
        """Test getting a session"""
        # Create a session first
        created_session = self.store.create_session(
            title="Test Session",
            description="Test Description",
            interviewer_name="Test Interviewer"
        )
        
        # Get the session
        retrieved_session = self.store.get_session(created_session.id)
        
        assert retrieved_session is not None
        assert retrieved_session.id == created_session.id
        assert retrieved_session.title == "Test Session"

    def test_get_nonexistent_session(self):
        """Test getting a non-existent session"""
        session = self.store.get_session(uuid4())
        assert session is None

    def test_join_session(self):
        """Test joining a session"""
        # Create a session first
        created_session = self.store.create_session(
            title="Test Session",
            description="Test Description",
            interviewer_name="Test Interviewer"
        )
        
        # Join the session
        joined_session = self.store.join_session(
            join_code=created_session.joinCode,
            candidate_name="Test Candidate"
        )
        
        assert joined_session is not None
        assert len(joined_session.participants) == 2
        assert joined_session.participants[1].name == "Test Candidate"
        assert joined_session.participants[1].role == Role.candidate

    def test_join_nonexistent_session(self):
        """Test joining a non-existent session"""
        session = self.store.join_session(
            join_code="NONEXIST",
            candidate_name="Test Candidate"
        )
        assert session is None

    def test_complete_session(self):
        """Test completing a session"""
        # Create a session first
        created_session = self.store.create_session(
            title="Test Session",
            description="Test Description",
            interviewer_name="Test Interviewer"
        )
        
        # Complete the session
        completed_session = self.store.complete_session(created_session.id)
        
        assert completed_session is not None
        assert completed_session.status == SessionStatus.completed

    def test_complete_nonexistent_session(self):
        """Test completing a non-existent session"""
        session = self.store.complete_session(uuid4())
        assert session is None

    def test_get_diagram_state(self):
        """Test getting diagram state"""
        # Create a session using the store
        self.store = InMemoryStore()
        session = self.store.create_session(
            title="Test Session",
            description="Test Description",
            interviewer_name="Interviewer"
        )
        
        # Get diagram state
        diagram_state = self.store.get_diagram_state(session.id)
        
        assert diagram_state is not None
        assert isinstance(diagram_state.elements, list)

    def test_add_diagram_element(self):
        """Test adding a diagram element"""
        element = DiagramElement(
            type=ElementType.box,
            x=100,
            y=100,
            width=200,
            height=100,
            label="Test Element"
        )
        
        added_element = self.store.add_diagram_element(
            session_id=self.session.id,
            element=element,
            actor_id=self.session.participants[0].id
        )
        
        assert added_element is not None
        assert added_element.label == "Test Element"
        assert len(self.store.diagram_elements[self.session.id]) == 1

    def test_update_diagram_element(self):
        """Test updating a diagram element"""
        element_id = uuid4()
        
        # Setup element
        original_element = DiagramElement(
            id=element_id,
            type=ElementType.box,
            x=100,
            y=100,
            width=200,
            height=100,
            label="Original Element"
        )
        
        self.store.diagram_elements[self.session.id] = [original_element]
        
        # Update the element
        updated_element = DiagramElement(
            id=element_id,
            type=ElementType.box,
            x=200,
            y=200,
            width=300,
            height=150,
            label="Updated Element"
        )
        
        result = self.store.update_diagram_element(
            session_id=self.session.id,
            element_id=element_id,
            updates=updated_element,
            actor_id=self.session.participants[0].id
        )
        
        assert result is not None
        assert result.label == "Updated Element"
        assert self.store.diagram_elements[self.session.id][0].label == "Updated Element"

    def test_remove_diagram_element(self):
        """Test removing a diagram element"""
        element_id = uuid4()
        
        # Setup element
        element = DiagramElement(
            id=element_id,
            type=ElementType.box,
            x=100,
            y=100,
            width=200,
            height=100,
            label="Test Element"
        )
        
        self.store.diagram_elements[self.session.id] = [element]
        
        # Remove the element
        result = self.store.remove_diagram_element(
            session_id=self.session.id,
            element_id=element_id,
            actor_id=self.session.participants[0].id
        )
        
        assert result is not None
        assert result["id"] == str(element_id)
        assert len(self.store.diagram_elements[self.session.id]) == 0

    def test_add_note(self):
        """Test adding a note"""
        note = self.store.add_note(
            session_id=self.session.id,
            author_id=self.participant_id,
            author_name="Test User",
            content="Test Note Content",
            visibility=NoteVisibility.shared
        )
        
        assert note is not None
        assert note.content == "Test Note Content"
        assert note.visibility == NoteVisibility.shared
        assert len(self.store.notes[self.session.id]) == 1

    def test_update_note(self):
        """Test updating a note"""
        note_id = uuid4()
        
        # Setup note
        original_note = Note(
            id=note_id,
            sessionId=self.session.id,
            authorId=self.participant_id,
            authorName="Test User",
            content="Original Note Content",
            visibility=NoteVisibility.private
        )
        
        self.store.notes[self.session.id] = [original_note]
        
        # Update the note
        updates = {"content": "Updated Note Content"}
        result = self.store.update_note(
            note_id=note_id,
            updates=updates,
            actor_id=self.participant_id
        )
        
        assert result is not None
        assert result.content == "Updated Note Content"
        assert self.store.notes[self.session.id][0].content == "Updated Note Content"

    def test_remove_note(self):
        """Test removing a note"""
        note_id = uuid4()
        
        # Setup note
        note = Note(
            id=note_id,
            sessionId=self.session.id,
            authorId=self.participant_id,
            authorName="Test User",
            content="Test Note Content",
            visibility=NoteVisibility.shared
        )
        
        self.store.notes[self.session.id] = [note]
        
        # Remove the note
        result = self.store.remove_note(
            note_id=note_id,
            actor_id=self.participant_id
        )
        
        assert result is not None
        assert result["id"] == str(note_id)
        assert len(self.store.notes[self.session.id]) == 0

    def test_add_event(self):
        """Test adding an event"""
        # Add an event
        self.store.add_event(
            session_id=self.session.id,
            event_type=EventType.join,
            participant_id=self.participant_id,
            participant_name="Test User"
        )
        
        # Should have 2 events now (1 from setup + 1 from this test)
        assert len(self.store.events[self.session.id]) == 2
        event = self.store.events[self.session.id][1]  # Get the second event
        assert event.type == EventType.join
        assert event.participantName == "Test User"

    def test_get_events(self):
        """Test getting events"""
        # Add some events
        self.store.add_event(
            session_id=self.session.id,
            event_type=EventType.join,
            participant_id=self.participant_id,
            participant_name="Test User"
        )
        
        self.store.add_event(
            session_id=self.session.id,
            event_type=EventType.element_add,
            participant_id=self.participant_id,
            participant_name="Test User",
            payload={"elementId": "test-element"}
        )
        
        # Get events - should have 3 events total (1 from setup + 2 from this test)
        events = self.store.get_events(self.session.id)
        
        assert len(events) == 3
        assert events[0].type == EventType.join  # From setup
        assert events[1].type == EventType.join  # From this test
        assert events[2].type == EventType.element_add  # From this test
        assert events[2].payload["elementId"] == "test-element"