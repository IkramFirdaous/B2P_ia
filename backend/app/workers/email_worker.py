"""Email Worker - Background task for automatic email processing"""
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.config import settings
from app.services.email_integration_service import (
    GmailIntegrationService,
    OutlookIntegrationService,
    EmailIntegrationService
)
from app.models import Employee


logger = logging.getLogger(__name__)


class EmailWorker:
    """
    Background worker for periodic email processing

    Polls email inbox at regular intervals and automatically:
    1. Fetches unread emails
    2. Extracts tasks using NLP
    3. Auto-assigns tasks to team members
    4. Updates task priorities
    """

    def __init__(
        self,
        check_interval_minutes: int = 5,
        default_team_id: Optional[UUID] = None,
        default_created_by: Optional[UUID] = None
    ):
        """
        Initialize email worker

        Args:
            check_interval_minutes: How often to check for new emails (default: 5 minutes)
            default_team_id: Default team for auto-assignment
            default_created_by: Default employee ID for task creation
        """
        self.check_interval = check_interval_minutes
        self.default_team_id = default_team_id
        self.default_created_by = default_created_by
        self.scheduler = BackgroundScheduler()
        self.is_running = False

        # Email configuration
        self.email_configs = self._load_email_configs()

    def _load_email_configs(self) -> list:
        """
        Load email configurations from settings

        In production, this could load from database or config file
        """
        configs = []

        # Check if email settings are configured
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            configs.append({
                "type": "gmail" if "gmail" in settings.SMTP_HOST else "outlook",
                "email": settings.SMTP_USER,
                "password": settings.SMTP_PASSWORD,
                "enabled": True
            })

        return configs

    def start(self):
        """Start the email worker"""
        if self.is_running:
            logger.warning("Email worker is already running")
            return

        if not self.email_configs:
            logger.warning("No email configurations found. Email worker not started.")
            return

        logger.info(f"Starting email worker (checking every {self.check_interval} minutes)")

        # Schedule email processing job
        self.scheduler.add_job(
            func=self.process_emails_job,
            trigger=IntervalTrigger(minutes=self.check_interval),
            id="email_processing_job",
            name="Process incoming emails",
            replace_existing=True
        )

        self.scheduler.start()
        self.is_running = True

        logger.info("Email worker started successfully")

    def stop(self):
        """Stop the email worker"""
        if not self.is_running:
            return

        logger.info("Stopping email worker")
        self.scheduler.shutdown(wait=True)
        self.is_running = False
        logger.info("Email worker stopped")

    def process_emails_job(self):
        """
        Main job function that processes emails

        This is called periodically by the scheduler
        """
        logger.info(f"[{datetime.now()}] Starting email processing job")

        db = SessionLocal()

        try:
            total_emails = 0
            total_tasks = 0

            for config in self.email_configs:
                if not config.get("enabled"):
                    continue

                try:
                    result = self._process_email_account(db, config)
                    total_emails += result["emails_processed"]
                    total_tasks += result["tasks_created"]

                except Exception as e:
                    logger.error(f"Error processing email account {config['email']}: {e}")

            logger.info(
                f"Email processing job completed: "
                f"{total_emails} emails processed, {total_tasks} tasks created"
            )

        except Exception as e:
            logger.error(f"Error in email processing job: {e}")

        finally:
            db.close()

    def _process_email_account(self, db: Session, config: dict) -> dict:
        """Process a single email account"""
        email_address = config["email"]
        logger.info(f"Processing email account: {email_address}")

        # Determine created_by (find employee with this email or use default)
        created_by = self.default_created_by

        if not created_by:
            employee = db.query(Employee).filter(Employee.email == email_address).first()
            if employee:
                created_by = employee.id
                team_id = employee.team_id or self.default_team_id
            else:
                logger.warning(
                    f"No employee found for email {email_address} and no default_created_by set"
                )
                return {"emails_processed": 0, "tasks_created": 0}
        else:
            # Get team from default creator
            employee = db.query(Employee).filter(Employee.id == created_by).first()
            team_id = employee.team_id if employee else self.default_team_id

        # Create appropriate email service
        if config["type"] == "gmail":
            email_service = GmailIntegrationService(
                db=db,
                email_address=config["email"],
                app_password=config["password"]
            )
        elif config["type"] == "outlook":
            email_service = OutlookIntegrationService(
                db=db,
                email_address=config["email"],
                password=config["password"]
            )
        else:
            logger.error(f"Unknown email type: {config['type']}")
            return {"emails_processed": 0, "tasks_created": 0}

        # Process inbox
        try:
            results = email_service.process_inbox(
                created_by=created_by,
                team_id=team_id,
                auto_assign=True,
                folder="INBOX",
                max_emails=50
            )

            return {
                "emails_processed": results["total_emails"],
                "tasks_created": results["total_tasks_created"]
            }

        except Exception as e:
            logger.error(f"Error processing inbox for {email_address}: {e}")
            return {"emails_processed": 0, "tasks_created": 0}

    def process_now(self):
        """
        Manually trigger email processing immediately

        Useful for testing or manual triggers
        """
        logger.info("Manual email processing triggered")
        self.process_emails_job()


# Global worker instance
_email_worker: Optional[EmailWorker] = None


def get_email_worker(
    check_interval_minutes: int = 5,
    default_team_id: Optional[UUID] = None,
    default_created_by: Optional[UUID] = None
) -> EmailWorker:
    """
    Get or create the global email worker instance

    This ensures only one worker is running
    """
    global _email_worker

    if _email_worker is None:
        _email_worker = EmailWorker(
            check_interval_minutes=check_interval_minutes,
            default_team_id=default_team_id,
            default_created_by=default_created_by
        )

    return _email_worker


def start_email_worker(
    check_interval_minutes: int = 5,
    default_team_id: Optional[UUID] = None,
    default_created_by: Optional[UUID] = None
):
    """
    Start the email worker

    Call this from your application startup
    """
    worker = get_email_worker(
        check_interval_minutes=check_interval_minutes,
        default_team_id=default_team_id,
        default_created_by=default_created_by
    )

    worker.start()
    return worker


def stop_email_worker():
    """Stop the email worker"""
    global _email_worker

    if _email_worker:
        _email_worker.stop()
        _email_worker = None
