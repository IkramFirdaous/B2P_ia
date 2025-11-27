"""Authentication API Endpoints - Password and Gmail OAuth"""
from datetime import timedelta, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid

from app.core.database import get_db
from app.core.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_active_user
)
from app.core.security import get_current_user
from app.core.config import settings
from app.models import Employee, EmployeeTeam, UserSession, EmailCredential
from app.schemas.auth_schema import (
    UserLogin,
    UserRegister,
    Token,
    UserResponse,
    ChangePassword
)
from app.services.gmail_service import GmailService


router = APIRouter()


# ============================================
# PASSWORD-BASED AUTHENTICATION (EXISTING)
# ============================================

@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user with email/password"""
    existing_user = db.query(Employee).filter(Employee.email == user_data.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_employee = Employee(
        name=user_data.name,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        team_id=user_data.team_id
    )

    db.add(new_employee)
    db.flush()  # Ensure ID is available without committing

    if user_data.team_id:
        primary_team_link = EmployeeTeam(
            employee_id=new_employee.id,
            team_id=user_data.team_id,
            is_primary=True
        )
        db.add(primary_team_link)

    db.commit()
    db.refresh(new_employee)

    return new_employee


@router.post("/auth/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login with email/password"""
    user = db.query(Employee).filter(Employee.email == credentials.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.password_hash or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ============================================
# GMAIL OAUTH AUTHENTICATION (NEW)
# ============================================

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

        # Return auth URL for frontend to redirect
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
                team_id=None,  # No team assigned yet
                password_hash=None  # OAuth users don't have passwords
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
                picture=user_info.get('picture'),
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
                "session_id": str(session.id),
                "employee_id": str(employee_id),
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


# ============================================
# COMMON ENDPOINTS (BOTH AUTH METHODS)
# ============================================

@router.get("/auth/me", response_model=UserResponse)
def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current authenticated user information (works for both password and OAuth)"""
    # Handle both UserSession and Employee types
    if isinstance(current_user, UserSession):
        # OAuth user - return employee info
        return current_user.employee
    else:
        # Password-based user
        return current_user


@router.post("/auth/logout")
def logout(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logout current user (invalidate session)"""
    # If it's an OAuth session, mark it as inactive
    if isinstance(current_user, UserSession):
        current_user.is_active = False
        db.commit()

    return {"message": "Logged out successfully"}


@router.post("/auth/refresh")
def refresh_token(current_user = Depends(get_current_user)):
    """Refresh JWT token (extend session)"""
    # Determine if it's OAuth or password-based
    if isinstance(current_user, UserSession):
        # OAuth session
        access_token = create_access_token(
            data={
                "session_id": str(current_user.id),
                "employee_id": str(current_user.employee_id),
                "email": current_user.email
            }
        )
        return LoginResponse(
            access_token=access_token,
            user={
                "employee_id": str(current_user.employee_id),
                "email": current_user.email,
                "name": current_user.name,
                "picture": current_user.picture
            }
        )
    else:
        # Password-based
        access_token = create_access_token(data={"sub": str(current_user.id)})
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }


@router.post("/auth/change-password")
def change_password(
    password_data: ChangePassword,
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change password (only for password-based auth users)"""
    if not current_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change password for OAuth users"
        )

    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )

    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()

    return {"message": "Password changed successfully"}
