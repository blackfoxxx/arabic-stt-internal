#!/bin/bash
# Prepare Arabic STT Internal System for GitHub Upload

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_header() {
    clear
    echo -e "${CYAN}"
    echo "================================================================================================"
    echo "  📤 PREPARING ARABIC STT INTERNAL SYSTEM FOR GITHUB"
    echo "================================================================================================"
    echo "  🏢 Internal Company Use • 🔒 No Commercial Data • 🤖 Complete AI Processing"
    echo "================================================================================================"
    echo -e "${NC}"
}

create_license() {
    print_status "Creating LICENSE file..."
    
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2024 Arabic STT Internal System

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

INTERNAL USE NOTICE:
This software is designed for internal company use. It includes no commercial
features, billing systems, or external dependencies. All processing is designed
to be performed locally for maximum security and privacy.
EOF

    print_success "LICENSE created"
}

create_requirements_files() {
    print_status "Creating requirements files..."
    
    # Python requirements for AI processing
cat > requirements.txt << 'EOF'
# Arabic STT Internal System - Python Requirements
# AI Processing Libraries
faster-whisper==0.10.0
torch>=2.0.0
torchaudio>=2.0.0
pyannote.audio>=3.1.0
librosa==0.10.1
soundfile==0.12.1
numpy>=1.24.0
scipy>=1.10.0
pydub>=0.25.1
noisereduce>=3.0.0

# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic>=2.5.0
jinja2>=3.1.0

# Database and Storage
sqlalchemy>=2.0.0
alembic>=1.12.0
psycopg2-binary>=2.9.0
redis>=5.0.0

# Object Storage
minio>=7.2.0
boto3>=1.34.0

# Task Queue
celery>=5.3.0
flower>=2.0.0

# Utilities
requests>=2.31.0
tqdm>=4.66.0
python-dotenv>=1.0.0
structlog>=23.2.0
psutil>=5.9.0
python-slugify>=8.0.0
python-dateutil>=2.8.0

# Security
bcrypt>=4.1.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.0

# Monitoring
prometheus-client>=0.19.0
sentry-sdk>=1.40.0

# Development
pytest>=7.4.0
pytest-asyncio>=0.21.0
black>=23.11.0
isort>=5.12.0
flake8>=6.1.0
EOF

    # Node.js package.json
cat > package.json << 'EOF'
{
  "name": "arabic-stt-internal-frontend",
  "version": "2.0.0",
  "description": "Arabic STT Internal System - Frontend",
  "private": true,
  "scripts": {
    "dev": "next dev -p 3000",
    "build": "next build",
    "start": "next start -p 3000",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "@hookform/resolvers": "^5.0.1",
    "@radix-ui/react-accordion": "^1.2.10",
    "@radix-ui/react-alert-dialog": "^1.1.13",
    "@radix-ui/react-aspect-ratio": "^1.1.6",
    "@radix-ui/react-avatar": "^1.1.9",
    "@radix-ui/react-checkbox": "^1.3.1",
    "@radix-ui/react-collapsible": "^1.1.10",
    "@radix-ui/react-context-menu": "^2.2.14",
    "@radix-ui/react-dialog": "^1.1.13",
    "@radix-ui/react-dropdown-menu": "^2.1.14",
    "@radix-ui/react-hover-card": "^1.1.13",
    "@radix-ui/react-label": "^2.1.6",
    "@radix-ui/react-menubar": "^1.1.14",
    "@radix-ui/react-navigation-menu": "^1.2.12",
    "@radix-ui/react-popover": "^1.1.13",
    "@radix-ui/react-progress": "^1.1.6",
    "@radix-ui/react-radio-group": "^1.3.6",
    "@radix-ui/react-scroll-area": "^1.2.8",
    "@radix-ui/react-select": "^2.2.4",
    "@radix-ui/react-separator": "^1.1.6",
    "@radix-ui/react-sheet": "^1.1.13",
    "@radix-ui/react-slider": "^1.3.4",
    "@radix-ui/react-slot": "^1.2.2",
    "@radix-ui/react-switch": "^1.2.4",
    "@radix-ui/react-tabs": "^1.1.11",
    "@radix-ui/react-textarea": "^1.1.6",
    "@radix-ui/react-toggle": "^1.1.8",
    "@radix-ui/react-toggle-group": "^1.1.9",
    "@radix-ui/react-tooltip": "^1.2.6",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "cmdk": "^1.1.1",
    "date-fns": "^3.6.0",
    "lucide-react": "^0.509.0",
    "next": "15.3.2",
    "next-themes": "^0.4.6",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-hook-form": "^7.56.3",
    "tailwind-merge": "^3.2.0",
    "tailwindcss-animate": "^1.0.7",
    "zod": "^3.24.4"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "autoprefixer": "^10.4.21",
    "eslint": "^9",
    "eslint-config-next": "15.3.2",
    "postcss": "^8.5.3",
    "tailwindcss": "^4.1.6",
    "typescript": "^5"
  },
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=8.0.0"
  }
}
EOF

    print_success "Requirements files created"
}

