"""Recognition Service - Achievement tracking and feedback"""
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Achievement, Employee, Task
from app.models.achievement import AchievementType
from app.schemas.analytics_schema import AchievementResponse


class RecognitionService:
    """Service for tracking and recognizing employee achievements"""

    def __init__(self, db: Session):
        self.db = db

    def track_achievement(
        self,
        employee_id: UUID,
        achievement_type: AchievementType,
        description: str,
        impact_score: float = 0.5,
        related_task_id: Optional[UUID] = None
    ) -> Achievement:
        """Record a new achievement for an employee"""
        achievement = Achievement(
            employee_id=employee_id,
            type=achievement_type,
            description=description,
            impact_score=impact_score,
            related_task_id=related_task_id
        )

        self.db.add(achievement)
        self.db.commit()
        self.db.refresh(achievement)

        return achievement

    def auto_detect_achievements(self, employee_id: UUID) -> List[Achievement]:
        """
        Automatically detect achievements based on task completion and performance

        Detection rules:
        - Completed high-priority task → Deliverable achievement
        - Completed task early → Innovation/Efficiency achievement
        - Completed multiple tasks in a day → Productivity achievement
        """
        achievements = []

        # Get recently completed tasks (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        completed_tasks = self.db.query(Task).filter(
            Task.assigned_to == employee_id,
            Task.status == "completed",
            Task.completed_at >= yesterday
        ).all()

        for task in completed_tasks:
            # High-priority deliverable
            if task.priority_score and task.priority_score >= 0.8:
                achievement = self.track_achievement(
                    employee_id=employee_id,
                    achievement_type=AchievementType.DELIVERABLE,
                    description=f"Completed high-priority task: {task.title}",
                    impact_score=task.priority_score,
                    related_task_id=task.id
                )
                achievements.append(achievement)

            # Early completion
            if task.deadline and task.completed_at and task.completed_at < task.deadline:
                days_early = (task.deadline - task.completed_at).days
                if days_early >= 2:
                    achievement = self.track_achievement(
                        employee_id=employee_id,
                        achievement_type=AchievementType.INNOVATION,
                        description=f"Completed task {days_early} days ahead of deadline: {task.title}",
                        impact_score=min(0.8, 0.5 + days_early * 0.05),
                        related_task_id=task.id
                    )
                    achievements.append(achievement)

            # Efficient execution (actual effort < estimated effort)
            if task.actual_effort and task.estimated_effort:
                if task.actual_effort < task.estimated_effort * 0.8:
                    achievement = self.track_achievement(
                        employee_id=employee_id,
                        achievement_type=AchievementType.INNOVATION,
                        description=f"Completed task efficiently (20%+ under estimate): {task.title}",
                        impact_score=0.7,
                        related_task_id=task.id
                    )
                    achievements.append(achievement)

        # High productivity day (multiple tasks completed)
        if len(completed_tasks) >= 3:
            achievement = self.track_achievement(
                employee_id=employee_id,
                achievement_type=AchievementType.DELIVERABLE,
                description=f"High productivity: Completed {len(completed_tasks)} tasks today",
                impact_score=0.8
            )
            achievements.append(achievement)

        return achievements

    def manager_recognition(
        self,
        achievement_id: UUID,
        recognition_note: str
    ) -> Achievement:
        """Manager adds recognition to an achievement"""
        achievement = self.db.query(Achievement).filter(
            Achievement.id == achievement_id
        ).first()

        if not achievement:
            raise ValueError("Achievement not found")

        achievement.recognized_by_manager = True
        achievement.recognition_note = recognition_note

        self.db.commit()
        self.db.refresh(achievement)

        return achievement

    def get_employee_achievements(
        self,
        employee_id: UUID,
        days: int = 30,
        achievement_type: Optional[AchievementType] = None
    ) -> List[Achievement]:
        """Get achievements for an employee"""
        cutoff_date = datetime.now() - timedelta(days=days)

        query = self.db.query(Achievement).filter(
            Achievement.employee_id == employee_id,
            Achievement.created_at >= cutoff_date
        )

        if achievement_type:
            query = query.filter(Achievement.type == achievement_type)

        return query.order_by(Achievement.created_at.desc()).all()

    def get_achievement_summary(self, employee_id: UUID, days: int = 30) -> Dict:
        """Get summary of achievements for an employee"""
        cutoff_date = datetime.now() - timedelta(days=days)

        # Count by type
        achievements_by_type = self.db.query(
            Achievement.type,
            func.count(Achievement.id).label("count"),
            func.avg(Achievement.impact_score).label("avg_impact")
        ).filter(
            Achievement.employee_id == employee_id,
            Achievement.created_at >= cutoff_date
        ).group_by(Achievement.type).all()

        # Count recognized vs not recognized
        total_count = self.db.query(func.count(Achievement.id)).filter(
            Achievement.employee_id == employee_id,
            Achievement.created_at >= cutoff_date
        ).scalar()

        recognized_count = self.db.query(func.count(Achievement.id)).filter(
            Achievement.employee_id == employee_id,
            Achievement.created_at >= cutoff_date,
            Achievement.recognized_by_manager == True
        ).scalar()

        # Calculate overall impact score
        avg_impact = self.db.query(
            func.avg(Achievement.impact_score)
        ).filter(
            Achievement.employee_id == employee_id,
            Achievement.created_at >= cutoff_date
        ).scalar()

        summary = {
            "total_achievements": total_count or 0,
            "recognized_by_manager": recognized_count or 0,
            "recognition_rate": (recognized_count / total_count * 100) if total_count else 0,
            "average_impact_score": float(avg_impact) if avg_impact else 0.0,
            "by_type": {
                row.type.value: {
                    "count": row.count,
                    "avg_impact": float(row.avg_impact)
                }
                for row in achievements_by_type
            }
        }

        return summary

    def get_unrecognized_achievements(
        self,
        team_id: Optional[UUID] = None,
        days: int = 7
    ) -> List[Dict]:
        """Get achievements that haven't been recognized by manager"""
        cutoff_date = datetime.now() - timedelta(days=days)

        query = self.db.query(Achievement, Employee).join(
            Employee, Achievement.employee_id == Employee.id
        ).filter(
            Achievement.recognized_by_manager == False,
            Achievement.created_at >= cutoff_date,
            Achievement.impact_score >= 0.6  # Only significant achievements
        )

        if team_id:
            query = query.filter(Employee.team_id == team_id)

        results = query.order_by(Achievement.impact_score.desc()).all()

        return [
            {
                "achievement_id": str(achievement.id),
                "employee_id": str(employee.id),
                "employee_name": employee.name,
                "type": achievement.type.value,
                "description": achievement.description,
                "impact_score": achievement.impact_score,
                "created_at": achievement.created_at
            }
            for achievement, employee in results
        ]

    def suggest_recognition_opportunities(self, team_id: UUID) -> List[Dict]:
        """Suggest recognition opportunities for team manager"""
        # Get unrecognized achievements
        unrecognized = self.get_unrecognized_achievements(team_id=team_id, days=7)

        # Get employees with multiple achievements but low recognition rate
        employees = self.db.query(Employee).filter(Employee.team_id == team_id).all()

        suggestions = []

        for emp in employees:
            summary = self.get_achievement_summary(emp.id, days=30)

            if summary["total_achievements"] >= 3 and summary["recognition_rate"] < 50:
                suggestions.append({
                    "employee_id": str(emp.id),
                    "employee_name": emp.name,
                    "reason": f"Has {summary['total_achievements']} achievements but only "
                             f"{summary['recognition_rate']:.0f}% recognition rate",
                    "achievement_count": summary["total_achievements"],
                    "unrecognized_count": summary["total_achievements"] - summary["recognized_by_manager"]
                })

        # Add high-impact unrecognized achievements
        for item in unrecognized[:5]:  # Top 5
            if item["impact_score"] >= 0.8:
                suggestions.append({
                    "employee_id": item["employee_id"],
                    "employee_name": item["employee_name"],
                    "reason": f"High-impact achievement: {item['description'][:100]}",
                    "achievement_id": item["achievement_id"],
                    "impact_score": item["impact_score"]
                })

        return suggestions
