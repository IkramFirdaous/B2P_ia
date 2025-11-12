"""Task Prioritization Service - AI-powered task scoring and scheduling"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import Task, Employee


class TaskPrioritizationService:
    """Service for calculating task priority scores and optimal scheduling"""

    def __init__(self, db: Session):
        self.db = db
        # Weights for priority scoring
        self.w_urgency = 0.3
        self.w_deadline = 0.25
        self.w_effort = 0.2
        self.w_productivity = 0.15
        self.w_dependencies = 0.1

    def calculate_priority_score(self, task: Task, employee: Employee) -> float:
        """
        Calculate priority score for a task assigned to an employee

        Score(T) = w1×Urgency + w2×(1/Deadline) + w3×Effort
                 + w4×Productivity + w5×Dependencies

        Returns: float between 0 and 1 (higher = more priority)
        """
        # Normalize urgency (1-5 scale to 0-1)
        urgency_norm = task.urgency / 5.0

        # Normalize deadline (closer deadline = higher score)
        deadline_norm = self._normalize_deadline(task.deadline)

        # Normalize effort (reasonable effort gets higher score)
        effort_norm = self._normalize_effort(task.estimated_effort)

        # Get employee productivity at current/scheduled time
        productivity_norm = self._get_productivity_at_time(employee, datetime.now())

        # Dependency score (tasks with dependencies get boost)
        dependency_score = 1.0 if (task.dependencies and len(task.dependencies) > 0) else 0.5

        # Calculate weighted score
        score = (
            self.w_urgency * urgency_norm +
            self.w_deadline * deadline_norm +
            self.w_effort * effort_norm +
            self.w_productivity * productivity_norm +
            self.w_dependencies * dependency_score
        )

        return min(max(score, 0.0), 1.0)  # Clamp between 0 and 1

    def _normalize_deadline(self, deadline: Optional[datetime]) -> float:
        """Convert deadline to normalized score (0-1)"""
        if not deadline:
            return 0.3  # Default for tasks without deadline

        days_until = (deadline - datetime.now()).days

        if days_until < 0:
            return 1.0  # Overdue tasks get max score
        elif days_until == 0:
            return 0.95  # Due today
        elif days_until <= 2:
            return 0.8
        elif days_until <= 7:
            return 0.6
        elif days_until <= 14:
            return 0.4
        else:
            return 0.2

    def _normalize_effort(self, estimated_effort: Optional[float]) -> float:
        """Normalize effort (tasks with reasonable effort get priority)"""
        if not estimated_effort:
            return 0.5  # Default

        # Sweet spot: 2-4 hours gets highest score
        if 2.0 <= estimated_effort <= 4.0:
            return 1.0
        elif estimated_effort < 2.0:
            return 0.7 + (estimated_effort / 2.0) * 0.3
        elif estimated_effort <= 8.0:
            return 1.0 - ((estimated_effort - 4.0) / 4.0) * 0.3
        else:
            # Very long tasks get lower priority (should be broken down)
            return 0.4

    def _get_productivity_at_time(self, employee: Employee, time: datetime) -> float:
        """Get employee's productivity level at given time"""
        hour = time.hour

        # Map time to period
        if 6 <= hour < 12:
            period = "morning"
        elif 12 <= hour < 18:
            period = "afternoon"
        else:
            period = "evening"

        return employee.productivity_periods.get(period, 0.7)

    def suggest_scheduling(
        self,
        tasks: List[Task],
        employee: Employee,
        start_time: datetime = None
    ) -> List[Dict]:
        """
        Suggest optimal scheduling for tasks based on:
        - Priority scores
        - Deadlines
        - Employee productivity patterns
        - Task dependencies

        Returns: List of scheduled tasks with suggested time slots
        """
        if not start_time:
            start_time = datetime.now()

        # Calculate priority for all tasks
        task_scores = []
        for task in tasks:
            score = self.calculate_priority_score(task, employee)
            task_scores.append({
                "task": task,
                "score": score,
                "deadline": task.deadline or (start_time + timedelta(days=30))
            })

        # Sort by score (descending) and deadline (ascending)
        task_scores.sort(key=lambda x: (-x["score"], x["deadline"]))

        # Schedule tasks in optimal time slots
        schedule = []
        current_time = start_time

        for item in task_scores:
            task = item["task"]

            # Find optimal time slot based on productivity
            optimal_slot = self._find_optimal_slot(
                employee,
                current_time,
                task.estimated_effort or 2.0
            )

            schedule.append({
                "task_id": task.id,
                "task_title": task.title,
                "priority_score": item["score"],
                "suggested_start": optimal_slot,
                "suggested_end": optimal_slot + timedelta(hours=task.estimated_effort or 2.0),
                "urgency": task.urgency,
                "deadline": task.deadline
            })

            # Move current time forward
            current_time = optimal_slot + timedelta(hours=task.estimated_effort or 2.0)

        return schedule

    def _find_optimal_slot(
        self,
        employee: Employee,
        start_from: datetime,
        duration_hours: float
    ) -> datetime:
        """Find the next optimal time slot based on productivity"""
        current = start_from
        max_productivity = 0
        best_slot = current

        # Check next 7 days
        for day in range(7):
            for hour in range(8, 18):  # Working hours 8 AM - 6 PM
                candidate = current.replace(hour=hour, minute=0) + timedelta(days=day)
                productivity = self._get_productivity_at_time(employee, candidate)

                if productivity > max_productivity:
                    max_productivity = productivity
                    best_slot = candidate

        return best_slot

    def update_task_priority(self, task_id: UUID, employee_id: UUID) -> float:
        """Update and persist priority score for a task"""
        task = self.db.query(Task).filter(Task.id == task_id).first()
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()

        if not task or not employee:
            raise ValueError("Task or Employee not found")

        score = self.calculate_priority_score(task, employee)
        task.priority_score = score
        self.db.commit()

        return score

    def recalculate_all_priorities(self, employee_id: UUID) -> int:
        """Recalculate priorities for all pending tasks of an employee"""
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise ValueError("Employee not found")

        tasks = self.db.query(Task).filter(
            Task.assigned_to == employee_id,
            Task.status.in_(["pending", "in_progress"])
        ).all()

        count = 0
        for task in tasks:
            task.priority_score = self.calculate_priority_score(task, employee)
            count += 1

        self.db.commit()
        return count
