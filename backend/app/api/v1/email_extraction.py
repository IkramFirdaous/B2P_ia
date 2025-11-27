"""
Email Extraction API Endpoints
Handles email fetching, task extraction, and review workflow
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import datetime
import math

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Employee, ExtractedEmail, ExtractedTask, Task, ExtractionStatus
from app.schemas.email_extraction_schema import (
    EmailFetchRequest,
    EmailProcessingResponse,
    ExtractedTaskResponse,
    ExtractedEmailResponse,
    ExtractionStatsResponse,
    TaskApprovalRequest,
    TaskApprovalResponse,
    PaginatedTasksResponse,
    PaginatedEmailsResponse,
    TaskDatasetExport
)
from app.services.email_extraction_service import EmailExtractionService


router = APIRouter()


# ============================================================================
# Email Processing Endpoints
# ============================================================================

@router.post("/email-extraction/fetch", response_model=EmailProcessingResponse)
def fetch_and_process_emails(
    request: EmailFetchRequest,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ⭐ MAIN ACTION - Fetch emails from Gmail and extract tasks using AI

    This endpoint:
    1. Fetches emails from user's Gmail account
    2. Filters out promotional/automated emails
    3. Uses Gemini AI to extract tasks from each email
    4. Saves extracted tasks to database for review

    Args:
        request: Email fetch configuration (max_emails, unread_only)
        current_user: Authenticated employee
        db: Database session

    Returns:
        Processing statistics
    """
    try:
        extraction_service = EmailExtractionService(db)

        # Process emails
        stats = extraction_service.process_emails(
            employee_id=str(current_user.id),
            max_emails=request.max_emails,
            unread_only=request.unread_only
        )

        # Build response message
        message = (
            f"Processed {stats['emails_processed']} emails, "
            f"extracted {stats['tasks_extracted']} tasks"
        )

        if stats['emails_failed'] > 0:
            message += f" ({stats['emails_failed']} emails failed)"

        return EmailProcessingResponse(
            success=True,
            message=message,
            stats=stats
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email processing failed: {str(e)}"
        )


