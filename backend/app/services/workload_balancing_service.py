"""Workload Balancing Service - Equitable task distribution"""
from typing import Dict, List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Employee, Task, Team
from app.schemas.analytics_schema import TeamEquityResponse, EmployeeWorkloadDetail


class WorkloadBalancingService:
    """Service for ensuring equitable workload distribution across teams"""

    def __init__(self, db: Session):
        self.db = db
        # Weights for global workload score
        self.alpha = 0.6  # Cumulative load weight
        self.beta = 0.4   # Critical tasks weight

    def calculate_team_equity(self, team_id: UUID) -> TeamEquityResponse:
        """
        Calculate workload equity across team members

        Global Score = α × Cumulative_Load + β × Critical_Score

        Returns equity score (0-1, where 1 = perfect equity)
        """
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise ValueError("Team not found")

        employees = self.db.query(Employee).filter(Employee.team_id == team_id).all()

        if not employees:
            return TeamEquityResponse(
                team_id=team_id,
                team_name=team.name,
                equity_score=1.0,
                member_workloads=[],
                recommendations=["No team members found"]
            )

        # Calculate workload for each employee
        workloads = []
        for emp in employees:
            workload = self._calculate_employee_workload(emp.id)
            workloads.append(workload)

        # Calculate equity score (lower variance = higher equity)
        equity_score = self._calculate_equity_score(workloads)

        # Generate recommendations
        recommendations = self._generate_balancing_recommendations(workloads)

        # Format response
        member_workloads = [
            {
                "employee_id": str(w["employee_id"]),
                "employee_name": w["employee_name"],
                "cumulative_load": w["cumulative_load"],
                "critical_score": w["critical_score"],
                "global_score": w["global_score"],
                "active_tasks": w["active_tasks_count"]
            }
            for w in workloads
        ]

        return TeamEquityResponse(
            team_id=team_id,
            team_name=team.name,
            equity_score=equity_score,
            member_workloads=member_workloads,
            recommendations=recommendations
        )

    def _calculate_employee_workload(self, employee_id: UUID) -> Dict:
        """Calculate comprehensive workload metrics for an employee"""
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()

        # Get active tasks (pending or in_progress)
        tasks = self.db.query(Task).filter(
            Task.assigned_to == employee_id,
            Task.status.in_(["pending", "in_progress"])
        ).all()

        # Calculate cumulative load (effort × priority)
        cumulative_load = sum(
            (task.estimated_effort or 2.0) * (task.priority_score or 0.5)
            for task in tasks
        )

        # Calculate critical task score (sum of high-urgency task priorities)
        critical_score = sum(
            task.priority_score or 0.5
            for task in tasks if task.urgency >= 4
        )

        # Count high-priority tasks
        high_priority_count = sum(1 for task in tasks if (task.priority_score or 0) >= 0.7)

        # Calculate global workload score
        global_score = self.alpha * cumulative_load + self.beta * critical_score

        return {
            "employee_id": employee_id,
            "employee_name": employee.name,
            "cumulative_load": cumulative_load,
            "critical_score": critical_score,
            "global_score": global_score,
            "active_tasks_count": len(tasks),
            "high_priority_tasks_count": high_priority_count
        }

    def _calculate_equity_score(self, workloads: List[Dict]) -> float:
        """
        Calculate equity score based on workload variance
        Lower variance = higher equity (closer to 1.0)
        """
        if not workloads:
            return 1.0

        scores = [w["global_score"] for w in workloads]

        # Calculate coefficient of variation (normalized standard deviation)
        mean_score = sum(scores) / len(scores)

        if mean_score == 0:
            return 1.0  # No workload = perfect equity

        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5

        # Coefficient of variation
        cv = std_dev / mean_score if mean_score > 0 else 0

        # Convert CV to equity score (0-1 scale, where 1 = perfect equity)
        # CV of 0 = perfect equity (score 1.0)
        # CV of 1+ = poor equity (score approaches 0)
        equity_score = max(0.0, 1.0 - cv)

        return equity_score

    def _generate_balancing_recommendations(self, workloads: List[Dict]) -> List[str]:
        """Generate recommendations for workload balancing"""
        recommendations = []

        if not workloads:
            return ["No team members to analyze"]

        # Sort by global score
        sorted_workloads = sorted(workloads, key=lambda x: x["global_score"], reverse=True)

        overloaded = sorted_workloads[0]
        underloaded = sorted_workloads[-1]

        # Check for significant imbalance
        imbalance_ratio = overloaded["global_score"] / (underloaded["global_score"] + 0.1)

        if imbalance_ratio > 2.0:
            recommendations.append(
                f"CRITICAL: {overloaded['employee_name']} is significantly overloaded. "
                f"Consider redistributing tasks to {underloaded['employee_name']}."
            )

        if imbalance_ratio > 1.5:
            recommendations.append(
                f"Workload imbalance detected. Review task distribution between "
                f"{overloaded['employee_name']} and {underloaded['employee_name']}."
            )

        # Check for individuals with too many critical tasks
        for workload in workloads:
            if workload["high_priority_tasks_count"] > 5:
                recommendations.append(
                    f"{workload['employee_name']} has {workload['high_priority_tasks_count']} "
                    f"high-priority tasks. Consider delegating lower-priority items."
                )

        # Check total team capacity
        total_load = sum(w["global_score"] for w in workloads)
        avg_load = total_load / len(workloads)

        if avg_load > 20:
            recommendations.append(
                "Team appears to be operating at high capacity. Consider extending deadlines "
                "or requesting additional resources."
            )

        if not recommendations:
            recommendations.append("Workload is well-balanced across the team. Keep monitoring.")

        return recommendations

    def redistribute_tasks(self, team_id: UUID, auto_assign: bool = False) -> List[Dict]:
        """
        Suggest or automatically redistribute tasks for better equity

        Returns list of suggested task transfers
        """
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise ValueError("Team not found")

        employees = self.db.query(Employee).filter(Employee.team_id == team_id).all()

        if len(employees) < 2:
            return []  # Can't redistribute with less than 2 people

        # Calculate current workloads
        workloads = [self._calculate_employee_workload(emp.id) for emp in employees]
        workloads.sort(key=lambda x: x["global_score"], reverse=True)

        suggestions = []

        # Try to balance by transferring tasks from overloaded to underloaded
        while True:
            overloaded = workloads[0]
            underloaded = workloads[-1]

            # Stop if balanced enough
            if overloaded["global_score"] < 1.5 * underloaded["global_score"]:
                break

            # Find suitable task to transfer
            transfer = self._find_transferable_task(
                overloaded["employee_id"],
                underloaded["employee_id"]
            )

            if not transfer:
                break  # No more suitable tasks to transfer

            suggestions.append({
                "task_id": str(transfer.id),
                "task_title": transfer.title,
                "from_employee": overloaded["employee_name"],
                "to_employee": underloaded["employee_name"],
                "priority_score": transfer.priority_score,
                "estimated_effort": transfer.estimated_effort
            })

            # If auto-assign, actually move the task
            if auto_assign:
                transfer.assigned_to = underloaded["employee_id"]
                self.db.commit()

            # Recalculate workloads
            workloads = [self._calculate_employee_workload(emp.id) for emp in employees]
            workloads.sort(key=lambda x: x["global_score"], reverse=True)

            # Prevent infinite loop
            if len(suggestions) >= 10:
                break

        return suggestions

    def _find_transferable_task(
        self,
        from_employee_id: UUID,
        to_employee_id: UUID
    ) -> Optional[Task]:
        """Find a suitable task to transfer between employees"""
        # Get tasks from overloaded employee
        # Prioritize: lower priority, no dependencies, future deadlines
        task = self.db.query(Task).filter(
            Task.assigned_to == from_employee_id,
            Task.status == "pending",
            Task.dependencies == []  # No dependencies
        ).order_by(
            Task.priority_score.asc(),  # Lower priority first
            Task.deadline.desc()  # Future deadlines first
        ).first()

        return task

    def suggest_new_task_assignment(
        self,
        team_id: UUID,
        task: Task
    ) -> Tuple[UUID, str]:
        """
        Suggest which team member should be assigned a new task

        Returns: (employee_id, reason)
        """
        employees = self.db.query(Employee).filter(Employee.team_id == team_id).all()

        if not employees:
            raise ValueError("No employees in team")

        if len(employees) == 1:
            return employees[0].id, "Only team member available"

        # Calculate current workloads
        workloads = [self._calculate_employee_workload(emp.id) for emp in employees]
        workloads.sort(key=lambda x: x["global_score"])

        # Find employee with lowest workload
        best_match = workloads[0]

        # Check if there's a skills match (would need skills matching service)
        # For now, just use workload balancing

        return (
            best_match["employee_id"],
            f"Lowest current workload (score: {best_match['global_score']:.2f})"
        )
