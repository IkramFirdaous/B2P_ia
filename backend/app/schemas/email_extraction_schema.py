"""
Pydantic Schemas for Email Extraction API
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============================================================================
# Request Schemas
# ============================================================================

class EmailFetchRequest(BaseModel):
    """Request to fetch and process emails"""
    max_emails: int = Field(default=20, ge=1, le=100, description="Maximum emails to fetch (1-100)")
    unread_only: bool = Field(default=False, description="Only fetch unread emails")

    class Config:
        json_schema_extra = {
            "example": {
                "max_emails": 20,
                "unread_only": True
            }
        }


class TaskApprovalRequest(BaseModel):
    """Request to approve a task and optionally create it"""
    create_task: bool = Field(default=True, description="Create actual Task in system")

    class Config:
        json_schema_extra = {
            "example": {
                "create_task": True
            }
        }


# ============================================================================
# Response Schemas
# ============================================================================

class ExtractionStatusEnum(str, Enum):
    """Email extraction status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExtractedEmailResponse(BaseModel):
    """Response for extracted email"""
    id: str
    email_id: str
    subject: str
    sender: str
    received_at: datetime
    extraction_status: ExtractionStatusEnum
    extraction_error: Optional[str] = None
    extracted_at: Optional[datetime] = None
    tasks_count: int = Field(default=0, description="Number of tasks extracted")
    created_at: datetime

    class Config:
        from_attributes = True


class ExtractedTaskResponse(BaseModel):
    """Response for extracted task (THE DATASET)"""
    id: str
    extracted_email_id: str
    employee_id: str
    task_title: str
    task_description: str
    deadline: Optional[datetime] = None
    urgency_level: int = Field(ge=1, le=5, description="Urgency level (1-5)")
    priority_score: float = Field(ge=0.0, le=1.0, description="Priority score (0-1)")
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Sentiment (-1 to 1)")
    sentiment_label: Optional[str] = None
    confidence_score: float = Field(ge=0.0, le=1.0, description="AI confidence (0-1)")
    approved: bool
    reviewed_at: Optional[datetime] = None
    created_task_id: Optional[str] = None
    created_at: datetime

    # Related email info
    email_subject: Optional[str] = None
    email_sender: Optional[str] = None

    class Config:
        from_attributes = True


class EmailProcessingResponse(BaseModel):
    """Response for email processing operation"""
    success: bool
    message: str
    stats: dict

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Processed 15 emails, extracted 23 tasks",
                "stats": {
                    "emails_fetched": 20,
                    "emails_processed": 15,
                    "emails_failed": 5,
                    "tasks_extracted": 23,
                    "errors": []
                }
            }
        }


class ExtractionStatsResponse(BaseModel):
    """Statistics about email extraction"""
    emails: dict = Field(description="Email statistics")
    tasks: dict = Field(description="Task statistics")

    class Config:
        json_schema_extra = {
            "example": {
                "emails": {
                    "total": 150,
                    "completed": 140,
                    "failed": 5,
                    "processing": 5
                },
                "tasks": {
                    "total": 245,
                    "pending_review": 42,
                    "approved": 203
                }
            }
        }


class TaskApprovalResponse(BaseModel):
    """Response after approving a task"""
    success: bool
    message: str
    task: ExtractedTaskResponse
    created_task_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Task approved and created successfully",
                "task": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "task_title": "Review Q4 report",
                    "approved": True
                },
                "created_task_id": "660e8400-e29b-41d4-a716-446655440001"
            }
        }


class PaginatedTasksResponse(BaseModel):
    """Paginated list of extracted tasks"""
    tasks: List[ExtractedTaskResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        json_schema_extra = {
            "example": {
                "tasks": [],
                "total": 42,
                "page": 1,
                "page_size": 20,
                "total_pages": 3
            }
        }


class PaginatedEmailsResponse(BaseModel):
    """Paginated list of extracted emails"""
    emails: List[ExtractedEmailResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        json_schema_extra = {
            "example": {
                "emails": [],
                "total": 150,
                "page": 1,
                "page_size": 20,
                "total_pages": 8
            }
        }


# ============================================================================
# Dataset Export Schemas
# ============================================================================

class TaskDatasetExport(BaseModel):
    """Schema for exporting task dataset (for ML/analysis)"""
    task_id: str
    task_title: str
    task_description: str
    deadline: Optional[datetime]
    urgency_level: int
    priority_score: float
    sentiment_score: Optional[float]
    sentiment_label: Optional[str]
    confidence_score: float
    email_subject: str
    email_sender: str
    email_received_at: datetime
    approved: bool
    created_at: datetime

    class Config:
        from_attributes = True
