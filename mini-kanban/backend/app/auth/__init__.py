from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models import User, TokenData
from app.database_service import DatabaseService
from app.database import get_db

# Security configuration
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# In-memory user storage (for backward compatibility)
users_db = {}
user_tokens = {}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    import hashlib
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password


def get_password_hash(password: str) -> str:
    """Hash a password using SHA-256"""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """Verify a JWT token and return TokenData"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return TokenData(user_id=UUID(user_id))
    except JWTError:
        raise credentials_exception
    except ValueError:
        raise credentials_exception
    return token_data


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from JWT token"""
    # Extract token from "Bearer <token>" format
    token = credentials.credentials
    
    token_data = verify_token(token)
    user_id = token_data.user_id
    
    # Try to get user from database first
    from app.dependencies import get_db_session
    db = next(get_db_session())
    try:
        from app.database_service import DatabaseService
        service = DatabaseService(db)
        user = service.get_user_by_id(str(user_id))
        if user:
            return User(
                id=UUID(user.id),
                email=user.email,
                name=user.name,
                createdAt=user.created_at
            )
    finally:
        db.close()
    
    # Fall back to in-memory storage for backward compatibility
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_data = users_db[user_id]
    return User(**{k: v for k, v in user_data.items() if k != "password"})


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    # Check if user exists in database
    from app.dependencies import get_db_session
    db = next(get_db_session())
    try:
        from app.database_service import DatabaseService
        service = DatabaseService(db)
        user = service.get_user_by_id(str(current_user.id))
        if not user:
            raise HTTPException(status_code=400, detail="Inactive user")
    finally:
        db.close()
    return current_user


def authenticate_user(email: str, password: str) -> Optional[User]:
    # Try to get user from database first
    from app.dependencies import get_db_session
    db = next(get_db_session())
    try:
        from app.database_service import DatabaseService
        service = DatabaseService(db)
        db_user = service.get_user_by_email(email)
        if db_user and verify_password(password, db_user.password_hash):
            return User(
                id=UUID(db_user.id),
                email=db_user.email,
                name=db_user.name,
                createdAt=db_user.created_at
            )
    finally:
        db.close()
    
    # Fall back to in-memory storage for backward compatibility
    user = None
    for u in users_db.values():
        if u["email"] == email:
            user = u
            break
    
    if not user or not verify_password(password, user["password"]):
        return None
    return User(**{k: v for k, v in user.items() if k != "password"})


def create_user(email: str, password: str, name: str) -> User:
    user_id = uuid4()
    hashed_password = get_password_hash(password)
    
    # Create user in database
    from app.dependencies import get_db_session
    db = next(get_db_session())
    try:
        service = DatabaseService(db)
        user = service.create_user(email, name, hashed_password)
        return User(
            id=UUID(user.id),
            email=user.email,
            name=user.name,
            createdAt=user.created_at
        )
    finally:
        db.close()
    
    # Also store in memory for backward compatibility
    user = User(
        id=user_id,
        email=email,
        name=name,
        createdAt=datetime.utcnow()
    )
    
    users_db[user_id] = {
        **user.model_dump(),
        "password": hashed_password
    }
    
    return user


def auth_create_user(email: str, name: str, password_hash: str, user_id: Optional[UUID] = None) -> User:
    """Create a user through the auth module with pre-hashed password"""
    if user_id is None:
        user_id = uuid4()
    
    # Create user in database
    from app.dependencies import get_db_session
    db = next(get_db_session())
    try:
        service = DatabaseService(db)
        user = service.create_user(email, name, password_hash)
        return User(
            id=UUID(user.id),
            email=user.email,
            name=user.name,
            createdAt=user.created_at
        )
    finally:
        db.close()
    
    # Also store in memory for backward compatibility
    user = User(
        id=user_id,
        email=email,
        name=name,
        createdAt=datetime.utcnow()
    )
    users_db[user_id] = {
        **user.model_dump(),
        "password": password_hash
    }
    return user


def logout_user(user_id: UUID) -> None:
    if user_id in user_tokens:
        del user_tokens[user_id]


def is_token_valid(user_id: UUID, token: str) -> bool:
    return user_id in user_tokens and user_tokens[user_id] == token


# Auth middleware for routes that require authentication
def auth_middleware(current_user: User = Depends(get_current_active_user)):
    return current_user


# Test helper function
def get_current_user_for_test(token: str) -> User:
    """Test helper to simulate the get_current_user dependency"""
    from fastapi.security import HTTPAuthorizationCredentials
    
    # Create a mock HTTPAuthorizationCredentials object
    class MockHTTPAuthorizationCredentials:
        def __init__(self, credentials: str):
            self.credentials = credentials
    
    credentials = MockHTTPAuthorizationCredentials(token)
    return get_current_user(credentials)