"""
Script pour cr er des donn es d'exemple dans la base de donn es
"""
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Add app to path
sys.path.insert(0, '.')

from app.models.base import BaseModel
from app.models.employee import Employee
from app.models.team import Team
from app.models.employee_team import EmployeeTeam
from app.models.task import Task, TaskStatus, TaskSource
from app.models.burnout_metric import BurnoutMetric
from app.models.achievement import Achievement, AchievementType
from app.models.skill import Skill, SkillCategory, EmployeeSkill, SkillLevel
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_sample_data():
    """Create sample data for development"""

    # Create engine and session
    engine = create_engine(settings.DATABASE_URL)
    BaseModel.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        print("==> Creation des donnees d'exemple...")

        # 1. Create Teams
        print("\n==> Creation des equipes...")
        teams_data = [
            {"name": " quipe D veloppement", "description": " quipe de d veloppement logiciel"},
            {"name": " quipe Design", "description": " quipe de design et UX/UI"},
            {"name": " quipe Data", "description": " quipe data science et analytics"},
        ]

        teams = []
        for team_data in teams_data:
            team = Team(**team_data)
            db.add(team)
            teams.append(team)
        db.commit()
        print(f"OK {len(teams)}  quipes cr es")

        # 2. Create Employees
        print("\n  Cr ation des employ s...")
        employees_data = [
            {
                "name": "Alice Martin",
                "email": "alice@example.com",
                "password": "password123",
                "role": "manager",
                "productivity_periods": {"morning": 0.9, "afternoon": 0.8, "evening": 0.5}
            },
            {
                "name": "Bob Dupont",
                "email": "bob@example.com",
                "password": "password123",
                "role": "employee",
                "productivity_periods": {"morning": 0.7, "afternoon": 0.9, "evening": 0.6}
            },
            {
                "name": "Claire Bernard",
                "email": "claire@example.com",
                "password": "password123",
                "role": "employee",
                "productivity_periods": {"morning": 0.8, "afternoon": 0.7, "evening": 0.8}
            },
            {
                "name": "David Leroy",
                "email": "david@example.com",
                "password": "password123",
                "role": "employee",
                "productivity_periods": {"morning": 0.6, "afternoon": 0.8, "evening": 0.7}
            },
            {
                "name": "Emma Petit",
                "email": "emma@example.com",
                "password": "password123",
                "role": "employee",
                "productivity_periods": {"morning": 0.9, "afternoon": 0.6, "evening": 0.4}
            },
        ]

        employees = []
        for emp_data in employees_data:
            password = emp_data.pop("password")
            employee = Employee(
                **emp_data,
                password_hash=pwd_context.hash(password)
            )
            db.add(employee)
            employees.append(employee)
        db.commit()
        print(f"OK {len(employees)} employ s cr s")

        # Set team manager
        teams[0].manager_id = employees[0].id
        db.commit()

        # 3. Assign Employees to Teams
        print("\n  Association employ s- quipes...")
        employee_teams = [
            EmployeeTeam(employee_id=employees[0].id, team_id=teams[0].id, is_primary=True),
            EmployeeTeam(employee_id=employees[1].id, team_id=teams[0].id, is_primary=True),
            EmployeeTeam(employee_id=employees[2].id, team_id=teams[0].id, is_primary=True),
            EmployeeTeam(employee_id=employees[2].id, team_id=teams[1].id, is_primary=False),
            EmployeeTeam(employee_id=employees[3].id, team_id=teams[1].id, is_primary=True),
            EmployeeTeam(employee_id=employees[4].id, team_id=teams[2].id, is_primary=True),
        ]

        for et in employee_teams:
            db.add(et)
        db.commit()
        print(f"OK {len(employee_teams)} associations cr es")

        # 4. Create Skills
        print("\n  Cr ation des comp tences...")
        skills_data = [
            {"name": "Python", "category": SkillCategory.TECHNICAL, "description": "Langage Python"},
            {"name": "JavaScript", "category": SkillCategory.TECHNICAL, "description": "JavaScript/TypeScript"},
            {"name": "React", "category": SkillCategory.TECHNICAL, "description": "Framework React"},
            {"name": "PostgreSQL", "category": SkillCategory.TECHNICAL, "description": "Base de donn es PostgreSQL"},
            {"name": "Communication", "category": SkillCategory.SOFT_SKILL, "description": "Communication efficace"},
            {"name": "Leadership", "category": SkillCategory.SOFT_SKILL, "description": "Comp tences en leadership"},
            {"name": "Data Analysis", "category": SkillCategory.DOMAIN, "description": "Analyse de donn es"},
        ]

        skills = []
        for skill_data in skills_data:
            skill = Skill(**skill_data)
            db.add(skill)
            skills.append(skill)
        db.commit()
        print(f"OK {len(skills)} comp tences cr es")

        # Assign skills to employees
        employee_skills = [
            EmployeeSkill(employee_id=employees[0].id, skill_id=skills[0].id, level=SkillLevel.EXPERT),
            EmployeeSkill(employee_id=employees[0].id, skill_id=skills[5].id, level=SkillLevel.EXPERT),
            EmployeeSkill(employee_id=employees[1].id, skill_id=skills[1].id, level=SkillLevel.INTERMEDIATE),
            EmployeeSkill(employee_id=employees[1].id, skill_id=skills[2].id, level=SkillLevel.EXPERT),
            EmployeeSkill(employee_id=employees[2].id, skill_id=skills[2].id, level=SkillLevel.EXPERT),
            EmployeeSkill(employee_id=employees[3].id, skill_id=skills[1].id, level=SkillLevel.INTERMEDIATE),
            EmployeeSkill(employee_id=employees[4].id, skill_id=skills[6].id, level=SkillLevel.EXPERT),
        ]

        for es in employee_skills:
            db.add(es)
        db.commit()

        # 5. Create Tasks
        print("\n  Cr ation des t ches...")
        tasks_data = [
            {
                "title": "Impl menter l'authentification JWT",
                "description": "Mettre en place le syst me d'authentification avec JWT",
                "assigned_to": employees[1].id,
                "created_by": employees[0].id,
                "team_id": teams[0].id,
                "urgency": 5,
                "difficulty": 4,
                "deadline": datetime.now() + timedelta(days=2),
                "estimated_effort": 8.0,
                "status": TaskStatus.IN_PROGRESS,
                "source": TaskSource.MANUAL,
                "priority_score": 0.92,
            },
            {
                "title": "Design de l'interface dashboard",
                "description": "Cr er les maquettes du dashboard principal",
                "assigned_to": employees[3].id,
                "created_by": employees[0].id,
                "team_id": teams[1].id,
                "urgency": 3,
                "difficulty": 3,
                "deadline": datetime.now() + timedelta(days=5),
                "estimated_effort": 6.0,
                "status": TaskStatus.PENDING,
                "source": TaskSource.MANUAL,
                "priority_score": 0.65,
            },
            {
                "title": "Analyse des m triques de burnout",
                "description": "Analyser les donn es de burnout et cr er un rapport",
                "assigned_to": employees[4].id,
                "created_by": employees[0].id,
                "team_id": teams[2].id,
                "urgency": 4,
                "difficulty": 5,
                "deadline": datetime.now() + timedelta(days=3),
                "estimated_effort": 12.0,
                "status": TaskStatus.IN_PROGRESS,
                "source": TaskSource.EMAIL,
                "priority_score": 0.85,
            },
            {
                "title": "Corriger le bug de validation",
                "description": "Bug dans le formulaire de cr ation de t ches",
                "assigned_to": employees[2].id,
                "created_by": employees[1].id,
                "team_id": teams[0].id,
                "urgency": 5,
                "difficulty": 2,
                "deadline": datetime.now() + timedelta(days=1),
                "estimated_effort": 2.0,
                "status": TaskStatus.PENDING,
                "source": TaskSource.MANUAL,
                "priority_score": 0.95,
            },
            {
                "title": "Documentation de l'API",
                "description": "R diger la documentation compl te de l'API",
                "assigned_to": employees[1].id,
                "created_by": employees[0].id,
                "team_id": teams[0].id,
                "urgency": 2,
                "difficulty": 2,
                "deadline": datetime.now() + timedelta(days=7),
                "estimated_effort": 4.0,
                "status": TaskStatus.PENDING,
                "source": TaskSource.MANUAL,
                "priority_score": 0.45,
            },
            {
                "title": "Optimisation des requ tes SQL",
                "description": "Am liorer les performances des requ tes",
                "assigned_to": employees[1].id,
                "created_by": employees[0].id,
                "team_id": teams[0].id,
                "urgency": 3,
                "difficulty": 4,
                "deadline": datetime.now() + timedelta(days=10),
                "estimated_effort": 8.0,
                "status": TaskStatus.COMPLETED,
                "source": TaskSource.MANUAL,
                "priority_score": 0.60,
                "completed_at": datetime.now() - timedelta(days=1),
                "actual_effort": 7.5,
            },
        ]

        tasks = []
        for task_data in tasks_data:
            task = Task(**task_data)
            db.add(task)
            tasks.append(task)
        db.commit()
        print(f"OK {len(tasks)} t ches cr es")

        # 6. Create Burnout Metrics
        print("\n  Cr ation des m triques de burnout...")
        burnout_metrics = []
        for i, employee in enumerate(employees):
            for days_ago in range(7):
                metric = BurnoutMetric(
                    employee_id=employee.id,
                    date=datetime.now().date() - timedelta(days=days_ago),
                    hours_worked=7.0 + (i * 0.5) + (days_ago * 0.2),
                    cognitive_load=0.3 + (i * 0.1),
                    breaks_taken=3 - i,
                    social_interactions=5 + i,
                    task_completion_rate=0.7 + (i * 0.05),
                    sentiment_score=0.5 - (i * 0.1),
                    risk_score=0.2 + (i * 0.15),
                )
                db.add(metric)
                burnout_metrics.append(metric)
        db.commit()
        print(f"OK {len(burnout_metrics)} m triques cr es")

        # 7. Create Achievements
        print("\n  Cr ation des accomplissements...")
        achievements_data = [
            {
                "employee_id": employees[1].id,
                "type": AchievementType.DELIVERABLE,
                "description": "A termin  l'optimisation SQL avant la deadline",
                "impact_score": 0.9,
                "recognized_by_manager": True,
                "recognition_note": "Excellent travail sur les performances!",
                "related_task_id": tasks[5].id,
            },
            {
                "employee_id": employees[2].id,
                "type": AchievementType.INNOVATION,
                "description": "A propos  une nouvelle architecture pour le frontend",
                "impact_score": 0.85,
                "recognized_by_manager": False,
            },
            {
                "employee_id": employees[4].id,
                "type": AchievementType.COLLABORATION,
                "description": "A aid  plusieurs membres de l' quipe sur leurs analyses",
                "impact_score": 0.75,
                "recognized_by_manager": True,
                "recognition_note": "Tr s bon esprit d' quipe",
            },
        ]

        achievements = []
        for ach_data in achievements_data:
            achievement = Achievement(**ach_data)
            db.add(achievement)
            achievements.append(achievement)
        db.commit()
        print(f"OK {len(achievements)} accomplissements cr s")

        # Summary
        print("\n" + "="*50)
        print("OK DONN ES CR ES AVEC SUCC S!")
        print("="*50)
        print(f"\n  R sum :")
        print(f"    {len(teams)}  quipes")
        print(f"    {len(employees)} employ s")
        print(f"    {len(tasks)} t ches")
        print(f"    {len(skills)} comp tences")
        print(f"    {len(burnout_metrics)} m triques de burnout")
        print(f"    {len(achievements)} accomplissements")

        print(f"\n  Comptes de test:")
        print(f"    alice@example.com / password123 (Manager)")
        print(f"    bob@example.com / password123 (Employ )")
        print(f"    claire@example.com / password123 (Employ )")
        print(f"    david@example.com / password123 (Employ )")
        print(f"    emma@example.com / password123 (Employ )")

        print(f"\n  Vous pouvez maintenant d marrer le serveur!")
        print(f"   uvicorn app.main:app --reload")

    except Exception as e:
        print(f"\nERREUR: Erreur: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
