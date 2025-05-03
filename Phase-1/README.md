# 📘 Smart Library System – Monolithic Architecture (FastAPI)

This project implements the backend for a Smart Library System using a monolithic architecture with FastAPI and PostgreSQL (NeonDB).

## ✨ Features

*   **User Management:** Register and retrieve user information.
*   **Book Management:** Add, update, remove, search, and view books.
*   **Loan Management:** Issue books, return books, view loan history, list overdue loans, and extend due dates.
*   **Statistics:** View popular books, active users, and system overview.

## 🛠️ Setup

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd Phase-1 # Or your project directory name
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    ```
    *   On Windows:
        ```powershell
        .\venv\Scripts\Activate.ps1
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    *   Create a file named `.env` in the project root (`Phase-1/`).
    *   Add your NeonDB (or other PostgreSQL) connection string:
        ```
        DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
        ```
        *(Replace with your actual connection string)*

## ▶️ Running the Application

1.  **Navigate to the directory *containing* the project folder:**
    ```bash
    cd .. # If you are inside the Phase-1 directory
    ```

2.  **Run Uvicorn:**
    ```bash
    uvicorn Phase-1.main:app --reload
    ```
    *(Replace `Phase-1` if your project directory name is different)*

3.  The API will be available at `http://127.0.0.1:8000`.
4.  Access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

## 🚀 API Endpoints

Below are examples for testing the API endpoints. Replace IDs (like `1`, `55`, `101`) with actual IDs generated when you create resources.

--- 

### Root

