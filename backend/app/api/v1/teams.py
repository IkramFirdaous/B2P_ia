"""Team and Skills Management API Endpoints"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Team, Skill, EmployeeSkill, Employee
from app.models.skill import SkillCategory, SkillLevel


router = APIRouter()


# Schemas

class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None
    manager_id: Optional[str] = None


class TeamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str]
    manager_id: Optional[str]
    created_at: datetime


class SkillCreate(BaseModel):
    name: str
    category: SkillCategory
    description: Optional[str] = None


class SkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    category: SkillCategory
    description: Optional[str]
    created_at: datetime


class EmployeeSkillCreate(BaseModel):
    skill_id: UUID
    level: SkillLevel


class EmployeeSkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    employee_id: UUID
    skill_id: UUID
    level: SkillLevel


# Team Endpoints

@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(team_data: TeamCreate, db: Session = Depends(get_db)):
    """Create a new team"""
    team = Team(**team_data.model_dump())
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


@router.get("/teams", response_model=List[TeamResponse])
def list_teams(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all teams"""
    teams = db.query(Team).offset(skip).limit(limit).all()
    return teams


@router.get("/teams/{team_id}", response_model=TeamResponse)
def get_team(team_id: UUID, db: Session = Depends(get_db)):
    """Get a specific team"""
    team = db.query(Team).filter(Team.id == team_id).first()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return team


# Skill Endpoints

@router.post("/skills", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill(skill_data: SkillCreate, db: Session = Depends(get_db)):
    """Create a new skill"""
    # Check if skill name already exists
    existing = db.query(Skill).filter(Skill.name == skill_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Skill with this name already exists")

    skill = Skill(**skill_data.model_dump())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.get("/skills", response_model=List[SkillResponse])
def list_skills(
    category: Optional[SkillCategory] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all skills"""
    query = db.query(Skill)

    if category:
        query = query.filter(Skill.category == category)

    skills = query.offset(skip).limit(limit).all()
    return skills


@router.get("/skills/{skill_id}", response_model=SkillResponse)
def get_skill(skill_id: UUID, db: Session = Depends(get_db)):
    """Get a specific skill"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()

    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    return skill


# Employee Skills Endpoints

@router.post("/employees/{employee_id}/skills", response_model=EmployeeSkillResponse, status_code=status.HTTP_201_CREATED)
def add_employee_skill(
    employee_id: UUID,
    skill_data: EmployeeSkillCreate,
    db: Session = Depends(get_db)
):
    """Add a skill to an employee"""
    # Check employee exists
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Check skill exists
    skill = db.query(Skill).filter(Skill.id == skill_data.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    # Check if employee already has this skill
    existing = db.query(EmployeeSkill).filter(
        EmployeeSkill.employee_id == employee_id,
        EmployeeSkill.skill_id == skill_data.skill_id
    ).first()

    if existing:
        # Update level instead
        existing.level = skill_data.level
        db.commit()
        db.refresh(existing)
        return existing

    # Create new employee skill
    employee_skill = EmployeeSkill(
        employee_id=employee_id,
        skill_id=skill_data.skill_id,
        level=skill_data.level
    )
    db.add(employee_skill)
    db.commit()
    db.refresh(employee_skill)
    return employee_skill


@router.get("/employees/{employee_id}/skills", response_model=List[dict])
def get_employee_skills(employee_id: UUID, db: Session = Depends(get_db)):
    """Get all skills for an employee"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    employee_skills = db.query(EmployeeSkill, Skill).join(
        Skill, EmployeeSkill.skill_id == Skill.id
    ).filter(
        EmployeeSkill.employee_id == employee_id
    ).all()

    result = []
    for emp_skill, skill in employee_skills:
        result.append({
            "id": emp_skill.id,
            "skill_id": skill.id,
            "skill_name": skill.name,
            "skill_category": skill.category,
            "level": emp_skill.level
        })

    return result


@router.delete("/employees/{employee_id}/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_employee_skill(
    employee_id: UUID,
    skill_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove a skill from an employee"""
    employee_skill = db.query(EmployeeSkill).filter(
        EmployeeSkill.employee_id == employee_id,
        EmployeeSkill.skill_id == skill_id
    ).first()

    if not employee_skill:
        raise HTTPException(status_code=404, detail="Employee skill not found")

    db.delete(employee_skill)
    db.commit()
    return None
