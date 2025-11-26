"""Extracted Email database model"""
from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class ExtractionStatus(str, enum.Enum):
    """Status of email extraction"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExtractedEmail(BaseModel):
    """Model for storing processed emails"""
    __tablename__ = "extracted_emails"

    employee_id = Column(String(36), ForeignKey("employees.id"), nullable=False, index=True)
    
    # Email metadata
    email_id = Column(String(255), nullable=False, unique=True, index=True)  # Gmail message ID
    subject = Column(String(500), nullable=True)
    sender = Column(String(255), nullable=False)
    received_at = Column(DateTime, nullable=False)
    
    # Email content
    raw_content = Column(Text, nullable=True)  # Original email text
    
    # Extraction status
    extraction_status = Column(SQLEnum(ExtractionStatus), nullable=False, default=ExtractionStatus.PENDING)
    extraction_error = Column(Text, nullable=True)  # Error message if failed
    extracted_at = Column(DateTime, nullable=True)
    
    # Relationships
    extracted_tasks = relationship("ExtractedTask", back_populates="email", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ExtractedEmail(id={self.id}, subject={self.subject}, status={self.extraction_status})>"