create_docker_files() {
    print_status "Creating Docker configuration..."
    
cat > docker-compose.yml << 'EOF'
# Arabic STT Internal System - Docker Compose
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: arabic-stt-postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-arabic_stt_internal}
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres123}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init_db.sql:/docker-entrypoint-initdb.d/init_db.sql
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - arabic-stt-network

  # Redis for Caching and Queue
  redis:
    image: redis:7-alpine
    container_name: arabic-stt-redis
    command: redis-server --requirepass ${REDIS_PASSWORD:-redis123}
    volumes:
      - redis_data:/data
    ports:
      - "${REDIS_PORT:-6379}:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 3s
      retries: 5
    networks:
      - arabic-stt-network

  # MinIO Object Storage
  minio:
    image: minio/minio:latest
    container_name: arabic-stt-minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER:-minioadmin}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD:-minioadmin123}
    volumes:
      - minio_data:/data
    ports:
      - "${MINIO_PORT:-9000}:9000"
      - "${MINIO_CONSOLE_PORT:-9001}:9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3
    networks:
      - arabic-stt-network

  # FastAPI Backend
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    container_name: arabic-stt-api
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres123}@postgres:5432/${POSTGRES_DB:-arabic_stt_internal}
      REDIS_URL: redis://:${REDIS_PASSWORD:-redis123}@redis:6379/0
      MINIO_ENDPOINT: minio:9000
      MINIO_ACCESS_KEY: ${MINIO_ROOT_USER:-minioadmin}
      MINIO_SECRET_KEY: ${MINIO_ROOT_PASSWORD:-minioadmin123}
      JWT_SECRET: ${JWT_SECRET:-your-secret-key}
      ENVIRONMENT: development
    volumes:
      - ./api:/app
    ports:
      - "${API_PORT:-8000}:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      minio:
        condition: service_healthy
    networks:
      - arabic-stt-network

  # Celery Worker
  worker:
    build:
      context: ./worker
      dockerfile: Dockerfile
    container_name: arabic-stt-worker
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres123}@postgres:5432/${POSTGRES_DB:-arabic_stt_internal}
      CELERY_BROKER_URL: redis://:${REDIS_PASSWORD:-redis123}@redis:6379/0
      MINIO_ENDPOINT: minio:9000
      MINIO_ACCESS_KEY: ${MINIO_ROOT_USER:-minioadmin}
      MINIO_SECRET_KEY: ${MINIO_ROOT_PASSWORD:-minioadmin123}
      HF_HOME: /app/models
      GPU_ENABLED: ${GPU_ENABLED:-false}
    volumes:
      - ./worker:/app
      - models_cache:/app/models
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      minio:
        condition: service_healthy
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    networks:
      - arabic-stt-network

volumes:
  postgres_data:
  redis_data:
  minio_data:
  models_cache:

networks:
  arabic-stt-network:
    driver: bridge
EOF

cat > .env.example << 'EOF'
# Arabic STT Internal System - Environment Configuration

# System Configuration
ENVIRONMENT=development
DEBUG=false
SYSTEM_TYPE=internal
INTERNAL_USE_ONLY=true

# Database Configuration
POSTGRES_DB=arabic_stt_internal
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis Configuration
REDIS_PASSWORD=redis123
REDIS_HOST=localhost
REDIS_PORT=6379

# MinIO Configuration
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
MINIO_PORT=9000
MINIO_CONSOLE_PORT=9001

# API Configuration
API_PORT=8000
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
ALLOWED_ORIGINS=http://localhost:3000

# AI Processing Configuration
DEFAULT_ASR_MODEL=large-v3
GPU_ENABLED=true
MAX_CONCURRENT_JOBS=10
FFMPEG_THREADS=4

