"""Employee-Team association table for many-to-many relationship"""
from sqlalchemy import Column, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import BaseModel, UUID


class EmployeeTeam(BaseModel):
    """
    Junction table for many-to-many relationship between Employees and Teams.

    Allows employees to belong to multiple teams simultaneously.
    Each employee can have one primary team marked with is_primary=True.
    """
    __tablename__ = "employee_teams"

    employee_id = Column(
        UUID(),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    team_id = Column(
        UUID(),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    joined_at = Column(DateTime, default=func.now(), nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="employee_teams")
    team = relationship("Team", back_populates="team_employees")

    # Constraints
    __table_args__ = (
        UniqueConstraint('employee_id', 'team_id', name='uq_employee_team'),
        {'comment': 'Many-to-many association between employees and teams'}
    )

    def __repr__(self):
        return f"<EmployeeTeam(employee_id={self.employee_id}, team_id={self.team_id}, is_primary={self.is_primary})>"
