import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import HTTPException
from app.auth import (
    verify_password, get_password_hash, create_access_token, verify_token,
    get_current_user, get_current_active_user, authenticate_user,
    auth_create_user, logout_user, is_token_valid, get_current_user_for_test,
    users_db, user_tokens, SECRET_KEY, ALGORITHM
)
from app.models import User, TokenData


@pytest.fixture
def cleanup_auth_dbs():
    """Clean up auth databases before each test"""
    users_db.clear()
    user_tokens.clear()


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
    
    # Decode token to verify
    from jose import jwt
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == str(user_id)
    assert "exp" in decoded


def test_create_access_token_with_expiration():
    """Test creating access token with custom expiration"""
    user_id = uuid4()
    expires_delta = timedelta(minutes=60)
    token = create_access_token(data={"sub": str(user_id)}, expires_delta=expires_delta)
    
    # Decode token to verify expiration
    from jose import jwt
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["exp"] > datetime.utcnow().timestamp()


def test_verify_token_valid(cleanup_auth_dbs):
    """Test verifying a valid token"""
    # Create user and token
    user_id = uuid4()
    token = create_access_token(data={"sub": str(user_id)})
    
    # Store token in user_tokens for testing
    user_tokens[user_id] = token
    
    # Verify token
    token_data = verify_token(token)
    assert token_data.user_id == user_id


def test_verify_token_invalid(cleanup_auth_dbs):
    """Test verifying an invalid token"""
    invalid_token = "invalid.token.here"
    
    with pytest.raises(Exception):  # Should raise HTTPException
        verify_token(invalid_token)


def test_verify_token_expired(cleanup_auth_dbs):
    """Test verifying an expired token"""
    # Create token with past expiration
    user_id = uuid4()
    expired_time = datetime.utcnow() - timedelta(hours=1)
    from jose import jwt
    
    # Create token manually with past expiration
    payload = {"sub": str(user_id), "exp": expired_time}
    expired_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    with pytest.raises(Exception):  # Should raise HTTPException
        verify_token(expired_token)


def test_get_current_user(cleanup_auth_dbs):
    """Test getting current user from valid token"""
    # Create user
    password = "testpassword"
    hashed_password = get_password_hash(password)
    user = auth_create_user("test@example.com", "Test User", hashed_password)
    user_id = user.id
    
    # Create and store token
    token = create_access_token(data={"sub": str(user_id)})
    user_tokens[user_id] = token
    
    # Get current user (simulate the dependency)
    current_user = get_current_user_for_test(token)
    
    print(f"Debug: current_user = {current_user}")
    print(f"Debug: current_user.name = {current_user.name}")
    print(f"Debug: users_db[{user_id}] = {users_db.get(user_id)}")
    
    assert current_user.id == user_id
    assert current_user.email == "test@example.com"
    assert current_user.name == "Test User"


def test_get_current_user_not_found(cleanup_auth_dbs):
    """Test getting current user when user doesn't exist"""
    # Create token for non-existent user
    fake_user_id = uuid4()
    token = create_access_token(data={"sub": str(fake_user_id)})
    
    with pytest.raises(Exception):  # Should raise HTTPException
        token_data = verify_token(token)
        get_current_user(token_data)


def test_get_current_active_user(cleanup_auth_dbs):
    """Test getting current active user"""
    # Create user
    password = "testpassword"
    hashed_password = get_password_hash(password)
    user = auth_create_user("test@example.com", "Test User", hashed_password)
    
    # Create and store token
    token = create_access_token(data={"sub": str(user.id)})
    user_tokens[user.id] = token
    
    # Get current active user
    current_user = get_current_user_for_test(token)
    active_user = get_current_active_user(current_user)
    
    assert active_user.id == user.id
    assert active_user.email == "test@example.com"


def test_get_current_active_user_inactive(cleanup_auth_dbs):
    """Test getting current active user when user is inactive"""
    # Create user (in a real app, this would have some inactive flag)
    password = "testpassword"
    hashed_password = get_password_hash(password)
    user = auth_create_user("test@example.com", "Test User", hashed_password)
    
    # Get current user first (this should work since user is still in users_db)
    token = create_access_token(data={"sub": str(user.id)})
    user_tokens[user.id] = token
    current_user = get_current_user_for_test(token)
    
    # Now remove user from users_db to simulate inactive state
    del users_db[user.id]
    
    # Should raise HTTPException when trying to get active user
    with pytest.raises(HTTPException) as exc_info:
        get_current_active_user(current_user)
    
    assert exc_info.value.status_code == 400
    assert "Inactive user" in exc_info.value.detail


