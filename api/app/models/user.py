"""
User model
"""

from sqlalchemy import Column, String, Boolean, DateTime, JSON, Enum as SQLEnum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from passlib.context import CryptContext

from app.models.base import SoftDeleteModel

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRole(str, enum.Enum):
    """User role enum"""
    OWNER = "owner"      # Organization owner
    ADMIN = "admin"      # Admin privileges
    MEMBER = "member"    # Standard user
    VIEWER = "viewer"    # Read-only access


class User(SoftDeleteModel):
    """User model"""
    
    __tablename__ = "users"
    
    # Organization relationship
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Authorization
    role = Column(SQLEnum(UserRole), default=UserRole.MEMBER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Email verification
    email_verified_at = Column(DateTime, nullable=True)
    email_verification_token = Column(String(255), nullable=True)
    
    # Password reset
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    
    # Login tracking
    last_login_at = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0)
    
    # User preferences
    preferences = Column(JSON, default=dict)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    media_files = relationship("MediaFile", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    exports = relationship("Export", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.email
    
    @property
    def is_owner(self) -> bool:
        """Check if user is organization owner"""
        return self.role == UserRole.OWNER
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges"""
        return self.role in [UserRole.OWNER, UserRole.ADMIN]
    
    @property
    def can_manage_users(self) -> bool:
        """Check if user can manage other users"""
        return self.role in [UserRole.OWNER, UserRole.ADMIN]
    
    @property
    def can_access_billing(self) -> bool:
        """Check if user can access billing"""
        return self.role in [UserRole.OWNER, UserRole.ADMIN]
    
    def set_password(self, password: str):
        """Set password hash"""
        self.password_hash = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(password, self.password_hash)
    
    def is_email_verified(self) -> bool:
        """Check if email is verified"""
        return self.email_verified_at is not None
    
    def get_preference(self, key: str, default=None):
        """Get user preference"""
        if not self.preferences:
            return default
        return self.preferences.get(key, default)
    
    def set_preference(self, key: str, value):
        """Set user preference"""
        if not self.preferences:
            self.preferences = {}
        self.preferences[key] = value
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login_at = datetime.utcnow()
        self.login_count += 1
    
    @classmethod
    def get_by_email(cls, db, email: str):
        """Get user by email"""
        return db.query(cls).filter(
            cls.email == email.lower(),
            ~cls.is_deleted
        ).first()
    
    @classmethod
    def get_active_by_email(cls, db, email: str):
        """Get active user by email"""
        return db.query(cls).filter(
            cls.email == email.lower(),
            cls.is_active == True,
            ~cls.is_deleted
        ).first()
    
    @classmethod
    def get_by_reset_token(cls, db, token: str):
        """Get user by password reset token"""
        return db.query(cls).filter(
            cls.password_reset_token == token,
            cls.password_reset_expires > datetime.utcnow(),
            ~cls.is_deleted
        ).first()
    
    @classmethod
    def get_by_verification_token(cls, db, token: str):
        """Get user by email verification token"""
        return db.query(cls).filter(
            cls.email_verification_token == token,
            ~cls.is_deleted
        ).first()