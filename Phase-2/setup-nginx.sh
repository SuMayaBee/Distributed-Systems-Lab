#!/bin/bash

echo "🌐 Setting up Smart Library System with Nginx Reverse Proxy"
echo "============================================================"

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start all services
echo "🏗️  Building and starting all services..."
docker-compose up --build -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service health..."

# Check Nginx
if curl -s http://localhost/health > /dev/null; then
    echo "✅ Nginx reverse proxy is running"
else
    echo "❌ Nginx reverse proxy is not responding"
fi

# Check services through proxy
if curl -s http://localhost/api/users > /dev/null; then
    echo "✅ User service is accessible through proxy"
else
    echo "❌ User service is not accessible through proxy"
fi

if curl -s http://localhost/api/books > /dev/null; then
    echo "✅ Book service is accessible through proxy"
else
    echo "❌ Book service is not accessible through proxy"
fi

if curl -s http://localhost/api/loans > /dev/null; then
    echo "✅ Loan service is accessible through proxy"
else
    echo "❌ Loan service is not accessible through proxy"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Access your services:"
echo "   🌐 Landing Page:  http://localhost/"
echo "   ❤️  Health Check:  http://localhost/health"
echo "   👥 User Service:  http://localhost/api/users"
echo "   📚 Book Service:  http://localhost/api/books"
echo "   📖 Loan Service:  http://localhost/api/loans"
echo ""
echo "📊 View logs:"
echo "   docker-compose logs -f nginx"
echo "   docker-compose logs -f user-service"
echo "   docker-compose logs -f book-service"
echo "   docker-compose logs -f loan-service"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down" 