"""Authentication API Endpoints - Global OAuth Gmail Login"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token, get_current_user
from app.models.user_session import UserSession
from app.models.email_credential import EmailCredential
from app.models.employee import Employee
from app.services.gmail_service import GmailService
from pydantic import BaseModel


router = APIRouter()


class LoginResponse(BaseModel):
    """Login response with JWT token"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserInfo(BaseModel):
    """Current user information"""
    employee_id: str
    email: str
    name: Optional[str]
    picture: Optional[str]


@router.get("/auth/login/gmail")
def initiate_gmail_login(db: Session = Depends(get_db)):
    """
    Initiate Gmail OAuth login flow
    This is the entry point for authentication
    """
    gmail_service = GmailService(db)
    
    try:
        # Generate a temporary state for OAuth
        state = str(uuid.uuid4())
        
        # Get OAuth URL (we'll use employee_id = state temporarily)
        auth_url, _ = gmail_service.get_authorization_url(state)
        
        # Redirect to Google OAuth
        return {
            "auth_url": auth_url,
            "message": "Redirect user to auth_url"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate login: {str(e)}"
        )


@router.get("/auth/callback")
@router.get("/auth/google/callback")  # Alternative path for Google redirects
def gmail_auth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Handle Gmail OAuth callback
    Creates or updates user session and returns JWT token
    """
    gmail_service = GmailService(db)
    
    try:
        # Exchange code for tokens
        credentials = gmail_service.exchange_code_for_token(code)
        
        # Get user info from Gmail API
        user_info = gmail_service.get_user_info(credentials)
        email = user_info.get('emailAddress', '')
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not retrieve email from Google"
            )
        
        # Check if employee exists with this email
        employee = db.query(Employee).filter(Employee.email == email).first()
        
        if not employee:
            # Create new employee (auto-registration)
            employee = Employee(
                id=str(uuid.uuid4()),
                email=email,
                name=user_info.get('name', email.split('@')[0]),
                role="employee",  # Default role
                team_id=None  # No team assigned yet
            )
            db.add(employee)
            db.commit()
            db.refresh(employee)
        
        employee_id = str(employee.id)
        
        # Store/update email credentials for email extraction
        email_credential = db.query(EmailCredential).filter(
            EmailCredential.employee_id == employee_id
        ).first()
        
        if email_credential:
            # Update existing
            email_credential.access_token = credentials.token
            email_credential.refresh_token = credentials.refresh_token
            email_credential.token_expiry = credentials.expiry
            email_credential.email_address = email
        else:
            # Create new
            email_credential = EmailCredential(
                id=str(uuid.uuid4()),
                employee_id=employee_id,
                email_provider="gmail",
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_expiry=credentials.expiry,
                email_address=email
            )
            db.add(email_credential)
        
        # Create or update user session
        session = db.query(UserSession).filter(
            UserSession.employee_id == employee_id,
            UserSession.is_active == True
        ).first()
        
        if session:
            # Update existing session
            session.access_token = credentials.token
            session.refresh_token = credentials.refresh_token
            session.token_expiry = credentials.expiry
            session.last_activity = datetime.utcnow()
        else:
            # Create new session
            session = UserSession(
                id=str(uuid.uuid4()),
                employee_id=employee_id,
                email=email,
                name=employee.name,
                picture=None,  # Could extract from Google profile if needed
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_expiry=credentials.expiry,
                is_active=True
            )
            db.add(session)
        
        db.commit()
        db.refresh(session)
        
        # Create JWT token
        access_token = create_access_token(
            data={
                "session_id": session.id,
                "employee_id": employee_id,
                "email": email
            }
        )
        
        # Redirect to frontend with token
        frontend_url = settings.BACKEND_CORS_ORIGINS[0] if settings.BACKEND_CORS_ORIGINS else "http://localhost:3000"
        redirect_url = f"{frontend_url}/auth/callback?token={access_token}"
        
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        print(f"[ERROR] OAuth callback error: {str(e)}")
        frontend_url = settings.BACKEND_CORS_ORIGINS[0] if settings.BACKEND_CORS_ORIGINS else "http://localhost:3000"
        error_url = f"{frontend_url}/login?error={str(e)}"
        return RedirectResponse(url=error_url)


@router.get("/auth/me", response_model=UserInfo)
def get_current_user_info(
    current_user: UserSession = Depends(get_current_user)
):
    """Get current authenticated user information"""
    return UserInfo(
        employee_id=current_user.employee_id,
        email=current_user.email,
        name=current_user.name,
        picture=current_user.picture
    )


@router.post("/auth/logout")
def logout(
    current_user: UserSession = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout current user (invalidate session)"""
    current_user.is_active = False
    db.commit()
    
    return {"message": "Logged out successfully"}


@router.post("/auth/refresh")
def refresh_token(
    current_user: UserSession = Depends(get_current_user)
):
    """Refresh JWT token (extend session)"""
    access_token = create_access_token(
        data={
            "session_id": current_user.id,
            "employee_id": current_user.employee_id,
            "email": current_user.email
        }
    )
    
    return LoginResponse(
        access_token=access_token,
        user={
            "employee_id": current_user.employee_id,
            "email": current_user.email,
            "name": current_user.name,
            "picture": current_user.picture
        }
    )

