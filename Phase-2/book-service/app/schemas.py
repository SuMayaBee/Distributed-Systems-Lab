from pydantic import BaseModel
from typing import Optional, List
import datetime

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    copies: int

class BookCreate(BookBase):
    genre: Optional[str] = None
    available_copies: Optional[int] = None  # If not provided, defaults to copies

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    genre: Optional[str] = None
    copies: Optional[int] = None
    available_copies: Optional[int] = None

class AvailabilityUpdate(BaseModel):
    available_copies: int
    operation: str  # "increment" or "decrement"

class Book(BookBase):
    id: int
    genre: Optional[str] = None
    available_copies: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class PaginatedBooks(BaseModel):
    books: List[Book]
    total: int
    page: int
    per_page: int 