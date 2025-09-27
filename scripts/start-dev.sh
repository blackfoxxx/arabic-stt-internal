#!/bin/bash

# Arabic STT SaaS - Development Environment Setup Script

set -e

echo "🚀 Starting Arabic STT SaaS Development Environment..."

# Check prerequisites
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed."
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is required but not installed."
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating environment file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
    echo "✏️  You can use the defaults for local development"
    echo ""
    read -p "Continue with default settings? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please edit .env file and run this script again"
        exit 1
    fi
fi

# Load environment variables
source .env

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis  
mkdir -p data/minio
mkdir -p models/cache
mkdir -p uploads/temp
mkdir -p scripts

# Start infrastructure services first
echo "🔧 Starting infrastructure services..."
docker-compose up -d postgres redis minio

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
echo "   - PostgreSQL..."
until docker-compose exec -T postgres pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-arabic_stt} > /dev/null 2>&1; do
    sleep 2
done

echo "   - Redis..."
until docker-compose exec -T redis redis-cli --raw incr ping > /dev/null 2>&1; do
    sleep 2
done

echo "   - MinIO..."
until curl -f http://localhost:${MINIO_PORT:-9000}/minio/health/live > /dev/null 2>&1; do
    sleep 2
done

echo "✅ Infrastructure services are ready!"

# Build and start API service
echo "🏗️  Building and starting API service..."
docker-compose up -d api

# Wait for API to be ready
echo "⏳ Waiting for API service..."
until curl -f http://localhost:${API_PORT:-8000}/health > /dev/null 2>&1; do
    sleep 3
done

echo "✅ API service is ready!"

# Start worker service
echo "🤖 Starting worker service..."
docker-compose up -d worker

# Start monitoring services
echo "📊 Starting monitoring services..."
docker-compose up -d prometheus grafana flower

# Start frontend (this will be our existing Next.js app)
echo "🎨 Frontend is already running at http://localhost:3000"

echo ""
echo "🎉 Arabic STT SaaS development environment is ready!"
echo ""
echo "📋 Service URLs:"
echo "   Frontend:      http://localhost:3000"
echo "   API:           http://localhost:${API_PORT:-8000}"
echo "   API Docs:      http://localhost:${API_PORT:-8000}/docs"
echo "   MinIO Console: http://localhost:${MINIO_CONSOLE_PORT:-9001}"
echo "   Grafana:       http://localhost:${GRAFANA_PORT:-3001}"
echo "   Flower:        http://localhost:${FLOWER_PORT:-5555}"
echo ""
echo "🔑 Demo Accounts:"
echo "   Admin: admin@demo.com / admin123"
echo "   User:  user@demo.com / user123"
echo ""
echo "📚 Next Steps:"
echo "   1. Visit http://localhost:3000 to access the web interface"
echo "   2. Test API endpoints at http://localhost:${API_PORT:-8000}/docs"
echo "   3. Monitor worker jobs at http://localhost:${FLOWER_PORT:-5555}"
echo "   4. Check system metrics at http://localhost:${GRAFANA_PORT:-3001}"
echo ""
echo "🛑 To stop all services:"
echo "   docker-compose down"
echo ""
echo "🔧 To view logs:"
echo "   docker-compose logs -f [service_name]"