@router.get("/email-extraction/stats", response_model=ExtractionStatsResponse)
def get_extraction_stats(
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics about email extraction for current user

    Returns counts of emails and tasks by status
    """
    extraction_service = EmailExtractionService(db)
    stats = extraction_service.get_extraction_stats(str(current_user.id))

    return ExtractionStatsResponse(**stats)


# ============================================================================
# Task Review Endpoints
# ============================================================================

@router.get("/email-extraction/tasks", response_model=PaginatedTasksResponse)
def get_extracted_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    approved: Optional[bool] = Query(None, description="Filter by approval status"),
    min_urgency: Optional[int] = Query(None, ge=1, le=5, description="Minimum urgency level"),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get extracted tasks for review

    Returns paginated list of tasks extracted from emails,
    sorted by priority score (highest first)

    Args:
        page: Page number (1-indexed)
        page_size: Items per page (max 100)
        approved: Filter by approval status
        min_urgency: Filter by minimum urgency level
        current_user: Authenticated employee
        db: Database session

    Returns:
        Paginated list of extracted tasks
    """
    # Build query
    query = db.query(ExtractedTask).filter(
        ExtractedTask.employee_id == str(current_user.id)
    )

    # Apply filters
    if approved is not None:
        query = query.filter(ExtractedTask.approved == approved)

    if min_urgency is not None:
        query = query.filter(ExtractedTask.urgency_level >= min_urgency)

    # Get total count
    total = query.count()

    # Calculate pagination
    total_pages = math.ceil(total / page_size)
    offset = (page - 1) * page_size

    # Get paginated results with eager loading of extracted_email
    tasks = query.options(joinedload(ExtractedTask.extracted_email)).order_by(
        ExtractedTask.priority_score.desc(),
        ExtractedTask.created_at.desc()
    ).offset(offset).limit(page_size).all()

    # Enrich with email data
    task_responses = []
    for task in tasks:
        task_dict = {
            "id": str(task.id),
            "extracted_email_id": str(task.extracted_email_id),
            "employee_id": str(task.employee_id),
            "task_title": task.task_title,
            "task_description": task.task_description,
            "deadline": task.deadline,
            "urgency_level": task.urgency_level,
            "priority_score": task.priority_score,
            "sentiment_score": task.sentiment_score,
            "sentiment_label": task.sentiment_label,
            "confidence_score": task.confidence_score,
            "approved": task.approved,
            "reviewed_at": task.reviewed_at,
            "created_task_id": str(task.created_task_id) if task.created_task_id else None,
            "created_at": task.created_at,
            "email_subject": task.extracted_email.subject if task.extracted_email else None,
            "email_sender": task.extracted_email.sender if task.extracted_email else None
        }
        task_responses.append(ExtractedTaskResponse(**task_dict))

    return PaginatedTasksResponse(
        tasks=task_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("/email-extraction/tasks/{task_id}/approve", response_model=TaskApprovalResponse)
def approve_extracted_task(
    task_id: str,
    request: TaskApprovalRequest,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve an extracted task

    Optionally creates an actual Task in the main system

    Args:
        task_id: ExtractedTask ID
        request: Approval configuration
        current_user: Authenticated employee
        db: Database session

    Returns:
        Approval result
    """
    extraction_service = EmailExtractionService(db)

    # Get the extracted task
    extracted_task = db.query(ExtractedTask).filter(
        ExtractedTask.id == task_id,
        ExtractedTask.employee_id == str(current_user.id)
    ).first()

    if not extracted_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if extracted_task.approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task already approved"
        )

    # Approve the task
    approved_task = extraction_service.approve_task(task_id)

    created_task_id = None

    # Optionally create actual Task
    if request.create_task:
        try:
            # Create Task in main system
            new_task = Task(
                title=approved_task.task_title,
                description=approved_task.task_description,
                deadline=approved_task.deadline,
                urgency=approved_task.urgency_level,
                assigned_to=str(current_user.id),
                status="todo",
                source="email_extraction"
            )

            db.add(new_task)
            db.flush()

            # Link the created task
            approved_task.created_task_id = str(new_task.id)
            db.commit()
            db.refresh(new_task)

            created_task_id = str(new_task.id)

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create task: {str(e)}"
            )

    # Build response
    task_dict = {
        "id": str(approved_task.id),
        "extracted_email_id": str(approved_task.extracted_email_id),
        "employee_id": str(approved_task.employee_id),
        "task_title": approved_task.task_title,
        "task_description": approved_task.task_description,
        "deadline": approved_task.deadline,
        "urgency_level": approved_task.urgency_level,
        "priority_score": approved_task.priority_score,
        "sentiment_score": approved_task.sentiment_score,
        "sentiment_label": approved_task.sentiment_label,
        "confidence_score": approved_task.confidence_score,
        "approved": approved_task.approved,
        "reviewed_at": approved_task.reviewed_at,
        "created_task_id": created_task_id,
        "created_at": approved_task.created_at
    }

    message = "Task approved"
    if created_task_id:
        message += " and created successfully"

    return TaskApprovalResponse(
        success=True,
        message=message,
        task=ExtractedTaskResponse(**task_dict),
        created_task_id=created_task_id
    )


@router.delete("/email-extraction/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def reject_extracted_task(
    task_id: str,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reject and delete an extracted task

    Args:
        task_id: ExtractedTask ID
        current_user: Authenticated employee
        db: Database session
    """
    # Verify task exists and belongs to user
    task = db.query(ExtractedTask).filter(
        ExtractedTask.id == task_id,
        ExtractedTask.employee_id == str(current_user.id)
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if task.approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete approved task"
        )

    # Delete the task
    extraction_service = EmailExtractionService(db)
    extraction_service.reject_task(task_id)

    return None


# ============================================================================
# Email History Endpoints
# ============================================================================

@router.get("/email-extraction/emails", response_model=PaginatedEmailsResponse)
def get_extracted_emails(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(None, description="Filter by extraction status"),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get history of extracted emails

    Returns paginated list of emails that have been processed

    Args:
        page: Page number (1-indexed)
        page_size: Items per page (max 100)
        status_filter: Filter by extraction status
        current_user: Authenticated employee
        db: Database session

    Returns:
        Paginated list of extracted emails
    """
    # Build query
    query = db.query(ExtractedEmail).filter(
        ExtractedEmail.employee_id == str(current_user.id)
    )

    # Apply status filter
    if status_filter:
        try:
            status_enum = ExtractionStatus(status_filter)
            query = query.filter(ExtractedEmail.extraction_status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status filter: {status_filter}"
            )

    # Get total count
    total = query.count()

    # Calculate pagination
    total_pages = math.ceil(total / page_size)
    offset = (page - 1) * page_size

    # Get paginated results with task count
    emails = query.order_by(
        ExtractedEmail.received_at.desc()
    ).offset(offset).limit(page_size).all()

    # Build response with task counts
    email_responses = []
    for email in emails:
        tasks_count = db.query(func.count(ExtractedTask.id)).filter(
            ExtractedTask.extracted_email_id == str(email.id)
        ).scalar()

        email_dict = {
            "id": str(email.id),
            "email_id": email.email_id,
            "subject": email.subject,
            "sender": email.sender,
            "received_at": email.received_at,
            "extraction_status": email.extraction_status.value,
            "extraction_error": email.extraction_error,
            "extracted_at": email.extracted_at,
            "tasks_count": tasks_count or 0,
            "created_at": email.created_at
        }
        email_responses.append(ExtractedEmailResponse(**email_dict))

    return PaginatedEmailsResponse(
        emails=email_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


# ============================================================================
# Dataset Export Endpoints
# ============================================================================

@router.get("/email-extraction/dataset/export", response_model=List[TaskDatasetExport])
def export_task_dataset(
    approved_only: bool = Query(True, description="Only export approved tasks"),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export task dataset for ML/analysis

    Returns all extracted tasks with email metadata
    Can be used for training, reporting, or data analysis

    Args:
        approved_only: Only include approved tasks
        current_user: Authenticated employee
        db: Database session

    Returns:
        List of tasks with full metadata
    """
    # Build query
    query = db.query(ExtractedTask).filter(
        ExtractedTask.employee_id == str(current_user.id)
    )

    if approved_only:
        query = query.filter(ExtractedTask.approved == True)

    # Get all tasks
    tasks = query.order_by(ExtractedTask.created_at.desc()).all()

    # Build dataset
    dataset = []
    for task in tasks:
        email = task.extracted_email

        dataset_item = TaskDatasetExport(
            task_id=str(task.id),
            task_title=task.task_title,
            task_description=task.task_description,
            deadline=task.deadline,
            urgency_level=task.urgency_level,
            priority_score=task.priority_score,
            sentiment_score=task.sentiment_score,
            sentiment_label=task.sentiment_label,
            confidence_score=task.confidence_score,
            email_subject=email.subject if email else "",
            email_sender=email.sender if email else "",
            email_received_at=email.received_at if email else datetime.utcnow(),
            approved=task.approved,
            created_at=task.created_at
        )
        dataset.append(dataset_item)

    return dataset
