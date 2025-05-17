from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from . import models, schemas
from .service_clients import UserServiceClient, BookServiceClient, ServiceError
import datetime

user_client = UserServiceClient()
book_client = BookServiceClient()

def get_loan(db: Session, loan_id: int):
    return db.query(models.Loan).filter(models.Loan.id == loan_id).first()

def get_user_loans(db: Session, user_id: int, active_only: bool = False, skip: int = 0, limit: int = 100):
    """Get all loans for a specific user."""
    query = db.query(models.Loan).filter(models.Loan.user_id == user_id)
    
    if active_only:
        query = query.filter(models.Loan.status == "ACTIVE")
    
    total = query.count()
    loans = query.order_by(models.Loan.issue_date.desc()).offset(skip).limit(limit).all()
    
    # Enrich with book details - in a real system this would be optimized
    enriched_loans = []
    for loan in loans:
        try:
            book_details = book_client.get_book(loan.book_id)
            loan_dict = {
                "id": loan.id,
                "book": {
                    "id": book_details["id"],
                    "title": book_details["title"],
                    "author": book_details["author"]
                },
                "issue_date": loan.issue_date,
                "due_date": loan.due_date,
                "return_date": loan.return_date,
                "status": loan.status
            }
            enriched_loans.append(loan_dict)
        except (HTTPException, ServiceError):
            # If book service is down, still show basic loan info
            loan_dict = {
                "id": loan.id,
                "book": {
                    "id": loan.book_id,
                    "title": "Book details unavailable",
                    "author": "Author details unavailable"
                },
                "issue_date": loan.issue_date,
                "due_date": loan.due_date,
                "return_date": loan.return_date,
                "status": loan.status
            }
            enriched_loans.append(loan_dict)
    
    return {
        "loans": enriched_loans,
        "total": total
    }

def get_loan_with_details(db: Session, loan_id: int):
    """Get a specific loan with user and book details."""
    db_loan = get_loan(db, loan_id=loan_id)
    if not db_loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    # Get user and book details via respective services
    try:
        user_details = user_client.get_user(db_loan.user_id)
    except ServiceError as e:
        user_details = {"id": db_loan.user_id, "name": "User details unavailable", "email": ""}
    
    try:
        book_details = book_client.get_book(db_loan.book_id)
    except ServiceError as e:
        book_details = {"id": db_loan.book_id, "title": "Book details unavailable", "author": ""}
    
    # Construct response with enriched data
    result = {
        "id": db_loan.id,
        "user": {
            "id": user_details["id"],
            "name": user_details["name"],
            "email": user_details["email"]
        },
        "book": {
            "id": book_details["id"],
            "title": book_details["title"],
            "author": book_details["author"]
        },
        "issue_date": db_loan.issue_date,
        "due_date": db_loan.due_date,
        "return_date": db_loan.return_date,
        "status": db_loan.status
    }
    
    return result

def create_loan(db: Session, loan: schemas.LoanCreate):
    """Issue a book to a user."""
    # First verify user exists via User Service
    try:
        user_client.get_user(loan.user_id)
    except HTTPException as e:
        raise e  # Pass through the 404 if user not found
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"User service unavailable: {e.message}"
        )
    
    # Then check book exists and has available copies via Book Service
    try:
        book = book_client.get_book(loan.book_id)
        if book["available_copies"] <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book with ID {loan.book_id} has no available copies"
            )
    except HTTPException as e:
        raise e  # Pass through the 404 if book not found
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Book service unavailable: {e.message}"
        )
    
    # Create the loan record
    db_loan = models.Loan(
        user_id=loan.user_id,
        book_id=loan.book_id,
        due_date=loan.due_date,
        status="ACTIVE"
    )
    
    # Update book availability
    try:
        book_client.update_availability(loan.book_id, "decrement")
    except (HTTPException, ServiceError) as e:
        # Roll back by not committing the loan
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to update book availability: {str(e)}"
        )
    
    # Commit the loan
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    
    return db_loan

def return_book(db: Session, return_data: schemas.ReturnCreate):
    """Process a book return."""
    db_loan = get_loan(db, loan_id=return_data.loan_id)
    if not db_loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    if db_loan.status == "RETURNED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Book already returned"
        )
    
    # Update loan status
    db_loan.status = "RETURNED"
    db_loan.return_date = datetime.datetime.now(datetime.timezone.utc)
    
    # Update book availability
    try:
        book_client.update_availability(db_loan.book_id, "increment")
    except (HTTPException, ServiceError) as e:
        # Continue with the return process even if book service fails
        # This is a business decision - you might want to handle differently
        pass
    
    db.commit()
    db.refresh(db_loan)
    
    return db_loan 