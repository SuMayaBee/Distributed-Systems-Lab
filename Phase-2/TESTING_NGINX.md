# 🧪 Testing Nginx Reverse Proxy - Smart Library System

This guide provides comprehensive testing procedures for the Nginx reverse proxy implementation in the Smart Library System microservices architecture.

## 📋 Testing Overview

The Nginx reverse proxy acts as a single entry point that routes requests to three backend microservices:
- **User Service** (port 8001) → `/api/users`
- **Book Service** (port 8002) → `/api/books`  
- **Loan Service** (port 8003) → `/api/loans`

## 🚀 Quick Start Testing

### 1. Start the System
```bash
# Option 1: Using the setup script
./setup-nginx.sh

# Option 2: Manual Docker Compose
docker-compose up --build -d

# Option 3: Local development (requires Nginx installation)
# Start services in separate terminals:
cd user-service && uvicorn app.main:app --host 0.0.0.0 --port 8001
cd book-service && uvicorn app.main:app --host 0.0.0.0 --port 8002
cd loan-service && uvicorn app.main:app --host 0.0.0.0 --port 8003
```

### 2. Basic Health Check
```bash
curl http://localhost/health
# Expected: "healthy"
```

## 🔍 Detailed Test Cases

### Test 1: System Health and Landing Page

#### 1.1 Health Check Endpoint
```bash
curl -v http://localhost/health
```
**Expected Response:**
- Status: `200 OK`
- Body: `healthy`
- Content-Type: `text/plain`

#### 1.2 Landing Page
```bash
curl http://localhost/
```
**Expected Response:**
- Status: `200 OK`
- Content-Type: `text/html`
- Body: HTML page with service overview

**Browser Test:**
Open `http://localhost/` in browser - should show a styled landing page with service links.

### Test 2: User Service Routing

#### 2.1 Get All Users
```bash
curl -X GET http://localhost/api/users
```
**Expected Response:**
- Status: `200 OK`
- Content-Type: `application/json`
- Body: `[]` (empty array initially)

#### 2.2 Create a User
```bash
curl -X POST http://localhost/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com"
  }'
```
**Expected Response:**
- Status: `200 OK`
- Body: User object with generated ID

#### 2.3 Get Specific User
```bash
# Replace {user_id} with actual ID from previous response
curl -X GET http://localhost/api/users/1
```

#### 2.4 Update User
```bash
curl -X PUT http://localhost/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Smith",
    "email": "john.smith@example.com"
  }'
```

### Test 3: Book Service Routing

#### 3.1 Get All Books
```bash
curl -X GET http://localhost/api/books
```

#### 3.2 Create a Book
```bash
curl -X POST http://localhost/api/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "isbn": "978-0-7432-7356-5",
    "available_copies": 3
  }'
```

#### 3.3 Get Specific Book
```bash
curl -X GET http://localhost/api/books/1
```

#### 3.4 Update Book Availability
```bash
curl -X PATCH http://localhost/api/books/1/availability \
  -H "Content-Type: application/json" \
  -d '{
    "available_copies": 2
  }'
```

### Test 4: Loan Service Routing

#### 4.1 Get All Loans
```bash
curl -X GET http://localhost/api/loans
```

#### 4.2 Create a Loan (Borrow Book)
```bash
# Ensure you have created a user (ID: 1) and book (ID: 1) first
curl -X POST http://localhost/api/loans \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "book_id": 1
  }'
```

#### 4.3 Return a Book
```bash
curl -X PUT http://localhost/api/loans/1/return
```

### Test 5: Error Handling

#### 5.1 Test 404 - Invalid Endpoint
```bash
curl -v http://localhost/api/invalid
```
**Expected Response:**
- Status: `404 Not Found`
- Content-Type: `application/json`
- Body: `{"error": "Not Found", "message": "The requested resource was not found"}`

#### 5.2 Test 404 - Invalid Service Path
```bash
curl -v http://localhost/invalid-path
```

#### 5.3 Test Backend Service Down (502 Error)
```bash
# Stop one service to test error handling
docker-compose stop user-service

# Try to access user service
curl -v http://localhost/api/users
```
**Expected Response:**
- Status: `502 Bad Gateway` or `500 Internal Server Error`

```bash
# Restart the service
docker-compose start user-service
```

### Test 6: CORS Headers

#### 6.1 Test CORS Preflight Request
```bash
curl -X OPTIONS http://localhost/api/users \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v
```
**Expected Response:**
- Status: `204 No Content`
- Headers should include:
  - `Access-Control-Allow-Origin: *`
  - `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
  - `Access-Control-Allow-Headers: ...`

#### 6.2 Test CORS on Actual Request
```bash
curl -X GET http://localhost/api/users \
  -H "Origin: http://localhost:3000" \
  -v
