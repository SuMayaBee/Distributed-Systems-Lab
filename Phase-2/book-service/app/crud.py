from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from . import models, schemas

def get_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def get_book_by_isbn(db: Session, isbn: str):
    return db.query(models.Book).filter(models.Book.isbn == isbn).first()

def get_books(db: Session, search: str = None, skip: int = 0, limit: int = 10):
    query = db.query(models.Book)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.Book.title.ilike(search_term),
                models.Book.author.ilike(search_term),
                models.Book.isbn.ilike(search_term),
                models.Book.genre.ilike(search_term)
            )
        )
    
    total = query.count()
    books = query.offset(skip).limit(limit).all()
    
    return {
        "books": books,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "per_page": limit
    }

def create_book(db: Session, book: schemas.BookCreate):
    # Check if ISBN is already registered
    existing_book = get_book_by_isbn(db, isbn=book.isbn)
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ISBN already registered"
        )
    
    # Set available_copies to copies if not provided
    book_dict = book.dict()
    if book_dict.get("available_copies") is None:
        book_dict["available_copies"] = book_dict["copies"]
    
    db_book = models.Book(**book_dict)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def update_book(db: Session, book_id: int, book_update: schemas.BookUpdate):
    db_book = get_book(db, book_id=book_id)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Update only provided fields
    update_data = book_update.dict(exclude_unset=True)
    
    # Check ISBN uniqueness if changing ISBN
    if "isbn" in update_data and update_data["isbn"] != db_book.isbn:
        existing_book = get_book_by_isbn(db, isbn=update_data["isbn"])
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ISBN already registered"
            )
    
    # Ensure available_copies doesn't exceed copies
    if "copies" in update_data and update_data["copies"] < db_book.available_copies:
        if "available_copies" not in update_data:
            update_data["available_copies"] = update_data["copies"]
    
    for key, value in update_data.items():
        setattr(db_book, key, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book

def update_availability(db: Session, book_id: int, update: schemas.AvailabilityUpdate):
    db_book = get_book(db, book_id=book_id)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    if update.operation == "increment":
        # Check that we don't exceed the total copies
        if db_book.available_copies >= db_book.copies:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Available copies cannot exceed total copies"
            )
        db_book.available_copies += 1
    elif update.operation == "decrement":
        # Check that we have available copies
        if db_book.available_copies <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No available copies to borrow"
            )
        db_book.available_copies -= 1
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid operation. Use 'increment' or 'decrement'."
        )
    
    db.commit()
    db.refresh(db_book)
    return db_book

def delete_book(db: Session, book_id: int):
    db_book = get_book(db, book_id=book_id)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # In the microservices architecture, we don't directly check if the book has loans
    # as that's managed by a different service. The Loan service should ensure
    # it doesn't leave dangling references.
    
    db.delete(db_book)
    db.commit()
    return True 