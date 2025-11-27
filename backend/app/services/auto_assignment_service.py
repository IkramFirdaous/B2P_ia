"""Auto-Assignment Service - Intelligent task assignment based on multiple factors"""
from typing import List, Dict, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Employee, Task, Team, EmployeeSkill, Skill, BurnoutMetric
from app.models.skill import SkillLevel
from datetime import date, timedelta
import re


class AutoAssignmentService:
    """
    Intelligent service for automatically assigning tasks to team members

    Factors considered:
    1. Workload balance (30%)
    2. Skill matching (35%)
    3. Availability/Burnout risk (20%)
    4. Productivity patterns (15%)
    """

    def __init__(self, db: Session):
        self.db = db
        # Weight factors for final score
        self.workload_weight = 0.30
        self.skills_weight = 0.35
        self.availability_weight = 0.20
        self.productivity_weight = 0.15

    def auto_assign_task(
        self,
        task: Task,
        team_id: Optional[UUID] = None,
        required_skills: Optional[List[str]] = None
    ) -> Tuple[UUID, Dict]:
        """
        Automatically assign a task to the best team member

        Args:
            task: The task to assign
            team_id: Target team (if None, uses task creator's team)
            required_skills: List of required skill names (if None, auto-extracted from task)

        Returns:
            Tuple of (employee_id, assignment_details)
        """
        # Determine team
        if not team_id:
            creator = self.db.query(Employee).filter(Employee.id == task.created_by).first()
            if not creator or not creator.team_id:
                raise ValueError("Task creator has no team and no team_id provided")
            team_id = creator.team_id

        # Get team members
        employees = self.db.query(Employee).filter(Employee.team_id == team_id).all()

        if not employees:
            raise ValueError(f"No employees found in team {team_id}")

        if len(employees) == 1:
            # Only one team member, assign to them
            return employees[0].id, {
                "reason": "Only team member available",
                "score": 1.0,
                "factors": {}
            }

        # Extract required skills if not provided
        if required_skills is None:
            required_skills = self._extract_skills_from_task(task)

        # Calculate scores for each employee
        scores = []
        for employee in employees:
            score_data = self._calculate_assignment_score(
                employee=employee,
                task=task,
                required_skills=required_skills
            )
            scores.append({
                "employee_id": employee.id,
                "employee_name": employee.name,
                "total_score": score_data["total_score"],
                "factors": score_data["factors"]
            })

        # Sort by score (descending)
        scores.sort(key=lambda x: x["total_score"], reverse=True)

        best_match = scores[0]

        return best_match["employee_id"], {
            "reason": "Best match based on workload, skills, and availability",
            "score": best_match["total_score"],
            "factors": best_match["factors"],
            "all_candidates": scores
        }

    def _calculate_assignment_score(
        self,
        employee: Employee,
        task: Task,
        required_skills: List[str]
    ) -> Dict:
        """Calculate comprehensive assignment score for an employee"""

        # 1. Workload score (lower workload = higher score)
        workload_score = self._calculate_workload_score(employee.id)

        # 2. Skills match score
        skills_score = self._calculate_skills_match_score(employee.id, required_skills)

        # 3. Availability score (based on burnout risk)
        availability_score = self._calculate_availability_score(employee.id)

        # 4. Productivity pattern score (based on task urgency)
        productivity_score = self._calculate_productivity_score(employee, task)

        # Calculate weighted total score
        total_score = (
            self.workload_weight * workload_score +
            self.skills_weight * skills_score +
            self.availability_weight * availability_score +
            self.productivity_weight * productivity_score
        )

        return {
            "total_score": total_score,
            "factors": {
                "workload": {
                    "score": workload_score,
                    "weight": self.workload_weight,
                    "contribution": self.workload_weight * workload_score
                },
                "skills": {
                    "score": skills_score,
                    "weight": self.skills_weight,
                    "contribution": self.skills_weight * skills_score
                },
                "availability": {
                    "score": availability_score,
                    "weight": self.availability_weight,
                    "contribution": self.availability_weight * availability_score
                },
                "productivity": {
                    "score": productivity_score,
                    "weight": self.productivity_weight,
                    "contribution": self.productivity_weight * productivity_score
                }
            }
        }

    def _calculate_workload_score(self, employee_id: UUID) -> float:
        """
        Calculate workload score (0-1, higher = less loaded)

        Based on current active tasks and their priorities
        """
        # Get active tasks
        tasks = self.db.query(Task).filter(
            Task.assigned_to == employee_id,
            Task.status.in_(["pending", "in_progress"])
        ).all()

        if not tasks:
            return 1.0  # No workload = perfect score

        # Calculate cumulative load
        cumulative_load = sum(
            (task.estimated_effort or 2.0) * (task.priority_score or 0.5)
            for task in tasks
        )

        # Normalize to 0-1 scale (inverse, so lower load = higher score)
        # Assume 40 as max reasonable load (20 hours × 2.0 avg priority)
        max_load = 40.0
        normalized_load = min(cumulative_load / max_load, 1.0)

        return 1.0 - normalized_load

    def _calculate_skills_match_score(
        self,
        employee_id: UUID,
        required_skills: List[str]
    ) -> float:
        """
        Calculate how well employee skills match task requirements (0-1)

        Perfect match = 1.0, no match = 0.3 (still can learn)
        """
        if not required_skills:
            return 0.7  # Neutral score if no specific skills required

        # Get employee skills
        employee_skills = self.db.query(EmployeeSkill, Skill).join(
            Skill, EmployeeSkill.skill_id == Skill.id
        ).filter(
            EmployeeSkill.employee_id == employee_id
        ).all()

        # Create skill map with levels
        skill_map = {
            skill.name.lower(): {
                "level": emp_skill.level,
                "score": self._skill_level_to_score(emp_skill.level)
            }
            for emp_skill, skill in employee_skills
        }

        # Calculate match score
        if not skill_map:
            return 0.3  # Can still assign, but not ideal

        matched_skills = []
        for required_skill in required_skills:
            skill_lower = required_skill.lower()
            if skill_lower in skill_map:
                matched_skills.append(skill_map[skill_lower]["score"])

        if not matched_skills:
            return 0.3  # No matching skills, but can learn

        # Average of matched skills
        avg_match = sum(matched_skills) / len(required_skills)

        return avg_match

    def _skill_level_to_score(self, level: SkillLevel) -> float:
        """Convert skill level to numeric score"""
        level_scores = {
            SkillLevel.BEGINNER: 0.5,
            SkillLevel.INTERMEDIATE: 0.8,
            SkillLevel.EXPERT: 1.0
        }
        return level_scores.get(level, 0.5)

    def _calculate_availability_score(self, employee_id: UUID) -> float:
        """
        Calculate availability score based on burnout risk (0-1)

        Lower burnout risk = higher availability
        """
        # Get recent burnout metrics (last 7 days)
        cutoff = date.today() - timedelta(days=7)

        metrics = self.db.query(BurnoutMetric).filter(
            BurnoutMetric.employee_id == employee_id,
            BurnoutMetric.date >= cutoff
        ).order_by(BurnoutMetric.date.desc()).limit(7).all()

        if not metrics:
            return 0.8  # Default good availability if no data

        # Calculate average burnout score
        avg_burnout = sum(m.burnout_score for m in metrics) / len(metrics)

        # Inverse: lower burnout = higher availability
        # Burnout score is 0-1, so availability = 1 - burnout
        availability = 1.0 - avg_burnout

        return availability

    def _calculate_productivity_score(self, employee: Employee, task: Task) -> float:
        """
        Calculate productivity score based on time patterns

        If urgent task, prefer employees with high current productivity
        """
        # If no urgency data, return neutral
        if not task.urgency:
            return 0.7

        # Get current time period (simplified: assume morning for now)
        # In production, would use actual time
        productivity_periods = employee.productivity_periods or {
            "morning": 0.7,
            "afternoon": 0.7,
            "evening": 0.5
        }

        # For urgent tasks (4-5), use average productivity
        if task.urgency >= 4:
            avg_productivity = sum(productivity_periods.values()) / len(productivity_periods)
            return avg_productivity

        # For normal tasks, neutral score
        return 0.7

    def _extract_skills_from_task(self, task: Task) -> List[str]:
        """
        Extract required skills from task title and description

        Uses keyword matching against known skills
        """
        # Get all skills from database
        all_skills = self.db.query(Skill).all()
        skill_keywords = [skill.name.lower() for skill in all_skills]

        # Combine task text
        text = f"{task.title} {task.description or ''}".lower()

        # Find matching skills
        matched_skills = []
        for skill in all_skills:
            skill_name = skill.name.lower()
            # Match whole word
            pattern = r'\b' + re.escape(skill_name) + r'\b'
            if re.search(pattern, text):
                matched_skills.append(skill.name)

        return matched_skills

    def batch_auto_assign(
        self,
        team_id: UUID,
        unassigned_tasks: Optional[List[Task]] = None
    ) -> List[Dict]:
        """
        Batch assign multiple unassigned tasks to optimize team workload

        Returns list of assignment results
        """
        if unassigned_tasks is None:
            # Get all unassigned tasks from team members
            team = self.db.query(Team).filter(Team.id == team_id).first()
            if not team:
                raise ValueError("Team not found")

            # Get tasks created by team members that are unassigned
            team_member_ids = [member.id for member in team.members]
            unassigned_tasks = self.db.query(Task).filter(
                Task.created_by.in_(team_member_ids),
                Task.assigned_to.is_(None),
                Task.status == "pending"
            ).all()

        if not unassigned_tasks:
            return []

        results = []
        for task in unassigned_tasks:
            try:
                employee_id, details = self.auto_assign_task(task, team_id=team_id)

                # Actually assign the task
                task.assigned_to = employee_id
                self.db.commit()

                results.append({
                    "task_id": str(task.id),
                    "task_title": task.title,
                    "assigned_to": str(employee_id),
                    "employee_name": details.get("all_candidates", [{}])[0].get("employee_name"),
                    "score": details["score"],
                    "reason": details["reason"]
                })
            except Exception as e:
                results.append({
                    "task_id": str(task.id),
                    "task_title": task.title,
                    "error": str(e)
                })

        return results

    def get_assignment_explanation(
        self,
        task_id: UUID,
        employee_id: UUID
    ) -> Dict:
        """
        Explain why a task was assigned to a specific employee

        Useful for transparency and debugging
        """
        task = self.db.query(Task).filter(Task.id == task_id).first()
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()

        if not task or not employee:
            raise ValueError("Task or employee not found")

        required_skills = self._extract_skills_from_task(task)
        score_data = self._calculate_assignment_score(employee, task, required_skills)

        return {
            "task": {
                "id": str(task.id),
                "title": task.title,
                "urgency": task.urgency,
                "estimated_effort": task.estimated_effort
            },
            "employee": {
                "id": str(employee.id),
                "name": employee.name,
                "email": employee.email
            },
            "assignment_score": score_data["total_score"],
            "factors": score_data["factors"],
            "required_skills": required_skills,
            "explanation": self._generate_explanation(score_data["factors"])
        }

    def _generate_explanation(self, factors: Dict) -> str:
        """Generate human-readable explanation of assignment decision"""
        explanations = []

        # Analyze each factor
        for factor_name, factor_data in factors.items():
            score = factor_data["score"]
            contribution = factor_data["contribution"]

            if factor_name == "workload" and score > 0.7:
                explanations.append(f"Low current workload (score: {score:.2f})")
            elif factor_name == "skills" and score > 0.7:
                explanations.append(f"Strong skill match (score: {score:.2f})")
            elif factor_name == "availability" and score > 0.7:
                explanations.append(f"Good availability (score: {score:.2f})")
            elif factor_name == "productivity" and score > 0.7:
                explanations.append(f"High productivity (score: {score:.2f})")

        if not explanations:
            return "Best available team member based on overall factors"

        return "; ".join(explanations)

    def rebalance_workload(self, team_id: Optional[UUID] = None) -> Dict:
        """
        Rebalance workload across team members by reassigning tasks

        This method:
        1. Identifies overloaded and underloaded team members
        2. Calculates optimal task distribution
        3. Reassigns tasks to balance workload

        Args:
            team_id: Target team (if None, rebalances all teams)

        Returns:
            Dictionary with rebalancing details and statistics
        """
        from app.models import TaskStatus

        # Get teams to rebalance
        if team_id:
            teams = [self.db.query(Team).filter(Team.id == team_id).first()]
            if not teams[0]:
                raise ValueError(f"Team {team_id} not found")
        else:
            teams = self.db.query(Team).all()

        total_reassignments = 0
        results = []

        for team in teams:
            # Get team members
            employees = self.db.query(Employee).filter(Employee.team_id == team.id).all()

            if len(employees) < 2:
                continue  # Skip teams with less than 2 members

            # Calculate current workload for each employee
            workload_data = []
            for employee in employees:
                active_tasks = self.db.query(Task).filter(
                    Task.assigned_to == employee.id,
                    Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
                ).all()

                total_effort = sum(t.estimated_effort or 8.0 for t in active_tasks)

                workload_data.append({
                    "employee": employee,
                    "tasks": active_tasks,
                    "total_effort": total_effort,
                    "task_count": len(active_tasks)
                })

            # Sort by workload (descending)
            workload_data.sort(key=lambda x: x["total_effort"], reverse=True)

            # Calculate average workload
            total_workload = sum(w["total_effort"] for w in workload_data)
            avg_workload = total_workload / len(workload_data) if workload_data else 0

            # Identify overloaded (>30% above avg) and underloaded (<30% below avg) members
            overloaded = [w for w in workload_data if w["total_effort"] > avg_workload * 1.3]
            underloaded = [w for w in workload_data if w["total_effort"] < avg_workload * 0.7]

            if not overloaded or not underloaded:
                continue  # No rebalancing needed

            # Reassign tasks from overloaded to underloaded
            reassignments = []

            for overloaded_data in overloaded:
                # Sort tasks by priority (lowest priority first to reassign)
                tasks_to_consider = sorted(
                    overloaded_data["tasks"],
                    key=lambda t: t.priority_score or 0
                )

                for task in tasks_to_consider:
                    # Check if still overloaded
                    if overloaded_data["total_effort"] <= avg_workload * 1.1:
                        break

                    # Find best underloaded member
                    best_candidate = None
                    best_score = -1

                    for underloaded_data in underloaded:
                        # Check if they're still underloaded
                        if underloaded_data["total_effort"] >= avg_workload * 0.9:
                            continue

                        # Calculate assignment score
                        required_skills = self._extract_skills_from_task(task)
                        score_data = self._calculate_assignment_score(
                            underloaded_data["employee"],
                            task,
                            required_skills
                        )

                        if score_data["total_score"] > best_score:
                            best_score = score_data["total_score"]
                            best_candidate = underloaded_data

                    # Reassign if good candidate found
                    if best_candidate and best_score > 0.4:  # Minimum threshold
                        old_assignee = overloaded_data["employee"]
                        new_assignee = best_candidate["employee"]

                        # Update task
                        task.assigned_to = new_assignee.id
                        self.db.commit()

                        # Update workload tracking
                        task_effort = task.estimated_effort or 8.0
                        overloaded_data["total_effort"] -= task_effort
                        best_candidate["total_effort"] += task_effort

                        reassignments.append({
                            "task_id": str(task.id),
                            "task_title": task.title,
                            "from_employee": old_assignee.name,
                            "to_employee": new_assignee.name,
                            "effort": task_effort,
                            "score": best_score
                        })

                        total_reassignments += 1

            if reassignments:
                results.append({
                    "team_id": str(team.id),
                    "team_name": team.name,
                    "reassignments": reassignments,
                    "original_avg_workload": avg_workload,
                    "members_balanced": len(overloaded) + len(underloaded)
                })

        return {
            "total_reassignments": total_reassignments,
            "teams_rebalanced": len(results),
            "details": results
        }
