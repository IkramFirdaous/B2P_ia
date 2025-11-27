"""
Email Extraction Orchestration Service
Coordinates the entire email processing pipeline:
1. Fetch emails from Gmail
2. Extract tasks using Gemini AI
3. Save results to database
"""

from typing import Dict, List
from datetime import datetime
from dateutil import parser as date_parser
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from app.models import ExtractedEmail, ExtractedTask, ExtractionStatus
from app.services.gmail_service import GmailService
from app.services.gemini_extraction_service import GeminiExtractionService

logger = logging.getLogger(__name__)


class EmailExtractionService:
    """Orchestrates the email extraction pipeline"""

    def __init__(self, db: Session):
        self.db = db
        self.gmail_service = GmailService(db)
        self.gemini_service = GeminiExtractionService()

    def process_emails(
        self,
        employee_id: str,
        max_emails: int = 20,
        unread_only: bool = False
    ) -> Dict:
        """
        Main orchestration method - fetches emails and extracts tasks

        Args:
            employee_id: Employee ID to fetch emails for
            max_emails: Maximum number of emails to process
            unread_only: Only process unread emails

        Returns:
            Dict with processing statistics
        """
        stats = {
            'emails_fetched': 0,
            'emails_processed': 0,
            'emails_failed': 0,
            'tasks_extracted': 0,
            'errors': []
        }

        try:
            # Step 1: Fetch emails from Gmail
            logger.info(f"Fetching up to {max_emails} emails for employee {employee_id}")
            emails = self.gmail_service.fetch_emails(
                employee_id=employee_id,
                max_emails=max_emails,
                unread_only=unread_only
            )
            stats['emails_fetched'] = len(emails)
            logger.info(f"Fetched {len(emails)} emails")

            # Step 2: Process each email
            for email_data in emails:
                try:
                    self._process_single_email(employee_id, email_data, stats)
                except Exception as e:
                    logger.error(f"Failed to process email {email_data.get('email_id')}: {str(e)}")
                    stats['emails_failed'] += 1
                    stats['errors'].append({
                        'email_id': email_data.get('email_id'),
                        'error': str(e)
                    })

            logger.info(f"Processing complete. Stats: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Email processing failed: {str(e)}")
            stats['errors'].append({'general_error': str(e)})
            return stats

    def _process_single_email(
        self,
        employee_id: str,
        email_data: Dict,
        stats: Dict
    ) -> None:
        """
        Process a single email through the extraction pipeline

        Args:
            employee_id: Employee ID
            email_data: Email data from Gmail API
            stats: Statistics dictionary to update
        """
        # Check if email already processed (duplicate prevention)
        existing_email = self.db.query(ExtractedEmail).filter(
            ExtractedEmail.email_id == email_data['email_id']
        ).first()

        if existing_email:
            logger.info(f"Email {email_data['email_id']} already processed, skipping")
            return

        # Step 2a: Create ExtractedEmail record (status=PROCESSING)
        extracted_email = ExtractedEmail(
            employee_id=employee_id,
            email_id=email_data['email_id'],
            subject=email_data['subject'],
            sender=email_data['sender'],
            received_at=email_data['received_at'],
            raw_content=email_data['content'][:10000],  # Truncate to prevent bloat
            extraction_status=ExtractionStatus.PROCESSING
        )

        self.db.add(extracted_email)
        self.db.flush()  # Get the ID without committing

        try:
            # Step 2b: Extract tasks using Gemini AI
            logger.info(f"Extracting tasks from email: {email_data['subject']}")
            extraction_result = self.gemini_service.extract_from_email(email_data)

            # Step 2c: Save each extracted task
            tasks_count = 0
            for task_data in extraction_result.get('tasks', []):
                extracted_task = ExtractedTask(
                    extracted_email_id=str(extracted_email.id),
                    employee_id=employee_id,
                    task_title=task_data.get('title', 'Untitled Task'),
                    task_description=task_data.get('description', ''),
                    deadline=self._parse_deadline(task_data.get('deadline')),
                    urgency_level=task_data.get('urgency', 3),
                    priority_score=self._calculate_priority(task_data),
                    sentiment_score=extraction_result.get('sentiment_score'),
                    sentiment_label=extraction_result.get('sentiment_label'),
                    confidence_score=task_data.get('confidence', 0.0),
                    approved=False  # ⭐ Requires human review
                )

                self.db.add(extracted_task)
                tasks_count += 1

            # Step 2d: Mark email as completed
            extracted_email.extraction_status = ExtractionStatus.COMPLETED
            extracted_email.extracted_at = datetime.utcnow()

            # Commit all changes for this email
            self.db.commit()

            stats['emails_processed'] += 1
            stats['tasks_extracted'] += tasks_count
            logger.info(f"Successfully extracted {tasks_count} tasks from email {email_data['email_id']}")

        except Exception as e:
            # Mark email as failed
            extracted_email.extraction_status = ExtractionStatus.FAILED
            extracted_email.extraction_error = str(e)
            self.db.commit()

            logger.error(f"Extraction failed for email {email_data['email_id']}: {str(e)}")
            raise

    def _calculate_priority(self, task_data: Dict) -> float:
        """
        Calculate priority score (0-1) based on urgency and confidence

        Args:
            task_data: Task data with urgency and confidence

        Returns:
            Priority score between 0 and 1
        """
        urgency = task_data.get('urgency', 3)  # 1-5 scale
        confidence = task_data.get('confidence', 0.5)  # 0-1 scale

        # Normalize urgency to 0-1 scale and weight with confidence
        urgency_normalized = (urgency - 1) / 4.0  # Convert 1-5 to 0-1
        priority = (urgency_normalized * 0.7) + (confidence * 0.3)

        return round(priority, 2)


    def _parse_deadline(self, deadline_str) -> datetime:
        """
        Parse deadline string to datetime object

        Args:
            deadline_str: ISO format string or None

        Returns:
            datetime object or None
        """
        if not deadline_str:
            return None

        if isinstance(deadline_str, datetime):
            return deadline_str

        try:
            # Parse ISO format string (e.g., "2025-11-28T17:00:00")
            return date_parser.parse(deadline_str)
        except Exception as e:
            logger.warning(f"Failed to parse deadline '{deadline_str}': {e}")
            return None

    def get_extraction_stats(self, employee_id: str) -> Dict:
        """
        Get statistics about email extraction for an employee

        Args:
            employee_id: Employee ID

        Returns:
            Statistics dictionary
        """
        # Count emails by status
        total_emails = self.db.query(ExtractedEmail).filter(
            ExtractedEmail.employee_id == employee_id
        ).count()

        completed_emails = self.db.query(ExtractedEmail).filter(
            ExtractedEmail.employee_id == employee_id,
            ExtractedEmail.extraction_status == ExtractionStatus.COMPLETED
        ).count()

        failed_emails = self.db.query(ExtractedEmail).filter(
            ExtractedEmail.employee_id == employee_id,
            ExtractedEmail.extraction_status == ExtractionStatus.FAILED
        ).count()

        # Count tasks
        total_tasks = self.db.query(ExtractedTask).filter(
            ExtractedTask.employee_id == employee_id
        ).count()

        pending_tasks = self.db.query(ExtractedTask).filter(
            ExtractedTask.employee_id == employee_id,
            ExtractedTask.approved == False
        ).count()

        approved_tasks = self.db.query(ExtractedTask).filter(
            ExtractedTask.employee_id == employee_id,
            ExtractedTask.approved == True
        ).count()

        return {
            'emails': {
                'total': total_emails,
                'completed': completed_emails,
                'failed': failed_emails,
                'processing': total_emails - completed_emails - failed_emails
            },
            'tasks': {
                'total': total_tasks,
                'pending_review': pending_tasks,
                'approved': approved_tasks
            }
        }

    def approve_task(self, task_id: str) -> ExtractedTask:
        """
        Approve an extracted task (ready to create actual Task)

        Args:
            task_id: ExtractedTask ID

        Returns:
            Updated ExtractedTask
        """
        task = self.db.query(ExtractedTask).filter(
            ExtractedTask.id == task_id
        ).first()

        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.approved = True
        task.reviewed_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(task)

        logger.info(f"Task {task_id} approved")
        return task

    def reject_task(self, task_id: str) -> None:
        """
        Reject and delete an extracted task

        Args:
            task_id: ExtractedTask ID
        """
        task = self.db.query(ExtractedTask).filter(
            ExtractedTask.id == task_id
        ).first()

        if not task:
            raise ValueError(f"Task {task_id} not found")

        self.db.delete(task)
        self.db.commit()

        logger.info(f"Task {task_id} rejected and deleted")

    def get_pending_tasks(self, employee_id: str) -> List[ExtractedTask]:
        """
        Get all pending tasks awaiting review

        Args:
            employee_id: Employee ID

        Returns:
            List of pending ExtractedTask objects
        """
        tasks = self.db.query(ExtractedTask).filter(
            ExtractedTask.employee_id == employee_id,
            ExtractedTask.approved == False
        ).order_by(
            ExtractedTask.priority_score.desc(),
            ExtractedTask.created_at.desc()
        ).all()

        return tasks
