from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from . import crud, models, schemas
from .database import engine, get_db
from .service_clients import ServiceError

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Library System - Loan Service",
    description="Microservice for managing library loans",
    version="1.0.0",
)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Loan Service API"}

@app.post("/api/loans/", response_model=schemas.Loan, status_code=status.HTTP_201_CREATED)
def create_loan(loan: schemas.LoanCreate, db: Session = Depends(get_db)):
    """Issue a book to a user."""
    try:
        return crud.create_loan(db=db, loan=loan)
    except HTTPException as e:
        raise e
    except ServiceError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@app.post("/api/returns/", response_model=schemas.Loan)
def return_book(return_data: schemas.ReturnCreate, db: Session = Depends(get_db)):
    """Return a borrowed book."""
    try:
        return crud.return_book(db=db, return_data=return_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@app.get("/api/loans/user/{user_id}", response_model=schemas.PaginatedLoans)
def read_user_loans(
    user_id: int,
    active_only: bool = Query(False, description="If True, return only active loans"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get a user's loan history (active and returned books)."""
    return crud.get_user_loans(db, user_id=user_id, active_only=active_only, skip=skip, limit=limit)

@app.get("/api/loans/{loan_id}", response_model=schemas.LoanWithDetails)
def read_loan(loan_id: int, db: Session = Depends(get_db)):
    """Get details of a specific loan."""
    try:
        return crud.get_loan_with_details(db, loan_id=loan_id)
    except HTTPException as e:
        raise e
    except ServiceError as e:
        # If a dependent service is down, we can still return partial data
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )