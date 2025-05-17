from pydantic import BaseModel
from typing import Optional, List
import datetime

class UserDetail(BaseModel):
    id: int
    name: str
    email: str

class BookDetail(BaseModel):
    id: int
    title: str
    author: str

class LoanBase(BaseModel):
    user_id: int
    book_id: int
    due_date: datetime.datetime

class LoanCreate(LoanBase):
    pass

class ReturnCreate(BaseModel):
    loan_id: int

class LoanExtend(BaseModel):
    extension_days: int

class Loan(LoanBase):
    id: int
    issue_date: datetime.datetime
    return_date: Optional[datetime.datetime] = None
    status: str
    extensions_count: int = 0

    class Config:
        from_attributes = True

# Open loan-service/app/schemas.py and update the LoanWithDetails class
class LoanWithDetails(BaseModel):
    id: int
    user: Optional[UserDetail] = None
    book: Optional[BookDetail] = None
    issue_date: datetime.datetime
    due_date: datetime.datetime
    return_date: Optional[datetime.datetime] = None
    status: str
    extensions_count: int = 0

    class Config:
        from_attributes = True

class LoanHistoryItem(BaseModel):
    id: int
    book: BookDetail
    issue_date: datetime.datetime
    due_date: datetime.datetime
    return_date: Optional[datetime.datetime] = None
    status: str

    class Config:
        from_attributes = True

class PaginatedLoans(BaseModel):
    loans: List[LoanHistoryItem]
    total: int