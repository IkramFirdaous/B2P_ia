"""Employee Management API Endpoints"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Employee, Task
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
        query = query.filter(Employee.team_id == team_id)

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
