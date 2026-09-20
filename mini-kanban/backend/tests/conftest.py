import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
import tempfile

# Override database URL for tests
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Reset engine to use test database URL
from app.database import reset_engine
reset_engine()

# Create tables for test database
from app.database import create_tables
create_tables()

client = TestClient(app)

@pytest.fixture(autouse=True)
def db_session():
    """Database session for each test"""
    from app.database import get_session
    db = get_session()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def cleanup_dbs():
    """Clean up all databases before each test"""
    # Clear the test database
    from app.database import get_engine, Base, reset_engine
    reset_engine()
    engine = get_engine()
    # Drop all tables and recreate them
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)