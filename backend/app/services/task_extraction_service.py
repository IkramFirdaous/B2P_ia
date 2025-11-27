"""Task Extraction Service - NLP-powered task extraction from text"""
from typing import List, Optional
from app.schemas.task_schema import TaskCandidate
from app.models.task import TaskSource
from app.ml.nlp_task_extractor.extractor import TaskExtractor, TaskEntity


class TaskExtractionService:
    """Service for extracting tasks from emails, meetings, and other text sources

    This service wraps the sophisticated NLP TaskExtractor and converts results
    to the TaskCandidate schema used by the API.
    """

    def __init__(self):
        """Initialize the service with the NLP task extractor"""
        self.extractor = TaskExtractor()

    def extract_from_email(self, email_body: str, email_subject: str = "") -> List[TaskCandidate]:
        """Extract tasks from email content"""
        full_text = f"{email_subject}\n\n{email_body}" if email_subject else email_body
        task_entities = self.extractor.extract_tasks(full_text, source_type="email")
        return [self._convert_to_candidate(entity) for entity in task_entities]

    def extract_from_meeting(self, meeting_notes: str, meeting_title: str = "") -> List[TaskCandidate]:
        """Extract action items from meeting notes"""
        full_text = f"{meeting_title}\n\n{meeting_notes}" if meeting_title else meeting_notes
        task_entities = self.extractor.extract_tasks(full_text, source_type="meeting")
        return [self._convert_to_candidate(entity) for entity in task_entities]

    def _convert_to_candidate(self, entity: TaskEntity) -> TaskCandidate:
        """Convert TaskEntity from NLP extractor to TaskCandidate schema"""
        return TaskCandidate(
            title=entity.text,
            description=entity.object,  # Use extracted object as description
            urgency=entity.urgency,
            estimated_effort=entity.estimated_effort,
            deadline=entity.deadline,
            confidence=entity.confidence
        )
