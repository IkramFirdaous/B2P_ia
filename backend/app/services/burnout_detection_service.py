"""Burnout Detection Service - AI-powered wellbeing monitoring"""
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import BurnoutMetric, Employee, Task
from app.schemas.analytics_schema import BurnoutRiskResponse


class BurnoutDetectionService:
    """Service for detecting and preventing employee burnout"""

    def __init__(self, db: Session):
        self.db = db
        # Weights for risk calculation
        self.w_hours = 0.3
        self.w_cognitive = 0.25
        self.w_isolation = 0.2
        self.w_completion = 0.1
        self.w_sentiment = 0.15

    def calculate_risk_score(self, employee_id: UUID, days: int = 7) -> float:
        """
        Calculate burnout risk score for an employee

        Risk = 0.3×Hours + 0.25×CognitiveLoad + 0.2×Isolation
             + 0.1×TaskCompletion + 0.15×Sentiment

        Returns: float between 0 and 1 (higher = more risk)
        """
        metrics = self._get_recent_metrics(employee_id, days)

        if not metrics:
            return 0.0  # No data = no risk calculated

        # Calculate component scores
        hours_score = self._normalize_hours(metrics["avg_hours_worked"])
        cognitive_score = metrics["avg_cognitive_load"]
        isolation_score = self._normalize_isolation(metrics["avg_social_interactions"])
        completion_score = 1.0 - metrics["avg_task_completion_rate"]
        sentiment_score = self._normalize_sentiment(metrics["avg_sentiment_score"])

        # Calculate weighted risk
        risk = (
            self.w_hours * hours_score +
            self.w_cognitive * cognitive_score +
            self.w_isolation * isolation_score +
            self.w_completion * completion_score +
            self.w_sentiment * sentiment_score
        )

        return min(max(risk, 0.0), 1.0)

    def _get_recent_metrics(self, employee_id: UUID, days: int) -> Optional[Dict]:
        """Get aggregated metrics for recent period"""
        cutoff_date = date.today() - timedelta(days=days)

        result = self.db.query(
            func.avg(BurnoutMetric.hours_worked).label("avg_hours_worked"),
            func.avg(BurnoutMetric.cognitive_load).label("avg_cognitive_load"),
            func.avg(BurnoutMetric.social_interactions).label("avg_social_interactions"),
            func.avg(BurnoutMetric.task_completion_rate).label("avg_task_completion_rate"),
            func.avg(BurnoutMetric.sentiment_score).label("avg_sentiment_score"),
        ).filter(
            BurnoutMetric.employee_id == employee_id,
            BurnoutMetric.date >= cutoff_date
        ).first()

        if not result or result.avg_hours_worked is None:
            return None

        return {
            "avg_hours_worked": float(result.avg_hours_worked or 8.0),
            "avg_cognitive_load": float(result.avg_cognitive_load or 0.5),
            "avg_social_interactions": float(result.avg_social_interactions or 5),
            "avg_task_completion_rate": float(result.avg_task_completion_rate or 1.0),
            "avg_sentiment_score": float(result.avg_sentiment_score or 0.0),
        }

    def _normalize_hours(self, hours: float) -> float:
        """Normalize hours worked (8h = ideal, more = higher risk)"""
        if hours <= 8:
            return 0.0
        elif hours <= 9:
            return 0.3
        elif hours <= 10:
            return 0.6
        elif hours <= 11:
            return 0.8
        else:
            return 1.0

    def _normalize_isolation(self, interactions: float) -> float:
        """Normalize social isolation (fewer interactions = higher risk)"""
        if interactions >= 10:
            return 0.0
        elif interactions >= 7:
            return 0.2
        elif interactions >= 5:
            return 0.4
        elif interactions >= 3:
            return 0.7
        else:
            return 1.0

    def _normalize_sentiment(self, sentiment: Optional[float]) -> float:
        """Normalize sentiment (-1 to 1 → 0 to 1 risk scale)"""
        if sentiment is None:
            return 0.5  # Neutral

        # Convert: positive sentiment (1) → low risk (0)
        #          negative sentiment (-1) → high risk (1)
        return (1.0 - sentiment) / 2.0

    def get_burnout_analysis(self, employee_id: UUID) -> BurnoutRiskResponse:
        """Get comprehensive burnout risk analysis"""
        risk_score = self.calculate_risk_score(employee_id)
        risk_level = self._get_risk_level(risk_score)

        # Get detailed factors
        metrics = self._get_recent_metrics(employee_id, days=7)
        factors = {}

        if metrics:
            factors = {
                "overwork": self._normalize_hours(metrics["avg_hours_worked"]),
                "cognitive_overload": metrics["avg_cognitive_load"],
                "social_isolation": self._normalize_isolation(metrics["avg_social_interactions"]),
                "poor_completion": 1.0 - metrics["avg_task_completion_rate"],
                "negative_sentiment": self._normalize_sentiment(metrics["avg_sentiment_score"])
            }

        # Generate recommendations
        recommendations = self._generate_recommendations(risk_score, factors)

        # Calculate trend
        trend = self._calculate_trend(employee_id)

        return BurnoutRiskResponse(
            employee_id=employee_id,
            current_risk_score=risk_score,
            risk_level=risk_level,
            factors=factors,
            recommendations=recommendations,
            trend=trend
        )

    def _get_risk_level(self, score: float) -> str:
        """Convert risk score to categorical level"""
        if score >= 0.8:
            return "critical"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"

    def _generate_recommendations(self, risk_score: float, factors: Dict[str, float]) -> List[str]:
        """Generate actionable recommendations based on risk factors"""
        recommendations = []

        if risk_score >= 0.8:
            recommendations.append("URGENT: Immediate intervention required. Consider task redistribution.")

        if factors.get("overwork", 0) > 0.6:
            recommendations.append("Reduce daily working hours. Block calendar for breaks.")

        if factors.get("cognitive_overload", 0) > 0.7:
            recommendations.append("Delegate complex tasks. Focus on simpler activities temporarily.")

        if factors.get("social_isolation", 0) > 0.6:
            recommendations.append("Schedule team meetings or informal check-ins.")

        if factors.get("poor_completion", 0) > 0.5:
            recommendations.append("Review task assignments. May indicate overload or unclear requirements.")

        if factors.get("negative_sentiment", 0) > 0.6:
            recommendations.append("Schedule 1-on-1 with manager to discuss concerns.")

        if not recommendations:
            recommendations.append("Keep up the good work! Maintain current work-life balance.")

        return recommendations

    def _calculate_trend(self, employee_id: UUID) -> str:
        """Calculate risk trend over time"""
        # Compare last 3 days vs previous 7 days
        recent_risk = self.calculate_risk_score(employee_id, days=3)
        previous_risk = self.calculate_risk_score(employee_id, days=7)

        if recent_risk < previous_risk - 0.1:
            return "improving"
        elif recent_risk > previous_risk + 0.1:
            return "declining"
        else:
            return "stable"

    def trigger_interventions(self, employee_id: UUID):
        """Trigger automatic interventions based on risk level"""
        risk_score = self.calculate_risk_score(employee_id)

        if risk_score >= 0.9:
            self._block_new_tasks(employee_id)
            self._alert_manager(employee_id, "critical")
        elif risk_score >= 0.8:
            self._alert_manager(employee_id, "high")
            self._suggest_delegation(employee_id)
        elif risk_score >= 0.7:
            self._suggest_delegation(employee_id)
        elif risk_score >= 0.5:
            self._insert_micro_breaks(employee_id)

    def _block_new_tasks(self, employee_id: UUID):
        """Prevent new task assignments (would need implementation in task assignment logic)"""
        # This is a placeholder - would integrate with task assignment service
        print(f"ALERT: Blocking new task assignments for employee {employee_id}")

    def _alert_manager(self, employee_id: UUID, severity: str):
        """Send alert to manager (would integrate with notification service)"""
        print(f"ALERT: Manager notified about {severity} burnout risk for employee {employee_id}")

    def _suggest_delegation(self, employee_id: UUID):
        """Suggest tasks that could be delegated"""
        # Find lower priority tasks that could be reassigned
        tasks = self.db.query(Task).filter(
            Task.assigned_to == employee_id,
            Task.status == "pending",
            Task.priority_score < 0.6
        ).order_by(Task.priority_score).limit(3).all()

        print(f"SUGGESTION: Consider delegating tasks: {[t.title for t in tasks]}")

    def _insert_micro_breaks(self, employee_id: UUID):
        """Suggest micro-breaks in schedule"""
        print(f"SUGGESTION: Schedule micro-breaks for employee {employee_id}")

    def update_daily_metric(
        self,
        employee_id: UUID,
        hours_worked: float,
        breaks_taken: int,
        sentiment: Optional[float] = None,
        metric_date: date = None
    ) -> BurnoutMetric:
        """Update or create daily burnout metric"""
        if not metric_date:
            metric_date = date.today()

        # Check if metric exists for today
        existing = self.db.query(BurnoutMetric).filter(
            BurnoutMetric.employee_id == employee_id,
            BurnoutMetric.date == metric_date
        ).first()

        if existing:
            existing.hours_worked = hours_worked
            existing.breaks_taken = breaks_taken
            if sentiment is not None:
                existing.sentiment_score = sentiment
            metric = existing
        else:
            metric = BurnoutMetric(
                employee_id=employee_id,
                date=metric_date,
                hours_worked=hours_worked,
                breaks_taken=breaks_taken,
                sentiment_score=sentiment
            )
            self.db.add(metric)

        # Calculate and update risk score
        self.db.flush()  # Ensure metric is in DB before calculating
        metric.risk_score = self.calculate_risk_score(employee_id)

        self.db.commit()
        self.db.refresh(metric)

        return metric
