# 🧩 Smart Library System – Microservices Architecture

This project implements a Smart Library System using a microservices architecture. The application is divided into three independent services, each responsible for a specific domain: User, Book, and Loan. Every service has its own database and communicates with others via HTTP APIs.

## 🏗️ Architecture Overview

### User Service
- Manages user profiles and authentication
- Port: 8001
- Endpoints: `/api/users/`
- Database: `user-service`

### Book Service
- Manages book inventory and availability
- Port: 8002
- Endpoints: `/api/books/`
- Database: `book-service`

### Loan Service
- Handles book borrowing and returns
- Port: 8003
- Endpoints: `/api/loans/` and `/api/returns/`
- Database: `loan-service`
- Communicates with both User and Book services

## 🚀 Local Setup

### Prerequisites
- Python 3.9+
- PostgreSQL (or use the provided NeonDB connections)
- [Optional] Postman for testing

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### Step 2: Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac
source venv/bin/activate
# On Windows
# venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in each service directory:

**user-service/.env**
```
USER_DATABASE_URL=postgresql://neondb_owner:pOhY1VrFUw8m@ep-black-scene-a1qxsve5-pooler.ap-southeast-1.aws.neon.tech/user-service?sslmode=prefer
```

**book-service/.env**
```
BOOK_DATABASE_URL=postgresql://neondb_owner:pOhY1VrFUw8m@ep-black-scene-a1qxsve5-pooler.ap-southeast-1.aws.neon.tech/book-service?sslmode=prefer
```

**loan-service/.env**
```
LOAN_DATABASE_URL=postgresql://neondb_owner:pOhY1VrFUw8m@ep-black-scene-a1qxsve5-pooler.ap-southeast-1.aws.neon.tech/loan-service?sslmode=prefer
USER_SERVICE_URL=http://localhost:8001
BOOK_SERVICE_URL=http://localhost:8002
```

### Step 5: Start the Services

Run each service in a separate terminal:

**Terminal 1 - User Service**
```bash
cd user-service
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 - Book Service**
```bash
cd book-service
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

**Terminal 3 - Loan Service**
```bash
cd loan-service
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

### Step 6: Access the Services
- User Service: http://localhost:8001/docs
- Book Service: http://localhost:8002/docs
- Loan Service: http://localhost:8003/docs

## 📝 API Examples

Here are examples of how to interact with the services:

### User Service

#### Create a User
**Request**
```http
POST http://localhost:8001/api/users/
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "role": "student"
}
```

**Response**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "role": "student",
  "created_at": "2023-05-16T10:15:30.123Z",
  "updated_at": null
}
```

#### Create Another User
**Request**
```http
POST http://localhost:8001/api/users/
Content-Type: application/json

{
  "name": "Jane Smith",
  "email": "jane.smith@example.com",
  "role": "faculty"
}
```

**Response**
```json
{
  "id": 2,
  "name": "Jane Smith",
  "email": "jane.smith@example.com",
  "role": "faculty",
  "created_at": "2023-05-16T10:16:45.789Z",
  "updated_at": null
}
```

#### Get a User
**Request**
```http
GET http://localhost:8001/api/users/1
```

**Response**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "role": "student",
  "created_at": "2023-05-16T10:15:30.123Z",
  "updated_at": null
}
```

### Book Service

#### Create Books
**Request**
```http
POST http://localhost:8002/api/books/
Content-Type: application/json

{
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "isbn": "9780132350884",
  "genre": "Programming",
  "copies": 3
}
```

**Response**
```json
{
  "id": 1,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "isbn": "9780132350884",
  "genre": "Programming",
  "copies": 3,
  "available_copies": 3,
  "created_at": "2023-05-16T10:20:15.456Z",
  "updated_at": "2023-05-16T10:20:15.456Z"
}
```

**Request**
```http
POST http://localhost:8002/api/books/
Content-Type: application/json

{
  "title": "Design Patterns",
  "author": "Erich Gamma et al.",
  "isbn": "9780201633610",
  "genre": "Programming",
  "copies": 2
}
```

**Response**
```json
{
  "id": 2,
  "title": "Design Patterns",
  "author": "Erich Gamma et al.",
  "isbn": "9780201633610",
  "genre": "Programming",
  "copies": 2,
  "available_copies": 2,
  "created_at": "2023-05-16T10:22:30.789Z",
  "updated_at": "2023-05-16T10:22:30.789Z"
}
```

**Request**
```http
POST http://localhost:8002/api/books/
Content-Type: application/json

