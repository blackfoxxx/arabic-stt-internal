"""
Configuration management for Arabic STT SaaS
"""

from typing import List, Optional
from functools import lru_cache
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    DEBUG: bool = Field(default=False, description="Debug mode")
    ENVIRONMENT: str = Field(default="development", description="Environment name")
    LOG_LEVEL: str = Field(default="info", description="Logging level")
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS allowed origins"
    )
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/arabic_stt",
        description="Database connection URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, description="Database max overflow connections")
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    REDIS_MAX_CONNECTIONS: int = Field(default=10, description="Redis max connections")
    
    # MinIO/S3 Storage
    MINIO_ENDPOINT: str = Field(default="localhost:9000", description="MinIO endpoint")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", description="MinIO access key")
    MINIO_SECRET_KEY: str = Field(default="minioadmin", description="MinIO secret key")
    MINIO_SECURE: bool = Field(default=False, description="MinIO use SSL")
    MINIO_REGION: str = Field(default="us-east-1", description="MinIO region")
    
    # Storage buckets
    MEDIA_BUCKET: str = Field(default="arabic-stt-media", description="Media files bucket")
    PROCESSED_BUCKET: str = Field(default="arabic-stt-processed", description="Processed files bucket")
    EXPORTS_BUCKET: str = Field(default="arabic-stt-exports", description="Export files bucket")
    MODELS_BUCKET: str = Field(default="arabic-stt-models", description="ML models bucket")
    
    # JWT Settings
    JWT_SECRET: str = Field(default="your-super-secret-jwt-key", description="JWT secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiry (minutes)")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiry (days)")
    
    # Encryption
    ENCRYPT_KEY: str = Field(default="your-32-byte-encryption-key-here", description="Encryption key")
    
    # Celery/Worker Configuration
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/0", 
        description="Celery result backend URL"
    )
    MAX_CONCURRENT_JOBS: int = Field(default=2, description="Max concurrent transcription jobs")
    
    # AI/ML Configuration
    DEFAULT_ASR_MODEL: str = Field(default="large-v3", description="Default ASR model")
    HUGGINGFACE_TOKEN: Optional[str] = Field(default=None, description="HuggingFace API token")
    GPU_ENABLED: bool = Field(default=False, description="Enable GPU acceleration")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="API rate limit per minute")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, description="API rate limit per hour")
    RATE_LIMIT_PER_DAY: int = Field(default=10000, description="API rate limit per day")
    
    # File Upload Limits
    MAX_FILE_SIZE_MB: int = Field(default=500, description="Max file size in MB")
    MAX_DURATION_MINUTES: int = Field(default=180, description="Max audio duration in minutes")
    ALLOWED_MIME_TYPES: List[str] = Field(
        default=[
            "audio/mpeg", "audio/wav", "audio/mp4", "audio/flac", "audio/ogg",
            "video/mp4", "video/avi", "video/mov", "video/wmv", "video/flv"
        ],
        description="Allowed file MIME types"
    )
    
    # External Services
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None, description="Stripe secret key")
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(default=None, description="Stripe webhook secret")
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")
    
    # Email Configuration (for notifications)
    SMTP_HOST: Optional[str] = Field(default=None, description="SMTP host")
    SMTP_PORT: int = Field(default=587, description="SMTP port")
    SMTP_USERNAME: Optional[str] = Field(default=None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP password")
    SMTP_USE_TLS: bool = Field(default=True, description="SMTP use TLS")
    FROM_EMAIL: str = Field(default="noreply@arabicstt.com", description="From email address")
    
    # Arabic Processing Settings
    ARABIC_FONT_PATH: str = Field(default="/fonts/NotoSansArabic.ttf", description="Arabic font path")
    DEFAULT_LANGUAGE: str = Field(default="ar", description="Default language code")
    SUPPORTED_DIALECTS: List[str] = Field(
        default=["ar", "ar-IQ", "ar-EG", "ar-SA", "ar-MA"],
        description="Supported Arabic dialects"
    )
    
    # Quality & Performance
    MIN_CONFIDENCE_SCORE: float = Field(default=0.6, description="Minimum confidence score")
    MAX_WER_THRESHOLD: float = Field(default=0.3, description="Maximum Word Error Rate threshold")
    PROCESSING_TIMEOUT_MINUTES: int = Field(default=30, description="Processing timeout (minutes)")
    
    # Webhook Configuration
    WEBHOOK_TIMEOUT_SECONDS: int = Field(default=30, description="Webhook timeout")
    WEBHOOK_RETRY_ATTEMPTS: int = Field(default=3, description="Webhook retry attempts")
    WEBHOOK_RETRY_DELAY_SECONDS: int = Field(default=60, description="Webhook retry delay")
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, description="Enable Prometheus metrics")
    METRICS_PORT: int = Field(default=9090, description="Metrics server port")
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [x.strip() for x in v.split(",")]
        return v
    
    @validator("JWT_SECRET")
    def validate_jwt_secret(cls, v):
        if len(v) < 32:
            raise ValueError("JWT secret must be at least 32 characters long")
        return v
    
    @validator("ENCRYPT_KEY")
    def validate_encrypt_key(cls, v):
        if len(v) < 32:
            raise ValueError("Encryption key must be at least 32 characters long")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings"""
    return Settings()


# Export settings instance
settings = get_settings()