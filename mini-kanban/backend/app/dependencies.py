from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_session

def get_db_session():
    db = get_session()
    try:
        yield db
    finally:
        db.close()