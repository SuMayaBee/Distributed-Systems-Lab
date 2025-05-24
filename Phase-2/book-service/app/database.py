import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL2 = os.getenv("BOOK_DATABASE_URL") or "postgresql://neondb_owner:pOhY1VrFUw8m@ep-black-scene-a1qxsve5-pooler.ap-southeast-1.aws.neon.tech/book-service?sslmode=prefer"

if not DATABASE_URL2:
    raise ValueError("No BOOK_DATABASE_URL found in environment variables")

engine = create_engine(DATABASE_URL2)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 