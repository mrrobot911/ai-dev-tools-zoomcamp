from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import time
import enum


class ServiceResult(BaseModel):
    data: Optional[Any] = None
    error: Optional[str] = None


class ServiceError(BaseModel):
    error: str


class Role(str, enum.Enum):
    interviewer = "interviewer"
    candidate = "candidate"


class SessionStatus(str, enum.Enum):
    active = "active"
    completed = "completed"


class SessionParticipant(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    role: Role
    joinedAt: int = Field(default_factory=lambda: int(time.time()))

    @field_validator('joinedAt')
    @classmethod
    def validate_joined_at(cls, v):
        return int(v)


class Session(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str = Field(max_length=200)
    description: str = Field(max_length=1000)
    joinCode: str = Field(pattern=r'^[A-Z0-9]{6}$')
    status: SessionStatus = SessionStatus.active
    createdAt: int = Field(default_factory=lambda: int(time.time()))
    participants: List[SessionParticipant] = []

    @field_validator('joinCode')
    @classmethod
    def validate_join_code(cls, v):
        return v.upper()


class ElementType(str, enum.Enum):
    box = "box"
    arrow = "arrow"
    text = "text"


class DiagramElement(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: ElementType
    x: float
    y: float
    width: float
    height: float
    label: Optional[str] = None
    fromId: Optional[UUID] = None
    toId: Optional[UUID] = None
    text: Optional[str] = None


class DiagramState(BaseModel):
    elements: List[DiagramElement] = []


class NoteVisibility(str, enum.Enum):
    private = "private"
    shared = "shared"


class Note(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    sessionId: UUID
    authorId: UUID
    authorName: str = Field(max_length=100)
    content: str = Field(max_length=2000)
    visibility: NoteVisibility = NoteVisibility.private
    createdAt: int = Field(default_factory=lambda: int(time.time()))
    updatedAt: int = Field(default_factory=lambda: int(time.time()))


class EventType(str, enum.Enum):
    join = "join"
    leave = "leave"
    element_add = "element-add"
    element_update = "element-update"
    element_remove = "element-remove"
    note_add = "note-add"
    note_update = "note-update"
    note_remove = "note-remove"
    session_complete = "session-complete"


class SessionEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    sessionId: UUID
    type: EventType
    participantId: Optional[UUID] = None
    participantName: str
    timestamp: int = Field(default_factory=lambda: int(time.time()))
    payload: Dict[str, Any] = {}


class CreateSessionRequest(BaseModel):
    title: str = Field(max_length=200)
    description: str = Field(max_length=1000)
    interviewerName: str = Field(max_length=100)


class JoinSessionRequest(BaseModel):
    joinCode: str = Field(pattern=r'^[A-Z0-9]{6}$')
    candidateName: str = Field(max_length=100)

    @field_validator('joinCode')
    @classmethod
    def validate_join_code(cls, v):
        return v.upper()


class AddDiagramElementRequest(BaseModel):
    sessionId: UUID
    element: DiagramElement
    actorId: UUID


class UpdateDiagramElementRequest(BaseModel):
    sessionId: UUID
    elementId: UUID
    updates: DiagramElement
    actorId: UUID


class RemoveDiagramElementRequest(BaseModel):
    sessionId: UUID
    elementId: UUID
    actorId: UUID


class AddNoteRequest(BaseModel):
    sessionId: UUID
    authorId: UUID
    authorName: str = Field(max_length=100)
    content: str = Field(max_length=2000)
    visibility: NoteVisibility = NoteVisibility.private


class UpdateNoteRequest(BaseModel):
    noteId: UUID
    updates: Dict[str, Any]
    actorId: UUID


class RemoveNoteRequest(BaseModel):
    noteId: UUID
    actorId: UUID