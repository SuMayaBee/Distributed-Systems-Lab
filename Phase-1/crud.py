from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case, text, or_
from . import models, schemas
from fastapi import HTTPException, status
import datetime
from typing import List, Optional
from sqlalchemy.orm import joinedload

# --- User CRUD ---

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    # Check if user already exists
    db_user_check = get_user_by_email(db, email=user.email)
    if db_user_check:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    db_user = models.User(name=user.name, email=user.email, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Add update_user if needed (Consider adding a separate endpoint/schema for this)
# def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
#     db_user = get_user(db, user_id)
#     if not db_user:
#         return None
#     update_data = user_update.dict(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(db_user, key, value)
#     db_user.updated_at = datetime.datetime.now(datetime.timezone.utc)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

# --- Book CRUD ---

def get_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def get_books(db: Session, search: Optional[str] = None, skip: int = 0, limit: int = 100):
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
    return query.offset(skip).limit(limit).all()

def create_book(db: Session, book: schemas.BookCreate):
    # Check if ISBN already exists
    db_book_check = db.query(models.Book).filter(models.Book.isbn == book.isbn).first()
    if db_book_check:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ISBN already exists")

    available_copies = book.available_copies if book.available_copies is not None else book.copies
    if available_copies > book.copies:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Available copies cannot exceed total copies")
    if available_copies < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Available copies cannot be negative")

    db_book = models.Book(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        genre=book.genre,
        copies=book.copies,
        available_copies=available_copies
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def update_book(db: Session, book_id: int, book_update: schemas.BookUpdate):
    db_book = get_book(db, book_id)
    if not db_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    update_data = book_update.dict(exclude_unset=True)

    # Check ISBN uniqueness if it's being updated
    if 'isbn' in update_data and update_data['isbn'] != db_book.isbn:
        db_book_check = db.query(models.Book).filter(models.Book.isbn == update_data['isbn']).first()
        if db_book_check:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ISBN already exists")

    new_total_copies = update_data.get('copies', db_book.copies)
    new_available_copies = update_data.get('available_copies', db_book.available_copies)

    # Check if available copies is being set directly
    if 'available_copies' in update_data:
        if new_available_copies > new_total_copies:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Available copies cannot exceed total copies")
        if new_available_copies < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Available copies cannot be negative")
    # If only total copies is updated, adjust available_copies if necessary
    elif 'copies' in update_data and db_book.available_copies > new_total_copies:
         update_data['available_copies'] = new_total_copies # Adjust available if total is reduced below current available

    for key, value in update_data.items():
        setattr(db_book, key, value)

    db_book.updated_at = datetime.datetime.now(datetime.timezone.utc) # Manually update timestamp
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def delete_book(db: Session, book_id: int):
    db_book = get_book(db, book_id)
    if not db_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    # Check if book is currently loaned out
    active_loans = db.query(models.Loan).filter(
        models.Loan.book_id == book_id,
        models.Loan.status.in_(["ACTIVE", "OVERDUE"])
    ).count()
    if active_loans > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete book with active or overdue loans")

    db.delete(db_book)
    db.commit()
    return True

# --- Loan CRUD ---

def get_loan(db: Session, loan_id: int):
    return db.query(models.Loan).filter(models.Loan.id == loan_id).first()

def create_loan(db: Session, loan: schemas.LoanCreate):
    db_user = get_user(db, loan.user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db_book = get_book(db, loan.book_id)
    if not db_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    if db_book.available_copies <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book not available")

    # Check if user already has an active loan for this book
    existing_loan = db.query(models.Loan).filter(
        models.Loan.user_id == loan.user_id,
        models.Loan.book_id == loan.book_id,
        models.Loan.status.in_(["ACTIVE", "OVERDUE"])
    ).first()
    if existing_loan:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already has an active or overdue loan for this book")

    db_loan = models.Loan(
        user_id=loan.user_id,
        book_id=loan.book_id,
        due_date=loan.due_date,
        status="ACTIVE"
    )
    db_book.available_copies -= 1
    db.add(db_loan)
    # db.add(db_book) # Not strictly necessary if relationship is set up correctly, but explicit can be clearer
    db.commit()
    db.refresh(db_loan)
    # db.refresh(db_book) # Refresh book to get updated available_copies
    return db_loan

def return_book(db: Session, return_info: schemas.ReturnCreate):
    db_loan = get_loan(db, return_info.loan_id)
    if not db_loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")

    if db_loan.status == "RETURNED":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book already returned")

    db_book = get_book(db, db_loan.book_id)
    if not db_book:
        # This should ideally not happen if data integrity is maintained
        # Log an error here if possible
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Associated book not found. Data integrity issue.")

    db_loan.return_date = datetime.datetime.now(datetime.timezone.utc)
    db_loan.status = "RETURNED"
    db_book.available_copies += 1

    # Ensure available copies doesn't exceed total copies
    if db_book.available_copies > db_book.copies:
        # Log a warning here - this indicates a potential issue
        db_book.available_copies = db_book.copies

    db.add(db_loan)
    # db.add(db_book)
    db.commit()
    db.refresh(db_loan)
    # db.refresh(db_book)
    return db_loan

def get_user_loans(db: Session, user_id: int):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # Use joinedload to efficiently fetch related book details
    return db.query(models.Loan).options(joinedload(models.Loan.book)).filter(models.Loan.user_id == user_id).order_by(models.Loan.issue_date.desc()).all()

def get_overdue_loans(db: Session) -> List[schemas.OverdueLoanItem]:
    now = datetime.datetime.now(datetime.timezone.utc)

    # Update status of loans that became overdue
    db.query(models.Loan).filter(
        models.Loan.due_date < now,
        models.Loan.status == "ACTIVE"
    ).update({models.Loan.status: "OVERDUE"}, synchronize_session='fetch')
    db.commit() # Commit the status update

    # Fetch overdue loans with user and book details joined
    overdue_loans_query = db.query(models.Loan)\
        .join(models.User, models.Loan.user_id == models.User.id)\
        .join(models.Book, models.Loan.book_id == models.Book.id)\
        .options(joinedload(models.Loan.user), joinedload(models.Loan.book))\
        .filter(models.Loan.status == "OVERDUE")\
        .all()

    results = []
    for loan in overdue_loans_query:
        # Calculate days overdue safely
        days_overdue = 0
        if loan.due_date < now:
             due_date_aware = loan.due_date
             if due_date_aware.tzinfo is None:
                 pass
             time_difference = now - due_date_aware
             days_overdue = time_difference.days

        # Let Pydantic handle nested conversion via from_attributes=True
        try:
            item = schemas.OverdueLoanItem(
                id=loan.id,
                user=loan.user, # Pass ORM object directly
                book=loan.book, # Pass ORM object directly
                issue_date=loan.issue_date,
                due_date=loan.due_date,
                days_overdue=max(0, days_overdue)
            )
            results.append(item)
        except Exception as e:
            # Log the error for debugging which item failed
            print(f"Error processing overdue loan ID {loan.id}: {e}")
            # Optionally re-raise or handle differently
            # raise e

    return results

def extend_loan(db: Session, loan_id: int, extend_info: schemas.LoanExtend):
    db_loan = get_loan(db, loan_id)
    if not db_loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")

    if db_loan.status == "RETURNED":
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot extend a returned loan")

    # Optional: Add logic for max extensions
    # MAX_EXTENSIONS = 2
    # if db_loan.extensions_count >= MAX_EXTENSIONS:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Maximum {MAX_EXTENSIONS} extensions reached")

    original_due_date = db_loan.due_date
    # Ensure original_due_date is timezone-aware if performing timedelta operations with aware datetimes
    # if original_due_date.tzinfo is None:
        # original_due_date = original_due_date.replace(tzinfo=datetime.timezone.utc) # Or appropriate timezone

    new_due_date = original_due_date + datetime.timedelta(days=extend_info.extension_days)

    db_loan.due_date = new_due_date
    db_loan.extensions_count += 1
    # If it was overdue, extending might make it active again
    # Compare with timezone-aware 'now'
    if db_loan.status == "OVERDUE" and new_due_date >= datetime.datetime.now(datetime.timezone.utc):
        db_loan.status = "ACTIVE"

    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)

    # Prepare response schema
    response_data = schemas.LoanExtended(
        id=db_loan.id,
        user_id=db_loan.user_id,
        book_id=db_loan.book_id,
        issue_date=db_loan.issue_date,
        due_date=new_due_date, # Show the new due date here
        return_date=db_loan.return_date,
        status=db_loan.status,
        extensions_count=db_loan.extensions_count,
        original_due_date=original_due_date,
        extended_due_date=new_due_date
        # Note: book and user details are not included here per the example response
        # If needed, query them and add: book=schemas.Book.from_orm(db_loan.book), user=... etc.
    )
    return response_data

# --- Statistics CRUD ---

def get_popular_books(db: Session, limit: int = 10) -> List[schemas.PopularBookStat]:
    # Subquery to count loans per book
    loan_counts = db.query(
        models.Loan.book_id,
        func.count(models.Loan.id).label('borrow_count')
    ).group_by(models.Loan.book_id).subquery()

    # Join Book with loan counts
    results = db.query(
        models.Book.id.label('book_id'),
        models.Book.title,
        models.Book.author,
        loan_counts.c.borrow_count
    ).join(loan_counts, models.Book.id == loan_counts.c.book_id)\
     .order_by(loan_counts.c.borrow_count.desc())\
     .limit(limit)\
     .all()

    # Manually construct the Pydantic models from the result tuples
    return [
        schemas.PopularBookStat(
            book_id=r.book_id,
            title=r.title,
            author=r.author,
            borrow_count=r.borrow_count
        )
        for r in results
    ]

def get_active_users(db: Session, limit: int = 10) -> List[schemas.ActiveUserStat]:
    # Total loans per user (all time)
    total_loans_subquery = db.query(
        models.Loan.user_id,
        func.count(models.Loan.id).label('total_borrowed')
    ).group_by(models.Loan.user_id).subquery()

    # Current active/overdue loans per user
    current_loans_subquery = db.query(
        models.Loan.user_id,
        func.count(models.Loan.id).label('current_borrows')
    ).filter(models.Loan.status.in_(["ACTIVE", "OVERDUE"]))\
     .group_by(models.Loan.user_id).subquery()

    # Join User with loan counts
    results = db.query(
        models.User.id.label('user_id'),
        models.User.name,
        func.coalesce(total_loans_subquery.c.total_borrowed, 0).label('books_borrowed'),
        func.coalesce(current_loans_subquery.c.current_borrows, 0).label('current_borrows')
    ).outerjoin(total_loans_subquery, models.User.id == total_loans_subquery.c.user_id)\
     .outerjoin(current_loans_subquery, models.User.id == current_loans_subquery.c.user_id)\
     .order_by(func.coalesce(total_loans_subquery.c.total_borrowed, 0).desc(), models.User.id)\
     .limit(limit)\
     .all()

    # Manually construct the Pydantic models
    return [
        schemas.ActiveUserStat(
            user_id=r.user_id,
            name=r.name,
            books_borrowed=r.books_borrowed,
            current_borrows=r.current_borrows
        )
        for r in results
    ]

def get_system_overview(db: Session) -> schemas.SystemOverviewStat:
    # Atomically get counts where possible
    total_books_res = db.query(func.sum(models.Book.copies)).scalar()
    total_users_res = db.query(func.count(models.User.id)).scalar()
    books_available_res = db.query(func.sum(models.Book.available_copies)).scalar()

    total_books = total_books_res or 0
    total_users = total_users_res or 0
    books_available = books_available_res or 0

    # Count loans based on status
    active_or_overdue_count = db.query(models.Loan).filter(models.Loan.status.in_(["ACTIVE", "OVERDUE"])).count()

    # Update status before counting overdue separately for accuracy
    now = datetime.datetime.now(datetime.timezone.utc)
    db.query(models.Loan).filter(
        models.Loan.due_date < now,
        models.Loan.status == "ACTIVE"
    ).update({models.Loan.status: "OVERDUE"}, synchronize_session='fetch')
    db.commit()
    # Count overdue after update
    overdue_count = db.query(models.Loan).filter(models.Loan.status == "OVERDUE").count()


    today_start = datetime.datetime.now(datetime.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + datetime.timedelta(days=1)

    loans_today = db.query(models.Loan).filter(
        models.Loan.issue_date >= today_start,
        models.Loan.issue_date < today_end
    ).count()

    returns_today = db.query(models.Loan).filter(
        models.Loan.return_date >= today_start,
        models.Loan.return_date < today_end,
        models.Loan.status == "RETURNED"
    ).count()

    return schemas.SystemOverviewStat(
        total_books=total_books,
        total_users=total_users,
        books_available=books_available,
        books_borrowed=active_or_overdue_count, # Total currently borrowed
        overdue_loans=overdue_count,
        loans_today=loans_today,
        returns_today=returns_today
    )
 