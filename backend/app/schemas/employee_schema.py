"""Employee Pydantic schemas"""
from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class EmployeeBase(BaseModel):
    """Base employee schema"""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    role: str = Field(..., min_length=1, max_length=100)
    team_id: Optional[UUID] = None
    productivity_periods: Dict[str, float] = Field(
        default_factory=lambda: {"morning": 0.7, "afternoon": 0.7, "evening": 0.5}
    )


class EmployeeCreate(EmployeeBase):
    """Schema for creating an employee"""
    pass


class EmployeeUpdate(BaseModel):
    """Schema for updating an employee"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, min_length=1, max_length=100)
    team_id: Optional[UUID] = None
    productivity_periods: Optional[Dict[str, float]] = None


class EmployeeResponse(EmployeeBase):
    """Schema for employee response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class EmployeeWithStats(EmployeeResponse):
    """Employee response with statistics"""
    active_tasks_count: int = 0
    completed_tasks_count: int = 0
    current_workload: float = 0.0
    burnout_risk_score: Optional[float] = None
    skills_count: int = 0


class SkillBase(BaseModel):
    """Base skill schema"""
    name: str
    category: str
    description: Optional[str] = None


class SkillCreate(SkillBase):
    """Schema for creating a skill"""
    pass


class SkillResponse(SkillBase):
    """Schema for skill response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime


class EmployeeSkillBase(BaseModel):
    """Base employee skill schema"""
    skill_id: UUID
    level: str


class EmployeeSkillCreate(EmployeeSkillBase):
    """Schema for creating employee skill"""
    employee_id: UUID


class EmployeeSkillResponse(BaseModel):
    """Schema for employee skill response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    employee_id: UUID
    skill_id: UUID
    level: str
    skill_name: Optional[str] = None
    skill_category: Optional[str] = None
