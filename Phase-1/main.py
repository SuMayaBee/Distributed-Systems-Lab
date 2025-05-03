from fastapi import FastAPI
from .database import engine, Base
from .routers import users, books, loans, stats
from . import models # Ensure models are imported so Base knows about them


# Create database tables
# In a real application, you would use Alembic for migrations.
# This is okay for simple examples or development.
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully (if they didn't exist).")
except Exception as e:
    print(f"Error creating database tables: {e}")
    # Depending on the error, you might want to exit or handle differently

app = FastAPI(
    title="Smart Library System - Monolithic",
    description="API for managing users, books, and loans in a monolithic architecture.",
    version="1.0.0",
)

# Include routers
app.include_router(users.router)
app.include_router(books.router)
app.include_router(loans.router)
app.include_router(stats.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Smart Library System API"}

# Optional: Add basic exception handlers if needed
# from fastapi import Request, status
# from fastapi.responses import JSONResponse
#
# @app.exception_handler(Exception)
# async def generic_exception_handler(request: Request, exc: Exception):
#     # Log the exception here
#     print(f"Unhandled exception: {exc}")
#     return JSONResponse(
#         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         content={"detail": "An internal server error occurred"},
#     ) 





# uvicorn Phase-1.main:app --reload