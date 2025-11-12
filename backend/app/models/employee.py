"""Employee database model"""
from sqlalchemy import Column, String, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class Employee(BaseModel):
    """Employee model with skills and productivity patterns"""
    __tablename__ = "employees"

    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    role = Column(String(100), nullable=False)

    # JSON format: {"morning": 0.8, "afternoon": 0.6, "evening": 0.4}
    productivity_periods = Column(JSON, default={"morning": 0.7, "afternoon": 0.7, "evening": 0.5})

    # Relationships
    team = relationship("Team", back_populates="members")
    tasks = relationship("Task", back_populates="assigned_employee", foreign_keys="Task.assigned_to")
    created_tasks = relationship("Task", back_populates="creator", foreign_keys="Task.created_by")
    burnout_metrics = relationship("BurnoutMetric", back_populates="employee", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="employee", cascade="all, delete-orphan")
    skills = relationship("EmployeeSkill", back_populates="employee", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Employee(id={self.id}, name={self.name}, email={self.email})>"
