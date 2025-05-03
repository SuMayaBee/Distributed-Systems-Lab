from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/api/books",
    tags=["books"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Book, status_code=status.HTTP_201_CREATED)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    """Add a new book."""
    # crud.create_book checks for existing ISBN
    return crud.create_book(db=db, book=book)

@router.get("/", response_model=List[schemas.Book])
def read_books(
    search: Optional[str] = Query(None, description="Search for books by title, author, ISBN, or genre"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Search for books by title, author, ISBN, or keyword, with pagination."""
    books = crud.get_books(db, search=search, skip=skip, limit=limit)
    return books

@router.get("/{book_id}", response_model=schemas.Book)
def read_book(book_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed information about a specific book."""
    db_book = crud.get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.put("/{book_id}", response_model=schemas.Book)
def update_book(book_id: int, book: schemas.BookUpdate, db: Session = Depends(get_db)):
    """Update book information."""
    db_book = crud.update_book(db=db, book_id=book_id, book_update=book)
    if db_book is None:
        # crud.update_book raises 404 if not found, but check again just in case
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Remove a book from the catalog."""
    # crud.delete_book raises 404 if not found and 400 if active loans exist
    success = crud.delete_book(db=db, book_id=book_id)
    if not success:
         # This case might not be reachable if crud raises exceptions
         raise HTTPException(status_code=404, detail="Book not found or could not be deleted")
    return # Return None for 204 status code 