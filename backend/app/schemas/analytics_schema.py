"""Analytics and Burnout Pydantic schemas"""
from datetime import date, datetime
from typing import Optional, List, Dict
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class BurnoutMetricBase(BaseModel):
    """Base burnout metric schema"""
    employee_id: UUID
    date: date
    hours_worked: float = Field(0.0, ge=0)
    breaks_taken: int = Field(0, ge=0)
    cognitive_load: float = Field(0.5, ge=0, le=1)
    social_interactions: int = Field(0, ge=0)
    task_completion_rate: float = Field(1.0, ge=0, le=1)
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1)


class BurnoutMetricCreate(BurnoutMetricBase):
    """Schema for creating a burnout metric"""
    pass


class BurnoutMetricResponse(BurnoutMetricBase):
    """Schema for burnout metric response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    risk_score: Optional[float]
    created_at: datetime


class BurnoutRiskResponse(BaseModel):
    """Schema for burnout risk analysis"""
    employee_id: UUID
    current_risk_score: float = Field(..., ge=0, le=1)
    risk_level: str  # "low", "medium", "high", "critical"
    factors: Dict[str, float]  # Contributing factors with weights
    recommendations: List[str]
    trend: str  # "improving", "stable", "declining"


class TeamEquityResponse(BaseModel):
    """Schema for team workload equity analysis"""
    team_id: UUID
    team_name: str
    equity_score: float = Field(..., ge=0, le=1)  # 1 = perfect equity
    member_workloads: List[Dict[str, any]]
    recommendations: List[str]


class EmployeeWorkloadDetail(BaseModel):
    """Detailed workload information for an employee"""
    employee_id: UUID
    employee_name: str
    cumulative_load: float
    critical_score: float
    global_score: float
    active_tasks_count: int
    high_priority_tasks_count: int


class ActivityTrackingRequest(BaseModel):
    """Request schema for tracking employee activity"""
    employee_id: UUID
    hours_worked: float = Field(..., ge=0, le=24)
    breaks_taken: int = Field(..., ge=0)
    sentiment: Optional[float] = Field(None, ge=-1, le=1)
    date: Optional[date] = None


class AchievementBase(BaseModel):
    """Base achievement schema"""
    employee_id: UUID
    type: str
    description: str
    impact_score: float = Field(0.5, ge=0, le=1)
    related_task_id: Optional[UUID] = None


class AchievementCreate(AchievementBase):
    """Schema for creating an achievement"""
    pass


class AchievementResponse(AchievementBase):
    """Schema for achievement response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recognized_by_manager: bool
    recognition_note: Optional[str]
    created_at: datetime


class RecognitionRequest(BaseModel):
    """Request schema for manager recognition"""
    achievement_id: UUID
    recognition_note: str