```
**Expected:** Response should include CORS headers.

### Test 7: Proxy Headers

#### 7.1 Verify Headers are Forwarded
Create a test endpoint in one of your services to echo headers, or check service logs to verify these headers are being received:
- `Host`
- `X-Real-IP`
- `X-Forwarded-For`
- `X-Forwarded-Proto`

## 🔄 Complete End-to-End Test Flow

### Scenario: Complete Library Workflow
```bash
# 1. Create a user
USER_RESPONSE=$(curl -s -X POST http://localhost/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice Johnson", "email": "alice@example.com"}')
echo "Created user: $USER_RESPONSE"

# 2. Create a book
BOOK_RESPONSE=$(curl -s -X POST http://localhost/api/books \
  -H "Content-Type: application/json" \
  -d '{"title": "1984", "author": "George Orwell", "isbn": "978-0-452-28423-4", "available_copies": 5}')
echo "Created book: $BOOK_RESPONSE"

# 3. Borrow the book
LOAN_RESPONSE=$(curl -s -X POST http://localhost/api/loans \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "book_id": 1}')
echo "Created loan: $LOAN_RESPONSE"

# 4. Check book availability (should be reduced)
curl -s http://localhost/api/books/1

# 5. Return the book
curl -s -X PUT http://localhost/api/loans/1/return

# 6. Check book availability again (should be restored)
curl -s http://localhost/api/books/1
```

## 📊 Performance Testing

### Test 8: Load Testing with Apache Bench

#### 8.1 Install Apache Bench
```bash
# Ubuntu/Debian
sudo apt install apache2-utils

# macOS
brew install httpie
```

#### 8.2 Basic Load Test
```bash
# Test 100 requests with 10 concurrent connections
ab -n 100 -c 10 http://localhost/health

# Test API endpoints
ab -n 50 -c 5 http://localhost/api/users
```

#### 8.3 POST Request Load Test
```bash
# Create a test data file
echo '{"name": "Test User", "email": "test@example.com"}' > user_data.json

# Load test POST requests
ab -n 50 -c 5 -p user_data.json -T application/json http://localhost/api/users
```

## 🔍 Monitoring and Debugging

### Test 9: Log Analysis

#### 9.1 View Nginx Access Logs
```bash
# Docker
docker-compose logs nginx | grep -E "(GET|POST|PUT|DELETE)"

# Local
sudo tail -f /var/log/nginx/access.log
```

#### 9.2 View Nginx Error Logs
```bash
# Docker
docker-compose logs nginx | grep -i error

# Local
sudo tail -f /var/log/nginx/error.log
```

#### 9.3 View Service Logs
```bash
docker-compose logs user-service
docker-compose logs book-service
docker-compose logs loan-service
```

### Test 10: Configuration Validation

#### 10.1 Test Nginx Configuration
```bash
# Docker
docker-compose exec nginx nginx -t

# Local
sudo nginx -t
```

#### 10.2 Reload Configuration
```bash
# Docker
docker-compose exec nginx nginx -s reload

# Local
sudo nginx -s reload
```

## 🛠️ Troubleshooting Common Issues

### Issue 1: 502 Bad Gateway
**Symptoms:** `502 Bad Gateway` error when accessing services
**Causes:**
- Backend service is down
- Wrong upstream configuration
- Network connectivity issues

**Debug Steps:**
```bash
# Check if services are running
docker-compose ps

# Check service health directly
curl http://localhost:8001/health  # If ports are exposed
docker-compose exec user-service curl http://localhost:8001/health

# Check nginx configuration
docker-compose exec nginx nginx -t
```

### Issue 2: 404 Not Found
**Symptoms:** `404 Not Found` for valid API endpoints
**Causes:**
- Incorrect location block configuration
- Wrong proxy_pass URL

**Debug Steps:**
```bash
# Check nginx configuration
cat nginx/nginx.conf | grep -A 5 "location /api"

# Test configuration
docker-compose exec nginx nginx -t
```

### Issue 3: CORS Issues
**Symptoms:** Browser console shows CORS errors
**Causes:**
- Missing CORS headers
- Incorrect CORS configuration

**Debug Steps:**
```bash
# Test CORS headers
curl -v -X OPTIONS http://localhost/api/users \
  -H "Origin: http://localhost:3000"
```

## ✅ Test Checklist

### Basic Functionality
- [ ] Health check endpoint responds
- [ ] Landing page loads correctly
- [ ] All service endpoints accessible through proxy
- [ ] CRUD operations work for all services
- [ ] Inter-service communication works (loan service)

### Error Handling
- [ ] 404 errors for invalid paths
- [ ] 502 errors when services are down
- [ ] Custom error pages display correctly

### Security & Headers
- [ ] CORS headers present
- [ ] Security headers added
- [ ] Proxy headers forwarded correctly

### Performance
- [ ] Response times acceptable
- [ ] Load testing passes
- [ ] No memory leaks under load

### Monitoring
- [ ] Access logs working
- [ ] Error logs working
- [ ] Service logs accessible

## 📝 Test Results Template

```
# Test Results - [Date]

## Environment
- OS: [Your OS]
- Docker Version: [Version]
- Docker Compose Version: [Version]

## Test Results
- [ ] Health Check: PASS/FAIL
- [ ] User Service: PASS/FAIL
- [ ] Book Service: PASS/FAIL
- [ ] Loan Service: PASS/FAIL
- [ ] Error Handling: PASS/FAIL
- [ ] CORS: PASS/FAIL
- [ ] Load Testing: PASS/FAIL

## Issues Found
[List any issues discovered during testing]

## Performance Metrics
- Average Response Time: [X]ms
- Requests per Second: [X]
- Error Rate: [X]%
```

## 🚀 Next Steps

After successful testing:
1. **Production Deployment**: Configure HTTPS and production settings
2. **Monitoring Setup**: Add Prometheus/Grafana for metrics
3. **Security Hardening**: Implement rate limiting and authentication
4. **Scaling**: Add load balancing for multiple service instances 