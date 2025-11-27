"""User Session Model for OAuth Authentication"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel


class UserSession(BaseModel):
    """
    User session created after OAuth login
    Stores active sessions with OAuth tokens
    """
    __tablename__ = "user_sessions"

    employee_id = Column(String, ForeignKey("employees.id"), nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    name = Column(String)
    picture = Column(String)  # Profile picture URL from OAuth provider

    # OAuth tokens
    access_token = Column(String, nullable=False)
    refresh_token = Column(String)
    token_expiry = Column(DateTime)

    # Session status
    is_active = Column(Boolean, default=True, index=True)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee = relationship("Employee", back_populates="sessions")

    def __repr__(self):
        return f"<UserSession(email={self.email}, active={self.is_active})>"
