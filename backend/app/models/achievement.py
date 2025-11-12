"""Achievement database model"""
from sqlalchemy import Column, String, Text, Float, Boolean, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class AchievementType(str, enum.Enum):
    """Achievement type enumeration"""
    DELIVERABLE = "deliverable"
    INNOVATION = "innovation"
    CLIENT_FEEDBACK = "client_feedback"
    COLLABORATION = "collaboration"
    LEARNING = "learning"


class Achievement(BaseModel):
    """Employee achievements and recognition tracking"""
    __tablename__ = "achievements"

    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    type = Column(Enum(AchievementType), nullable=False)

    description = Column(Text, nullable=False)

    # Impact scoring (0-1 scale)
    impact_score = Column(Float, nullable=False, default=0.5)

    # Recognition tracking
    recognized_by_manager = Column(Boolean, default=False)
    recognition_note = Column(Text, nullable=True)

    # Related task (if applicable)
    related_task_id = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    employee = relationship("Employee", back_populates="achievements")

    def __repr__(self):
        return f"<Achievement(id={self.id}, type={self.type}, employee_id={self.employee_id})>"
