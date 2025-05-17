import os
import requests
from fastapi import HTTPException, status
from dotenv import load_dotenv

load_dotenv()

# Service URLs - in production would be configured via environment variables
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL") or "http://localhost:8001"
BOOK_SERVICE_URL = os.getenv("BOOK_SERVICE_URL") or "http://localhost:8002"

class ServiceError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class UserServiceClient:
    def get_user(self, user_id: int):
        """Get user details from User Service."""
        try:
            response = requests.get(f"{USER_SERVICE_URL}/api/users/{user_id}")
            
            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {user_id} not found"
                )
            
            if response.status_code != 200:
                raise ServiceError(
                    message=f"User Service error: {response.text}",
                    status_code=response.status_code
                )
            
            return response.json()
            
        except requests.RequestException as e:
            raise ServiceError(
                message=f"User Service unavailable: {str(e)}",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )

class BookServiceClient:
    def get_book(self, book_id: int):
        """Get book details from Book Service."""
        try:
            response = requests.get(f"{BOOK_SERVICE_URL}/api/books/{book_id}")
            
            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Book with ID {book_id} not found"
                )
            
            if response.status_code != 200:
                raise ServiceError(
                    message=f"Book Service error: {response.text}",
                    status_code=response.status_code
                )
            
            return response.json()
            
        except requests.RequestException as e:
            raise ServiceError(
                message=f"Book Service unavailable: {str(e)}",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    def update_availability(self, book_id: int, operation: str):
        """Update book availability in Book Service."""
        try:
            data = {
                "available_copies": 1,  # Doesn't matter for increment/decrement operations
                "operation": operation
            }
            
            response = requests.patch(
                f"{BOOK_SERVICE_URL}/api/books/{book_id}/availability",
                json=data
            )
            
            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Book with ID {book_id} not found"
                )
            
            if response.status_code == 400:
                # For example, when trying to borrow a book with no available copies
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response.json().get("detail", "Invalid operation on book")
                )
            
            if response.status_code != 200:
                raise ServiceError(
                    message=f"Book Service error: {response.text}",
                    status_code=response.status_code
                )
            
            return response.json()
            
        except requests.RequestException as e:
            raise ServiceError(
                message=f"Book Service unavailable: {str(e)}",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )