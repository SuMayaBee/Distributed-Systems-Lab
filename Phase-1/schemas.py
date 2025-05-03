from pydantic import BaseModel, EmailStr
from typing import List, Optional
import datetime

# Base schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    genre: Optional[str] = None
    copies: int

class LoanBase(BaseModel):
    user_id: int
    book_id: int
    due_date: datetime.datetime

# Schemas for creating resources (inheriting from Base)
class UserCreate(UserBase):
    pass

class BookCreate(BookBase):
    available_copies: Optional[int] = None # If not provided, defaults to copies

class LoanCreate(LoanBase):
    pass

class ReturnCreate(BaseModel):
    loan_id: int

class LoanExtend(BaseModel):
    extension_days: int

# Schemas for reading resources (including ID and timestamps)
class Book(BookBase):
    id: int
    available_copies: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    # loans: List['Loan'] = [] # Avoid circular dependency for now, handle in specific responses

    class Config:
        from_attributes = True

class LoanBookDetail(BaseModel):
    id: int
    title: str
    author: str

    class Config:
        from_attributes = True

class LoanUserDetail(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True

class Loan(LoanBase):
    id: int
    issue_date: datetime.datetime
    return_date: Optional[datetime.datetime] = None
    status: str
    extensions_count: int
    book: Optional[Book] = None # Include full book details if needed
    user: Optional[User] = None # Include full user details if needed

    class Config:
        from_attributes = True

class LoanHistoryItem(BaseModel):
    id: int
    book: LoanBookDetail
    issue_date: datetime.datetime
    due_date: datetime.datetime
    return_date: Optional[datetime.datetime] = None
    status: str

    class Config:
        from_attributes = True

class OverdueLoanItem(BaseModel):
    id: int
    user: LoanUserDetail
    book: LoanBookDetail
    issue_date: datetime.datetime
    due_date: datetime.datetime
    days_overdue: int

    class Config:
        from_attributes = True

class LoanExtended(Loan):
    original_due_date: datetime.datetime
    extended_due_date: datetime.datetime

# Schemas for Statistics
class PopularBookStat(BaseModel):
    book_id: int
    title: str
    author: str
    borrow_count: int

class ActiveUserStat(BaseModel):
    user_id: int
    name: str
    books_borrowed: int       # Total books ever borrowed by the user
    current_borrows: int      # Number of books currently borrowed by the user

class SystemOverviewStat(BaseModel):
    total_books: int
    total_users: int
    books_available: int
    books_borrowed: int
    overdue_loans: int
    loans_today: int
    returns_today: int

# Schema for updating book details (only specific fields)
class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    genre: Optional[str] = None
    copies: Optional[int] = None
    available_copies: Optional[int] = None 