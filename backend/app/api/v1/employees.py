"""Employee Management API Endpoints"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Employee, Task, EmployeeTeam, Team
from app.schemas.employee_schema import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeWithStats
)


router = APIRouter()


@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(employee_data: EmployeeCreate, db: Session = Depends(get_db)):
    """Create a new employee"""
    # Check if email already exists
    existing = db.query(Employee).filter(Employee.email == employee_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    employee = Employee(**employee_data.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee


@router.get("/employees", response_model=List[EmployeeResponse])
def list_employees(
    team_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List employees with optional filters"""
    query = db.query(Employee)

    if team_id:
        # Filter by team using the many-to-many relationship
        query = query.join(EmployeeTeam).filter(EmployeeTeam.team_id == team_id)

    employees = query.offset(skip).limit(limit).all()
    return employees


@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: UUID, db: Session = Depends(get_db)):
    """Get a specific employee"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


@router.get("/employees/{employee_id}/stats", response_model=EmployeeWithStats)
def get_employee_stats(employee_id: UUID, db: Session = Depends(get_db)):
    """Get employee with statistics"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Calculate statistics
    active_tasks = db.query(Task).filter(
        Task.assigned_to == employee_id,
        Task.status.in_(["pending", "in_progress"])
    ).count()

    completed_tasks = db.query(Task).filter(
        Task.assigned_to == employee_id,
        Task.status == "completed"
    ).count()

    # Calculate current workload
    tasks = db.query(Task).filter(
        Task.assigned_to == employee_id,
        Task.status.in_(["pending", "in_progress"])
    ).all()

    workload = sum(
        (task.estimated_effort or 2.0) * (task.priority_score or 0.5)
        for task in tasks
    )

    # Get burnout risk (would call burnout service)
    burnout_risk = None  # Placeholder

    # Get skills count
    skills_count = len(employee.skills) if employee.skills else 0

    # Build response
    employee_dict = {
        **employee.__dict__,
        "active_tasks_count": active_tasks,
        "completed_tasks_count": completed_tasks,
        "current_workload": workload,
        "burnout_risk_score": burnout_risk,
        "skills_count": skills_count
    }

    return employee_dict


@router.put("/employees/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: UUID,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db)
):
    """Update an employee"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Update fields
    update_data = employee_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(employee, field, value)

    db.commit()
    db.refresh(employee)

    return employee


@router.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: UUID, db: Session = Depends(get_db)):
    """Delete an employee"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(employee)
    db.commit()

    return None


# ============================================================================
# Multi-Team Management Endpoints
# ============================================================================

@router.get("/employees/{employee_id}/teams")
def get_employee_teams(employee_id: UUID, db: Session = Depends(get_db)):
    """Get all teams that an employee belongs to"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Get all team memberships
    employee_teams = db.query(EmployeeTeam).filter(
        EmployeeTeam.employee_id == employee_id
    ).all()

    teams_data = []
    for emp_team in employee_teams:
        team = db.query(Team).filter(Team.id == emp_team.team_id).first()
        if team:
            teams_data.append({
                "id": str(team.id),
                "name": team.name,
                "description": team.description,
                "is_primary": emp_team.is_primary,
                "joined_at": emp_team.joined_at.isoformat() if emp_team.joined_at else None,
                "member_count": len(team.members) if team.members else 0
            })

    return {
        "employee_id": str(employee_id),
        "employee_name": employee.name,
        "teams": teams_data,
        "team_count": len(teams_data)
    }


@router.post("/employees/{employee_id}/teams/{team_id}")
def add_employee_to_team(
    employee_id: UUID,
    team_id: UUID,
    is_primary: bool = False,
    db: Session = Depends(get_db)
):
    """Add an employee to a team"""
    # Verify employee exists
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Verify team exists
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Check if employee is already in this team
    existing = db.query(EmployeeTeam).filter(
        EmployeeTeam.employee_id == employee_id,
        EmployeeTeam.team_id == team_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Employee is already a member of this team"
        )

    # If this is being set as primary, unset other primary teams
    if is_primary:
        db.query(EmployeeTeam).filter(
            EmployeeTeam.employee_id == employee_id,
            EmployeeTeam.is_primary == True
        ).update({"is_primary": False})

    # Create the association
    employee_team = EmployeeTeam(
        employee_id=employee_id,
        team_id=team_id,
        is_primary=is_primary,
        joined_at=datetime.now()
    )
    db.add(employee_team)
    db.commit()
    db.refresh(employee_team)

    return {
        "message": "Employee added to team successfully",
        "employee_id": str(employee_id),
        "team_id": str(team_id),
        "is_primary": is_primary
    }


@router.delete("/employees/{employee_id}/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_employee_from_team(
    employee_id: UUID,
    team_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove an employee from a team"""
    # Find the association
    employee_team = db.query(EmployeeTeam).filter(
        EmployeeTeam.employee_id == employee_id,
        EmployeeTeam.team_id == team_id
    ).first()

    if not employee_team:
        raise HTTPException(
            status_code=404,
            detail="Employee is not a member of this team"
        )

    db.delete(employee_team)
    db.commit()

    return None


@router.put("/employees/{employee_id}/teams/{team_id}/primary")
def set_primary_team(
    employee_id: UUID,
    team_id: UUID,
    db: Session = Depends(get_db)
):
    """Set a team as the employee's primary team"""
    # Verify the employee is a member of this team
    employee_team = db.query(EmployeeTeam).filter(
        EmployeeTeam.employee_id == employee_id,
        EmployeeTeam.team_id == team_id
    ).first()

    if not employee_team:
        raise HTTPException(
            status_code=404,
            detail="Employee is not a member of this team"
        )

    # Unset all other primary teams for this employee
    db.query(EmployeeTeam).filter(
        EmployeeTeam.employee_id == employee_id,
        EmployeeTeam.is_primary == True
    ).update({"is_primary": False})

    # Set this team as primary
    employee_team.is_primary = True
    db.commit()

    return {
        "message": "Primary team updated successfully",
        "employee_id": str(employee_id),
        "primary_team_id": str(team_id)
    }
