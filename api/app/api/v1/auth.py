"""
Authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid
import secrets
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth import auth_manager, token_manager, get_current_user, security
from app.models.user import User, UserRole
from app.models.organization import Organization, SubscriptionStatus
from app.services.email_service import send_verification_email, send_password_reset_email

router = APIRouter()


# Request/Response schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    organization_name: str = Field(..., min_length=1, max_length=255)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: UserRole
    is_active: bool
    email_verified_at: Optional[datetime]
    last_login_at: Optional[datetime]
    organization_id: str
    organization_name: str
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserResponse


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """User login"""
    
    # Authenticate user
    user = auth_manager.authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if organization is active
    if not user.organization.is_active and not user.organization.is_trial:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization subscription is inactive"
        )
    
    # Create tokens
    tokens = auth_manager.create_user_tokens(user)
    
    # Prepare user response
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        is_active=user.is_active,
        email_verified_at=user.email_verified_at,
        last_login_at=user.last_login_at,
        organization_id=str(user.organization_id),
        organization_name=user.organization.name
    )
    
    return LoginResponse(
        **tokens,
        user=user_response
    )


@router.post("/register", response_model=LoginResponse)
async def register(
    request: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """User registration"""
    
    # Check if email already exists
    existing_user = User.get_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create organization
    org_slug = request.organization_name.lower().replace(" ", "-").replace("_", "-")
    org_slug = f"{org_slug}-{uuid.uuid4().hex[:8]}"  # Ensure uniqueness
    
    organization = Organization(
        name=request.organization_name,
        slug=org_slug,
        subscription_status=SubscriptionStatus.TRIAL
    )
    db.add(organization)
    db.flush()
    
    # Create user
    user = User(
        organization_id=organization.id,
        email=request.email.lower(),
        first_name=request.first_name,
        last_name=request.last_name,
        role=UserRole.OWNER,  # First user is owner
        is_active=True
    )
    user.set_password(request.password)
    
    # Generate email verification token
    verification_token = token_manager.create_email_verification_token(request.email)
    user.email_verification_token = verification_token
    
    db.add(user)
    db.commit()
    db.refresh(user)
    db.refresh(organization)
    
    # Send verification email
    background_tasks.add_task(
        send_verification_email,
        user.email,
        user.first_name or "User", 
        verification_token
    )
    
    # Create tokens
    tokens = auth_manager.create_user_tokens(user)
    
    # Prepare response
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        is_active=user.is_active,
        email_verified_at=user.email_verified_at,
        last_login_at=user.last_login_at,
        organization_id=str(user.organization_id),
        organization_name=organization.name
    )
    
    return LoginResponse(
        **tokens,
        user=user_response
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    
    tokens = auth_manager.refresh_access_token(db, request.refresh_token)
    
    return RefreshResponse(**tokens)


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    
    user = User.get_by_email(db, request.email)
    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    user.password_reset_token = reset_token
    user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
    
    db.commit()
    
    # Send reset email
    background_tasks.add_task(
        send_password_reset_email,
        user.email,
        user.first_name or "User",
        reset_token
    )
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """Reset password with token"""
    
    user = User.get_by_reset_token(db, request.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update password
    user.set_password(request.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    
    db.commit()
    
    return {"message": "Password reset successfully"}


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    
    # Verify current password
    if not current_user.verify_password(request.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid current password"
        )
    
    # Update password
    current_user.set_password(request.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/verify-email")
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """Verify email address"""
    
    try:
        email = token_manager.verify_email_token(token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    user = User.get_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    
    if user.email_verification_token != token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    # Mark email as verified
    user.email_verified_at = datetime.utcnow()
    user.email_verification_token = None
    
    db.commit()
    
    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
async def resend_verification(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resend email verification"""
    
    if current_user.is_email_verified():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Generate new verification token
    verification_token = token_manager.create_email_verification_token(current_user.email)
    current_user.email_verification_token = verification_token
    
    db.commit()
    
    # Send verification email
    background_tasks.add_task(
        send_verification_email,
        current_user.email,
        current_user.first_name or "User",
        verification_token
    )
    
    return {"message": "Verification email sent"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        is_active=current_user.is_active,
        email_verified_at=current_user.email_verified_at,
        last_login_at=current_user.last_login_at,
        organization_id=str(current_user.organization_id),
        organization_name=current_user.organization.name
    )


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Logout user (invalidate token)"""
    
    # In a production system, you would add the token to a blacklist
    # For now, we'll just return success since tokens will expire naturally
    
    return {"message": "Logged out successfully"}