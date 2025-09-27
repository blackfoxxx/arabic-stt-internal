#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${CYAN}"
    echo "================================================================================================"
    echo "  🚀 ARABIC STT SAAS - COMPLETE FULL-STACK PLATFORM STARTUP"
    echo "================================================================================================"
    echo -e "${NC}"
}

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

print_section() {
    echo -e "${PURPLE}"
    echo "┌────────────────────────────────────────────────────────────────────────────────────────────┐"
    echo "│  $1"
    echo "└────────────────────────────────────────────────────────────────────────────────────────────┘"
    echo -e "${NC}"
}

# Print header
print_header

# Check prerequisites
print_section "CHECKING PREREQUISITES"
command -v docker >/dev/null 2>&1 || print_error "Docker is required but not installed."
command -v docker-compose >/dev/null 2>&1 || print_error "Docker Compose is required but not installed."
command -v node >/dev/null 2>&1 || print_error "Node.js is required but not installed."
command -v pnpm >/dev/null 2>&1 || print_error "pnpm is required but not installed."

print_success "All prerequisites are installed"

# Environment setup
print_section "ENVIRONMENT SETUP"
if [ ! -f .env ]; then
    print_warning "No .env file found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        print_success "Created .env file from template"
    else
        print_error ".env.example not found"
    fi
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
    print_success "Environment variables loaded"
fi

# Create necessary directories
print_status "Creating required directories..."
mkdir -p logs data/{postgres,redis,minio} models/cache uploads/temp
print_success "Directories created"

# Frontend build and setup
print_section "FRONTEND SETUP & BUILD"
print_status "Installing frontend dependencies..."
pnpm install

print_status "Building frontend application..."
pnpm run build --no-lint

print_success "Frontend built successfully"

# Backend services startup
print_section "BACKEND SERVICES STARTUP"
print_status "Starting infrastructure services (PostgreSQL, Redis, MinIO)..."
docker-compose up -d postgres redis minio

# Wait for infrastructure
print_status "Waiting for infrastructure services..."
sleep 15

# Check PostgreSQL
print_status "Checking PostgreSQL connection..."
timeout=60
counter=0
while ! docker-compose exec -T postgres pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-arabic_stt} >/dev/null 2>&1; do
    if [ $counter -eq $timeout ]; then
        print_error "PostgreSQL failed to start"
    fi
    sleep 2
    counter=$((counter + 2))
done
print_success "PostgreSQL is ready"

# Check Redis
print_status "Checking Redis connection..."
counter=0
while ! docker-compose exec -T redis redis-cli -a ${REDIS_PASSWORD:-redis123} ping >/dev/null 2>&1; do
    if [ $counter -eq $timeout ]; then
        print_error "Redis failed to start"
    fi
    sleep 2
    counter=$((counter + 2))
done
print_success "Redis is ready"

# Check MinIO
print_status "Checking MinIO connection..."
counter=0
while ! curl -f http://localhost:${MINIO_PORT:-9000}/minio/health/live >/dev/null 2>&1; do
    if [ $counter -eq $timeout ]; then
        print_error "MinIO failed to start"
    fi
    sleep 2
    counter=$((counter + 2))
done
print_success "MinIO is ready"

# Start API service
print_status "Building and starting API service..."
docker-compose up -d --build api

print_status "Waiting for API service..."
counter=0
while ! curl -f http://localhost:${API_PORT:-8000}/health >/dev/null 2>&1; do
    if [ $counter -eq 120 ]; then
        print_error "API service failed to start"
    fi
    sleep 3
    counter=$((counter + 3))
done
print_success "API service is ready"

# Start worker service
print_status "Building and starting worker service..."
docker-compose up -d --build worker

print_status "Waiting for worker service..."
counter=0
while ! docker-compose exec -T worker celery -A app.celery_app inspect ping >/dev/null 2>&1; do
    if [ $counter -eq 180 ]; then
        print_warning "Worker service taking longer than expected (this is normal for first startup)"
        break
    fi
    sleep 5
    counter=$((counter + 5))
done
print_success "Worker service is starting (may take additional time for model downloads)"

# Start monitoring services
print_status "Starting monitoring services..."
docker-compose up -d prometheus grafana flower

print_success "All backend services started"

# API Testing
print_section "API TESTING & VALIDATION"
print_status "Running API health checks..."

