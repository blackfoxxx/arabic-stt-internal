FROM python:3.11-slim

# Install system dependencies including ML libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    git \
    curl \
    libsndfile1 \
    libpq-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for models and temp processing
RUN mkdir -p /app/models /tmp/processing

# Create non-root user
RUN useradd -m -u 1000 worker && \
    chown -R worker:worker /app /tmp/processing
USER worker

# Health check
HEALTHCHECK --interval=60s --timeout=30s --start-period=120s --retries=3 \
    CMD celery -A app.celery_app inspect ping || exit 1

# Start Celery worker
CMD ["celery", "-A", "app.celery_app", "worker", "--loglevel=info", "--concurrency=2"]