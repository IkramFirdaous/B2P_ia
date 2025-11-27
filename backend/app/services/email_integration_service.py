"""Email Integration Service - Automatic email processing and task extraction"""
import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from uuid import UUID
import re
import logging
from sqlalchemy.orm import Session

from app.models import Task, Employee
from app.services.task_extraction_service import TaskExtractionService
from app.services.auto_assignment_service import AutoAssignmentService
from app.services.task_prioritization_service import TaskPrioritizationService


logger = logging.getLogger(__name__)


class EmailIntegrationService:
    """
    Service for integrating with email providers (Gmail, Outlook, etc.)

    Supports:
    - IMAP connection for polling emails
    - Email parsing and content extraction
    - Automatic task creation and assignment
    """

    def __init__(
        self,
        db: Session,
        smtp_host: str,
        smtp_port: int,
        email_address: str,
        password: str,
        use_ssl: bool = True
    ):
        self.db = db
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.email_address = email_address
        self.password = password
        self.use_ssl = use_ssl

        self.imap = None
        self.task_extraction_service = TaskExtractionService()
        self.auto_assignment_service = AutoAssignmentService(db)
        self.priority_service = TaskPrioritizationService(db)

    def connect(self) -> bool:
        """Connect to IMAP server"""
        try:
            if self.use_ssl:
                self.imap = imaplib.IMAP4_SSL(self.smtp_host, self.smtp_port)
            else:
                self.imap = imaplib.IMAP4(self.smtp_host, self.smtp_port)

            self.imap.login(self.email_address, self.password)
            logger.info(f"Successfully connected to {self.email_address}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to email: {e}")
            return False

    def disconnect(self):
        """Disconnect from IMAP server"""
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
            except:
                pass

    def fetch_unread_emails(
        self,
        folder: str = "INBOX",
        max_emails: int = 50
    ) -> List[Dict]:
        """
        Fetch unread emails from specified folder

        Returns list of email dictionaries with parsed content
        """
        if not self.imap:
            raise ConnectionError("Not connected to email server. Call connect() first.")

        try:
            # Select mailbox
            self.imap.select(folder)

            # Search for unread emails
            status, messages = self.imap.search(None, "UNSEEN")

            if status != "OK":
                logger.error("Failed to search for emails")
                return []

            email_ids = messages[0].split()

            # Limit number of emails
            email_ids = email_ids[:max_emails]

            emails = []
            for email_id in email_ids:
                email_data = self._fetch_and_parse_email(email_id)
                if email_data:
                    emails.append(email_data)

            logger.info(f"Fetched {len(emails)} unread emails")
            return emails

        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []

    def _fetch_and_parse_email(self, email_id: bytes) -> Optional[Dict]:
        """Fetch and parse a single email"""
        try:
            # Fetch email
            status, msg_data = self.imap.fetch(email_id, "(RFC822)")

            if status != "OK":
                return None

            # Parse email
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)

            # Extract headers
            subject = self._decode_header_value(email_message["Subject"])
            from_email = self._decode_header_value(email_message["From"])
            date_str = email_message["Date"]
            message_id = email_message["Message-ID"]

            # Parse date
            email_date = None
            if date_str:
                try:
                    email_date = parsedate_to_datetime(date_str)
                except:
                    pass

            # Extract body
            body = self._extract_email_body(email_message)

            # Extract urgency markers from subject
            urgency = self._detect_urgency(subject, body)

            return {
                "id": email_id.decode(),
                "message_id": message_id,
                "subject": subject,
                "from": from_email,
                "date": email_date,
                "body": body,
                "urgency": urgency,
                "raw": email_message
            }

        except Exception as e:
            logger.error(f"Error parsing email {email_id}: {e}")
            return None

    def _decode_header_value(self, header_value: str) -> str:
        """Decode email header value"""
        if not header_value:
            return ""

        decoded_parts = decode_header(header_value)
        decoded_string = ""

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_string += part.decode(encoding or "utf-8", errors="ignore")
            else:
                decoded_string += part

        return decoded_string

    def _extract_email_body(self, email_message) -> str:
        """Extract plain text body from email"""
        body = ""

        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                # Skip attachments
                if "attachment" in content_disposition:
                    continue

                # Get text/plain parts
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        break
                    except:
                        pass
        else:
            # Not multipart
            try:
                body = email_message.get_payload(decode=True).decode("utf-8", errors="ignore")
            except:
                body = str(email_message.get_payload())

        return body.strip()

    def _detect_urgency(self, subject: str, body: str) -> int:
        """
        Detect urgency level from email content (1-5)

        Looks for keywords like URGENT, ASAP, CRITICAL, etc.
        """
        text = f"{subject} {body}".lower()

        # Urgency keywords with levels
        urgency_patterns = {
            5: [r'\burgent\b', r'\bcritical\b', r'\bemergency\b', r'\basap\b', r'\bimmediately\b'],
            4: [r'\bimportant\b', r'\bhigh priority\b', r'\bpriority\b'],
            3: [r'\bsoon\b', r'\bquickly\b'],
            2: [r'\bwhen possible\b', r'\bif possible\b'],
        }

        for level, patterns in urgency_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return level

        return 3  # Default medium urgency

    def process_email_to_tasks(
        self,
        email_data: Dict,
        created_by: UUID,
        team_id: Optional[UUID] = None,
        auto_assign: bool = True
    ) -> List[Dict]:
        """
        Process an email and create tasks automatically

        Args:
            email_data: Parsed email dictionary
            created_by: Employee UUID who "owns" this email processing
            team_id: Target team for auto-assignment
            auto_assign: If True, automatically assign tasks to team members

        Returns:
            List of created task dictionaries
        """
        try:
            # Extract tasks from email
            email_content = f"Subject: {email_data['subject']}\n\n{email_data['body']}"
            task_candidates = self.task_extraction_service.extract_from_email(
                email_body=email_data['body'],
                email_subject=email_data['subject']
            )

            logger.info(f"Extracted {len(task_candidates)} task candidates from email")

            created_tasks = []

            for candidate in task_candidates:
                # Create task in database
                task = Task(
                    title=candidate.title,
                    description=candidate.description,
                    created_by=created_by,
                    urgency=candidate.urgency or email_data.get('urgency', 3),
                    deadline=candidate.deadline,
                    estimated_effort=candidate.estimated_effort,
                    status="pending",
                    source="email",
                    source_metadata={
                        "email_id": email_data.get("message_id"),
                        "email_from": email_data.get("from"),
                        "email_subject": email_data.get("subject"),
                        "email_date": email_data.get("date").isoformat() if email_data.get("date") else None,
                        "confidence": candidate.confidence
                    }
                )

                self.db.add(task)
                self.db.flush()  # Get task ID without committing

                # Auto-assign if requested
                if auto_assign:
                    try:
                        employee_id, assignment_details = self.auto_assignment_service.auto_assign_task(
                            task=task,
                            team_id=team_id
                        )

                        task.assigned_to = employee_id

                        # Calculate priority
                        self.priority_service.update_task_priority(task.id, employee_id)

                        logger.info(f"Auto-assigned task '{task.title}' to employee {employee_id}")

                        created_tasks.append({
                            "task_id": str(task.id),
                            "title": task.title,
                            "assigned_to": str(employee_id),
                            "assignment_score": assignment_details.get("score"),
                            "priority_score": task.priority_score
                        })
                    except Exception as e:
                        logger.warning(f"Failed to auto-assign task: {e}")
                        created_tasks.append({
                            "task_id": str(task.id),
                            "title": task.title,
                            "assigned_to": None,
                            "error": str(e)
                        })
                else:
                    # Task created but not assigned
                    created_tasks.append({
                        "task_id": str(task.id),
                        "title": task.title,
                        "assigned_to": None
                    })

            # Commit all tasks
            self.db.commit()

            logger.info(f"Created {len(created_tasks)} tasks from email")
            return created_tasks

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error processing email to tasks: {e}")
            raise

    def process_inbox(
        self,
        created_by: UUID,
        team_id: Optional[UUID] = None,
        auto_assign: bool = True,
        folder: str = "INBOX",
        max_emails: int = 50
    ) -> Dict:
        """
        Process all unread emails in inbox and create tasks

        Returns summary of processing results
        """
        if not self.connect():
            raise ConnectionError("Failed to connect to email server")

        try:
            # Fetch unread emails
            emails = self.fetch_unread_emails(folder=folder, max_emails=max_emails)

            results = {
                "total_emails": len(emails),
                "total_tasks_created": 0,
                "emails_processed": []
            }

            for email_data in emails:
                try:
                    tasks = self.process_email_to_tasks(
                        email_data=email_data,
                        created_by=created_by,
                        team_id=team_id,
                        auto_assign=auto_assign
                    )

                    results["emails_processed"].append({
                        "email_subject": email_data["subject"],
                        "email_from": email_data["from"],
                        "tasks_created": len(tasks),
                        "tasks": tasks
                    })

                    results["total_tasks_created"] += len(tasks)

                except Exception as e:
                    logger.error(f"Error processing email '{email_data.get('subject')}': {e}")
                    results["emails_processed"].append({
                        "email_subject": email_data["subject"],
                        "error": str(e)
                    })

            return results

        finally:
            self.disconnect()

    def mark_email_as_read(self, email_id: bytes):
        """Mark an email as read"""
        if not self.imap:
            return False

        try:
            self.imap.store(email_id, '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            logger.error(f"Error marking email as read: {e}")
            return False

    def get_email_by_subject(self, subject_pattern: str, folder: str = "INBOX") -> List[Dict]:
        """
        Search for emails by subject pattern

        Useful for testing or finding specific emails
        """
        if not self.imap:
            raise ConnectionError("Not connected to email server")

        try:
            self.imap.select(folder)

            # Search for emails with subject
            status, messages = self.imap.search(None, f'SUBJECT "{subject_pattern}"')

            if status != "OK":
                return []

            email_ids = messages[0].split()

            emails = []
            for email_id in email_ids[:20]:  # Limit to 20
                email_data = self._fetch_and_parse_email(email_id)
                if email_data:
                    emails.append(email_data)

            return emails

        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return []


class GmailIntegrationService(EmailIntegrationService):
    """
    Gmail-specific integration service

    Uses Gmail IMAP settings
    """

    def __init__(self, db: Session, email_address: str, app_password: str):
        super().__init__(
            db=db,
            smtp_host="imap.gmail.com",
            smtp_port=993,
            email_address=email_address,
            password=app_password,
            use_ssl=True
        )


class OutlookIntegrationService(EmailIntegrationService):
    """
    Outlook-specific integration service

    Uses Outlook IMAP settings
    """

    def __init__(self, db: Session, email_address: str, password: str):
        super().__init__(
            db=db,
            smtp_host="outlook.office365.com",
            smtp_port=993,
            email_address=email_address,
            password=password,
            use_ssl=True
        )
