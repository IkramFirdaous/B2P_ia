"""Task Pydantic schemas"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.models.task import TaskStatus, TaskSource


class TaskBase(BaseModel):
    """Base task schema"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    urgency: int = Field(3, ge=1, le=5)
    deadline: Optional[datetime] = None
    estimated_effort: Optional[float] = Field(None, ge=0)
    source: TaskSource = TaskSource.MANUAL
    source_metadata: Optional[dict] = None


class TaskCreate(TaskBase):
    """Schema for creating a task"""
    assigned_to: Optional[UUID] = None
    created_by: UUID
    dependencies: List[str] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    urgency: Optional[int] = Field(None, ge=1, le=5)
    deadline: Optional[datetime] = None
    estimated_effort: Optional[float] = Field(None, ge=0)
    status: Optional[TaskStatus] = None
    assigned_to: Optional[UUID] = None
    actual_effort: Optional[float] = Field(None, ge=0)


class TaskResponse(TaskBase):
    """Schema for task response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    assigned_to: Optional[UUID]
    created_by: UUID
    status: TaskStatus
    priority_score: Optional[float]
    dependencies: List[str]
    completed_at: Optional[datetime]
    actual_effort: Optional[float]
    created_at: datetime
    updated_at: datetime


class TaskWithDetails(TaskResponse):
    """Task response with related entity details"""
    assigned_employee_name: Optional[str] = None
    creator_name: str


class TaskExtractRequest(BaseModel):
    """Request schema for extracting tasks from text"""
    source_type: TaskSource
    content: str
    created_by: UUID


class TaskCandidate(BaseModel):
    """Extracted task candidate from NLP"""
    title: str
    description: Optional[str] = None
    urgency: int = 3
    estimated_effort: Optional[float] = None
    deadline: Optional[datetime] = None
    confidence: float = Field(..., ge=0, le=1)
