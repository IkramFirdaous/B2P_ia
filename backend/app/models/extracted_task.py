"""Extracted Task Model - THE DATASET for AI-extracted tasks"""
from sqlalchemy import Column, String, Text, DateTime, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class ExtractedTask(BaseModel):
    """
    THE DATASET: Stores AI-extracted tasks from emails

    This is the core of the email extraction system - each row represents
    a task that Gemini AI extracted from an email. Tasks stay here awaiting
    human review/approval before becoming actual Task objects.

    Flow:
    1. Email arrives → ExtractedEmail created
    2. Gemini AI extracts tasks → ExtractedTask(s) created with approved=False
    3. Human reviews → Clicks approve/reject
    4. If approved → Task created, ExtractedTask.created_task_id set
    """
    __tablename__ = "extracted_tasks"

    # Links
    extracted_email_id = Column(String, ForeignKey("extracted_emails.id"), nullable=False, index=True)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False, index=True)

    # Extracted Information (from Gemini AI)
    task_title = Column(String(500), nullable=False)
    task_description = Column(Text, nullable=False)
    deadline = Column(DateTime)  # Parsed deadline (e.g., "tomorrow" → actual date)
    urgency_level = Column(Integer, default=3)  # 1-5 scale
    priority_score = Column(Float, default=0.5)  # 0-1 calculated priority

    # AI Metadata
    sentiment_score = Column(Float)  # -1 to 1 (negative to positive)
    sentiment_label = Column(String(50))  # "positive", "neutral", "negative"
    confidence_score = Column(Float, default=0.0)  # 0-1 (AI confidence in extraction)

    # Review Status
    approved = Column(Boolean, default=False, index=True)  # Human approved this task?
    reviewed_at = Column(DateTime)  # When human reviewed
    created_task_id = Column(String, ForeignKey("tasks.id"), nullable=True)  # Link to actual Task if approved

    # Relationships
    extracted_email = relationship("ExtractedEmail", back_populates="extracted_tasks")
    employee = relationship("Employee", backref="extracted_tasks")
    created_task = relationship("Task", foreign_keys=[created_task_id], backref="extraction_source")

    def __repr__(self):
        status = "APPROVED" if self.approved else "PENDING"
        return f"<ExtractedTask(id={self.id}, title='{self.task_title[:30]}...', status={status})>"
