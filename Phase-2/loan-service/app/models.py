from sqlalchemy import Column, Integer, String, DateTime, func
from .database import Base

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    book_id = Column(Integer, index=True)
    issue_date = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=False)
    return_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="ACTIVE")  # ACTIVE, RETURNED, OVERDUE
    extensions_count = Column(Integer, default=0) 