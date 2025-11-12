"""Task database model"""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, Enum, JSON, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class TaskStatus(str, enum.Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskSource(str, enum.Enum):
    """Task source enumeration"""
    EMAIL = "email"
    MEETING = "meeting"
    MANUAL = "manual"
    CALENDAR = "calendar"


class Task(BaseModel):
    """Task model with automatic prioritization"""
    __tablename__ = "tasks"

    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    # Assignment
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)

    # Priority and urgency
    urgency = Column(Integer, nullable=False, default=3)  # 1-5 scale (manager input)
    deadline = Column(DateTime, nullable=True)
    estimated_effort = Column(Float, nullable=True)  # Hours

    # Status
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING)

    # AI-calculated priority score
    priority_score = Column(Float, nullable=True)  # 0-1 scale

    # Dependencies (array of task UUIDs)
    dependencies = Column(JSON, default=list)  # List of UUID strings

    # Source information
    source = Column(Enum(TaskSource), nullable=False, default=TaskSource.MANUAL)
    source_metadata = Column(JSON, nullable=True)  # Email ID, meeting link, etc.

    # Completion tracking
    completed_at = Column(DateTime, nullable=True)
    actual_effort = Column(Float, nullable=True)  # Actual hours spent

    # Relationships
    assigned_employee = relationship("Employee", back_populates="tasks", foreign_keys=[assigned_to])
    creator = relationship("Employee", back_populates="created_tasks", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, status={self.status}, priority={self.priority_score})>"
