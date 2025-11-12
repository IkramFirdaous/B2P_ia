"""Analytics and Burnout Detection API Endpoints"""
from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Employee, BurnoutMetric
from app.schemas.analytics_schema import (
    BurnoutMetricCreate, BurnoutMetricResponse, BurnoutRiskResponse,
    TeamEquityResponse, ActivityTrackingRequest, AchievementCreate,
    AchievementResponse, RecognitionRequest
)
from app.services.burnout_detection_service import BurnoutDetectionService
from app.services.workload_balancing_service import WorkloadBalancingService
from app.services.recognition_service import RecognitionService


router = APIRouter()


# Burnout Detection Endpoints

@router.get("/analytics/burnout/{employee_id}", response_model=BurnoutRiskResponse)
def get_burnout_risk(employee_id: UUID, db: Session = Depends(get_db)):
    """Get burnout risk analysis for an employee"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    burnout_service = BurnoutDetectionService(db)
    analysis = burnout_service.get_burnout_analysis(employee_id)

    return analysis


@router.post("/analytics/track-activity", response_model=BurnoutMetricResponse)
def track_activity(request: ActivityTrackingRequest, db: Session = Depends(get_db)):
    """Track daily activity for burnout monitoring"""
    employee = db.query(Employee).filter(Employee.id == request.employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    burnout_service = BurnoutDetectionService(db)
    metric = burnout_service.update_daily_metric(
        employee_id=request.employee_id,
        hours_worked=request.hours_worked,
        breaks_taken=request.breaks_taken,
        sentiment=request.sentiment,
        metric_date=request.date or date.today()
    )

    return metric


@router.get("/analytics/burnout/{employee_id}/metrics", response_model=List[BurnoutMetricResponse])
def get_burnout_metrics(
    employee_id: UUID,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get historical burnout metrics for an employee"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    from datetime import timedelta
    cutoff = date.today() - timedelta(days=days)

    metrics = db.query(BurnoutMetric).filter(
        BurnoutMetric.employee_id == employee_id,
        BurnoutMetric.date >= cutoff
    ).order_by(BurnoutMetric.date.desc()).all()

    return metrics


@router.post("/analytics/burnout/{employee_id}/intervene")
def trigger_interventions(employee_id: UUID, db: Session = Depends(get_db)):
    """Trigger automatic interventions based on burnout risk"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    burnout_service = BurnoutDetectionService(db)
    burnout_service.trigger_interventions(employee_id)

    return {"message": "Interventions triggered based on risk level"}


# Workload Balancing Endpoints

@router.get("/analytics/team/{team_id}/equity", response_model=TeamEquityResponse)
def get_team_equity(team_id: UUID, db: Session = Depends(get_db)):
    """Get workload equity analysis for a team"""
    balance_service = WorkloadBalancingService(db)
    equity = balance_service.calculate_team_equity(team_id)

    return equity


@router.post("/analytics/team/{team_id}/redistribute")
def redistribute_tasks(
    team_id: UUID,
    auto_assign: bool = False,
    db: Session = Depends(get_db)
):
    """Suggest or automatically redistribute tasks for better equity"""
    balance_service = WorkloadBalancingService(db)
    suggestions = balance_service.redistribute_tasks(team_id, auto_assign)

    return {
        "suggestions": suggestions,
        "auto_assigned": auto_assign,
        "count": len(suggestions)
    }


@router.get("/analytics/team/{team_id}/suggest-assignment")
def suggest_assignment(team_id: UUID, db: Session = Depends(get_db)):
    """Suggest which team member should receive the next task"""
    # This would be called when creating a new task
    # For now, returns placeholder
    balance_service = WorkloadBalancingService(db)

    # Would need task details to make proper suggestion
    return {"message": "Use this endpoint when assigning new tasks"}


# Achievement and Recognition Endpoints

@router.post("/analytics/achievements", response_model=AchievementResponse, status_code=status.HTTP_201_CREATED)
def create_achievement(achievement_data: AchievementCreate, db: Session = Depends(get_db)):
    """Record an achievement"""
    recognition_service = RecognitionService(db)
    achievement = recognition_service.track_achievement(
        employee_id=achievement_data.employee_id,
        achievement_type=achievement_data.type,
        description=achievement_data.description,
        impact_score=achievement_data.impact_score,
        related_task_id=achievement_data.related_task_id
    )

    return achievement


@router.get("/analytics/achievements/{employee_id}", response_model=List[AchievementResponse])
def get_employee_achievements(
    employee_id: UUID,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get achievements for an employee"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    recognition_service = RecognitionService(db)
    achievements = recognition_service.get_employee_achievements(employee_id, days)

    return achievements


@router.get("/analytics/achievements/{employee_id}/summary")
def get_achievement_summary(employee_id: UUID, days: int = 30, db: Session = Depends(get_db)):
    """Get achievement summary for an employee"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    recognition_service = RecognitionService(db)
    summary = recognition_service.get_achievement_summary(employee_id, days)

    return summary


@router.post("/analytics/achievements/{achievement_id}/recognize")
def add_recognition(
    achievement_id: UUID,
    request: RecognitionRequest,
    db: Session = Depends(get_db)
):
    """Manager adds recognition to an achievement"""
    recognition_service = RecognitionService(db)
    achievement = recognition_service.manager_recognition(
        achievement_id=request.achievement_id,
        recognition_note=request.recognition_note
    )

    return achievement


@router.get("/analytics/team/{team_id}/unrecognized")
def get_unrecognized_achievements(team_id: UUID, days: int = 7, db: Session = Depends(get_db)):
    """Get achievements that haven't been recognized by manager"""
    recognition_service = RecognitionService(db)
    unrecognized = recognition_service.get_unrecognized_achievements(team_id, days)

    return unrecognized


@router.post("/analytics/employees/{employee_id}/detect-achievements")
def auto_detect_achievements(employee_id: UUID, db: Session = Depends(get_db)):
    """Automatically detect achievements based on completed tasks"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    recognition_service = RecognitionService(db)
    achievements = recognition_service.auto_detect_achievements(employee_id)

    return {
        "detected_achievements": len(achievements),
        "achievements": achievements
    }
