"""
Configuration for NLP Task Extractor
"""
from typing import Optional, List, Dict
from pathlib import Path
from pydantic import BaseModel, Field


class NLPConfig(BaseModel):
    """Configuration for NLP models and processing"""

    # Model paths
    spacy_model: str = Field(
        default="fr_core_news_lg",
        description="spaCy model to use (fr_core_news_lg for French, en_core_web_lg for English)"
    )

    custom_ner_model: Optional[Path] = Field(
        default=None,
        description="Path to custom trained NER model"
    )

    # Language settings
    primary_language: str = Field(
        default="fr",
        description="Primary language (fr or en)"
    )

    support_multilingual: bool = Field(
        default=True,
        description="Support multiple languages in the same text"
    )

    # Task extraction parameters
    min_confidence: float = Field(
        default=0.6,
        description="Minimum confidence score for task extraction (0-1)"
    )

    max_task_length: int = Field(
        default=200,
        description="Maximum length of extracted task title"
    )

    min_task_words: int = Field(
        default=4,
        description="Minimum number of words for a valid task"
    )

    # Entity labels
    custom_entity_labels: List[str] = Field(
        default=["TASK_ACTION", "DEADLINE", "ASSIGNEE", "PROJECT", "PRIORITY"],
        description="Custom entity labels for task extraction"
    )

    # Action verbs
    action_verbs_fr: List[str] = Field(
        default=[
            "faire", "créer", "analyser", "préparer", "rédiger", "développer",
            "implémenter", "tester", "réviser", "vérifier", "envoyer", "contacter",
            "organiser", "planifier", "mettre en place", "finaliser", "compléter",
            "documenter", "présenter", "reviewer", "valider", "déployer", "installer",
            "configurer", "résoudre", "corriger", "améliorer", "optimiser"
        ],
        description="French action verbs that indicate tasks"
    )

    action_verbs_en: List[str] = Field(
        default=[
            "create", "develop", "implement", "design", "write", "prepare",
            "analyze", "test", "review", "send", "contact", "organize",
            "plan", "setup", "finalize", "complete", "document", "present",
            "validate", "update", "fix", "deploy", "install", "configure",
            "resolve", "improve", "optimize", "build", "integrate"
        ],
        description="English action verbs that indicate tasks"
    )

    # Urgency keywords mapping
    urgency_keywords: Dict[int, List[str]] = Field(
        default={
            5: ["urgent", "asap", "immédiat", "critique", "emergency", "critical"],
            4: ["important", "prioritaire", "priority", "soon", "rapidement"],
            3: ["normal", "standard", "regular"],
            2: ["when possible", "si possible", "low priority", "low"],
            1: ["someday", "eventually", "un jour", "later"]
        },
        description="Keywords mapped to urgency levels (1-5)"
    )

    # Deadline patterns
    deadline_patterns: List[tuple] = Field(
        default=[
            (r"avant (?:le )?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", "before_date"),
            (r"by (\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", "by_date"),
            (r"pour (?:le )?(\d{1,2}[/-]\d{1,2})", "for_date"),
            (r"(aujourd'hui|today)", "today"),
            (r"(demain|tomorrow)", "tomorrow"),
            (r"cette semaine|this week", "this_week"),
            (r"la semaine prochaine|next week", "next_week"),
            (r"dans (\d+) jours?", "in_x_days"),
            (r"in (\d+) days?", "in_x_days"),
            (r"(\d{1,2})/(\d{1,2})/(\d{2,4})", "date_slash"),
            (r"(\d{1,2})-(\d{1,2})-(\d{2,4})", "date_dash"),
        ],
        description="Regex patterns for detecting deadlines"
    )

    # Processing settings
    enable_dependency_parsing: bool = Field(
        default=True,
        description="Enable dependency parsing for better action-object extraction"
    )

    enable_sentiment_analysis: bool = Field(
        default=True,
        description="Enable sentiment analysis for cognitive load estimation"
    )

    enable_caching: bool = Field(
        default=True,
        description="Cache processed documents for better performance"
    )

    cache_size: int = Field(
        default=100,
        description="Maximum number of documents to cache"
    )

    # Training settings
    training_data_path: Optional[Path] = Field(
        default=Path("backend/app/ml/nlp_task_extractor/data/training"),
        description="Path to training data directory"
    )

    model_output_path: Optional[Path] = Field(
        default=Path("backend/app/ml/nlp_task_extractor/models"),
        description="Path to save trained models"
    )

    class Config:
        arbitrary_types_allowed = True


# Default configuration instance
default_config = NLPConfig()
