from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas
from ..database import get_db

router = APIRouter(
    prefix="/api/stats",
    tags=["statistics"],
    responses={404: {"description": "Not found"}}, # Example, adjust if needed
)

@router.get("/books/popular", response_model=List[schemas.PopularBookStat])
def get_most_borrowed_books(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Get the most borrowed books."""
    return crud.get_popular_books(db=db, limit=limit)

@router.get("/users/active", response_model=List[schemas.ActiveUserStat])
def get_most_active_users(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Get the most active users (based on total loans)."""
    return crud.get_active_users(db=db, limit=limit)

@router.get("/overview", response_model=schemas.SystemOverviewStat)
def get_system_overview_stats(db: Session = Depends(get_db)):
    """Get system overview statistics."""
    return crud.get_system_overview(db=db) 