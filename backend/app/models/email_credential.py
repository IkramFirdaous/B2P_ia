"""Email Credential database model for storing OAuth tokens"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class EmailProvider(str, enum.Enum):
    """Email provider enumeration"""
    GMAIL = "gmail"
    OUTLOOK = "outlook"


class EmailCredential(BaseModel):
    """Model for storing OAuth credentials per employee"""
    __tablename__ = "email_credentials"

    employee_id = Column(String(36), ForeignKey("employees.id"), nullable=False, unique=True, index=True)
    email_provider = Column(SQLEnum(EmailProvider), nullable=False, default=EmailProvider.GMAIL)
    
    # OAuth tokens
    access_token = Column(String(2048), nullable=False)
    refresh_token = Column(String(2048), nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    
    # Email address
    email_address = Column(String(255), nullable=True)
    
    # Relationship - if needed later
    # employee = relationship("Employee", back_populates="email_credential")

    def __repr__(self):
        return f"<EmailCredential(employee_id={self.employee_id}, provider={self.email_provider})>"