*   **GET /**
    *   **Description:** Check if the API is running.
    *   **Request:** `GET http://127.0.0.1:8000/`
    *   **Response (200 OK):**
        ```json
        {
          "message": "Welcome to the Smart Library System API"
        }
        ```

--- 

### Users

*   **POST /api/users/**
    *   **Description:** Create/register a new user.
    *   **Request Body:**
        ```json
        {
          "name": "Fatima Khan",
          "email": "fatima.k@example.org",
          "role": "student"
        }
        ```
    *   **Response (201 Created):**
        ```json
        {
          "name": "Fatima Khan",
          "email": "fatima.k@example.org",
          "role": "student",
          "id": 2, // Example ID
          "created_at": "2023-10-27T11:00:00Z",
          "updated_at": null
        }
        ```

*   **GET /api/users/{user_id}**
    *   **Description:** Fetch user profile by ID.
    *   **Request:** `GET http://127.0.0.1:8000/api/users/2`
    *   **Response (200 OK):**
        ```json
        {
          "name": "Fatima Khan",
          "email": "fatima.k@example.org",
          "role": "student",
          "id": 2,
          "created_at": "2023-10-27T11:00:00Z",
          "updated_at": null
        }
        ```

--- 

### Books

*   **POST /api/books/**
    *   **Description:** Add a new book.
    *   **Request Body:**
        ```json
        {
          "title": "The Hitchhiker's Guide to the Galaxy",
          "author": "Douglas Adams",
          "isbn": "978-0345391803",
          "genre": "Science Fiction",
          "copies": 7
        }
        ```
    *   **Response (201 Created):**
        ```json
        {
          "title": "The Hitchhiker's Guide to the Galaxy",
          "author": "Douglas Adams",
          "isbn": "978-0345391803",
          "genre": "Science Fiction",
          "copies": 7,
          "id": 55, // Example ID
          "available_copies": 7,
          "created_at": "2023-10-27T11:05:00Z",
          "updated_at": "2023-10-27T11:05:00Z"
        }
        ```

*   **GET /api/books/**
    *   **Description:** Search for books (optional search, pagination).
    *   **Request:** `GET http://127.0.0.1:8000/api/books/?search=Galaxy`
    *   **Response (200 OK):**
        ```json
        [
          {
            "title": "The Hitchhiker's Guide to the Galaxy",
            "author": "Douglas Adams",
            // ... other fields
          }
          // ... other matching books
        ]
        ```

*   **GET /api/books/{book_id}**
    *   **Description:** Retrieve details for a specific book.
    *   **Request:** `GET http://127.0.0.1:8000/api/books/55`
    *   **Response (200 OK):**
        ```json
        {
          "title": "The Hitchhiker's Guide to the Galaxy",
          "author": "Douglas Adams",
          "isbn": "978-0345391803",
          "genre": "Science Fiction",
          "copies": 7,
          "id": 55,
          "available_copies": 7,
          "created_at": "2023-10-27T11:05:00Z",
          "updated_at": "2023-10-27T11:05:00Z"
        }
        ```

*   **PUT /api/books/{book_id}**
    *   **Description:** Update book information.
    *   **Request:** `PUT http://127.0.0.1:8000/api/books/55`
    *   **Request Body:**
        ```json
        {
          "available_copies": 6
        }
        ```
    *   **Response (200 OK):**
        ```json
        {
          "title": "The Hitchhiker's Guide to the Galaxy",
          "author": "Douglas Adams",
          "isbn": "978-0345391803",
          "genre": "Science Fiction",
          "copies": 7,
          "id": 55,
          "available_copies": 6, // Updated
          "created_at": "2023-10-27T11:05:00Z",
          "updated_at": "2023-10-27T11:10:00Z" // Updated timestamp
        }
        ```

*   **DELETE /api/books/{book_id}**
    *   **Description:** Remove a book (if no active loans).
    *   **Request:** `DELETE http://127.0.0.1:8000/api/books/56` *(Assuming 56 is another book ID)*
    *   **Response:** `204 No Content`

--- 

### Loans

*   **POST /api/loans**
    *   **Description:** Issue a book to a user.
    *   **Request Body:**
        ```json
        {
          "user_id": 2, // User ID from previous example
          "book_id": 55, // Book ID from previous example
          "due_date": "2024-01-10T23:59:00Z"
        }
        ```
    *   **Response (201 Created):**
        ```json
        {
          "user_id": 2,
          "book_id": 55,
          "due_date": "2024-01-10T23:59:00Z",
          "id": 101, // Example Loan ID
          "issue_date": "2023-10-27T11:15:00Z",
          "return_date": null,
          "status": "ACTIVE",
          "extensions_count": 0
        }
        ```

*   **POST /api/returns**
    *   **Description:** Return a borrowed book.
    *   **Request Body:**
        ```json
        {
          "loan_id": 101 // Loan ID from previous example
        }
        ```
    *   **Response (200 OK):**
        ```json
        {
          "user_id": 2,
          "book_id": 55,
          "due_date": "2024-01-10T23:59:00Z",
          "id": 101,
          "issue_date": "2023-10-27T11:15:00Z",
          "return_date": "2023-10-27T11:20:00Z", // Return timestamp
          "status": "RETURNED",
          "extensions_count": 0
        }
        ```

*   **GET /api/loans/overdue**
    *   **Description:** List all overdue loans.
    *   **Request:** `GET http://127.0.0.1:8000/api/loans/overdue`
    *   **Response (200 OK):** (Example assumes a loan with ID 102 was due yesterday)
        ```json
        [
          {
            "id": 102,
            "user": {"id": 1, "name": "Jane Doe", "email": "jane.doe@example.com"},
            "book": {"id": 42, "title": "Design Patterns", "author": "Erich Gamma et al."},
            "issue_date": "2023-10-10T10:00:00Z",
            "due_date": "2023-10-26T23:59:59Z",
            "days_overdue": 1 // Or more depending on current date
          }
        ]
        ```

*   **GET /api/loans/{user_id}**
    *   **Description:** View loan history for a specific user.
    *   **Request:** `GET http://127.0.0.1:8000/api/loans/2`
    *   **Response (200 OK):**
        ```json
        [
          {
            "id": 101,
            "book": {
              "id": 55,
              "title": "The Hitchhiker's Guide to the Galaxy",
              "author": "Douglas Adams"
            },
            "issue_date": "2023-10-27T11:15:00Z",
            "due_date": "2024-01-10T23:59:00Z",
            "return_date": "2023-10-27T11:20:00Z",
            "status": "RETURNED"
          }
          // ... other loans for this user
        ]
        ```

*   **PUT /api/loans/{loan_id}/extend**
    *   **Description:** Extend the due date for a loan.
    *   **Note:** Requires an *active* loan (e.g., create another loan like the first POST /api/loans example and use its ID).
    *   **Request:** `PUT http://127.0.0.1:8000/api/loans/103/extend` *(Assuming 103 is an active loan)*
    *   **Request Body:**
        ```json
        {
          "extension_days": 14
        }
        ```
    *   **Response (200 OK):**
        ```json
        {
          "id": 103,
          "user_id": 2,
          "book_id": 55,
          "issue_date": "2023-10-27T11:30:00Z",
          "original_due_date": "2024-01-10T23:59:00Z", // Example original
          "due_date": "2024-01-24T23:59:00Z", // New extended date
          "extended_due_date": "2024-01-24T23:59:00Z", // New extended date
          "return_date": null,
          "status": "ACTIVE",
          "extensions_count": 1
        }
        ```

--- 

### Statistics

*   **GET /api/stats/books/popular**
    *   **Description:** Get the most borrowed books.
    *   **Request:** `GET http://127.0.0.1:8000/api/stats/books/popular?limit=3`
    *   **Response (200 OK):**
        ```json
        [
          {
            "book_id": 55,
            "title": "The Hitchhiker's Guide to the Galaxy",
            "author": "Douglas Adams",
            "borrow_count": 2 // Example count
          },
          {
            "book_id": 42,
            "title": "Design Patterns",
            "author": "Erich Gamma et al.",
            "borrow_count": 1
          }
        ]
        ```

*   **GET /api/stats/users/active**
    *   **Description:** Get the most active users.
    *   **Request:** `GET http://127.0.0.1:8000/api/stats/users/active?limit=3`
    *   **Response (200 OK):**
        ```json
        [
          {
            "user_id": 2,
            "name": "Fatima Khan",
            "books_borrowed": 2, // Total loans
            "current_borrows": 1 // Currently active/overdue loans
          },
          {
            "user_id": 1,
            "name": "Jane Doe",
            "books_borrowed": 1,
            "current_borrows": 1
          }
        ]
        ```

*   **GET /api/stats/overview**
    *   **Description:** Get system overview statistics.
    *   **Request:** `GET http://127.0.0.1:8000/api/stats/overview`
    *   **Response (200 OK):**
        ```json
        {
          "total_books": 17, // Sum of copies
          "total_users": 2,
          "books_available": 14,
          "books_borrowed": 2, // Active + Overdue
          "overdue_loans": 1,
          "loans_today": 2,
          "returns_today": 1
        }
        ```


</rewritten_file> 