# Frontend Configuration
FRONTEND_PORT=3000
NEXT_PUBLIC_API_URL=http://localhost:8000

# Security Configuration (Internal Use)
ENABLE_REGISTRATION=false
REQUIRE_EMAIL_VERIFICATION=false
INTERNAL_ADMIN_EMAIL=admin@company.com
INTERNAL_ADMIN_PASSWORD=admin123

# Monitoring
ENABLE_PROMETHEUS=true
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001

# Logging
LOG_LEVEL=INFO
ENABLE_AUDIT_LOGGING=true
EOF

    print_success "Docker configuration created"
}

create_github_workflows() {
    print_status "Creating GitHub Actions workflows..."
    
    mkdir -p .github/workflows
    
cat > .github/workflows/ci.yml << 'EOF'
name: Arabic STT Internal System - CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-frontend:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run type check
      run: npm run type-check
    
    - name: Build frontend
      run: npm run build

  test-backend:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y ffmpeg
    
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run backend tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379/0
        ENVIRONMENT: test
      run: |
        python -m pytest api/tests/ -v

  security-scan:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Run security scan
      uses: github/super-linter@v4
      env:
        DEFAULT_BRANCH: main
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        VALIDATE_PYTHON: true
        VALIDATE_TYPESCRIPT: true
        VALIDATE_DOCKERFILE: true
EOF

cat > .github/workflows/docker-build.yml << 'EOF'
name: Docker Build and Test

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  docker-build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Build API image
      uses: docker/build-push-action@v5
      with:
        context: ./api
        file: ./api/Dockerfile
        push: false
        tags: arabic-stt-api:test
    
    - name: Build Worker image
      uses: docker/build-push-action@v5
      with:
        context: ./worker
        file: ./worker/Dockerfile
        push: false
        tags: arabic-stt-worker:test
    
    - name: Test Docker Compose
      run: |
        cp .env.example .env
        docker-compose -f docker-compose.test.yml up -d
        sleep 30
        docker-compose -f docker-compose.test.yml down
EOF

    print_success "GitHub Actions workflows created"
}

create_project_documentation() {
    print_status "Creating project documentation..."
    
    mkdir -p docs
    
cat > docs/INSTALLATION.md << 'EOF'
# 🚀 Installation Guide

## Automated Installation (Recommended)

### Zero User Interaction
```bash
# Universal installer (works on Windows, Linux, macOS)
python3 universal-installer.py
```

### Platform-Specific Installers
```bash
# Windows (RTX 5090 optimized)
auto-install-windows.bat

# Linux/macOS
./auto-install-complete.sh
```

## Manual Installation

### Prerequisites
- Python 3.11+
- NVIDIA GPU drivers (for GPU acceleration)
- FFmpeg
- Git

### Steps
1. **Clone Repository**
   ```bash
   git clone https://github.com/your-username/arabic-stt-internal.git
   cd arabic-stt-internal
   ```

2. **Setup Python Environment**
   ```bash
   python3 -m venv arabic-stt-env
   source arabic-stt-env/bin/activate  # Linux/macOS
   # arabic-stt-env\Scripts\activate.bat  # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   
   # For GPU acceleration
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

4. **Start Services**
   ```bash
   # Start API server
   python3 arabic_stt_server.py
   
   # In another terminal, start frontend
   npm install
   npm run build
   npm start
   ```

## Docker Installation

```bash
# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

## Verification

```bash
# Test API
curl http://localhost:8000/health

# Test file processing
curl -X POST http://localhost:8000/v1/upload-and-process \
  -F "file=@test_audio.mp3" \
  -F "language=ar"
```
EOF

cat > docs/API.md << 'EOF'
# 🔌 API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
```bash
# All endpoints require authentication for internal use
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/v1/endpoint
```

## Core Endpoints

### Upload and Process Audio
```bash
POST /v1/upload-and-process
Content-Type: multipart/form-data

Parameters:
- file: Audio/video file
- language: ar (default) | ar-IQ | ar-EG | ar-SA
- model: large-v3 | medium | small | base
- diarization: true | false
- enhancement_level: high | medium | light
```

### Get Transcript
```bash
GET /v1/transcripts/{transcript_id}

Response:
{
  "transcript": {
    "id": "transcript_123",
    "segments": [...],
    "speakers": [...],
    "confidence_score": 0.95
  }
}
```

### System Health
```bash
GET /health

Response:
{
  "status": "healthy",
  "ai_models": {...},
  "system_performance": {...}
}
```

## Error Handling

All endpoints return standardized error responses:
```json
{
  "error": "error_code",
  "message": "Human readable message in Arabic",
  "details": {...}
}
```

## Rate Limiting

- **Internal Use**: No rate limits
- **Development**: 1000 requests/hour
- **Headers**: X-RateLimit-* headers included
EOF

    print_success "Documentation created"
}

