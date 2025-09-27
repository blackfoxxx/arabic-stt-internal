"""
Organization model
"""

from sqlalchemy import Column, String, DateTime, JSON, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship
import enum

from app.models.base import SoftDeleteModel


class SubscriptionStatus(str, enum.Enum):
    """Subscription status enum"""
    TRIAL = "trial"
    ACTIVE = "active" 
    CANCELED = "canceled"
    SUSPENDED = "suspended"
    PAST_DUE = "past_due"


class Organization(SoftDeleteModel):
    """Organization model"""
    
    __tablename__ = "organizations"
    
    # Basic info
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    
    # Settings
    settings = Column(JSON, default=dict)
    
    # Subscription
    subscription_status = Column(
        SQLEnum(SubscriptionStatus), 
        default=SubscriptionStatus.TRIAL,
        nullable=False
    )
    subscription_expires_at = Column(DateTime, nullable=True)
    
    # Stripe integration
    stripe_customer_id = Column(String(255), nullable=True, unique=True)
    stripe_subscription_id = Column(String(255), nullable=True, unique=True)
    
    # Usage limits
    monthly_minutes_limit = Column(Integer, default=60)  # Free tier default
    storage_limit_gb = Column(Integer, default=1)
    
    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="organization", cascade="all, delete-orphan")
    media_files = relationship("MediaFile", back_populates="organization", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="organization", cascade="all, delete-orphan")
    transcripts = relationship("Transcript", back_populates="organization", cascade="all, delete-orphan")
    webhooks = relationship("Webhook", back_populates="organization", cascade="all, delete-orphan")
    usage_records = relationship("UsageRecord", back_populates="organization", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="organization", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name={self.name}, slug={self.slug})>"
    
    @property
    def is_active(self) -> bool:
        """Check if organization has active subscription"""
        return self.subscription_status == SubscriptionStatus.ACTIVE
    
    @property
    def is_trial(self) -> bool:
        """Check if organization is on trial"""
        return self.subscription_status == SubscriptionStatus.TRIAL
    
    def get_setting(self, key: str, default=None):
        """Get organization setting"""
        if not self.settings:
            return default
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value):
        """Set organization setting"""
        if not self.settings:
            self.settings = {}
        self.settings[key] = value
    
    @classmethod
    def get_by_slug(cls, db, slug: str):
        """Get organization by slug"""
        return db.query(cls).filter(cls.slug == slug, ~cls.is_deleted).first()
    
    @classmethod
    def get_by_stripe_customer_id(cls, db, customer_id: str):
        """Get organization by Stripe customer ID"""
        return db.query(cls).filter(
            cls.stripe_customer_id == customer_id,
            ~cls.is_deleted
        ).first()