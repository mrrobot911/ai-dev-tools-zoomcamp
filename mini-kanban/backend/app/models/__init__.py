from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, EmailStr


class UserRole(str, Enum):
    OWNER = "owner"
    PARTICIPANT = "participant"


class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    name: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('createdAt', mode='before')
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v


class Board(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    ownerId: UUID
    ownerName: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('createdAt', 'updatedAt', mode='before')
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v


class BoardSummary(BaseModel):
    board: Board
    participantCount: int = Field(..., ge=1)
    role: UserRole


class Participant(BaseModel):
    userId: UUID
    email: EmailStr
    name: str
    role: UserRole
    joinedAt: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('joinedAt', mode='before')
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v


class Column(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    boardId: UUID
    name: str
    order: int = Field(..., ge=0)
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('createdAt', mode='before')
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v


class Card(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    boardId: UUID
    columnId: UUID
    title: str
    description: Optional[str] = None
    creatorId: UUID
    creatorName: str
    assigneeId: Optional[UUID] = None
    assigneeName: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('createdAt', 'updatedAt', mode='before')
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v


class BoardWithDetails(BaseModel):
    id: UUID
    name: str
    ownerId: UUID
    ownerName: str
    createdAt: datetime
    updatedAt: datetime
    participants: List[Participant]
    columns: List[Column]
    cards: List[Card]
    role: UserRole


class Invitation(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    boardId: UUID
    boardName: str
    token: str
    used: bool = False
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    createdBy: UUID

    @field_validator('createdAt', mode='before')
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[UUID] = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=4)
    name: str
    invitationToken: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class BoardCreate(BaseModel):
    name: str


class ColumnCreate(BaseModel):
    name: str


class ColumnUpdate(BaseModel):
    name: Optional[str] = None
    order: Optional[int] = None


class CardCreate(BaseModel):
    title: str
    columnId: UUID
    description: Optional[str] = None
    assigneeId: Optional[UUID] = None


class CardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigneeId: Optional[UUID] = None


class CardMove(BaseModel):
    cardId: UUID
    targetColumnId: UUID


class ColumnReorder(BaseModel):
    columnIds: List[UUID]


class InvitationCreate(BaseModel):
    pass


class Error(BaseModel):
    message: str
    status: int