"""
Wellbeing Service - Calculate employee wellbeing metrics
Analyzes tasks to determine workload, stress, burnout risk, and deadline conflicts
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import Task, Employee, BurnoutMetric, TaskStatus


class WellbeingService:
    """Calculate employee wellbeing metrics based on their tasks"""

    @staticmethod
    def calculate_workload_score(employee_id: str, db: Session) -> float:
        """
        Calculate total workload score based on active tasks.

        Formula: Sum of (difficulty × urgency × effort) for active tasks
        Returns: Float value (typically 0-100+)

        Args:
            employee_id: UUID of the employee
            db: Database session

        Returns:
            Workload score (higher = more workload)
        """
        # Get all active tasks (pending or in_progress)
        tasks = db.query(Task).filter(
            Task.assigned_to == employee_id,
            Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
        ).all()

        if not tasks:
            return 0.0

        total_score = 0.0
        for task in tasks:
            difficulty = task.difficulty or 3
            urgency = task.urgency or 3
            effort = task.estimated_effort or 1.0

            # Workload formula: (difficulty/5) × (urgency/5) × effort
            # Normalized to 0-1 scale, then multiplied by effort
            task_score = (difficulty / 5.0) * (urgency / 5.0) * effort
            total_score += task_score

        return round(total_score, 2)

    @staticmethod
    def calculate_stress_level(employee_id: str, db: Session) -> float:
        """
        Calculate stress level (0-1 scale) based on urgency and deadlines.

        Factors:
        - High urgency tasks (4-5)
        - Upcoming deadlines (within 7 days)
        - Overdue tasks

        Args:
            employee_id: UUID of the employee
            db: Database session

        Returns:
            Stress level (0.0 = low stress, 1.0 = high stress)
        """
        now = datetime.now()
        week_ahead = now + timedelta(days=7)

        # Get all active tasks
        tasks = db.query(Task).filter(
            Task.assigned_to == employee_id,
            Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
        ).all()

        if not tasks:
            return 0.0

        # Count high urgency tasks (urgency >= 4)
        urgent_tasks = [t for t in tasks if t.urgency >= 4]

        # Count tasks with upcoming deadlines (within 7 days)
        deadline_tasks = [
            t for t in tasks
            if t.deadline and now <= t.deadline <= week_ahead
        ]

        # Count overdue tasks
        overdue_tasks = [
            t for t in tasks
            if t.deadline and t.deadline < now
        ]

        # Stress calculation
        urgency_stress = min(0.4, len(urgent_tasks) * 0.1)  # Max 0.4
        deadline_stress = min(0.3, len(deadline_tasks) * 0.1)  # Max 0.3
        overdue_stress = min(0.3, len(overdue_tasks) * 0.15)  # Max 0.3

        total_stress = urgency_stress + deadline_stress + overdue_stress
        return round(min(1.0, total_stress), 2)

    @staticmethod
    def calculate_overlap_risk(employee_id: str, db: Session) -> Dict:
        """
        Detect tasks with overlapping deadlines that may cause conflicts.

        Returns tasks where deadlines are within 24 hours of each other.

        Args:
            employee_id: UUID of the employee
            db: Database session

        Returns:
            Dict with overlap_count and list of conflicts
        """
        # Get active tasks with deadlines
        tasks = db.query(Task).filter(
            Task.assigned_to == employee_id,
            Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
            Task.deadline.isnot(None)
        ).order_by(Task.deadline).all()

        conflicts = []

        # Check each pair of tasks for deadline overlap
        for i, task1 in enumerate(tasks):
            for task2 in tasks[i+1:]:
                # Calculate time difference in seconds
                time_diff = abs((task1.deadline - task2.deadline).total_seconds())

                # If deadlines are within 24 hours (86400 seconds)
                if time_diff < 86400:
                    conflicts.append({
                        "task1": {
                            "id": str(task1.id),
                            "title": task1.title,
                            "difficulty": task1.difficulty,
                            "urgency": task1.urgency
                        },
                        "task2": {
                            "id": str(task2.id),
                            "title": task2.title,
                            "difficulty": task2.difficulty,
                            "urgency": task2.urgency
                        },
                        "deadline": task1.deadline.isoformat(),
                        "time_diff_hours": round(time_diff / 3600, 1)
                    })

        return {
            "overlap_count": len(conflicts),
            "conflicts": conflicts,
            "has_conflicts": len(conflicts) > 0
        }

    @staticmethod
    def calculate_cognitive_load(employee_id: str, db: Session) -> float:
        """
        Calculate cognitive load based on task difficulty and variety.

        Higher difficulty tasks and variety of tasks increase cognitive load.

        Args:
            employee_id: UUID of the employee
            db: Database session

        Returns:
            Cognitive load (0.0-1.0 scale)
        """
        # Get active tasks
        tasks = db.query(Task).filter(
            Task.assigned_to == employee_id,
            Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
        ).all()

        if not tasks:
            return 0.0

        # Calculate average difficulty
        avg_difficulty = sum(t.difficulty for t in tasks) / len(tasks)

        # Number of tasks factor (more tasks = higher cognitive load)
        task_count_factor = min(1.0, len(tasks) / 10.0)  # Cap at 10 tasks

        # Difficulty factor (normalized to 0-1)
        difficulty_factor = avg_difficulty / 5.0

        # Cognitive load: weighted combination
        cognitive_load = (difficulty_factor * 0.6) + (task_count_factor * 0.4)

        return round(min(1.0, cognitive_load), 2)

    @staticmethod
    def calculate_burnout_risk(employee_id: str, db: Session) -> float:
        """
        Calculate overall burnout risk (0-1 scale).

        Combines:
        - Workload score (normalized)
        - Stress level
        - Cognitive load
        - Historical burnout data (if available)

        Args:
            employee_id: UUID of the employee
            db: Database session

        Returns:
            Burnout risk (0.0 = low risk, 1.0 = high risk)
        """
        # Calculate individual metrics
        workload = WellbeingService.calculate_workload_score(employee_id, db)
        stress = WellbeingService.calculate_stress_level(employee_id, db)
        cognitive_load = WellbeingService.calculate_cognitive_load(employee_id, db)

        # Normalize workload to 0-1 scale (assume 20+ is very high)
        normalized_workload = min(1.0, workload / 20.0)

        # Get recent burnout metric if available
        recent_metric = db.query(BurnoutMetric).filter(
            BurnoutMetric.employee_id == employee_id
        ).order_by(BurnoutMetric.date.desc()).first()

        historical_risk = recent_metric.risk_score if recent_metric else 0.3

        # Burnout risk formula: weighted average
        burnout_risk = (
            normalized_workload * 0.35 +
            stress * 0.30 +
            cognitive_load * 0.20 +
            historical_risk * 0.15
        )

        return round(min(1.0, burnout_risk), 2)

    @staticmethod
    def get_wellbeing_summary(employee_id: str, db: Session) -> Dict:
        """
        Get complete wellbeing summary for an employee.

        Returns all wellbeing metrics in one call.

        Args:
            employee_id: UUID of the employee
            db: Database session

        Returns:
            Dict containing all wellbeing metrics
        """
        workload = WellbeingService.calculate_workload_score(employee_id, db)
        stress = WellbeingService.calculate_stress_level(employee_id, db)
        cognitive_load = WellbeingService.calculate_cognitive_load(employee_id, db)
        burnout_risk = WellbeingService.calculate_burnout_risk(employee_id, db)
        overlap_analysis = WellbeingService.calculate_overlap_risk(employee_id, db)

        # Get task counts
        active_tasks = db.query(Task).filter(
            Task.assigned_to == employee_id,
            Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
        ).count()

        completed_tasks_week = db.query(Task).filter(
            Task.assigned_to == employee_id,
            Task.status == TaskStatus.COMPLETED,
            Task.completed_at >= datetime.now() - timedelta(days=7)
        ).count()

        # Determine risk level
        risk_level = "low"
        if burnout_risk >= 0.7:
            risk_level = "high"
        elif burnout_risk >= 0.4:
            risk_level = "medium"

        # Generate recommendations
        recommendations = WellbeingService._generate_recommendations(
            workload, stress, cognitive_load, burnout_risk, overlap_analysis
        )

        return {
            "employee_id": str(employee_id),
            "metrics": {
                "workload_score": workload,
                "stress_level": stress,
                "cognitive_load": cognitive_load,
                "burnout_risk": burnout_risk
            },
            "task_summary": {
                "active_tasks": active_tasks,
                "completed_this_week": completed_tasks_week
            },
            "overlap_analysis": overlap_analysis,
            "risk_level": risk_level,
            "recommendations": recommendations,
            "calculated_at": datetime.now().isoformat()
        }

    @staticmethod
    def _generate_recommendations(
        workload: float,
        stress: float,
        cognitive_load: float,
        burnout_risk: float,
        overlap_analysis: Dict
    ) -> List[str]:
        """
        Generate personalized recommendations based on wellbeing metrics.

        Args:
            workload: Workload score
            stress: Stress level
            cognitive_load: Cognitive load
            burnout_risk: Burnout risk
            overlap_analysis: Overlap analysis results

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # High burnout risk
        if burnout_risk >= 0.7:
            recommendations.append("⚠️ High burnout risk detected. Consider delegating some tasks.")
            recommendations.append("Schedule breaks between high-intensity tasks.")

        # High workload
        if workload >= 15:
            recommendations.append("Your workload is very high. Review task priorities.")
            recommendations.append("Consider requesting deadline extensions for non-urgent tasks.")

        # High stress
        if stress >= 0.6:
            recommendations.append("High stress level detected. Focus on urgent tasks first.")
            recommendations.append("Break down complex tasks into smaller steps.")

        # High cognitive load
        if cognitive_load >= 0.7:
            recommendations.append("High cognitive load. Try to batch similar tasks together.")
            recommendations.append("Take short breaks to maintain focus and productivity.")

        # Deadline conflicts
        if overlap_analysis["has_conflicts"]:
            recommendations.append(
                f"⚠️ {overlap_analysis['overlap_count']} deadline conflicts detected. "
                "Review task scheduling."
            )

        # All good
        if burnout_risk < 0.4 and stress < 0.4 and not overlap_analysis["has_conflicts"]:
            recommendations.append("✅ Wellbeing metrics look good. Keep up the great work!")

        return recommendations

    @staticmethod
    def get_team_wellbeing_summary(team_id: str, db: Session) -> Dict:
        """
        Get wellbeing summary for all members of a team.

        Args:
            team_id: UUID of the team
            db: Database session

        Returns:
            Dict with team-wide wellbeing metrics
        """
        from app.models import EmployeeTeam

        # Get all employees in the team
        employee_teams = db.query(EmployeeTeam).filter(
            EmployeeTeam.team_id == team_id
        ).all()

        if not employee_teams:
            return {
                "team_id": str(team_id),
                "member_count": 0,
                "members": [],
                "team_averages": {},
                "at_risk_members": []
            }

        members_data = []
        total_burnout = 0
        total_stress = 0
        total_workload = 0
        at_risk = []

        for emp_team in employee_teams:
            employee_id = str(emp_team.employee_id)
            summary = WellbeingService.get_wellbeing_summary(employee_id, db)

            # Get employee name
            employee = db.query(Employee).filter(Employee.id == employee_id).first()

            member_data = {
                "employee_id": employee_id,
                "employee_name": employee.name if employee else "Unknown",
                "metrics": summary["metrics"],
                "risk_level": summary["risk_level"]
            }

            members_data.append(member_data)

            # Accumulate for averages
            total_burnout += summary["metrics"]["burnout_risk"]
            total_stress += summary["metrics"]["stress_level"]
            total_workload += summary["metrics"]["workload_score"]

            # Track at-risk members
            if summary["metrics"]["burnout_risk"] >= 0.6:
                at_risk.append({
                    "employee_name": employee.name if employee else "Unknown",
                    "burnout_risk": summary["metrics"]["burnout_risk"]
                })

        count = len(members_data)

        return {
            "team_id": str(team_id),
            "member_count": count,
            "members": members_data,
            "team_averages": {
                "avg_burnout_risk": round(total_burnout / count, 2),
                "avg_stress_level": round(total_stress / count, 2),
                "avg_workload_score": round(total_workload / count, 2)
            },
            "at_risk_members": at_risk,
            "calculated_at": datetime.now().isoformat()
        }