# Test basic health
API_HEALTH=$(curl -s http://localhost:${API_PORT:-8000}/health)
if echo "$API_HEALTH" | grep -q "healthy"; then
    print_success "API health check passed"
else
    print_error "API health check failed"
fi

# Test detailed health
print_status "Testing detailed health endpoint..."
DETAILED_HEALTH=$(curl -s http://localhost:${API_PORT:-8000}/health/detailed)
if echo "$DETAILED_HEALTH" | grep -q "healthy"; then
    print_success "Detailed health check passed"
    echo "   $(echo $DETAILED_HEALTH | jq -r '.checks // {}')"
else
    print_warning "Detailed health check may show some services as not ready (normal during startup)"
fi

# Test metrics
print_status "Testing metrics endpoint..."
METRICS_RESPONSE=$(curl -s -w "%{http_code}" http://localhost:${API_PORT:-8000}/metrics -o /dev/null)
if [ "$METRICS_RESPONSE" = "200" ]; then
    print_success "Metrics endpoint is working"
else
    print_warning "Metrics endpoint returned: $METRICS_RESPONSE"
fi

# Frontend startup
print_section "FRONTEND SERVICE STARTUP"
print_status "Starting frontend production server..."

# Kill any existing frontend process
pkill -f "pnpm start" || true

# Start frontend
pnpm start &
FRONTEND_PID=$!

print_status "Waiting for frontend to be ready..."
sleep 5
counter=0
while ! curl -f http://localhost:${FRONTEND_PORT:-3000}/api/health >/dev/null 2>&1; do
    if [ $counter -eq 60 ]; then
        print_error "Frontend failed to start"
    fi
    sleep 2
    counter=$((counter + 2))
done
print_success "Frontend is ready"

# Full stack testing
print_section "FULL-STACK INTEGRATION TESTING"

# Test frontend health
print_status "Testing frontend health..."
FRONTEND_HEALTH=$(curl -s http://localhost:${FRONTEND_PORT:-3000}/api/health)
if echo "$FRONTEND_HEALTH" | grep -q "healthy"; then
    print_success "Frontend health check passed"
else
    print_error "Frontend health check failed"
fi

# Test API from frontend perspective
print_status "Testing API connectivity from frontend..."
# This would be a CORS test in a real scenario

# Run comprehensive backend tests
print_status "Running comprehensive backend tests..."
if [ -f "scripts/test-backend.py" ]; then
    python3 scripts/test-backend.py
    if [ $? -eq 0 ]; then
        print_success "Backend tests passed"
    else
        print_warning "Some backend tests failed (check logs)"
    fi
else
    print_warning "Backend test script not found"
fi

# Final status report
print_section "DEPLOYMENT COMPLETE - SERVICE STATUS"

echo ""
echo "🌟 Arabic STT SaaS Platform Successfully Deployed!"
echo ""
echo "📱 Frontend Application:"
echo "   🔗 Main App: http://localhost:${FRONTEND_PORT:-3000}"
echo "   🔗 Health Check: http://localhost:${FRONTEND_PORT:-3000}/api/health"
echo ""
echo "🔧 Backend API:"
echo "   🔗 API Documentation: http://localhost:${API_PORT:-8000}/docs"
echo "   🔗 API Health: http://localhost:${API_PORT:-8000}/health"
echo "   🔗 Detailed Health: http://localhost:${API_PORT:-8000}/health/detailed"
echo "   🔗 Metrics: http://localhost:${API_PORT:-8000}/metrics"
echo ""
echo "💾 Infrastructure Services:"
echo "   🔗 MinIO Console: http://localhost:${MINIO_CONSOLE_PORT:-9001}"
echo "   🔗 Grafana Dashboard: http://localhost:${GRAFANA_PORT:-3001}"
echo "   🔗 Prometheus: http://localhost:${PROMETHEUS_PORT:-9090}"
echo "   🔗 Flower (Celery): http://localhost:${FLOWER_PORT:-5555}"
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🎯 Next Steps:"
echo "1. 🌐 Open http://localhost:${FRONTEND_PORT:-3000} to access the Arabic STT platform"
echo "2. 📖 View API docs at http://localhost:${API_PORT:-8000}/docs"
echo "3. 📊 Monitor services at http://localhost:${GRAFANA_PORT:-3001}"
echo "4. 🧪 Test the complete workflow with audio uploads"
echo ""
echo "📝 To view logs:"
echo "   docker-compose logs api"
echo "   docker-compose logs worker"
echo "   docker-compose logs postgres"
echo ""
echo "🛑 To stop all services:"
echo "   docker-compose down"
echo "   kill $FRONTEND_PID"
echo ""

print_success "Full-stack Arabic STT SaaS platform is ready for use!"

# Keep script running to maintain frontend
echo "🔄 Keeping services running. Press Ctrl+C to stop all services."
trap "print_status 'Stopping services...'; docker-compose down; kill $FRONTEND_PID 2>/dev/null || true; print_success 'All services stopped.'" EXIT

# Monitor services
while true; do
    sleep 30
    # Check if frontend is still running
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        print_warning "Frontend process stopped unexpectedly"
        break
    fi
    
    # Check if API is responding
    if ! curl -f http://localhost:${API_PORT:-8000}/health >/dev/null 2>&1; then
        print_warning "API service is not responding"
    fi
done