"""Task Management API Endpoints"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Task, Employee
from app.schemas.task_schema import (
    TaskCreate, TaskUpdate, TaskResponse, TaskWithDetails,
    TaskExtractRequest, TaskCandidate
)
from app.services.task_prioritization_service import TaskPrioritizationService
from app.services.task_extraction_service import TaskExtractionService


router = APIRouter()


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task"""
    # Create task
    task = Task(**task_data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)

    # Calculate priority score if assigned
    if task.assigned_to:
        priority_service = TaskPrioritizationService(db)
        priority_service.update_task_priority(task.id, task.assigned_to)

    return task


@router.get("/tasks", response_model=List[TaskResponse])
def list_tasks(
    assigned_to: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List tasks with optional filters"""
    query = db.query(Task)

    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)

    if status:
        query = query.filter(Task.status == status)

    tasks = query.offset(skip).limit(limit).all()
    return tasks


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: UUID, db: Session = Depends(get_db)):
    """Get a specific task"""
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: UUID, task_data: TaskUpdate, db: Session = Depends(get_db)):
    """Update a task"""
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    # Recalculate priority if relevant fields changed
    if task.assigned_to and any(f in update_data for f in ["urgency", "deadline", "estimated_effort"]):
        priority_service = TaskPrioritizationService(db)
        priority_service.update_task_priority(task.id, task.assigned_to)

    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: UUID, db: Session = Depends(get_db)):
    """Delete a task"""
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()

    return None


@router.get("/tasks/employee/{employee_id}/prioritized", response_model=List[TaskResponse])
def get_prioritized_tasks(employee_id: UUID, db: Session = Depends(get_db)):
    """Get prioritized task list for an employee"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Get active tasks
    tasks = db.query(Task).filter(
        Task.assigned_to == employee_id,
        Task.status.in_(["pending", "in_progress"])
    ).all()

    # Sort by priority score (descending)
    tasks.sort(key=lambda t: t.priority_score or 0, reverse=True)

    return tasks


@router.post("/tasks/extract", response_model=List[TaskCandidate])
def extract_tasks(request: TaskExtractRequest, db: Session = Depends(get_db)):
    """Extract tasks from text using NLP"""
    extraction_service = TaskExtractionService()

    if request.source_type == "email":
        candidates = extraction_service.extract_from_email(request.content)
    elif request.source_type == "meeting":
        candidates = extraction_service.extract_from_meeting(request.content)
    else:
        raise HTTPException(status_code=400, detail="Invalid source type")

    return candidates


@router.post("/tasks/{task_id}/schedule")
def schedule_task(
    task_id: UUID,
    preferred_time: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Suggest optimal scheduling for a task"""
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not task.assigned_to:
        raise HTTPException(status_code=400, detail="Task must be assigned first")

    employee = db.query(Employee).filter(Employee.id == task.assigned_to).first()

    priority_service = TaskPrioritizationService(db)
    schedule = priority_service.suggest_scheduling([task], employee)

    return schedule[0] if schedule else None


@router.post("/tasks/employee/{employee_id}/recalculate-priorities")
def recalculate_priorities(employee_id: UUID, db: Session = Depends(get_db)):
    """Recalculate priority scores for all employee's tasks"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    priority_service = TaskPrioritizationService(db)
    count = priority_service.recalculate_all_priorities(employee_id)

    return {"message": f"Recalculated priorities for {count} tasks"}
