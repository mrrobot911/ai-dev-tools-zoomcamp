from typing import Dict, List, Optional
from uuid import UUID
import time
import random
import string

from ..models import (
    Session, SessionParticipant, SessionStatus, SessionEvent, EventType,
    DiagramElement, DiagramState, Note, NoteVisibility, Role
)


class InMemoryStore:
    def __init__(self):
        self.sessions: Dict[UUID, Session] = {}
        self.events: Dict[UUID, List[SessionEvent]] = {}
        self.notes: Dict[UUID, Note] = {}
        self.diagram_elements: Dict[UUID, List[DiagramElement]] = {}
        
        # Seed initial data
        self._seed_data()

    def _seed_data(self):
        """Seed the store with initial data for testing"""
        # Create a sample session
        session_id = UUID('12345678-1234-5678-1234-567812345678')
        session = Session(
            id=session_id,
            title="Sample Interview Session",
            description="This is a sample interview session for testing purposes",
            joinCode="ABC123",
            status=SessionStatus.active,
            participants=[
                SessionParticipant(
                    id=UUID('11111111-1111-1111-1111-111111111111'),
                    name="John Interviewer",
                    role=Role.interviewer
                ),
                SessionParticipant(
                    id=UUID('22222222-2222-2222-2222-222222222222'),
                    name="Jane Candidate",
                    role=Role.candidate
                )
            ]
        )
        self.sessions[session_id] = session
        self.events[session_id] = []
        self.diagram_elements[session_id] = []
        self.notes[session_id] = []
        
        # Add some sample diagram elements
        self.diagram_elements[session_id].extend([
            DiagramElement(
                id=UUID('10000000-1000-1000-1000-100000000001'),
                type="box",
                x=100,
                y=100,
                width=200,
                height=100,
                label="Start"
            ),
            DiagramElement(
                id=UUID('10000000-1000-1000-1000-100000000002'),
                type="box",
                x=400,
                y=100,
                width=200,
                height=100,
                label="Process"
            ),
            DiagramElement(
                id=UUID('10000000-1000-1000-1000-100000000003'),
                type="arrow",
                x=300,
                y=150,
                width=100,
                height=20,
                fromId=UUID('10000000-1000-1000-1000-100000000001'),
                toId=UUID('10000000-1000-1000-1000-100000000002')
            )
        ])
        
        # Add some sample notes
        self.notes[session_id].extend([
            Note(
                id=UUID('30000000-1000-1000-1000-100000000001'),
                sessionId=session_id,
                authorId=UUID('11111111-1111-1111-1111-111111111111'),
                authorName="John Interviewer",
                content="Welcome to the interview! Please introduce yourself.",
                visibility=NoteVisibility.shared
            ),
            Note(
                id=UUID('30000000-1000-1000-1000-100000000002'),
                sessionId=session_id,
                authorId=UUID('22222222-2222-2222-2222-222222222222'),
                authorName="Jane Candidate",
                content="I have 5 years of experience in Python and FastAPI.",
                visibility=NoteVisibility.shared
            )
        ])
        
        # Add some events
        self.events[session_id].extend([
            SessionEvent(
                id=UUID('40000000-1000-1000-1000-100000000001'),
                sessionId=session_id,
                type=EventType.join,
                participantId=UUID('11111111-1111-1111-1111-111111111111'),
                participantName="John Interviewer",
                timestamp=int(time.time()) - 3600
            ),
            SessionEvent(
                id=UUID('40000000-1000-1000-1000-100000000002'),
                sessionId=session_id,
                type=EventType.join,
                participantId=UUID('22222222-2222-2222-2222-222222222222'),
                participantName="Jane Candidate",
                timestamp=int(time.time()) - 1800
            )
        ])

    def _generate_join_code(self) -> str:
        """Generate a unique join code"""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            # Check if code already exists
            for session in self.sessions.values():
                if session.joinCode == code:
                    break
            else:
                return code

    # Session operations
    def create_session(self, title: str, description: str, interviewer_name: str) -> Session:
        session_id = UUID(int=int(time.time()))
        participant_id = UUID(int=int(time.time()) + 1)
        
        session = Session(
            id=session_id,
            title=title,
            description=description,
            joinCode=self._generate_join_code(),
            status=SessionStatus.active,
            participants=[
                SessionParticipant(
                    id=participant_id,
                    name=interviewer_name,
                    role=Role.interviewer
                )
            ]
        )
        
        self.sessions[session_id] = session
        self.events[session_id] = []
        self.diagram_elements[session_id] = []
        self.notes[session_id] = []
        
        # Add join event
        self.add_event(
            session_id=session_id,
            event_type=EventType.join,
            participant_id=participant_id,
            participant_name=interviewer_name
        )
        
        return session

    def get_session(self, session_id: UUID) -> Optional[Session]:
        return self.sessions.get(session_id)

    def join_session(self, join_code: str, candidate_name: str) -> Optional[Session]:
        for session in self.sessions.values():
            if session.joinCode == join_code and session.status == SessionStatus.active:
                participant_id = UUID(int=int(time.time()))
                
                # Check if participant already exists
                existing_participants = [p for p in session.participants if p.name == candidate_name]
                if existing_participants:
                    return session
                
                participant = SessionParticipant(
                    id=participant_id,
                    name=candidate_name,
                    role=Role.candidate
                )
                
                session.participants.append(participant)
                self.add_event(
                    session_id=session.id,
                    event_type=EventType.join,
                    participant_id=participant_id,
                    participant_name=candidate_name
                )
                
                return session
        return None

    def complete_session(self, session_id: UUID) -> Optional[Session]:
        session = self.sessions.get(session_id)
        if session and session.status == SessionStatus.active:
            session.status = SessionStatus.completed
            self.add_event(
                session_id=session_id,
                event_type=EventType.session_complete,
                participant_id=None,
                participant_name="System"
            )
            return session
        return None

    # Diagram operations
    def get_diagram_state(self, session_id: UUID) -> Optional[DiagramState]:
        elements = self.diagram_elements.get(session_id, [])
        return DiagramState(elements=elements)

    def add_diagram_element(self, session_id: UUID, element: DiagramElement, actor_id: UUID) -> Optional[DiagramElement]:
        if session_id not in self.diagram_elements:
            self.diagram_elements[session_id] = []
        
        self.diagram_elements[session_id].append(element)
        
        # Add event
        session = self.sessions.get(session_id)
        if session:
            for participant in session.participants:
                if participant.id == actor_id:
                    self.add_event(
                        session_id=session_id,
                        event_type=EventType.element_add,
                        participant_id=actor_id,
                        participant_name=participant.name,
                        payload={"elementId": str(element.id), "elementType": element.type}
                    )
                    break
        
        return element

    def update_diagram_element(self, session_id: UUID, element_id: UUID, updates: DiagramElement, actor_id: UUID) -> Optional[DiagramElement]:
        elements = self.diagram_elements.get(session_id, [])
        for i, element in enumerate(elements):
            if element.id == element_id:
                elements[i] = updates
                self.diagram_elements[session_id] = elements
                
                # Add event
                session = self.sessions.get(session_id)
                if session:
                    for participant in session.participants:
                        if participant.id == actor_id:
                            self.add_event(
                                session_id=session_id,
                                event_type=EventType.element_update,
                                participant_id=actor_id,
                                participant_name=participant.name,
                                payload={"elementId": str(element_id)}
                            )
                            break
                
                return updates
        return None

    def remove_diagram_element(self, session_id: UUID, element_id: UUID, actor_id: UUID) -> Optional[Dict]:
        elements = self.diagram_elements.get(session_id, [])
        for i, element in enumerate(elements):
            if element.id == element_id:
                removed_element = elements.pop(i)
                self.diagram_elements[session_id] = elements
                
                # Add event
                session = self.sessions.get(session_id)
                if session:
                    for participant in session.participants:
                        if participant.id == actor_id:
                            self.add_event(
                                session_id=session_id,
                                event_type=EventType.element_remove,
                                participant_id=actor_id,
                                participant_name=participant.name,
                                payload={"elementId": str(element_id)}
                            )
                            break
                
                return {"id": str(element_id)}
        return None

    # Note operations
    def get_notes(self, session_id: UUID, participant_id: UUID) -> List[Note]:
        notes = self.notes.get(session_id, [])
        return notes

    def add_note(self, session_id: UUID, author_id: UUID, author_name: str, content: str, visibility: NoteVisibility) -> Optional[Note]:
        if session_id not in self.notes:
            self.notes[session_id] = []
        
        note = Note(
            sessionId=session_id,
            authorId=author_id,
            authorName=author_name,
            content=content,
            visibility=visibility
        )
        
        self.notes[session_id].append(note)
        
        # Add event
        self.add_event(
            session_id=session_id,
            event_type=EventType.note_add,
            participant_id=author_id,
            participant_name=author_name,
            payload={"noteId": str(note.id)}
        )
        
        return note

    def update_note(self, note_id: UUID, updates: Dict, actor_id: UUID) -> Optional[Note]:
        for session_id, notes in self.notes.items():
            for i, note in enumerate(notes):
                if note.id == note_id:
                    # Apply updates
                    if 'content' in updates:
                        note.content = updates['content']
                    if 'visibility' in updates:
                        note.visibility = updates['visibility']
                    note.updatedAt = int(time.time())
                    
                    # Add event
                    session = self.sessions.get(session_id)
                    if session:
                        for participant in session.participants:
                            if participant.id == actor_id:
                                self.add_event(
                                    session_id=session_id,
                                    event_type=EventType.note_update,
                                    participant_id=actor_id,
                                    participant_name=participant.name,
                                    payload={"noteId": str(note_id)}
                                )
                                break
                    
                    return note
        return None

    def remove_note(self, note_id: UUID, actor_id: UUID) -> Optional[Dict]:
        for session_id, notes in self.notes.items():
            for i, note in enumerate(notes):
                if note.id == note_id:
                    removed_note = notes.pop(i)
                    
                    # Add event
                    session = self.sessions.get(session_id)
                    if session:
                        for participant in session.participants:
                            if participant.id == actor_id:
                                self.add_event(
                                    session_id=session_id,
                                    event_type=EventType.note_remove,
                                    participant_id=actor_id,
                                    participant_name=participant.name,
                                    payload={"noteId": str(note_id)}
                                )
                                break
                    
                    return {"id": str(note_id)}
        return None

    # Event operations
    def get_events(self, session_id: UUID) -> List[SessionEvent]:
        return self.events.get(session_id, [])

    def add_event(self, session_id: UUID, event_type: EventType, participant_id: Optional[UUID], participant_name: str, payload: Dict = None):
        if session_id not in self.events:
            self.events[session_id] = []
        
        event = SessionEvent(
            sessionId=session_id,
            type=event_type,
            participantId=participant_id,
            participantName=participant_name,
            payload=payload or {}
        )
        
        self.events[session_id].append(event)


# Global store instance
store = InMemoryStore()