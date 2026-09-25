import pytest
import os
import requests
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base


@pytest.fixture(scope="session")
def postgres_engine():
    """Create a PostgreSQL engine for integration tests"""
    # Use the DATABASE_URL from environment (will be set by docker-compose)
    database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/minikanban")
    engine = create_engine(database_url)
    return engine


@pytest.fixture(scope="session")
def setup_database(postgres_engine):
    """Set up the database with migrations"""
    # Run migrations
    import subprocess
    import sys
    sys.path.append('/app')
    
    # Reset engine to use the PostgreSQL database
    from app.database import reset_engine
    reset_engine()
    
    # Run alembic upgrade
    result = subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        cwd="/app",
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        pytest.fail(f"Migration failed: {result.stderr}")
    
    yield
    
    # Clean up - drop all tables
    Base.metadata.drop_all(bind=postgres_engine)


@pytest.fixture
def wait_for_backend():
    """Wait for the backend service to be healthy"""
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    max_retries = 30
    retry_delay = 5
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{backend_url}/health", timeout=5)
            if response.status_code == 200:
                return
        except requests.exceptions.RequestException:
            pass
        
        if i < max_retries - 1:
            time.sleep(retry_delay)
    
    pytest.fail(f"Backend service at {backend_url} did not become healthy after {max_retries} retries")


@pytest.fixture
def api_client(wait_for_backend):
    """Create an API client for integration tests"""
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    class TestClient:
        def __init__(self, base_url):
            self.base_url = base_url
        
        def post(self, endpoint, json=None, headers=None):
            url = f"{self.base_url}{endpoint}"
            return requests.post(url, json=json, headers=headers)
        
        def get(self, endpoint, headers=None):
            url = f"{self.base_url}{endpoint}"
            return requests.get(url, headers=headers)
        
        def put(self, endpoint, json=None, headers=None):
            url = f"{self.base_url}{endpoint}"
            return requests.put(url, json=json, headers=headers)
        
        def delete(self, endpoint, headers=None):
            url = f"{self.base_url}{endpoint}"
            return requests.delete(url, headers=headers)
    
    return TestClient(backend_url)