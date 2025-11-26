"""Email Extraction Pydantic schemas"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


# Request Schemas

class EmailFetchRequest(BaseModel):
    """Request schema for fetching and processing emails"""
    employee_id: UUID
    max_emails: int = Field(default=10, ge=1, le=100)
    unread_only: bool = Field(default=True)
    

class TaskApprovalRequest(BaseModel):
    """Request schema for approving extracted task"""
    extracted_task_id: UUID
    assigned_to: Optional[UUID] = None


# Response Schemas

class ExtractedTaskResponse(BaseModel):
    """Response schema for extracted task"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    extracted_email_id: UUID
    employee_id: UUID
    task_title: str
    task_description: Optional[str]
    deadline: Optional[datetime]
    urgency_level: Optional[int]
    priority_score: Optional[float]
    sentiment_score: Optional[float]
    sentiment_label: Optional[str]
    confidence_score: Optional[float]
    approved: bool
    reviewed_at: Optional[datetime]
    created_task_id: Optional[UUID]
    created_at: datetime


class ExtractedEmailResponse(BaseModel):
    """Response schema for extracted email"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    employee_id: UUID
    email_id: str
    subject: Optional[str]
    sender: str
    received_at: datetime
    extraction_status: str
    extraction_error: Optional[str]
    extracted_at: Optional[datetime]
    created_at: datetime
    extracted_tasks: List[ExtractedTaskResponse] = []


class EmailExtractionStats(BaseModel):
    """Statistics about email extractions"""
    total_emails_processed: int
    total_tasks_extracted: int
    average_sentiment: float
    average_confidence: float
    pending_approvals: int
    approved_tasks: int
    

class OAuthUrlResponse(BaseModel):
    """Response with OAuth URL for Gmail connection"""
    auth_url: str
    state: str


class OAuthCallbackResponse(BaseModel):
    """Response after successful OAuth"""
    success: bool
    message: str
    email_address: Optional[str] = None


class ExtractionJobResponse(BaseModel):
    """Response for extraction job initiation"""
    job_id: str
    message: str
    status: str
    emails_to_process: int


# Dataset Export Schemas

class DatasetTaskItem(BaseModel):
    """Single task item for dataset export"""
    email_subject: str
    email_sender: str
    email_received_at: datetime
    task_title: str
    task_description: Optional[str]
    deadline: Optional[datetime]
    urgency_level: Optional[int]
    sentiment_score: Optional[float]
    sentiment_label: Optional[str]
    confidence_score: Optional[float]
    approved: bool
    

class DatasetExport(BaseModel):
    """Complete dataset for export"""
    employee_id: UUID
    export_date: datetime
    total_items: int
    items: List[DatasetTaskItem]