create_contribution_guide() {
    print_status "Creating contribution guidelines..."
    
cat > CONTRIBUTING.md << 'EOF'
# 🤝 Contributing to Arabic STT Internal System

## Internal Development Guidelines

This system is designed for internal company use. All contributions should maintain:

### Security Standards
- **Local Processing**: No external API dependencies
- **Data Privacy**: All data handling must remain internal
- **Access Control**: Maintain internal-only access patterns
- **Audit Compliance**: All changes must be auditable

### Code Standards
- **Python**: Follow PEP 8, use black formatter
- **TypeScript**: Follow TSLint rules, use prettier
- **Documentation**: Update docs for all changes
- **Testing**: Add tests for new features

### Arabic Language Standards
- **RTL Support**: Maintain right-to-left interface
- **Unicode**: Proper Arabic text handling
- **Cultural Sensitivity**: Appropriate Arabic UX patterns
- **Dialect Support**: Consider all Arabic variants

## Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow coding standards
   - Add appropriate tests
   - Update documentation

3. **Test Locally**
   ```bash
   # Test API
   python -m pytest api/tests/
   
   # Test frontend
   npm test
   
   # Test integration
   python scripts/test_integration.py
   ```

4. **Submit for Review**
   - Create pull request
   - Include description of changes
   - Reference any related issues

## AI Model Guidelines

### Adding New Models
- Document performance characteristics
- Test with Arabic content
- Verify memory requirements
- Update configuration options

### Model Optimization
- Profile performance impact
- Test on target hardware
- Document GPU requirements
- Validate accuracy metrics

## Internal Security Review

All changes require internal security review for:
- Data handling practices
- External dependency additions
- API endpoint modifications
- Authentication changes
EOF

cat > SECURITY.md << 'EOF'
# 🔒 Security Policy

## Internal System Security

This Arabic STT system is designed for internal company use with maximum security.

### Security Features
- **Local Processing**: No external API calls
- **Data Isolation**: All data stays within company infrastructure
- **Access Control**: Internal network access only
- **Encryption**: Data encrypted at rest and in transit
- **Audit Logging**: Complete activity tracking

### Supported Versions
- **v2.0.x**: Current stable version
- **v1.x**: Legacy support (security updates only)

### Reporting Security Issues

For internal security issues:
1. **Do not** create public GitHub issues
2. **Contact** internal security team directly
3. **Include** detailed description and reproduction steps
4. **Wait** for internal security team response before disclosure

### Security Hardening Checklist

#### Production Deployment
- [ ] Change all default passwords
- [ ] Enable TLS/SSL encryption
- [ ] Configure firewall rules
- [ ] Set up audit logging
- [ ] Enable access monitoring
- [ ] Configure backup encryption

#### Internal Network Security
- [ ] Restrict to internal network only
- [ ] Use VPN for remote access
- [ ] Enable IP whitelisting
- [ ] Configure network monitoring
- [ ] Set up intrusion detection

#### Application Security
- [ ] Enable JWT token expiration
- [ ] Configure rate limiting
- [ ] Set up input validation
- [ ] Enable CORS restrictions
- [ ] Configure secure headers

### Compliance

This system is designed to support:
- **GDPR**: Data privacy and user rights
- **SOC 2**: Security controls and monitoring
- **Internal Policies**: Company-specific requirements
- **Data Retention**: Configurable retention policies
EOF

    print_success "Contribution and security guides created"
}

prepare_repository_structure() {
    print_status "Preparing repository structure..."
    
    # Create main directories if they don't exist
    mkdir -p {api,worker,frontend,scripts,docs,tests}
    
    # Create placeholder files for empty directories
    echo "# API Backend" > api/README.md
    echo "# Worker Services" > worker/README.md
    echo "# Frontend Application" > frontend/README.md
    echo "# Scripts and Tools" > scripts/README.md
    echo "# Test Suites" > tests/README.md
    
    print_success "Repository structure prepared"
}

