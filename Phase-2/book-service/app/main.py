from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from . import crud, models, schemas
from .database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Library System - Book Service",
    description="Microservice for managing library books",
    version="1.0.0",
)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Book Service API"}

@app.post("/api/books/", response_model=schemas.Book, status_code=status.HTTP_201_CREATED)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    """Add a new book."""
    return crud.create_book(db=db, book=book)

@app.get("/api/books/", response_model=schemas.PaginatedBooks)
def read_books(
    search: Optional[str] = Query(None, description="Search for books by title, author, ISBN, or genre"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search for books by title, author, ISBN, or keyword, with pagination."""
    return crud.get_books(db, search=search, skip=skip, limit=limit)

@app.get("/api/books/{book_id}", response_model=schemas.Book)
def read_book(book_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed information about a specific book."""
    db_book = crud.get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@app.put("/api/books/{book_id}", response_model=schemas.Book)
def update_book(book_id: int, book: schemas.BookUpdate, db: Session = Depends(get_db)):
    """Update book information."""
    return crud.update_book(db=db, book_id=book_id, book_update=book)

@app.patch("/api/books/{book_id}/availability", response_model=schemas.Book)
def update_book_availability(book_id: int, update: schemas.AvailabilityUpdate, db: Session = Depends(get_db)):
    """Update a book's available copies (used internally by Loan Service during issue/return)."""
    return crud.update_availability(db=db, book_id=book_id, update=update)

@app.delete("/api/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Remove a book from the catalog."""
    crud.delete_book(db=db, book_id=book_id)
    return None 