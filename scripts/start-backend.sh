#!/bin/bash
set -e

echo "🚀 Starting Arabic STT SaaS Backend Services..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Check if Docker and Docker Compose are available
command -v docker >/dev/null 2>&1 || print_error "Docker is required but not installed."
command -v docker-compose >/dev/null 2>&1 || print_error "Docker Compose is required but not installed."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_warning "No .env file found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        print_success "Created .env file from template"
        print_warning "Please edit .env with your configuration before continuing"
        echo ""
        echo "Key settings to configure:"
        echo "- JWT_SECRET (generate a secure 32+ character string)"
        echo "- Database passwords"
        echo "- Redis password" 
        echo "- MinIO credentials"
        echo "- External service tokens (Stripe, HuggingFace, Sentry)"
        echo ""
        read -p "Press Enter after configuring .env file..."
    else
        print_error ".env.example not found. Cannot create .env file."
    fi
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

print_status "Starting infrastructure services (PostgreSQL, Redis, MinIO)..."

# Start infrastructure services first
docker-compose up -d postgres redis minio

print_status "Waiting for infrastructure services to be ready..."

# Wait for PostgreSQL
print_status "Waiting for PostgreSQL..."
timeout=60
counter=0
while ! docker-compose exec -T postgres pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-arabic_stt} >/dev/null 2>&1; do
    if [ $counter -eq $timeout ]; then
        print_error "PostgreSQL failed to start within $timeout seconds"
    fi
    sleep 2
    counter=$((counter + 2))
    echo -n "."
done
print_success "PostgreSQL is ready"

# Wait for Redis
print_status "Waiting for Redis..."
counter=0
while ! docker-compose exec -T redis redis-cli -a ${REDIS_PASSWORD:-redis123} ping >/dev/null 2>&1; do
    if [ $counter -eq $timeout ]; then
        print_error "Redis failed to start within $timeout seconds"
    fi
    sleep 2
    counter=$((counter + 2))
    echo -n "."
done
print_success "Redis is ready"

# Wait for MinIO
print_status "Waiting for MinIO..."
counter=0
while ! docker-compose exec -T minio curl -f http://localhost:9000/minio/health/live >/dev/null 2>&1; do
    if [ $counter -eq $timeout ]; then
        print_error "MinIO failed to start within $timeout seconds"
    fi
    sleep 2
    counter=$((counter + 2))
    echo -n "."
done
print_success "MinIO is ready"

print_status "Building and starting API service..."
docker-compose up -d --build api

print_status "Waiting for API service to be ready..."
counter=0
while ! docker-compose exec -T api curl -f http://localhost:8000/health >/dev/null 2>&1; do
    if [ $counter -eq 120 ]; then
        print_error "API service failed to start within 120 seconds"
    fi
    sleep 3
    counter=$((counter + 3))
    echo -n "."
done
print_success "API service is ready"

print_status "Starting worker service..."
docker-compose up -d --build worker

print_status "Waiting for worker service to be ready..."
counter=0
while ! docker-compose exec -T worker celery -A app.celery_app inspect ping >/dev/null 2>&1; do
    if [ $counter -eq 120 ]; then
        print_error "Worker service failed to start within 120 seconds"
    fi
    sleep 3
    counter=$((counter + 3))
    echo -n "."
done
print_success "Worker service is ready"

print_status "Starting monitoring services..."
docker-compose up -d prometheus grafana flower

print_success "All backend services are running!"

echo ""
echo "📋 Service URLs:"
echo "🔗 API Documentation: http://localhost:${API_PORT:-8000}/docs"
echo "🔗 API Health Check: http://localhost:${API_PORT:-8000}/health"
echo "🔗 MinIO Console: http://localhost:${MINIO_CONSOLE_PORT:-9001}"
echo "🔗 Grafana Dashboard: http://localhost:${GRAFANA_PORT:-3001}"
echo "🔗 Prometheus: http://localhost:${PROMETHEUS_PORT:-9090}"
echo "🔗 Flower (Celery): http://localhost:${FLOWER_PORT:-5555}"
echo ""

print_status "Testing API connection..."
API_RESPONSE=$(curl -s http://localhost:${API_PORT:-8000}/health)
if echo "$API_RESPONSE" | grep -q "healthy"; then
    print_success "API is responding correctly"
else
    print_warning "API may not be fully ready yet"
fi

echo ""
print_success "Backend services started successfully!"
print_status "You can now start the frontend with: npm run dev"
print_status "Or start all services with: docker-compose up -d"

echo ""
echo "📊 To view logs:"
echo "  docker-compose logs api"
echo "  docker-compose logs worker" 
echo "  docker-compose logs postgres"
echo ""
echo "🛑 To stop services:"
echo "  docker-compose down"
echo ""

# Optional: Show current service status
echo "📈 Current service status:"
docker-compose ps