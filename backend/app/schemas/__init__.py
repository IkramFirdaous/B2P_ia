"""Pydantic Schemas"""
from .task_schema import (
    TaskBase, TaskCreate, TaskUpdate, TaskResponse,
    TaskWithDetails, TaskExtractRequest, TaskCandidate
)
from .employee_schema import (
    EmployeeBase, EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    EmployeeWithStats, SkillBase, SkillCreate, SkillResponse,
    EmployeeSkillBase, EmployeeSkillCreate, EmployeeSkillResponse
)
from .analytics_schema import (
    BurnoutMetricBase, BurnoutMetricCreate, BurnoutMetricResponse,
    BurnoutRiskResponse, TeamEquityResponse, EmployeeWorkloadDetail,
    ActivityTrackingRequest, AchievementBase, AchievementCreate,
    AchievementResponse, RecognitionRequest
)

__all__ = [
    # Task schemas
    "TaskBase", "TaskCreate", "TaskUpdate", "TaskResponse",
    "TaskWithDetails", "TaskExtractRequest", "TaskCandidate",
    # Employee schemas
    "EmployeeBase", "EmployeeCreate", "EmployeeUpdate", "EmployeeResponse",
    "EmployeeWithStats", "SkillBase", "SkillCreate", "SkillResponse",
    "EmployeeSkillBase", "EmployeeSkillCreate", "EmployeeSkillResponse",
    # Analytics schemas
    "BurnoutMetricBase", "BurnoutMetricCreate", "BurnoutMetricResponse",
    "BurnoutRiskResponse", "TeamEquityResponse", "EmployeeWorkloadDetail",
    "ActivityTrackingRequest", "AchievementBase", "AchievementCreate",
    "AchievementResponse", "RecognitionRequest",
]
