# 🌐 Nginx Reverse Proxy Setup

This directory contains the Nginx reverse proxy configuration for the Smart Library System microservices.

## 📋 What is a Reverse Proxy?

A **reverse proxy** acts as an intermediary between clients and backend servers. Instead of clients connecting directly to your microservices, they connect to Nginx, which then forwards requests to the appropriate backend service.

### Benefits:
- **Single Entry Point**: All API calls go through `http://localhost/api/*`
- **Load Balancing**: Distribute requests across multiple service instances
- **SSL Termination**: Handle HTTPS encryption centrally
- **Caching**: Cache responses to improve performance
- **Security**: Hide backend service details from clients
- **Static File Serving**: Efficiently serve frontend assets

## 🏗️ Architecture

```
Client Request → Nginx (Port 80) → Backend Service
                     ↓
    /api/users  → User Service (Port 8001)
    /api/books  → Book Service (Port 8002)
    /api/loans  → Loan Service (Port 8003)
```

## 📁 Files Explained

### `nginx.conf`
Main configuration file for Docker deployment:
- **Upstream blocks**: Define backend service locations
- **Location blocks**: Route requests based on URL paths
- **Proxy headers**: Forward client information to backend services
- **CORS handling**: Enable cross-origin requests
- **Error handling**: Custom error pages

### `nginx-local.conf`
Simplified configuration for local development without Docker.

### `Dockerfile`
Container definition for Nginx service.

## 🚀 Usage

### Option 1: Docker Compose (Recommended)

```bash
# Start all services including Nginx
docker-compose up --build

# Access the system
curl http://localhost/health
curl http://localhost/api/users
curl http://localhost/api/books
curl http://localhost/api/loans
```

### Option 2: Local Development

1. **Install Nginx** (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install nginx
```

2. **Start your microservices**:
```bash
# Terminal 1
cd user-service && uvicorn app.main:app --host 0.0.0.0 --port 8001

# Terminal 2  
cd book-service && uvicorn app.main:app --host 0.0.0.0 --port 8002

# Terminal 3
cd loan-service && uvicorn app.main:app --host 0.0.0.0 --port 8003
```

3. **Configure Nginx**:
```bash
# Backup original config
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

# Copy our config
sudo cp nginx-local.conf /etc/nginx/nginx.conf

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## 🔍 Testing the Reverse Proxy

### Health Check
```bash
curl http://localhost/health
# Expected: "healthy"
```

### API Endpoints
```bash
# User Service through proxy
curl -X GET http://localhost/api/users
curl -X POST http://localhost/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'

# Book Service through proxy
curl -X GET http://localhost/api/books
curl -X POST http://localhost/api/books \
  -H "Content-Type: application/json" \
  -d '{"title": "1984", "author": "George Orwell", "isbn": "978-0-452-28423-4", "available_copies": 5}'

# Loan Service through proxy
curl -X GET http://localhost/api/loans
curl -X POST http://localhost/api/loans \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "book_id": 1}'
```

### Landing Page
Visit `http://localhost/` in your browser to see the system overview.

## 🔧 Configuration Details

### Key Nginx Directives Explained

#### Upstream Blocks
```nginx
upstream user_service {
    server user-service:8001;  # Docker container name
    # server localhost:8001;   # For local development
}
```
Defines backend server groups for load balancing.

#### Location Blocks
```nginx
location /api/users {
    proxy_pass http://user_service;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    # ... more headers
}
```
Routes requests and sets proxy headers.

#### Proxy Headers
- `Host`: Original host header
- `X-Real-IP`: Client's real IP address
- `X-Forwarded-For`: Chain of proxy IPs
- `X-Forwarded-Proto`: Original protocol (http/https)

## 📊 Monitoring and Logs

### Access Logs
```bash
# Docker
docker-compose logs nginx

# Local
sudo tail -f /var/log/nginx/access.log
```

### Error Logs
```bash
# Docker
docker-compose logs nginx | grep error

# Local
sudo tail -f /var/log/nginx/error.log
```

### Log Format
Our custom log format includes:
- Client IP and user
- Request details
- Response status and size
- Upstream server and response time

## 🛠️ Troubleshooting

### Common Issues

1. **502 Bad Gateway**
   - Backend service is down
   - Check service health: `curl http://localhost:8001/health`

2. **404 Not Found**
   - URL path doesn't match location blocks
   - Check nginx configuration

3. **Connection Refused**
   - Nginx is not running
   - Check: `sudo systemctl status nginx`

4. **Permission Denied**
   - Nginx doesn't have permission to access files
   - Check file permissions and SELinux settings

### Debug Commands
```bash
# Test Nginx configuration
sudo nginx -t

# Reload configuration without restart
sudo nginx -s reload

# Check if Nginx is running
sudo systemctl status nginx

# View real-time logs
sudo tail -f /var/log/nginx/access.log /var/log/nginx/error.log
```

## 🔒 Security Features

### Headers Added
- `X-Frame-Options`: Prevent clickjacking
- `X-XSS-Protection`: Enable XSS filtering
- `X-Content-Type-Options`: Prevent MIME sniffing
- `Content-Security-Policy`: Control resource loading

### CORS Support
Configured to allow cross-origin requests for API development.

## 🚀 Next Steps

1. **HTTPS Setup**: Add SSL certificates for production
2. **Rate Limiting**: Prevent abuse with request limits
3. **Caching**: Add response caching for better performance
4. **Load Balancing**: Scale services horizontally
5. **Monitoring**: Add metrics collection with Prometheus 