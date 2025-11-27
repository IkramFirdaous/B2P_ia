"""
NLP Task Extractor Module

This module provides advanced NLP capabilities for extracting tasks from text,
including emails, meeting notes, and other unstructured content.

Main components:
- TaskExtractor: Main class for extracting tasks using spaCy and custom models
- EntityRecognizer: Custom NER for task-specific entities
- IntentClassifier: Classify text intent (task assignment, status update, etc.)
- DeadlineExtractor: Extract and parse deadline information
"""

from .extractor import TaskExtractor, TaskEntity
from .config import NLPConfig

__all__ = ["TaskExtractor", "TaskEntity", "NLPConfig"]
