"""
Wellbeing API Endpoints
Provides endpoints for employee wellbeing metrics and recommendations
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models import Employee
from app.services.wellbeing_service import WellbeingService

router = APIRouter(prefix="/wellbeing", tags=["wellbeing"])


@router.get("/summary")
def get_my_wellbeing_summary(
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complete wellbeing summary for the current user.

    Returns:
    - Workload score
    - Stress level
    - Cognitive load
    - Burnout risk
    - Task overlaps
    - Personalized recommendations
    """
    try:
        summary = WellbeingService.get_wellbeing_summary(
            str(current_user.id),
            db
        )
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate wellbeing summary: {str(e)}"
        )


@router.get("/employee/{employee_id}")
def get_employee_wellbeing_summary(
    employee_id: str,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get wellbeing summary for a specific employee.

    Requires: User must be a manager or the employee themselves.
    """
    # Check if user is requesting their own data or is a manager
    if str(current_user.id) != employee_id and current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own wellbeing data unless you're a manager"
        )

    # Verify employee exists
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    try:
        summary = WellbeingService.get_wellbeing_summary(employee_id, db)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate wellbeing summary: {str(e)}"
        )


@router.get("/workload")
def get_my_workload(
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current workload score for the authenticated user."""
    try:
        workload = WellbeingService.calculate_workload_score(
            str(current_user.id),
            db
        )
        return {
            "employee_id": str(current_user.id),
            "workload_score": workload,
            "status": "high" if workload >= 15 else "moderate" if workload >= 8 else "normal"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate workload: {str(e)}"
        )


@router.get("/stress")
def get_my_stress_level(
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current stress level for the authenticated user."""
    try:
        stress = WellbeingService.calculate_stress_level(
            str(current_user.id),
            db
        )
        return {
            "employee_id": str(current_user.id),
            "stress_level": stress,
            "status": "high" if stress >= 0.6 else "moderate" if stress >= 0.4 else "normal"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate stress level: {str(e)}"
        )


@router.get("/burnout-risk")
def get_my_burnout_risk(
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current burnout risk for the authenticated user."""
    try:
        burnout_risk = WellbeingService.calculate_burnout_risk(
            str(current_user.id),
            db
        )
        return {
            "employee_id": str(current_user.id),
            "burnout_risk": burnout_risk,
            "risk_level": "high" if burnout_risk >= 0.7 else "medium" if burnout_risk >= 0.4 else "low",
            "warning": burnout_risk >= 0.7
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate burnout risk: {str(e)}"
        )


@router.get("/overlap-risks")
def get_my_overlap_risks(
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get tasks with overlapping deadlines for the authenticated user.

    Returns conflicts where multiple tasks have deadlines within 24 hours.
    """
    try:
        overlap_analysis = WellbeingService.calculate_overlap_risk(
            str(current_user.id),
            db
        )
        return overlap_analysis
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze deadline overlaps: {str(e)}"
        )


@router.get("/cognitive-load")
def get_my_cognitive_load(
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current cognitive load for the authenticated user."""
    try:
        cognitive_load = WellbeingService.calculate_cognitive_load(
            str(current_user.id),
            db
        )
        return {
            "employee_id": str(current_user.id),
            "cognitive_load": cognitive_load,
            "status": "high" if cognitive_load >= 0.7 else "moderate" if cognitive_load >= 0.5 else "normal"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate cognitive load: {str(e)}"
        )


@router.get("/team/{team_id}")
def get_team_wellbeing(
    team_id: str,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get wellbeing summary for all members of a team.

    Requires: User must be a manager or member of the team.
    """
    from app.models import EmployeeTeam, Team

    # Check if user is a member of this team or is a manager
    is_member = db.query(EmployeeTeam).filter(
        EmployeeTeam.employee_id == current_user.id,
        EmployeeTeam.team_id == team_id
    ).first()

    if not is_member and current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="You can only view wellbeing data for teams you're a member of"
        )

    # Verify team exists
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    try:
        team_summary = WellbeingService.get_team_wellbeing_summary(team_id, db)
        team_summary["team_name"] = team.name
        return team_summary
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate team wellbeing: {str(e)}"
        )
