"""Extracted Email Model for Email Extraction System"""
from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class ExtractionStatus(str, enum.Enum):
    """Status of email extraction process"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExtractedEmail(BaseModel):
    """
    Stores emails that have been fetched from Gmail and processed
    Each email can contain multiple extracted tasks
    """
    __tablename__ = "extracted_emails"

    employee_id = Column(String, ForeignKey("employees.id"), nullable=False, index=True)
    email_id = Column(String, unique=True, nullable=False, index=True)  # Gmail message ID

    # Email metadata
    subject = Column(String(500), nullable=False)
    sender = Column(String(255), nullable=False)
    received_at = Column(DateTime, nullable=False)
    raw_content = Column(Text)  # Email body content (truncated to 10,000 chars)

    # Extraction status
    extraction_status = Column(SQLEnum(ExtractionStatus), default=ExtractionStatus.PENDING, index=True)
    extraction_error = Column(Text)  # Error message if extraction failed
    extracted_at = Column(DateTime)  # When AI extraction completed

    # Relationships
    employee = relationship("Employee", backref="extracted_emails")
    extracted_tasks = relationship("ExtractedTask", back_populates="extracted_email", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ExtractedEmail(id={self.id}, subject='{self.subject[:30]}...', status={self.extraction_status})>"
