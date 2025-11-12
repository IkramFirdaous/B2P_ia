"""Burnout Prediction ML Model"""
from typing import List, Dict, Optional
import numpy as np


class BurnoutPredictor:
    """
    Machine Learning model for predicting burnout risk

    In production, this would be a trained scikit-learn or neural network model
    trained on historical employee data with features like:
    - Hours worked patterns
    - Task completion rates
    - Sentiment trends
    - Social interaction frequency
    - Historical burnout cases

    For now, using a rule-based scoring system
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        # In production: self.model = joblib.load(model_path)
        print(f"BurnoutPredictor initialized (placeholder mode)")

    def predict_risk(self, features: Dict) -> float:
        """
        Predict burnout risk from employee features

        Args:
            features: Dict containing:
                - hours_worked_7d: Avg hours worked in last 7 days
                - hours_worked_30d: Avg hours worked in last 30 days
                - task_completion_rate: 0-1 scale
                - cognitive_load: 0-1 scale
                - social_interactions: Count per day
                - sentiment_score: -1 to 1
                - breaks_taken: Count per day
                - weekend_work: Boolean
                - late_night_work: Boolean

        Returns:
            Risk score 0-1 (higher = more risk)
        """
        # Extract features with defaults
        hours_7d = features.get("hours_worked_7d", 8.0)
        hours_30d = features.get("hours_worked_30d", 8.0)
        completion = features.get("task_completion_rate", 1.0)
        cognitive = features.get("cognitive_load", 0.5)
        social = features.get("social_interactions", 5)
        sentiment = features.get("sentiment_score", 0.0)
        breaks = features.get("breaks_taken", 3)
        weekend_work = features.get("weekend_work", False)
        late_night = features.get("late_night_work", False)

        # Calculate risk score (placeholder algorithm)
        risk = 0.0

        # Overwork indicators
        if hours_7d > 10:
            risk += 0.3
        elif hours_7d > 9:
            risk += 0.15

        if hours_30d > 9:
            risk += 0.2

        # Increasing hours trend
        if hours_7d > hours_30d + 1:
            risk += 0.15

        # Poor completion rate
        if completion < 0.7:
            risk += 0.2

        # High cognitive load
        if cognitive > 0.8:
            risk += 0.2
        elif cognitive > 0.6:
            risk += 0.1

        # Social isolation
        if social < 3:
            risk += 0.2
        elif social < 5:
            risk += 0.1

        # Negative sentiment
        if sentiment < -0.3:
            risk += 0.2
        elif sentiment < 0:
            risk += 0.1

        # Insufficient breaks
        if breaks < 2:
            risk += 0.15

        # Weekend/late work
        if weekend_work:
            risk += 0.15
        if late_night:
            risk += 0.15

        # Clamp to 0-1
        risk = min(max(risk, 0.0), 1.0)

        return risk

    def predict_batch(self, features_list: List[Dict]) -> List[float]:
        """Predict burnout risk for multiple employees"""
        return [self.predict_risk(features) for features in features_list]

    def get_risk_factors(self, features: Dict) -> Dict[str, float]:
        """
        Identify which factors contribute most to burnout risk

        Returns dict of factor names to contribution scores
        """
        factors = {}

        hours_7d = features.get("hours_worked_7d", 8.0)
        hours_30d = features.get("hours_worked_30d", 8.0)
        completion = features.get("task_completion_rate", 1.0)
        cognitive = features.get("cognitive_load", 0.5)
        social = features.get("social_interactions", 5)
        sentiment = features.get("sentiment_score", 0.0)
        breaks = features.get("breaks_taken", 3)

        # Calculate individual factor contributions
        if hours_7d > 9:
            factors["excessive_hours"] = min((hours_7d - 8) / 4, 1.0)

        if cognitive > 0.6:
            factors["high_cognitive_load"] = cognitive

        if social < 5:
            factors["social_isolation"] = (5 - social) / 5

        if sentiment < 0:
            factors["negative_sentiment"] = abs(sentiment)

        if completion < 0.8:
            factors["poor_completion_rate"] = 1 - completion

        if breaks < 3:
            factors["insufficient_breaks"] = (3 - breaks) / 3

        return factors

    def recommend_interventions(self, risk_score: float, features: Dict) -> List[str]:
        """
        Recommend specific interventions based on risk factors

        Returns list of actionable recommendations
        """
        recommendations = []

        factors = self.get_risk_factors(features)

        if "excessive_hours" in factors and factors["excessive_hours"] > 0.5:
            recommendations.append("Reduce working hours - aim for 8 hours per day maximum")
            recommendations.append("Block calendar after 6 PM to ensure work-life balance")

        if "high_cognitive_load" in factors:
            recommendations.append("Delegate complex tasks to reduce cognitive burden")
            recommendations.append("Take regular mental breaks (5 min every hour)")

        if "social_isolation" in factors:
            recommendations.append("Schedule team coffee breaks or social activities")
            recommendations.append("Increase face-to-face or video communication")

        if "negative_sentiment" in factors:
            recommendations.append("Schedule 1-on-1 with manager for support")
            recommendations.append("Consider employee assistance program or counseling")

        if "poor_completion_rate" in factors:
            recommendations.append("Review current workload and priorities")
            recommendations.append("Break large tasks into smaller, manageable pieces")

        if "insufficient_breaks" in factors:
            recommendations.append("Use Pomodoro technique (25 min work, 5 min break)")
            recommendations.append("Schedule mandatory lunch breaks away from desk")

        # General recommendations for high risk
        if risk_score > 0.8:
            recommendations.insert(0, "URGENT: Immediate intervention needed - consider temporary leave")
        elif risk_score > 0.6:
            recommendations.insert(0, "HIGH RISK: Reduce workload by 30-40% immediately")

        return recommendations

    def train_model(self, training_data: List[Dict], labels: List[float]):
        """
        Train the burnout prediction model

        Args:
            training_data: List of feature dicts
            labels: List of actual burnout scores (0-1)

        This is a placeholder - in production would train sklearn model
        """
        # Placeholder for model training
        # In production:
        # X = self._prepare_features(training_data)
        # self.model.fit(X, labels)
        # joblib.dump(self.model, self.model_path)

        print(f"Model training placeholder - would train on {len(training_data)} samples")

    def _prepare_features(self, features_dict: Dict) -> np.ndarray:
        """Convert feature dict to numpy array for sklearn"""
        # Placeholder for feature engineering
        feature_vector = [
            features_dict.get("hours_worked_7d", 8.0),
            features_dict.get("hours_worked_30d", 8.0),
            features_dict.get("task_completion_rate", 1.0),
            features_dict.get("cognitive_load", 0.5),
            features_dict.get("social_interactions", 5),
            features_dict.get("sentiment_score", 0.0),
            features_dict.get("breaks_taken", 3),
            1.0 if features_dict.get("weekend_work", False) else 0.0,
            1.0 if features_dict.get("late_night_work", False) else 0.0,
        ]

        return np.array(feature_vector)
