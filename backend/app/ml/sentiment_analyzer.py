"""Sentiment Analysis ML Model"""
from typing import Optional, Dict
import re


class SentimentAnalyzer:
    """
    Sentiment analysis for employee communications

    In production, this would use a pre-trained transformer model like:
    - CamemBERT for French
    - BERT/RoBERTa for English

    For now, using lexicon-based approach as placeholder
    """

    def __init__(self):
        # Positive sentiment keywords
        self.positive_keywords = {
            # French
            "excellent", "super", "génial", "parfait", "merci", "bien",
            "content", "heureux", "satisfait", "efficace", "réussi",
            # English
            "great", "excellent", "good", "thanks", "happy", "pleased",
            "successful", "effective", "awesome", "perfect"
        }

        # Negative sentiment keywords
        self.negative_keywords = {
            # French
            "difficile", "problème", "inquiet", "stressé", "fatigué",
            "débordé", "compliqué", "impossible", "frustré", "désolé",
            # English
            "difficult", "problem", "worried", "stressed", "tired",
            "overwhelmed", "complicated", "impossible", "frustrated", "sorry"
        }

        # Intensifiers
        self.intensifiers = {"très", "vraiment", "extremely", "very", "really"}

        # Negations
        self.negations = {"pas", "non", "ne", "not", "no", "never"}

    def analyze_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of text

        Returns: float between -1 (very negative) and 1 (very positive)
        """
        if not text or len(text.strip()) == 0:
            return 0.0

        # Normalize text
        text_lower = text.lower()
        words = self._tokenize(text_lower)

        # Calculate sentiment score
        score = 0.0

        for i, word in enumerate(words):
            word_score = 0.0

            # Check if positive
            if word in self.positive_keywords:
                word_score = 1.0
            # Check if negative
            elif word in self.negative_keywords:
                word_score = -1.0

            # Apply intensifier if present
            if i > 0 and words[i-1] in self.intensifiers:
                word_score *= 1.5

            # Apply negation if present
            if i > 0 and words[i-1] in self.negations:
                word_score *= -1

            score += word_score

        # Normalize by text length
        if len(words) > 0:
            score = score / len(words) * 10  # Scale factor

        # Clamp between -1 and 1
        score = max(-1.0, min(1.0, score))

        return score

    def analyze_batch(self, texts: list[str]) -> list[float]:
        """Analyze sentiment for multiple texts"""
        return [self.analyze_sentiment(text) for text in texts]

    def get_sentiment_category(self, score: float) -> str:
        """Convert sentiment score to category"""
        if score >= 0.3:
            return "positive"
        elif score <= -0.3:
            return "negative"
        else:
            return "neutral"

    def analyze_with_details(self, text: str) -> Dict:
        """Analyze sentiment with detailed breakdown"""
        score = self.analyze_sentiment(text)
        category = self.get_sentiment_category(score)

        # Find keywords that contributed
        text_lower = text.lower()
        words = self._tokenize(text_lower)

        positive_found = [w for w in words if w in self.positive_keywords]
        negative_found = [w for w in words if w in self.negative_keywords]

        return {
            "score": score,
            "category": category,
            "confidence": abs(score),  # How strong the sentiment is
            "positive_keywords": positive_found,
            "negative_keywords": negative_found
        }

    def _tokenize(self, text: str) -> list[str]:
        """Simple word tokenization"""
        # Remove punctuation and split
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        return [w.strip() for w in words if len(w.strip()) > 2]

    def calculate_employee_sentiment_trend(
        self,
        recent_communications: list[str]
    ) -> Dict:
        """
        Calculate sentiment trend from employee's recent communications

        Args:
            recent_communications: List of text communications (emails, messages, etc.)

        Returns:
            Dict with trend analysis
        """
        if not recent_communications:
            return {
                "average_sentiment": 0.0,
                "trend": "neutral",
                "data_points": 0
            }

        sentiments = self.analyze_batch(recent_communications)

        avg_sentiment = sum(sentiments) / len(sentiments)

        # Calculate trend (are recent messages more positive or negative?)
        if len(sentiments) >= 3:
            recent_avg = sum(sentiments[-3:]) / 3
            older_avg = sum(sentiments[:-3]) / len(sentiments[:-3]) if len(sentiments) > 3 else avg_sentiment

            if recent_avg > older_avg + 0.1:
                trend = "improving"
            elif recent_avg < older_avg - 0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "average_sentiment": avg_sentiment,
            "trend": trend,
            "data_points": len(sentiments),
            "recent_scores": sentiments[-5:],  # Last 5 scores
            "category": self.get_sentiment_category(avg_sentiment)
        }
