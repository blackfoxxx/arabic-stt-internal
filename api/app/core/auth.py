"""
Authentication and authorization utilities
"""

from jose import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uuid
import secrets

from app.core.config import get_settings
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.api_key import ApiKey

settings = get_settings()
security = HTTPBearer()


class TokenManager:
    """JWT token management"""
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        self.refresh_token_expire = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    def create_access_token(self, user_id: str, organization_id: str, role: str) -> str:
        """Create access token"""
        payload = {
            "sub": user_id,
            "org_id": organization_id,
            "role": role,
            "type": "access",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + self.access_token_expire,
            "jti": secrets.token_urlsafe(32)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create refresh token"""
        payload = {
            "sub": user_id,
            "type": "refresh",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + self.refresh_token_expire,
            "jti": secrets.token_urlsafe(32)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": True, "verify_iat": True}
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def create_email_verification_token(self, email: str) -> str:
        """Create email verification token"""
        payload = {
            "email": email,
            "type": "email_verification",
            "exp": datetime.now(timezone.utc) + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_email_token(self, token: str) -> str:
        """Verify email verification token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "email_verification":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token type"
                )
            return payload["email"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email verification token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email verification token"
            )


class AuthManager:
    """Authentication manager"""
    
    def __init__(self):
        self.token_manager = TokenManager()
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password"""
        user = User.get_active_by_email(db, email)
        if not user or not user.verify_password(password):
            return None
        
        # Update login tracking
        user.update_last_login()
        db.commit()
        
        return user
    
    def create_user_tokens(self, user: User) -> Dict[str, str]:
        """Create access and refresh tokens for user"""
        access_token = self.token_manager.create_access_token(
            user_id=str(user.id),
            organization_id=str(user.organization_id),
            role=user.role.value
        )
        
        refresh_token = self.token_manager.create_refresh_token(
            user_id=str(user.id)
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    def refresh_access_token(self, db: Session, refresh_token: str) -> Dict[str, str]:
        """Refresh access token"""
        payload = self.token_manager.verify_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload["sub"]
        user = db.query(User).filter(
            User.id == user_id,
            User.is_active == True,
            ~User.is_deleted
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token = self.token_manager.create_access_token(
            user_id=str(user.id),
            organization_id=str(user.organization_id),
            role=user.role.value
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }


# Global instances
token_manager = TokenManager()
auth_manager = AuthManager()


# Dependency functions
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = token_manager.verify_token(token)
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = payload["sub"]
    user = db.query(User).filter(
        User.id == user_id,
        User.is_active == True,
        ~User.is_deleted
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_role(required_role: UserRole):
    """Require specific user role"""
    def role_checker(current_user: User = Depends(get_current_active_user)):
        user_role_hierarchy = {
            UserRole.VIEWER: 1,
            UserRole.MEMBER: 2,
            UserRole.ADMIN: 3,
            UserRole.OWNER: 4
        }
        
        if user_role_hierarchy.get(current_user.role, 0) < user_role_hierarchy.get(required_role, 5):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return role_checker


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Require admin role"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_owner(current_user: User = Depends(get_current_active_user)) -> User:
    """Require owner role"""
    if not current_user.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner access required"
        )
    return current_user


async def verify_api_key(
    api_key: str,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Verify API key and return associated user"""
    # API keys have format: "ak_" + prefix + hash
    if not api_key.startswith("ak_"):
        return None
    
    try:
        # Extract prefix (first 8 chars after ak_)
        prefix = api_key[3:11]
        
        # Find API key by prefix
        key_record = db.query(ApiKey).filter(
            ApiKey.key_prefix == prefix,
            ApiKey.is_active == True
        ).first()
        
        if not key_record:
            return None
        
        # Verify full key hash
        import hashlib
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        if key_hash != key_record.key_hash:
            return None
        
        # Check expiration
        if key_record.expires_at and key_record.expires_at < datetime.utcnow():
            return None
        
        # Update last used
        key_record.last_used_at = datetime.utcnow()
        db.commit()
        
        return key_record.user
        
    except Exception:
        return None


# Optional authentication (for public endpoints that can benefit from user context)
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        
        # Try API key first
        user = await verify_api_key(token, db)
        if user:
            return user
        
        # Try JWT token
        payload = token_manager.verify_token(token)
        if payload.get("type") != "access":
            return None
        
        user_id = payload["sub"]
        user = db.query(User).filter(
            User.id == user_id,
            User.is_active == True,
            ~User.is_deleted
        ).first()
        
        return user
        
    except Exception:
        return None