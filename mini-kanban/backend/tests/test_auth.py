import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import HTTPException
from app.auth import (
    verify_password, get_password_hash, create_access_token, verify_token,
    get_current_user, get_current_active_user, authenticate_user,
    auth_create_user, logout_user, is_token_valid, get_current_user_for_test,
    SECRET_KEY, ALGORITHM
)
from app.models import User, TokenData
from app.store import get_user_by_id


@pytest.fixture
def cleanup_auth_dbs():
    """Clean up auth databases before each test"""
    # Clear the test database by dropping and recreating tables
    from app.database import Base, engine
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    # Recreate all tables
    Base.metadata.create_all(bind=engine)


def test_password_hashing(cleanup_auth_dbs):
    """Test password hashing and verification"""
    password = "testpass"
    hashed_password = get_password_hash(password)
    
    # Check that hash is different from original password
    assert hashed_password != password
    
    # Check that hash contains SHA-256 prefix (64-character hex string)
    assert len(hashed_password) == 64
    assert all(c in '0123456789abcdef' for c in hashed_password)
    
    # Check that verification works
    assert verify_password(password, hashed_password) is True
    
    # Check that wrong password fails
    assert verify_password("wrongpass", hashed_password) is False


def test_create_access_token():
    """Test creating access token"""
    user_id = uuid4()
    token = create_access_token(data={"sub": str(user_id)})
    
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_access_token_with_expiration():
    """Test creating access token with custom expiration"""
    user_id = uuid4()
    expires_delta = timedelta(minutes=30)
    token = create_access_token(data={"sub": str(user_id)}, expires_delta=expires_delta)
    
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_token_valid():
    """Test verifying a valid token"""
    user_id = uuid4()
    token = create_access_token(data={"sub": str(user_id)})
    
    payload = verify_token(token)
    assert payload is not None
    assert payload.user_id == user_id


def test_verify_token_invalid():
    """Test verifying an invalid token"""
    invalid_token = "invalid.token.here"
    
    with pytest.raises(HTTPException):
        verify_token(invalid_token)


def test_verify_token_expired():
    """Test verifying an expired token"""
    # Create token with negative expiration to force it to expire
    user_id = uuid4()
    expires_delta = timedelta(minutes=-1)  # Already expired
    token = create_access_token(data={"sub": str(user_id)}, expires_delta=expires_delta)
    
    # Wait a moment to ensure expiration
    import time
    time.sleep(0.1)
    
    with pytest.raises(HTTPException):
        verify_token(token)


def test_get_current_user(cleanup_auth_dbs):
    """Test getting current user from valid token"""
    # Create user
    user = auth_create_user("test@example.com", "Test User", get_password_hash("password"))
    
    # Create token
    token = create_access_token(data={"sub": str(user.id)})
    
    # Get current user
    current_user = get_current_user_for_test(token)
    
    assert current_user is not None
    assert current_user.id == user.id
    assert current_user.email == user.email
    assert current_user.name == user.name


def test_get_current_user_not_found(cleanup_auth_dbs):
    """Test getting current user with invalid token"""
    invalid_token = "invalid.token.here"
    
    with pytest.raises(HTTPException):
        get_current_user_for_test(invalid_token)


def test_get_current_active_user(cleanup_auth_dbs):
    """Test getting current active user"""
    # Create user
    user = auth_create_user("test@example.com", "Test User", get_password_hash("password"))
    
    # Create token
    token = create_access_token(data={"sub": str(user.id)})
    
    # Get current active user
    current_user = get_current_active_user(get_current_user_for_test(token))
    
    assert current_user is not None
    assert current_user.id == user.id
    assert current_user.email == user.email
    assert current_user.name == user.name


def test_get_current_active_user_inactive(cleanup_auth_dbs):
    """Test getting current active user when user is inactive"""
    # Create user
    password = "testpassword"
    hashed_password = get_password_hash(password)
    user = auth_create_user("test@example.com", "Test User", hashed_password)
    
    # Get current user first (this should work since user is still in database)
    token = create_access_token(data={"sub": str(user.id)})
    current_user = get_current_user_for_test(token)
    
    # Remove user from database to simulate inactive state
    from app.database import get_session
    db = get_session()
    try:
        from app.models.database import User as DbUser
        db_user = db.query(DbUser).filter(DbUser.id == str(user.id)).first()
        if db_user:
            db.delete(db_user)
            db.commit()
    finally:
        db.close()
    
    # Try to get current active user (should fail)
    with pytest.raises(HTTPException):
        get_current_active_user(current_user)


