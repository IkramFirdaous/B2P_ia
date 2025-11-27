"""User Session Model - Stores authenticated user sessions"""
from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime
from app.models.base import BaseModel


class UserSession(BaseModel):
    """User session model for OAuth authentication"""
    __tablename__ = "user_sessions"
    
    # id, created_at, updated_at inherited from BaseModel
    employee_id = Column(String(36), nullable=False, index=True)
    email = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    picture = Column(String(500), nullable=True)  # Profile picture URL
    
    # OAuth tokens
    access_token = Column(String(2048), nullable=False)
    refresh_token = Column(String(512), nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    
    # Session management
    is_active = Column(Boolean, default=True)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

