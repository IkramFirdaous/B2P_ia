"""Security utilities for authentication and authorization"""
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme (for password-based auth)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login", auto_error=False)

# HTTP Bearer scheme (for OAuth tokens)
http_bearer = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token

    Args:
        data: Data to encode in the token (e.g., {"sub": user_id})
        expires_delta: Token expiration time
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token

    Returns the payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    oauth_token: Optional[str] = Depends(oauth2_scheme),
    bearer_credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    db: Session = Depends(get_db)
) -> Union["UserSession", "Employee"]:
    """
    Dependency for getting the current authenticated user
    Supports both OAuth sessions and password-based Employee auth

    Usage:
        @app.get("/me")
        def read_current_user(current_user = Depends(get_current_user)):
            return current_user
    """
    from app.models import UserSession, Employee

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Get token from either scheme
    token = None
    if bearer_credentials:
        token = bearer_credentials.credentials
    elif oauth_token:
        token = oauth_token

    if not token:
        raise credentials_exception

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # Check if it's an OAuth session token (has session_id)
    session_id = payload.get("session_id")
    if session_id:
        # OAuth session
        session = db.query(UserSession).filter(
            UserSession.id == session_id,
            UserSession.is_active == True
        ).first()

        if not session:
            raise credentials_exception

        # Update last activity
        session.last_activity = datetime.utcnow()
        db.commit()

        # Return the Employee, not the session
        employee = db.query(Employee).filter(Employee.id == session.employee_id).first()
        if not employee:
            raise credentials_exception

        return employee
    else:
        # Password-based authentication (Employee)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        user = db.query(Employee).filter(Employee.id == user_id).first()
        if user is None:
            raise credentials_exception

        return user


def check_permissions(required_role: str):
    """
    Dependency for checking user permissions

    Usage:
        @app.delete("/users/{user_id}")
        def delete_user(
            user_id: str,
            current_user = Depends(get_current_user),
            _: None = Depends(check_permissions("admin"))
        ):
            # Only admins can access this endpoint
    """
    async def permission_checker(current_user = Depends(get_current_user)):
        # Get role from either UserSession or Employee
        if hasattr(current_user, 'employee'):
            # It's a UserSession
            user_role = current_user.employee.role if current_user.employee else "user"
        elif hasattr(current_user, 'role'):
            # It's an Employee
            user_role = current_user.role
        else:
            user_role = "user"

        if user_role != required_role and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        return None

    return permission_checker
