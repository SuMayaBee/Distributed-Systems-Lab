from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas
from .database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Library System - User Service",
    description="Microservice for managing library users",
    version="1.0.0",
)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the User Service API"}

@app.post("/api/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create/register a new user."""
    return crud.create_user(db=db, user=user)

@app.get("/api/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Fetch user profile by ID."""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/api/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    """Update user information."""
    return crud.update_user(db=db, user_id=user_id, user_update=user) 