{
  "title": "The Pragmatic Programmer",
  "author": "Andrew Hunt, David Thomas",
  "isbn": "9780201616224",
  "genre": "Programming",
  "copies": 4
}
```

**Response**
```json
{
  "id": 3,
  "title": "The Pragmatic Programmer",
  "author": "Andrew Hunt, David Thomas",
  "isbn": "9780201616224",
  "genre": "Programming",
  "copies": 4,
  "available_copies": 4,
  "created_at": "2023-05-16T10:25:45.123Z",
  "updated_at": "2023-05-16T10:25:45.123Z"
}
```

#### Search Books
**Request**
```http
GET http://localhost:8002/api/books/?search=programmer
```

**Response**
```json
{
  "books": [
    {
      "id": 3,
      "title": "The Pragmatic Programmer",
      "author": "Andrew Hunt, David Thomas",
      "isbn": "9780201616224",
      "genre": "Programming",
      "copies": 4,
      "available_copies": 4,
      "created_at": "2023-05-16T10:25:45.123Z",
      "updated_at": "2023-05-16T10:25:45.123Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10
}
```

### Loan Service

#### Create a Loan (Issue a Book)
**Request**
```http
POST http://localhost:8003/api/loans/
Content-Type: application/json

{
  "user_id": 1,
  "book_id": 1,
  "due_date": "2023-06-15T23:59:59Z"
}
```

**Response**
```json
{
  "id": 1,
  "user_id": 1,
  "book_id": 1,
  "issue_date": "2023-05-16T10:30:00.123Z",
  "due_date": "2023-06-15T23:59:59Z",
  "return_date": null,
  "status": "ACTIVE",
  "extensions_count": 0
}
```

#### Create Another Loan
**Request**
```http
POST http://localhost:8003/api/loans/
Content-Type: application/json

{
  "user_id": 2,
  "book_id": 3,
  "due_date": "2023-06-20T23:59:59Z"
}
```

**Response**
```json
{
  "id": 2,
  "user_id": 2,
  "book_id": 3,
  "issue_date": "2023-05-16T10:35:15.456Z",
  "due_date": "2023-06-20T23:59:59Z",
  "return_date": null,
  "status": "ACTIVE",
  "extensions_count": 0
}
```

#### Get User's Loans
**Request**
```http
GET http://localhost:8003/api/loans/user/1
```

**Response**
```json
{
  "loans": [
    {
      "id": 1,
      "book": {
        "id": 1,
        "title": "Clean Code",
        "author": "Robert C. Martin"
      },
      "issue_date": "2023-05-16T10:30:00.123Z",
      "due_date": "2023-06-15T23:59:59Z",
      "return_date": null,
      "status": "ACTIVE"
    }
  ],
  "total": 1
}
```

#### Get Loan Details
**Request**
```http
GET http://localhost:8003/api/loans/1
```

**Response**
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com"
  },
  "book": {
    "id": 1,
    "title": "Clean Code",
    "author": "Robert C. Martin"
  },
  "issue_date": "2023-05-16T10:30:00.123Z",
  "due_date": "2023-06-15T23:59:59Z",
  "return_date": null,
  "status": "ACTIVE"
}
```

#### Return a Book
**Request**
```http
POST http://localhost:8003/api/returns/
Content-Type: application/json

{
  "loan_id": 1
}
```

**Response**
```json
{
  "id": 1,
  "user_id": 1,
  "book_id": 1,
  "issue_date": "2023-05-16T10:30:00.123Z",
  "due_date": "2023-06-15T23:59:59Z",
  "return_date": "2023-05-16T11:00:30.789Z",
  "status": "RETURNED",
  "extensions_count": 0
}
```

## 🧪 Testing Workflow

Here's a recommended sequence for testing the system:

1. **Create Users**
   - Create at least two different users

2. **Create Books**
   - Add multiple books with different titles, authors, and copy counts

3. **Issue Books**
   - Create loans for different user-book combinations
   - Verify that book availability decreases

4. **View Loans**
   - Check user loan history
   - Verify loan details with user and book information

5. **Return Books**
   - Process book returns
   - Verify book availability increases
   - Check loan status changes to "RETURNED"

## 🚨 Troubleshooting

### Database Connection Issues
- If you encounter SSL errors connecting to NeonDB, try changing `sslmode=require` to `sslmode=prefer` in the connection strings
- Ensure your NeonDB instance is active and not in sleep mode

### Service Communication Errors
- Verify that all three services are running
- Check the URL settings in loan-service/.env
- Ensure network connectivity between services

### Port Conflicts
If you encounter port conflicts, you can change the ports:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8011 --reload  # User Service on alt port
```
Then update the corresponding service URL in loan-service/.env.

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Microservices Architecture Patterns](https://microservices.io/patterns/microservices.html) 