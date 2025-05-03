from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/api", # Loans have mixed prefixes (/loans, /returns)
    tags=["loans"],
    responses={404: {"description": "Not found"}},
)

@router.post("/loans", response_model=schemas.Loan, status_code=status.HTTP_201_CREATED)
def issue_book_to_user(loan: schemas.LoanCreate, db: Session = Depends(get_db)):
    """Issue a book to a user."""
    # crud.create_loan handles checks for user/book existence, availability, and existing loans
    return crud.create_loan(db=db, loan=loan)

@router.post("/returns", response_model=schemas.Loan)
def return_borrowed_book(return_info: schemas.ReturnCreate, db: Session = Depends(get_db)):
    """Return a borrowed book."""
    # crud.return_book handles checks for loan existence and status
    return crud.return_book(db=db, return_info=return_info)

@router.get("/loans/overdue", response_model=List[schemas.OverdueLoanItem])
def list_overdue_loans(db: Session = Depends(get_db)):
    """List all overdue loans."""
    # crud.get_overdue_loans handles updating status and fetching details
    return crud.get_overdue_loans(db=db)

@router.get("/loans/{user_id}", response_model=List[schemas.LoanHistoryItem])
def view_user_loan_history(user_id: int, db: Session = Depends(get_db)):
    """View loan history for a user."""
    # crud.get_user_loans handles user existence check and returns loans with book details
    loans = crud.get_user_loans(db=db, user_id=user_id)
    # Convert to the specific response schema
    history_items = [
        schemas.LoanHistoryItem(
            id=loan.id,
            book=schemas.LoanBookDetail.from_orm(loan.book),
            issue_date=loan.issue_date,
            due_date=loan.due_date,
            return_date=loan.return_date,
            status=loan.status
        )
        for loan in loans
    ]
    return history_items

@router.put("/loans/{loan_id}/extend", response_model=schemas.LoanExtended)
def extend_loan_due_date(loan_id: int, extend_info: schemas.LoanExtend, db: Session = Depends(get_db)):
    """Extend the due date for a loan."""
    # crud.extend_loan handles checks and updates
    return crud.extend_loan(db=db, loan_id=loan_id, extend_info=extend_info) 