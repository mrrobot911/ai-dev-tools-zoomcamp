from datetime import timedelta
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.models import User, UserCreate, UserLogin, Token, TokenData
from app.auth import (
    authenticate_user, create_access_token, get_password_hash,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.store import create_user as store_create_user, get_user_by_email

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=Dict[str, Any], status_code=201)
async def register(user_data: UserCreate):
    """Register a new user"""
    # Check if user already exists
    if get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    # Create user
    user = store_create_user(
        email=user_data.email,
        name=user_data.name,
        password_hash=get_password_hash(user_data.password)
    )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "user": user,
        "token": access_token
    }


@router.post("/login", response_model=Dict[str, Any])
async def login(user_data: UserLogin):
    """User login"""
    user = authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "user": user,
        "token": access_token
    }


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """User logout"""
    from app.auth import logout_user
    logout_user(current_user.id)
    return {"message": "Logout successful"}


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user