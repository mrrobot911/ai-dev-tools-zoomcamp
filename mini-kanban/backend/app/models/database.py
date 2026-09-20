from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    owned_boards = relationship("Board", foreign_keys="Board.owner_id", back_populates="owner")
    created_cards = relationship("Card", foreign_keys="Card.creator_id", back_populates="creator")
    assigned_cards = relationship("Card", foreign_keys="Card.assignee_id", back_populates="assignee")
    board_participants = relationship("BoardParticipant", back_populates="user")
    created_invitations = relationship("Invitation", foreign_keys="Invitation.created_by", back_populates="creator")

class Board(Base):
    __tablename__ = "boards"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_boards")
    columns = relationship("BoardColumn", back_populates="board", cascade="all, delete-orphan")
    cards = relationship("Card", back_populates="board", cascade="all, delete-orphan")
    participants = relationship("BoardParticipant", back_populates="board", cascade="all, delete-orphan")
    invitations = relationship("Invitation", back_populates="board", cascade="all, delete-orphan")

class BoardColumn(Base):
    __tablename__ = "columns"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    board_id = Column(String, ForeignKey("boards.id"), nullable=False)
    name = Column(String, nullable=False)
    order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    board = relationship("Board", back_populates="columns")
    cards = relationship("Card", back_populates="column", cascade="all, delete-orphan")

class Card(Base):
    __tablename__ = "cards"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    board_id = Column(String, ForeignKey("boards.id"), nullable=False)
    column_id = Column(String, ForeignKey("columns.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    creator_id = Column(String, ForeignKey("users.id"), nullable=False)
    creator_name = Column(String, nullable=False)
    assignee_id = Column(String, ForeignKey("users.id"), nullable=True)
    assignee_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    board = relationship("Board", back_populates="cards")
    column = relationship("BoardColumn", back_populates="cards")
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_cards")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_cards")

class BoardParticipant(Base):
    __tablename__ = "board_participants"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    board_id = Column(String, ForeignKey("boards.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)  # "owner" or "participant"
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    board = relationship("Board", back_populates="participants")
    user = relationship("User", back_populates="board_participants")

class Invitation(Base):
    __tablename__ = "invitations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    board_id = Column(String, ForeignKey("boards.id"), nullable=False)
    board_name = Column(String, nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    board = relationship("Board", back_populates="invitations")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_invitations")