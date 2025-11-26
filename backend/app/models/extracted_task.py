"""Extracted Task database model - the dataset"""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class ExtractedTask(BaseModel):
    """
    Model for storing extracted tasks from emails (the dataset)
    This serves as the structured dataset for analysis and review
    """
    __tablename__ = "extracted_tasks"

    # Foreign keys
    extracted_email_id = Column(String(36), ForeignKey("extracted_emails.id"), nullable=False, index=True)
    employee_id = Column(String(36), ForeignKey("employees.id"), nullable=False, index=True)
    
    # Extracted task information
    task_title = Column(String(500), nullable=False)
    task_description = Column(Text, nullable=True)
    
    # Extracted metadata
    deadline = Column(DateTime, nullable=True)
    urgency_level = Column(Integer, nullable=True)  # 1-5 scale
    priority_score = Column(Float, nullable=True)  # 0-1 scale
    
    # Sentiment analysis
    sentiment_score = Column(Float, nullable=True)  # -1 to 1 scale
    sentiment_label = Column(String(50), nullable=True)  # positive, neutral, negative
    
    # Confidence from LLM
    confidence_score = Column(Float, nullable=True)  # 0-1 scale
    
    # Review and approval
    approved = Column(Boolean, default=False, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)
    
    # Link to actual created task (if approved)
    created_task_id = Column(String(36), ForeignKey("tasks.id"), nullable=True)
    
    # Relationships
    email = relationship("ExtractedEmail", back_populates="extracted_tasks")

    def __repr__(self):
        return f"<ExtractedTask(id={self.id}, title={self.task_title}, approved={self.approved})>"

