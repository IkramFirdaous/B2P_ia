"""Email Extraction Orchestration Service"""
from typing import List, Dict
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.extracted_email import ExtractedEmail, ExtractionStatus
from app.models.extracted_task import ExtractedTask
from app.models.task import Task
from app.services.gmail_service import GmailService
from app.services.gemini_extraction_service import GeminiExtractionService


class EmailExtractionService:
    """Orchestrates the email extraction pipeline"""
    
    def __init__(self, db: Session):
        self.db = db
        self.gmail_service = GmailService(db)
        self.gemini_service = GeminiExtractionService()
    
    def process_emails(
        self,
        employee_id: UUID,
        max_emails: int = 10,
        unread_only: bool = True
    ) -> Dict:
        """
        Main orchestration: fetch emails and extract information
        
        Returns:
            Dictionary with processing results
        """
        results = {
            'emails_fetched': 0,
            'emails_processed': 0,
            'tasks_extracted': 0,
            'errors': []
        }
        
        try:
            # Fetch emails from Gmail
            emails = self.gmail_service.fetch_emails(
                str(employee_id),
                max_results=max_emails,
                unread_only=unread_only
            )
            results['emails_fetched'] = len(emails)
            
            # Process each email
            for email_data in emails:
                try:
                    extracted_email = self._process_single_email(employee_id, email_data)
                    
                    # Skip if None (automated email)
                    if extracted_email is None:
                        continue
                    
                    results['emails_processed'] += 1
                    results['tasks_extracted'] += len(extracted_email.extracted_tasks)
                    
                except Exception as e:
                    error_msg = f"Error processing email {email_data.get('email_id')}: {str(e)}"
                    results['errors'].append(error_msg)
                    print(error_msg)
            
        except Exception as e:
            error_msg = f"Error fetching emails: {str(e)}"
            results['errors'].append(error_msg)
            print(error_msg)
        
        return results
    
    def _process_single_email(self, employee_id: UUID, email_data: Dict) -> ExtractedEmail:
        """Process a single email: extract info and store in database"""
        
        # Skip automated/promotional emails (already filtered by Gmail service)
        if email_data.get('is_automated', False):
            print(f"[WARNING] Skipping automated email from: {email_data.get('sender', 'unknown')}")
            return None
        
        # Check if email already processed
        existing = self.db.query(ExtractedEmail).filter(
            ExtractedEmail.email_id == email_data['email_id']
        ).first()
        
        if existing:
            print(f"Email {email_data['email_id']} already processed, skipping")
            return existing
        
        # Create ExtractedEmail record
        extracted_email = ExtractedEmail(
            employee_id=str(employee_id),  # Convert UUID to string
            email_id=email_data['email_id'],
            subject=email_data.get('subject'),
            sender=email_data.get('sender'),
            received_at=email_data.get('received_at'),
            raw_content=email_data.get('body', '')[:10000],  # Limit size
            extraction_status=ExtractionStatus.PROCESSING
        )
        self.db.add(extracted_email)
        self.db.flush()  # Get ID
        
        try:
            # Extract information using Gemini
            extraction_result = self.gemini_service.extract_from_email(email_data)
            
            # Create ExtractedTask records
            tasks = extraction_result.get('tasks', [])
            sentiment = extraction_result.get('sentiment', {})
            
            for task_data in tasks:
                extracted_task = ExtractedTask(
                    extracted_email_id=extracted_email.id,
                    employee_id=str(employee_id),  # Convert UUID to string
                    task_title=task_data['title'],
                    task_description=task_data.get('description'),
                    deadline=task_data.get('deadline'),
                    urgency_level=task_data.get('urgency'),
                    sentiment_score=sentiment.get('score'),
                    sentiment_label=sentiment.get('label'),
                    confidence_score=task_data.get('confidence'),
                    approved=False
                )
                self.db.add(extracted_task)
            
            # Update email status
            extracted_email.extraction_status = ExtractionStatus.COMPLETED
            extracted_email.extracted_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(extracted_email)
            
        except Exception as e:
            # Mark as failed
            extracted_email.extraction_status = ExtractionStatus.FAILED
            extracted_email.extraction_error = str(e)
            self.db.commit()
            raise
        
        return extracted_email
    
    def approve_and_create_task(
        self,
        extracted_task_id: UUID,
        assigned_to: UUID = None
    ) -> Task:
        """
        Approve extracted task and create actual Task
        
        Args:
            extracted_task_id: ID of the ExtractedTask to approve
            assigned_to: Optional UUID of employee to assign to
            
        Returns:
            Created Task object
        """
        extracted_task = self.db.query(ExtractedTask).filter(
            ExtractedTask.id == extracted_task_id
        ).first()
        
        if not extracted_task:
            raise ValueError("Extracted task not found")
        
        if extracted_task.approved:
            raise ValueError("Task already approved")
        
        # Create actual Task
        task = Task(
            title=extracted_task.task_title,
            description=extracted_task.task_description,
            assigned_to=assigned_to or extracted_task.employee_id,
            created_by=extracted_task.employee_id,
            urgency=extracted_task.urgency_level or 3,
            deadline=extracted_task.deadline,
            estimated_effort=None,  # Not extracted from email
            status='pending',
            priority_score=extracted_task.priority_score or 0.5,
            source='email',
            source_metadata={
                'extracted_email_id': str(extracted_task.extracted_email_id),
                'extracted_task_id': str(extracted_task.id)
            }
        )
        
        self.db.add(task)
        self.db.flush()
        
        # Update extracted task
        extracted_task.approved = True
        extracted_task.reviewed_at = datetime.now()
        extracted_task.created_task_id = task.id
        
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def get_extraction_stats(self, employee_id: UUID) -> Dict:
        """Get statistics about email extractions"""
        # Convert UUID to string for SQLite compatibility
        employee_id_str = str(employee_id)
        
        # Total emails processed
        total_emails = self.db.query(ExtractedEmail).filter(
            ExtractedEmail.employee_id == employee_id_str
        ).count()
        
        # Total tasks extracted
        total_tasks = self.db.query(ExtractedTask).filter(
            ExtractedTask.employee_id == employee_id_str
        ).count()
        
        # Average sentiment
        from sqlalchemy import func
        avg_sentiment = self.db.query(
            func.avg(ExtractedTask.sentiment_score)
        ).filter(
            ExtractedTask.employee_id == employee_id_str,
            ExtractedTask.sentiment_score.isnot(None)
        ).scalar() or 0.0
        
        # Average confidence
        avg_confidence = self.db.query(
            func.avg(ExtractedTask.confidence_score)
        ).filter(
            ExtractedTask.employee_id == employee_id_str,
            ExtractedTask.confidence_score.isnot(None)
        ).scalar() or 0.0
        
        # Pending approvals
        pending = self.db.query(ExtractedTask).filter(
            ExtractedTask.employee_id == employee_id_str,
            ExtractedTask.approved == False
        ).count()
        
        # Approved tasks
        approved = self.db.query(ExtractedTask).filter(
            ExtractedTask.employee_id == employee_id_str,
            ExtractedTask.approved == True
        ).count()
        
        return {
            'total_emails_processed': total_emails,
            'total_tasks_extracted': total_tasks,
            'average_sentiment': float(avg_sentiment),
            'average_confidence': float(avg_confidence),
            'pending_approvals': pending,
            'approved_tasks': approved
        }
    
    def export_dataset(self, employee_id: UUID) -> List[Dict]:
        """Export extracted data as dataset"""
        # Convert UUID to string for SQLite compatibility
        employee_id_str = str(employee_id)
        
        extractions = self.db.query(ExtractedTask, ExtractedEmail).join(
            ExtractedEmail,
            ExtractedTask.extracted_email_id == ExtractedEmail.id
        ).filter(
            ExtractedTask.employee_id == employee_id_str
        ).all()
        
        dataset = []
        for task, email in extractions:
            dataset.append({
                'email_subject': email.subject,
                'email_sender': email.sender,
                'email_received_at': email.received_at.isoformat(),
                'task_title': task.task_title,
                'task_description': task.task_description,
                'deadline': task.deadline.isoformat() if task.deadline else None,
                'urgency_level': task.urgency_level,
                'sentiment_score': task.sentiment_score,
                'sentiment_label': task.sentiment_label,
                'confidence_score': task.confidence_score,
                'approved': task.approved
            })
        
        return dataset

