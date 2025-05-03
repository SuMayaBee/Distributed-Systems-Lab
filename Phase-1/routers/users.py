from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create/register a new user."""
    # crud.create_user handles email uniqueness check
    return crud.create_user(db=db, user=user)

@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Fetch user profile by ID."""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Potential future endpoints:
# @router.get("/", response_model=List[schemas.User])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = crud.get_users(db, skip=skip, limit=limit) # Requires crud.get_users
#     return users

# @router.put("/{user_id}", response_model=schemas.User)
# def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
#      db_user = crud.update_user(db=db, user_id=user_id, user_update=user) # Requires crud.update_user and schemas.UserUpdate
#      if db_user is None:
#          raise HTTPException(status_code=404, detail="User not found")
#      return db_user 