"""BurnoutMetric database model"""
from sqlalchemy import Column, Date, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class BurnoutMetric(BaseModel):
    """Daily burnout indicators for employees"""
    __tablename__ = "burnout_metrics"

    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)

    # Activity metrics
    hours_worked = Column(Float, nullable=False, default=0.0)
    breaks_taken = Column(Integer, nullable=False, default=0)

    # Cognitive load (0-1 scale, calculated from task complexity)
    cognitive_load = Column(Float, nullable=False, default=0.5)

    # Social metrics
    social_interactions = Column(Integer, nullable=False, default=0)  # Meetings, messages, etc.

    # Performance metrics
    task_completion_rate = Column(Float, nullable=False, default=1.0)  # 0-1 scale

    # Sentiment analysis (-1 to 1 scale from communications)
    sentiment_score = Column(Float, nullable=True)

    # AI-calculated risk score (0-1 scale)
    risk_score = Column(Float, nullable=True)

    # Relationships
    employee = relationship("Employee", back_populates="burnout_metrics")

    def __repr__(self):
        return f"<BurnoutMetric(employee_id={self.employee_id}, date={self.date}, risk={self.risk_score})>"