def test_authenticate_user_valid(cleanup_auth_dbs):
    """Test authenticating user with valid credentials"""
    # Create user
    password = "testpass"
    hashed_password = get_password_hash(password)
    user = auth_create_user("test@example.com", "Test User", hashed_password)
    
    # Authenticate user
    authenticated_user = authenticate_user("test@example.com", password)
    
    assert authenticated_user is not None
    assert authenticated_user.id == user.id
    assert authenticated_user.email == "test@example.com"
    assert authenticated_user.name == "Test User"


def test_authenticate_user_invalid_email(cleanup_auth_dbs):
    """Test authenticating user with invalid email"""
    # Create user
    password = "testpass"
    hashed_password = get_password_hash(password)
    auth_create_user("test@example.com", "Test User", hashed_password)
    
    # Authenticate with wrong email
    authenticated_user = authenticate_user("wrong@example.com", password)
    assert authenticated_user is None


def test_authenticate_user_invalid_password(cleanup_auth_dbs):
    """Test authenticating user with invalid password"""
    # Create user
    password = "testpass"
    wrong_password = "wrongpass"
    hashed_password = get_password_hash(password)
    auth_create_user("test@example.com", "Test User", hashed_password)
    
    # Authenticate with wrong password
    authenticated_user = authenticate_user("test@example.com", wrong_password)
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
    assert user.id in users_db
    assert users_db[user.id]["password"] == password_hash


def test_logout_user(cleanup_auth_dbs):
    """Test logging out user"""
    # Create user and store token
    password = "testpassword"
    hashed_password = get_password_hash(password)
    user = auth_create_user("test@example.com", "Test User", hashed_password)
    token = create_access_token(data={"sub": str(user.id)})
    user_tokens[user.id] = token
    
    # Verify token exists
    assert user.id in user_tokens
    
    # Logout user
    logout_user(user.id)
    
    # Verify token is removed
    assert user.id not in user_tokens


def test_logout_user_not_found(cleanup_auth_dbs):
    """Test logging out user that doesn't exist"""
    fake_user_id = uuid4()
    
    # Should not raise exception
    logout_user(fake_user_id)


def test_is_token_valid(cleanup_auth_dbs):
    """Test checking if token is valid"""
    # Create user and store token
    password = "testpassword"
    hashed_password = get_password_hash(password)
    user = auth_create_user("test@example.com", "Test User", hashed_password)
    token = create_access_token(data={"sub": str(user.id)})
    user_tokens[user.id] = token
    
    # Check token validity
    assert is_token_valid(user.id, token) is True
    
    # Check with wrong token
    assert is_token_valid(user.id, "wrong-token") is False
    
    # Check with wrong user ID
    fake_user_id = uuid4()
    assert is_token_valid(fake_user_id, token) is False


def test_is_token_valid_user_not_found(cleanup_auth_dbs):
    """Test checking token validity for non-existent user"""
    fake_user_id = uuid4()
    fake_token = "fake-token"
    
    assert is_token_valid(fake_user_id, fake_token) is False


def test_token_data_model():
    """Test TokenData model"""
    user_id = uuid4()
    token_data = TokenData(user_id=user_id)
    
    assert token_data.user_id == user_id


def test_token_data_model_none():
    """Test TokenData model with None user_id"""
    token_data = TokenData()
    
    assert token_data.user_id is None


def test_password_hash_consistency(cleanup_auth_dbs):
    """Test that same password always produces same hash"""
    password = "testpass"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    assert hash1 == hash2


def test_password_hash_different_passwords(cleanup_auth_dbs):
    """Test that different passwords produce different hashes"""
    password1 = "pass1"
    password2 = "pass2"
    
    hash1 = get_password_hash(password1)
    hash2 = get_password_hash(password2)
    
    assert hash1 != hash2


if __name__ == "__main__":
    pytest.main([__file__])