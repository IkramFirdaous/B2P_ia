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
from app.services.auto_assignment_service import AutoAssignmentService


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
    team_id: Optional[UUID] = None,
    status: Optional[str] = None,
    source: Optional[str] = None,
    difficulty: Optional[int] = None,
    min_urgency: Optional[int] = None,
    max_urgency: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List tasks with optional filters.

    Filters:
    - assigned_to: Filter by assigned employee
    - team_id: Filter by team
    - status: Filter by status (pending, in_progress, completed, blocked, cancelled)
    - source: Filter by source (email, meeting, manual, calendar, assigned)
    - difficulty: Filter by difficulty level (1-5)
    - min_urgency: Minimum urgency level (1-5)
    - max_urgency: Maximum urgency level (1-5)
    """
    query = db.query(Task)

    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)

    if team_id:
        query = query.filter(Task.team_id == team_id)

    if status:
        query = query.filter(Task.status == status)

    if source:
        query = query.filter(Task.source == source)

    if difficulty:
        query = query.filter(Task.difficulty == difficulty)

    if min_urgency:
        query = query.filter(Task.urgency >= min_urgency)

    if max_urgency:
        query = query.filter(Task.urgency <= max_urgency)

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
    if task.assigned_to and any(f in update_data for f in ["urgency", "difficulty", "deadline", "estimated_effort"]):
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


# Auto-Assignment Endpoints

@router.post("/tasks/{task_id}/auto-assign")
def auto_assign_single_task(
    task_id: UUID,
    team_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """
    Automatically assign a task to the best team member

    Uses intelligent matching based on:
    - Current workload
    - Skill matching
    - Availability (burnout risk)
    - Productivity patterns
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.assigned_to:
        raise HTTPException(
            status_code=400,
            detail=f"Task already assigned to employee {task.assigned_to}"
        )

    auto_service = AutoAssignmentService(db)

    try:
        employee_id, details = auto_service.auto_assign_task(task, team_id=team_id)

        # Actually assign the task
        task.assigned_to = employee_id
        db.commit()
        db.refresh(task)

        # Calculate priority score
        priority_service = TaskPrioritizationService(db)
        priority_service.update_task_priority(task.id, employee_id)

        return {
            "task_id": str(task.id),
            "assigned_to": str(employee_id),
            "assignment_details": details
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tasks/team/{team_id}/auto-assign-all")
def auto_assign_team_tasks(
    team_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Automatically assign all unassigned tasks in a team

    Optimizes workload distribution across the entire team
    """
    from app.models import Team

    team = db.query(Team).filter(Team.id == team_id).first()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    auto_service = AutoAssignmentService(db)

    try:
        results = auto_service.batch_auto_assign(team_id)

        # Recalculate priorities for all assigned tasks
        priority_service = TaskPrioritizationService(db)
        for result in results:
            if "assigned_to" in result:
                task_id = UUID(result["task_id"])
                employee_id = UUID(result["assigned_to"])
                priority_service.update_task_priority(task_id, employee_id)

        return {
            "team_id": str(team_id),
            "assignments": results,
            "total_assigned": len([r for r in results if "assigned_to" in r])
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tasks/{task_id}/assignment-explanation")
def get_assignment_explanation(
    task_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get detailed explanation of why a task was assigned to a specific employee

    Useful for transparency and understanding the auto-assignment algorithm
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not task.assigned_to:
        raise HTTPException(
            status_code=400,
            detail="Task is not assigned to anyone"
        )

    auto_service = AutoAssignmentService(db)

    try:
        explanation = auto_service.get_assignment_explanation(task_id, task.assigned_to)
        return explanation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tasks/{task_id}/suggest-reassignment")
def suggest_reassignment(
    task_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Suggest better assignment for an already-assigned task

    Useful when workload has changed or new team members joined
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Get creator's team
    creator = db.query(Employee).filter(Employee.id == task.created_by).first()
    if not creator or not creator.team_id:
        raise HTTPException(status_code=400, detail="Cannot determine team")

    auto_service = AutoAssignmentService(db)

    try:
        # Temporarily unassign to get fresh suggestion
        current_assignee = task.assigned_to
        employee_id, details = auto_service.auto_assign_task(task, team_id=creator.team_id)

        return {
            "task_id": str(task.id),
            "current_assignee": str(current_assignee) if current_assignee else None,
            "suggested_assignee": str(employee_id),
            "should_reassign": current_assignee != employee_id,
            "details": details
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tasks/rebalance-workload")
def rebalance_workload(
    team_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """
    Rebalance workload across team members

    Redistributes tasks to achieve better workload balance by:
    - Identifying overloaded and underloaded team members
    - Reassigning tasks based on workload, skills, and availability
    - Maintaining task priorities and dependencies

    Args:
        team_id: Optional team ID to rebalance (if None, rebalances all teams)

    Returns:
        Summary of rebalancing actions taken
    """
    auto_service = AutoAssignmentService(db)

    try:
        result = auto_service.rebalance_workload(team_id=team_id)

        # Recalculate priorities for reassigned tasks
        if result["total_reassignments"] > 0:
            priority_service = TaskPrioritizationService(db)
            for team_result in result["details"]:
                for reassignment in team_result["reassignments"]:
                    task_id = UUID(reassignment["task_id"])
                    # Find the task to get new assignee
                    task = db.query(Task).filter(Task.id == task_id).first()
                    if task and task.assigned_to:
                        priority_service.update_task_priority(task_id, task.assigned_to)

        return {
            "success": True,
            "message": f"Rebalanced workload with {result['total_reassignments']} reassignments",
            **result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
