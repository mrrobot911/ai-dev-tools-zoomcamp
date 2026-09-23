import os
from typing import Generator
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

# Global variables
engine = None
SessionLocal = None
Base = declarative_base()
metadata = MetaData()

def reset_engine():
    """Reset the engine to use current environment variables"""
    global engine, SessionLocal
    engine = None
    SessionLocal = None

def get_engine():
    """Get or create database engine"""
    global engine
    if engine is None:
        # Get database URL from environment variable with default
        database_url = os.getenv("DATABASE_URL", "sqlite:///./mini_kanban.db")
        
        # For testing, use a file-based database to ensure persistence
        if database_url == "sqlite:///:memory:":
            database_url = "sqlite:///./test_kanban.db"
        
        # Create database engine
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
        )
    return engine

def get_session():
    """Get database session factory"""
    global SessionLocal
    if SessionLocal is None:
        engine = get_engine()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
    return SessionLocal()

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get database session with proper cleanup"""
    db = get_session()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)