def test_authenticate_user_valid(cleanup_auth_dbs):
    """Test authenticating user with valid credentials"""
    # Create user
    email = "test@example.com"
    name = "Test User"
    password = "testpassword"
    hashed_password = get_password_hash(password)
    user = auth_create_user(email, name, hashed_password)
    
    # Authenticate user
    authenticated_user = authenticate_user(email, password)
    
    assert authenticated_user is not None
    assert authenticated_user.id == user.id
    assert authenticated_user.email == email
    assert authenticated_user.name == name


def test_authenticate_user_invalid_email(cleanup_auth_dbs):
    """Test authenticating user with invalid email"""
    # Create user
    email = "test@example.com"
    name = "Test User"
    password = "testpassword"
    hashed_password = get_password_hash(password)
    auth_create_user(email, name, hashed_password)
    
    # Try to authenticate with wrong email
    authenticated_user = authenticate_user("wrong@example.com", password)
    
    assert authenticated_user is None


def test_authenticate_user_invalid_password(cleanup_auth_dbs):
    """Test authenticating user with invalid password"""
    # Create user
    email = "test@example.com"
    name = "Test User"
    password = "testpassword"
    hashed_password = get_password_hash(password)
    auth_create_user(email, name, hashed_password)
    
    # Try to authenticate with wrong password
    authenticated_user = authenticate_user(email, "wrongpassword")
    
    assert authenticated_user is None


def test_authenticate_user_nonexistent(cleanup_auth_dbs):
    """Test authenticating non-existent user"""
    # Try to authenticate user that doesn't exist
    authenticated_user = authenticate_user("nonexistent@example.com", "password")
    
    assert authenticated_user is None


def test_create_user(cleanup_auth_dbs):
    """Test creating user through auth module"""
    email = "test@example.com"
    name = "Test User"
    password_hash = "hashedpassword123"
    
    user = auth_create_user(email, name, password_hash)
    
    assert user.email == email
    assert user.name == name


def test_logout_user(cleanup_auth_dbs):
    """Test logging out user"""
    # Create user
    user = auth_create_user("test@example.com", "Test User", get_password_hash("password"))
    
    # Logout user
    result = logout_user(user.id)
    
    assert result is True


def test_logout_user_not_found(cleanup_auth_dbs):
    """Test logging out non-existent user"""
    fake_id = uuid4()
    result = logout_user(fake_id)
    
    assert result is False


def test_is_token_valid(cleanup_auth_dbs):
    """Test checking if token is valid"""
    # Create user
    user = auth_create_user("test@example.com", "Test User", get_password_hash("password"))
    
    # Create token
    token = create_access_token(data={"sub": str(user.id)})
    
    # Check if token is valid
    is_valid = is_token_valid(token)
    
    assert is_valid is True


def test_is_token_valid_user_not_found(cleanup_auth_dbs):
    """Test checking if token is valid when user is not found"""
    # Create user
    user = auth_create_user("test@example.com", "Test User", get_password_hash("password"))
    
    # Create token
    token = create_access_token(data={"sub": str(user.id)})
    
    # Remove user from database
    from app.database import get_session
    db = get_session()
    try:
        from app.models.database import User as DbUser
        db_user = db.query(DbUser).filter(DbUser.id == str(user.id)).first()
        if db_user:
            db.delete(db_user)
            db.commit()
    finally:
        db.close()
    
    # Check if token is valid (should be False since user doesn't exist)
    is_valid = is_token_valid(token)
    
    assert is_valid is False


def test_token_data_model():
    """Test TokenData model"""
    user_id = uuid4()
    token_data = TokenData(user_id=user_id)
    
    assert token_data.user_id == user_id


def test_token_data_model_none():
    """Test TokenData model with None values"""
    token_data = TokenData(user_id=None)
    
    assert token_data.user_id is None


def test_password_hash_consistency(cleanup_auth_dbs):
    """Test that password hashing is consistent"""
    password = "testpassword"
    
    # Hash the same password multiple times
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    hash3 = get_password_hash(password)
    
    # All hashes should be the same
    assert hash1 == hash2 == hash3


def test_password_hash_different_passwords(cleanup_dbs):
    """Test that different passwords produce different hashes"""
    password1 = "password1"
    password2 = "password2"
    
    hash1 = get_password_hash(password1)
    hash2 = get_password_hash(password2)
    
    # Hashes should be different
    assert hash1 != hash2