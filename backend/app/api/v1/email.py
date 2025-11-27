"""Email Integration API Endpoints"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models import Employee
from app.services.email_integration_service import (
    GmailIntegrationService,
    OutlookIntegrationService
)
from app.workers.email_worker import get_email_worker


router = APIRouter()


# Request/Response Schemas

class EmailProcessRequest(BaseModel):
    """Request to process emails manually"""
    email_address: EmailStr
    password: str
    provider: str = "gmail"  # gmail or outlook
    folder: str = "INBOX"
    max_emails: int = 50
    auto_assign: bool = True
    team_id: Optional[UUID] = None


class EmailProcessResponse(BaseModel):
    """Response from email processing"""
    total_emails: int
    total_tasks_created: int
    emails_processed: list


class WebhookEmailData(BaseModel):
    """Webhook data for incoming email (for future webhook integration)"""
    subject: str
    from_email: EmailStr
    body: str
    received_at: str
    message_id: Optional[str] = None


class WorkerStatusResponse(BaseModel):
    """Worker status response"""
    is_running: bool
    check_interval_minutes: int
    email_accounts_configured: int


class WorkerControlRequest(BaseModel):
    """Request to control worker"""
    check_interval_minutes: int = 5
    default_team_id: Optional[UUID] = None
    default_created_by: Optional[UUID] = None


# Manual Email Processing Endpoints

@router.post("/email/process", response_model=EmailProcessResponse)
def process_emails_manually(
    request: EmailProcessRequest,
    db: Session = Depends(get_db)
):
    """
    Manually process emails from an inbox

    This endpoint allows you to manually trigger email processing
    without setting up the automatic worker.

    Useful for:
    - Testing
    - One-time imports
    - Manual processing
    """
    # Find employee by email or use first employee
    employee = db.query(Employee).filter(Employee.email == request.email_address).first()

    if not employee:
        # Use first employee as default
        employee = db.query(Employee).first()
        if not employee:
            raise HTTPException(
                status_code=400,
                detail="No employees found in database"
            )

    created_by = employee.id
    team_id = request.team_id or employee.team_id

    # Create appropriate email service
    if request.provider == "gmail":
        email_service = GmailIntegrationService(
            db=db,
            email_address=request.email_address,
            app_password=request.password
        )
    elif request.provider == "outlook":
        email_service = OutlookIntegrationService(
            db=db,
            email_address=request.email_address,
            password=request.password
        )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown email provider: {request.provider}"
        )

    try:
        results = email_service.process_inbox(
            created_by=created_by,
            team_id=team_id,
            auto_assign=request.auto_assign,
            folder=request.folder,
            max_emails=request.max_emails
        )

        return EmailProcessResponse(
            total_emails=results["total_emails"],
            total_tasks_created=results["total_tasks_created"],
            emails_processed=results["emails_processed"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing emails: {str(e)}"
        )


@router.post("/email/webhook/incoming")
def receive_email_webhook(
    webhook_data: WebhookEmailData,
    team_id: Optional[UUID] = None,
    created_by: Optional[UUID] = None,
    auto_assign: bool = True,
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for receiving emails from external services

    This can be used with services like:
    - SendGrid Inbound Parse
    - Mailgun Routes
    - Zapier Email Parser
    - Custom email forwarding

    The webhook should send email data in the specified format.
    """
    from app.services.task_extraction_service import TaskExtractionService
    from app.services.auto_assignment_service import AutoAssignmentService
    from app.services.task_prioritization_service import TaskPrioritizationService
    from app.models import Task

    # Find employee if not specified
    if not created_by:
        employee = db.query(Employee).filter(
            Employee.email == webhook_data.from_email
        ).first()

        if not employee:
            employee = db.query(Employee).first()

        if not employee:
            raise HTTPException(status_code=400, detail="No employee found")

        created_by = employee.id
        team_id = team_id or employee.team_id

    # Extract tasks
    extraction_service = TaskExtractionService()
    task_candidates = extraction_service.extract_from_email(
        email_body=webhook_data.body,
        email_subject=webhook_data.subject
    )

    created_tasks = []

    for candidate in task_candidates:
        task = Task(
            title=candidate.title,
            description=candidate.description,
            created_by=created_by,
            urgency=candidate.urgency or 3,
            deadline=candidate.deadline,
            estimated_effort=candidate.estimated_effort,
            status="pending",
            source="email",
            source_metadata={
                "email_from": webhook_data.from_email,
                "email_subject": webhook_data.subject,
                "received_at": webhook_data.received_at,
                "message_id": webhook_data.message_id,
                "confidence": candidate.confidence
            }
        )

        db.add(task)
        db.flush()

        # Auto-assign if requested
        if auto_assign and team_id:
            auto_service = AutoAssignmentService(db)
            try:
                employee_id, _ = auto_service.auto_assign_task(task, team_id=team_id)
                task.assigned_to = employee_id

                # Calculate priority
                priority_service = TaskPrioritizationService(db)
                priority_service.update_task_priority(task.id, employee_id)

            except Exception as e:
                # Continue even if auto-assignment fails
                pass

        created_tasks.append({
            "task_id": str(task.id),
            "title": task.title,
            "assigned_to": str(task.assigned_to) if task.assigned_to else None
        })

    db.commit()

    return {
        "tasks_created": len(created_tasks),
        "tasks": created_tasks
    }


