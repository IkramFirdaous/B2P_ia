"""Team database model"""
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from .base import BaseModel


class Team(BaseModel):
    """Team model for organizing employees"""
    __tablename__ = "teams"

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    manager_id = Column(String(255), nullable=True)  # Could be FK to Employee if managers are in system

    # Relationships
    members = relationship("Employee", back_populates="team")

    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name})>"
