"""
Script de génération de données de test pour B2P.AI
Crée des équipes, employés, tâches, métriques de burnout, et exemples d'emails
"""
import sys
import os
from datetime import datetime, timedelta, date
from uuid import uuid4
import random

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.core.auth import get_password_hash
from app.models import (
    Base, Employee, Team, Skill, EmployeeSkill, SkillCategory, SkillLevel,
    Task, TaskStatus, TaskSource, BurnoutMetric, Achievement, AchievementType
)


# Exemples d'emails pour tester l'extraction de tâches
SAMPLE_EMAILS = [
    {
        "subject": "Urgent: Fix production bug",
        "body": """Bonjour,

Nous avons détecté un bug critique en production qui affecte les utilisateurs.
Il faut absolument corriger ce problème avant demain 14h.

Le bug se situe dans le module de paiement - les transactions échouent de manière aléatoire.

Merci de traiter cela en priorité.

Cordialement,
Manager""",
        "urgency": 5,
        "source_type": "email"
    },
    {
        "subject": "Réunion client - Nouveau projet",
        "body": """Bonjour l'équipe,

Suite à la réunion client de ce matin, voici les actions à entreprendre:

1. Préparer une proposition technique pour le nouveau module CRM
2. Estimer le temps de développement et les ressources nécessaires
3. Organiser une réunion de kick-off avec l'équipe technique la semaine prochaine

Deadline pour la proposition: vendredi prochain.

Merci,
Chef de projet""",
        "urgency": 3,
        "source_type": "email"
    },
    {
        "subject": "Formation React avancé",
        "body": """Bonjour,

Une formation React avancé aura lieu le mois prochain.
Merci de vous inscrire avant le 15 du mois si vous êtes intéressés.

Thèmes abordés:
- Hooks avancés
- Performance optimization
- Server-side rendering

Places limitées à 10 personnes.

RH""",
        "urgency": 2,
        "source_type": "email"
    },
    {
        "subject": "Code review - Feature authentification",
        "body": """Salut,

J'ai terminé l'implémentation de la nouvelle feature d'authentification OAuth.
Pourrais-tu faire une code review avant la fin de la semaine?

Le code est sur la branche feature/oauth-integration.

Merci!""",
        "urgency": 3,
        "source_type": "email"
    },
    {
        "subject": "Mise à jour documentation API",
        "body": """Bonjour,

Il faudrait mettre à jour la documentation de l'API suite aux derniers changements.

Les endpoints modifiés sont:
- POST /api/users
- GET /api/tasks
- PUT /api/employees/{id}

Merci de documenter les nouveaux paramètres et les exemples de réponses.

Tech Lead""",
        "urgency": 2,
        "source_type": "email"
    }
]


