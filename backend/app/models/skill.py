"""Skill and EmployeeSkill database models"""
from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class SkillCategory(str, enum.Enum):
    """Skill category enumeration"""
    TECHNICAL = "technical"
    SOFT_SKILL = "soft_skill"
    DOMAIN = "domain"


class SkillLevel(str, enum.Enum):
    """Skill level enumeration"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class Skill(BaseModel):
    """Skill master table"""
    __tablename__ = "skills"

    name = Column(String(255), nullable=False, unique=True)
    category = Column(Enum(SkillCategory), nullable=False)
    description = Column(String(500), nullable=True)

    # Relationships
    employee_skills = relationship("EmployeeSkill", back_populates="skill")

    def __repr__(self):
        return f"<Skill(id={self.id}, name={self.name}, category={self.category})>"


class EmployeeSkill(BaseModel):
    """Many-to-many relationship between Employee and Skill with level"""
    __tablename__ = "employee_skills"

    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False)
    level = Column(Enum(SkillLevel), nullable=False, default=SkillLevel.BEGINNER)

    # Relationships
    employee = relationship("Employee", back_populates="skills")
    skill = relationship("Skill", back_populates="employee_skills")

    def __repr__(self):
        return f"<EmployeeSkill(employee_id={self.employee_id}, skill_id={self.skill_id}, level={self.level})>"