# Worker Control Endpoints

@router.get("/email/worker/status", response_model=WorkerStatusResponse)
def get_worker_status():
    """Get the current status of the email worker"""
    worker = get_email_worker()

    # Count configured email accounts
    email_accounts = 1 if settings.SMTP_USER and settings.SMTP_PASSWORD else 0

    return WorkerStatusResponse(
        is_running=worker.is_running,
        check_interval_minutes=worker.check_interval,
        email_accounts_configured=email_accounts
    )


@router.post("/email/worker/start")
def start_worker(request: WorkerControlRequest):
    """
    Start the automatic email worker

    The worker will periodically check for new emails and process them
    """
    from app.workers.email_worker import start_email_worker

    worker = start_email_worker(
        check_interval_minutes=request.check_interval_minutes,
        default_team_id=request.default_team_id,
        default_created_by=request.default_created_by
    )

    return {
        "message": "Email worker started successfully",
        "check_interval_minutes": worker.check_interval,
        "is_running": worker.is_running
    }


@router.post("/email/worker/stop")
def stop_worker():
    """Stop the automatic email worker"""
    from app.workers.email_worker import stop_email_worker

    stop_email_worker()

    return {
        "message": "Email worker stopped successfully"
    }


@router.post("/email/worker/process-now")
def trigger_worker_now():
    """
    Manually trigger the email worker to process emails immediately

    Useful for testing or forcing an immediate check
    """
    worker = get_email_worker()

    if not worker.is_running:
        raise HTTPException(
            status_code=400,
            detail="Worker is not running. Start it first or use /email/process endpoint"
        )

    # Run in background
    worker.process_now()

    return {
        "message": "Email processing triggered successfully"
    }


# Test Endpoints

@router.get("/email/test-connection")
def test_email_connection(
    email_address: str,
    password: str,
    provider: str = "gmail"
):
    """
    Test email connection without processing

    Returns success or error message
    """
    from app.core.database import SessionLocal

    db = SessionLocal()

    try:
        if provider == "gmail":
            service = GmailIntegrationService(db, email_address, password)
        elif provider == "outlook":
            service = OutlookIntegrationService(db, email_address, password)
        else:
            raise HTTPException(status_code=400, detail="Unknown provider")

        if service.connect():
            service.disconnect()
            return {
                "success": True,
                "message": f"Successfully connected to {email_address}"
            }
        else:
            return {
                "success": False,
                "message": "Failed to connect"
            }

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

    finally:
        db.close()