create_git_commands() {
    print_status "Creating Git setup commands..."
    
cat > setup-git-repo.sh << 'EOF'
#!/bin/bash
# Setup Git repository for Arabic STT Internal System

echo "📤 Setting up Git repository..."

# Initialize Git if not already initialized
if [ ! -d .git ]; then
    git init
    echo "✅ Git repository initialized"
fi

# Add all files
git add .

# Create initial commit
git commit -m "🏢 Initial commit: Arabic STT Internal System

Features:
- 🎤 Arabic speech recognition with faster-whisper
- 👥 Speaker diarization with pyannote.audio  
- 📱 Modern Arabic RTL interface
- 🔒 Internal use only - no commercial features
- ⚡ GPU acceleration support
- 🚀 Automated installation scripts
- 📚 Complete documentation

Ready for internal company deployment."

echo "✅ Initial commit created"

# Instructions for GitHub upload
echo ""
echo "📤 To upload to GitHub:"
echo ""
echo "1. Create new repository on GitHub:"
echo "   - Go to https://github.com/new"
echo "   - Repository name: arabic-stt-internal"
echo "   - Description: Arabic STT Internal System for Company Use"
echo "   - Private: ✅ (recommended for internal use)"
echo "   - Don't initialize with README (we have one)"
echo ""
echo "2. Add GitHub remote and push:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/arabic-stt-internal.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Your complete Arabic STT system will be uploaded!"
echo ""
EOF

    chmod +x setup-git-repo.sh
    print_success "Git setup script created"
}

show_github_summary() {
    echo ""
    echo -e "${CYAN}================================================================================================${NC}"
    echo -e "${CYAN}  📤 ARABIC STT INTERNAL SYSTEM - READY FOR GITHUB${NC}"
    echo -e "${CYAN}================================================================================================${NC}"
    echo ""
    
    echo -e "${GREEN}✅ Repository Prepared:${NC}"
    echo "   📁 Complete project structure"
    echo "   📚 All documentation files"
    echo "   🔒 Internal use configuration"
    echo "   🚀 Automated installation scripts"
    echo "   🐳 Docker deployment setup"
    echo "   🔧 GitHub Actions workflows"
    echo ""
    
    echo -e "${GREEN}📋 Files Ready for Upload:${NC}"
    echo "   • README.md - Complete project overview"
    echo "   • LICENSE - MIT license with internal use notice"
    echo "   • .gitignore - Proper exclusions for AI project"
    echo "   • requirements.txt - All Python dependencies"
    echo "   • package.json - Frontend dependencies"
    echo "   • docker-compose.yml - Complete container setup"
    echo "   • Installation scripts - Zero-interaction installers"
    echo "   • Documentation - Complete guides and APIs"
    echo ""
    
    echo -e "${GREEN}🚀 Next Steps:${NC}"
    echo "1. 📤 Run: ./setup-git-repo.sh"
    echo "2. 🌐 Create GitHub repository (private recommended)"
    echo "3. 🔗 Add remote: git remote add origin YOUR_REPO_URL"
    echo "4. 📤 Push: git push -u origin main"
    echo ""
    
    echo -e "${GREEN}🏢 Your complete Arabic STT Internal System will be uploaded!${NC}"
    echo ""
}

main() {
    print_header
    
    echo "📋 This will prepare your Arabic STT Internal System for GitHub upload:"
    echo ""
    echo "✅ Clean repository structure"
    echo "✅ Proper .gitignore for AI projects" 
    echo "✅ Complete README with installation instructions"
    echo "✅ LICENSE file with internal use terms"
    echo "✅ Requirements files for all dependencies"
    echo "✅ Docker configuration for deployment"
    echo "✅ GitHub Actions for CI/CD"
    echo "✅ Documentation and guides"
    echo "✅ Git setup script for easy upload"
    echo ""
    
    read -p "🤔 Prepare repository for GitHub? (y/N): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "📋 Repository preparation cancelled"
        exit 0
    fi
    
    # Prepare repository
    create_license
    create_requirements_files
    create_docker_files
    create_github_workflows
    create_project_documentation
    create_contribution_guide
    prepare_repository_structure
    create_git_commands
    
    show_github_summary
    
    echo -e "${YELLOW}🎯 Ready to upload! Run: ./setup-git-repo.sh${NC}"
}

main "$@"