def clear_database():
    """Supprime toutes les tables et les recrée"""
    print("[DELETE] Suppression des anciennes donnees...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("[OK] Base de donnees reinitialisee")


def create_teams(db: Session):
    """Crée des équipes de test"""
    print("\n[TEAMS] Creation des equipes...")

    teams = [
        Team(
            id=uuid4(),
            name="Équipe Backend",
            description="Développement des APIs et services backend",
            manager_id="manager@b2p.ai"
        ),
        Team(
            id=uuid4(),
            name="Équipe Frontend",
            description="Développement de l'interface utilisateur",
            manager_id="manager@b2p.ai"
        ),
        Team(
            id=uuid4(),
            name="Équipe DevOps",
            description="Infrastructure et déploiement continu",
            manager_id="manager@b2p.ai"
        )
    ]

    db.add_all(teams)
    db.commit()

    print(f"[OK] {len(teams)} equipes creees")
    return teams


def create_skills(db: Session):
    """Crée des compétences de test"""
    print("\n[SKILLS] Creation des competences...")

    skills = [
        # Compétences techniques
        Skill(id=uuid4(), name="Python", category=SkillCategory.TECHNICAL,
              description="Langage de programmation Python"),
        Skill(id=uuid4(), name="JavaScript", category=SkillCategory.TECHNICAL,
              description="Langage de programmation JavaScript"),
        Skill(id=uuid4(), name="React", category=SkillCategory.TECHNICAL,
              description="Framework frontend React"),
        Skill(id=uuid4(), name="FastAPI", category=SkillCategory.TECHNICAL,
              description="Framework API Python"),
        Skill(id=uuid4(), name="PostgreSQL", category=SkillCategory.TECHNICAL,
              description="Base de données relationnelle"),
        Skill(id=uuid4(), name="Docker", category=SkillCategory.TECHNICAL,
              description="Containerisation"),

        # Compétences soft
        Skill(id=uuid4(), name="Communication", category=SkillCategory.SOFT_SKILL,
              description="Communication efficace"),
        Skill(id=uuid4(), name="Leadership", category=SkillCategory.SOFT_SKILL,
              description="Capacité de leadership"),
        Skill(id=uuid4(), name="Travail d'équipe", category=SkillCategory.SOFT_SKILL,
              description="Collaboration en équipe"),

        # Compétences domaine
        Skill(id=uuid4(), name="IA/ML", category=SkillCategory.DOMAIN,
              description="Intelligence artificielle et Machine Learning"),
        Skill(id=uuid4(), name="Architecture", category=SkillCategory.DOMAIN,
              description="Architecture logicielle"),
    ]

    db.add_all(skills)
    db.commit()

    print(f"[OK] {len(skills)} competences creees")
    return skills


def create_employees(db: Session, teams: list, skills: list):
    """Crée des employés de test avec leurs compétences"""
    print("\n[EMPLOYEES] Creation des employes...")

    employees_data = [
        {"name": "Alice Martin", "email": "alice.martin@b2p.ai", "role": "Senior Backend Developer", "team": 0},
        {"name": "Bob Dupont", "email": "bob.dupont@b2p.ai", "role": "Frontend Developer", "team": 1},
        {"name": "Claire Bernard", "email": "claire.bernard@b2p.ai", "role": "DevOps Engineer", "team": 2},
        {"name": "David Leroy", "email": "david.leroy@b2p.ai", "role": "Full Stack Developer", "team": 0},
        {"name": "Emma Petit", "email": "emma.petit@b2p.ai", "role": "UI/UX Developer", "team": 1},
        {"name": "François Moreau", "email": "francois.moreau@b2p.ai", "role": "Backend Developer", "team": 0},
        {"name": "Julie Roux", "email": "julie.roux@b2p.ai", "role": "Frontend Developer", "team": 1},
        {"name": "Thomas Garcia", "email": "thomas.garcia@b2p.ai", "role": "Site Reliability Engineer", "team": 2},
    ]

    employees = []
    # Default password for all test employees: "password123"
    default_password_hash = get_password_hash("password123")

    for emp_data in employees_data:
        employee = Employee(
            id=uuid4(),
            name=emp_data["name"],
            email=emp_data["email"],
            password_hash=default_password_hash,
            role=emp_data["role"],
            team_id=teams[emp_data["team"]].id,
            productivity_periods={"morning": True, "afternoon": True, "evening": False}
        )
        db.add(employee)
        employees.append(employee)

        # Ajouter des compétences aléatoires
        num_skills = random.randint(3, 6)
        employee_skills_list = random.sample(skills, num_skills)

        for skill in employee_skills_list:
            emp_skill = EmployeeSkill(
                id=uuid4(),
                employee_id=employee.id,
                skill_id=skill.id,
                level=random.choice(list(SkillLevel))
            )
            db.add(emp_skill)

    db.commit()

    print(f"[OK] {len(employees)} employes crees avec leurs competences")
    return employees


def create_tasks(db: Session, employees: list):
    """Crée des tâches de test basées sur les emails exemples"""
    print("\n[TASKS] Creation des taches...")

    tasks = []

    # Créer des tâches à partir des emails exemples
    for i, email in enumerate(SAMPLE_EMAILS):
        assigned_to = random.choice(employees)
        created_by = random.choice([e for e in employees if e.id != assigned_to.id])

        # Extraire le titre du sujet
        title = email["subject"].replace("Urgent: ", "").replace("Re: ", "")

        # Deadline aléatoire dans les 7 prochains jours
        deadline = datetime.now() + timedelta(days=random.randint(1, 7))

        task = Task(
            id=uuid4(),
            title=title,
            description=email["body"][:500],
            assigned_to=assigned_to.id,
            created_by=created_by.id,
            urgency=email["urgency"],
            deadline=deadline,
            estimated_effort=random.uniform(1.0, 8.0),
            status=random.choice([TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED]),
            priority_score=random.uniform(0.5, 1.0),
            source=TaskSource.EMAIL,
            source_metadata={
                "email_subject": email["subject"],
                "email_from": created_by.email,
                "email_date": datetime.now().isoformat()
            }
        )
        tasks.append(task)
        db.add(task)

    # Ajouter quelques tâches supplémentaires
    additional_tasks = [
        {
            "title": "Refactoring du module authentification",
            "description": "Améliorer la structure du code d'authentification",
            "urgency": 3,
            "days_ahead": 5
        },
        {
            "title": "Tests unitaires pour le service de tâches",
            "description": "Écrire des tests pour couvrir 80% du code",
            "urgency": 3,
            "days_ahead": 10
        },
        {
            "title": "Optimisation des requêtes SQL",
            "description": "Améliorer les performances des requêtes lentes",
            "urgency": 4,
            "days_ahead": 3
        },
    ]

    for task_data in additional_tasks:
        assigned_to = random.choice(employees)
        created_by = random.choice([e for e in employees if e.id != assigned_to.id])

        task = Task(
            id=uuid4(),
            title=task_data["title"],
            description=task_data["description"],
            assigned_to=assigned_to.id,
            created_by=created_by.id,
            urgency=task_data["urgency"],
            deadline=datetime.now() + timedelta(days=task_data["days_ahead"]),
            estimated_effort=random.uniform(2.0, 16.0),
            status=random.choice([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
            priority_score=random.uniform(0.4, 0.9),
            source=TaskSource.MANUAL,
            source_metadata={}
        )
        tasks.append(task)
        db.add(task)

    db.commit()

    print(f"[OK] {len(tasks)} taches creees")
    return tasks


def create_burnout_metrics(db: Session, employees: list):
    """Crée des métriques de burnout pour les 30 derniers jours"""
    print("\n[BURNOUT] Creation des metriques de burnout...")

    metrics_count = 0

    for employee in employees:
        # Créer des métriques pour les 30 derniers jours
        for days_ago in range(30):
            metric_date = date.today() - timedelta(days=days_ago)

            # Générer des valeurs réalistes avec tendance
            base_hours = random.uniform(7.0, 9.5)
            base_load = random.uniform(0.4, 0.8)

            # Simuler une charge croissante pour certains employés
            if hash(employee.email) % 3 == 0:  # 1/3 des employés
                stress_factor = days_ago / 30.0
                base_hours += stress_factor * 2
                base_load += stress_factor * 0.2

            metric = BurnoutMetric(
                id=uuid4(),
                employee_id=employee.id,
                date=metric_date,
                hours_worked=min(base_hours, 12.0),
                breaks_taken=random.randint(1, 4),
                cognitive_load=min(base_load, 1.0),
                social_interactions=random.randint(2, 10),
                task_completion_rate=random.uniform(0.6, 1.0),
                sentiment_score=random.uniform(-0.3, 0.8),
                risk_score=min(base_load + (base_hours - 8) / 8, 1.0)
            )
            db.add(metric)
            metrics_count += 1

    db.commit()

    print(f"[OK] {metrics_count} metriques de burnout creees")


def create_achievements(db: Session, employees: list):
    """Crée des achievements de test"""
    print("\n[ACHIEVEMENTS] Creation des achievements...")

    achievements_data = [
        {
            "type": AchievementType.DELIVERABLE,
            "description": "Livraison réussie du module de paiement en avance",
            "impact_score": 0.9
        },
        {
            "type": AchievementType.INNOVATION,
            "description": "Proposition d'une nouvelle architecture microservices",
            "impact_score": 0.85
        },
        {
            "type": AchievementType.CLIENT_FEEDBACK,
            "description": "Retour client excellent sur la nouvelle interface",
            "impact_score": 0.8
        },
        {
            "type": AchievementType.COLLABORATION,
            "description": "Organisation d'un atelier de partage de connaissances",
            "impact_score": 0.7
        },
        {
            "type": AchievementType.LEARNING,
            "description": "Certification AWS obtenue",
            "impact_score": 0.75
        },
    ]

    achievements = []
    for ach_data in achievements_data:
        employee = random.choice(employees)

        achievement = Achievement(
            id=uuid4(),
            employee_id=employee.id,
            type=ach_data["type"],
            description=ach_data["description"],
            impact_score=ach_data["impact_score"],
            recognized_by_manager=random.choice([True, False]),
            recognition_note="Excellent travail!" if random.random() > 0.5 else None
        )
        achievements.append(achievement)
        db.add(achievement)

    db.commit()

    print(f"[OK] {len(achievements)} achievements crees")


def save_sample_emails():
    """Sauvegarde les emails exemples dans un fichier pour référence"""
    print("\n[EMAIL] Sauvegarde des emails exemples...")

    output_dir = os.path.join(os.path.dirname(__file__), 'sample_emails')
    os.makedirs(output_dir, exist_ok=True)

    for i, email in enumerate(SAMPLE_EMAILS, 1):
        filename = os.path.join(output_dir, f'email_{i}.txt')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Subject: {email['subject']}\n")
            f.write(f"Urgency: {email['urgency']}/5\n")
            f.write(f"Source: {email['source_type']}\n")
            f.write("\n" + "="*50 + "\n\n")
            f.write(email['body'])

    print(f"[OK] {len(SAMPLE_EMAILS)} emails sauvegardes dans {output_dir}")


def main():
    """Fonction principale"""
    print("="*60)
    print("B2P.AI - Generation de donnees de test")
    print("="*60)

    # Créer une session
    db = SessionLocal()

    try:
        # Demander confirmation
        response = input("\n[WARNING] Cela va supprimer toutes les donnees existantes. Continuer? (y/N): ")
        if response.lower() != 'y':
            print("[CANCELLED] Operation annulee")
            return

        # Réinitialiser la base
        clear_database()

        # Créer les données
        teams = create_teams(db)
        skills = create_skills(db)
        employees = create_employees(db, teams, skills)
        tasks = create_tasks(db, employees)
        create_burnout_metrics(db, employees)
        create_achievements(db, employees)

        # Sauvegarder les emails exemples
        save_sample_emails()

        print("\n" + "="*60)
        print("[SUCCESS] Generation terminee avec succes!")
        print("="*60)
        print(f"\n[SUMMARY] Resume:")
        print(f"   - {len(teams)} équipes")
        print(f"   - {len(skills)} compétences")
        print(f"   - {len(employees)} employés")
        print(f"   - {len(tasks)} tâches")
        print(f"   - ~{len(employees) * 30} métriques de burnout")
        print(f"   - {len(SAMPLE_EMAILS)} emails exemples sauvegardés")

        print("\n[INFO] Testez maintenant:")
        print("   - Frontend: http://localhost:3000")
        print("   - API Docs: http://localhost:8000/docs")
        print("   - Emails: backend/scripts/sample_emails/")
        print("\n[AUTH] Informations de connexion:")
        print("   - Email: [utilisez un email ci-dessus, ex: alice.martin@b2p.ai]")
        print("   - Mot de passe: password123")

    except Exception as e:
        print(f"\n[ERROR] Erreur: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
