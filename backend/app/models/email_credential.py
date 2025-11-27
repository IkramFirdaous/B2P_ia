"""Email Credential Model for Email Integration"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class EmailCredential(BaseModel):
    """
    Stores OAuth credentials for email access
    Used by email extraction worker
    """
    __tablename__ = "email_credentials"

    employee_id = Column(String, ForeignKey("employees.id"), nullable=False, unique=True, index=True)
    email_provider = Column(String, default="gmail")  # gmail, outlook, etc.
    email_address = Column(String, nullable=False, index=True)

    # OAuth tokens
    access_token = Column(String, nullable=False)
    refresh_token = Column(String)
    token_expiry = Column(DateTime)

    # Relationships
    employee = relationship("Employee", back_populates="email_credential")

    def __repr__(self):
        return f"<EmailCredential(employee_id={self.employee_id}, provider={self.email_provider})>"
