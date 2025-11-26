"""Email Extraction API Endpoints"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.extracted_email import ExtractedEmail, ExtractionStatus
from app.models.extracted_task import ExtractedTask
from app.schemas.email_extraction_schema import (
    EmailFetchRequest,
    TaskApprovalRequest,
    ExtractedEmailResponse,
    ExtractedTaskResponse,
    EmailExtractionStats,
    OAuthUrlResponse,
    OAuthCallbackResponse,
    ExtractionJobResponse,
    DatasetExport,
    DatasetTaskItem
)
from app.services.gmail_service import GmailService
from app.services.email_extraction_service import EmailExtractionService
from datetime import datetime


router = APIRouter()


@router.get("/email-extraction/check-connection")
def check_gmail_connection(
    employee_id: UUID = Query(...),
    db: Session = Depends(get_db)
):
    """Check if Gmail is connected for this employee"""
    from app.models.email_credential import EmailCredential
    
    # Convert UUID to string for SQLite compatibility
    employee_id_str = str(employee_id)
    
    credential = db.query(EmailCredential).filter(
        EmailCredential.employee_id == employee_id_str
    ).first()
    
    return {
        "connected": credential is not None,
        "email": credential.email_address if credential else None
    }


@router.delete("/email-extraction/disconnect")
def disconnect_gmail(
    employee_id: UUID = Query(...),
    db: Session = Depends(get_db)
):
    """Disconnect Gmail for this employee"""
    from app.models.email_credential import EmailCredential
    
    # Convert UUID to string for SQLite compatibility
    employee_id_str = str(employee_id)
    
    credential = db.query(EmailCredential).filter(
        EmailCredential.employee_id == employee_id_str
    ).first()
    
    if credential:
        db.delete(credential)
        db.commit()
        print(f"✅ Disconnected Gmail for employee {employee_id}")
    
    return {"message": "Gmail disconnected successfully"}


@router.post("/email-extraction/connect", response_model=OAuthUrlResponse)
def initiate_gmail_oauth(
    employee_id: UUID,
    db: Session = Depends(get_db)
):
    """Initiate Gmail OAuth flow"""
    gmail_service = GmailService(db)
    
    try:
        auth_url, state = gmail_service.get_authorization_url(str(employee_id))
        
        return OAuthUrlResponse(
            auth_url=auth_url,
            state=state
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate OAuth URL: {str(e)}"
        )


@router.get("/email-extraction/oauth/callback")
def gmail_oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db)
):
    """Handle Gmail OAuth callback"""
    print(f"📧 OAuth callback received - State: {state[:50]}...")
    gmail_service = GmailService(db)
    
    try:
        credential = gmail_service.handle_oauth_callback(code, state)
        print(f"✅ OAuth callback successful for {credential.email_address}")
        
        # Redirect to frontend success page
        return RedirectResponse(
            url=f"http://localhost:3000/email-extraction?status=connected&email={credential.email_address}",
            status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        print(f"❌ OAuth callback error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        # Redirect to frontend error page
        return RedirectResponse(
            url=f"http://localhost:3000/email-extraction?status=error&message={str(e)}",
            status_code=status.HTTP_302_FOUND
        )


@router.post("/email-extraction/fetch", response_model=ExtractionJobResponse)
def fetch_and_extract_emails(
    request: EmailFetchRequest,
    db: Session = Depends(get_db)
):
    """Fetch emails from Gmail and extract information"""
    extraction_service = EmailExtractionService(db)
    
    try:
        results = extraction_service.process_emails(
            employee_id=request.employee_id,
            max_emails=request.max_emails,
            unread_only=request.unread_only
        )
        
        return ExtractionJobResponse(
            job_id=str(request.employee_id),
            message=f"Processed {results['emails_processed']} emails, extracted {results['tasks_extracted']} tasks",
            status="completed" if not results['errors'] else "completed_with_errors",
            emails_to_process=results['emails_fetched']
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}"
        )


@router.get("/email-extraction/extractions", response_model=List[ExtractedEmailResponse])
def list_extracted_emails(
    employee_id: UUID,
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List extracted emails with their tasks"""
    # Convert UUID to string for SQLite compatibility
    employee_id_str = str(employee_id)
    
    query = db.query(ExtractedEmail).filter(
        ExtractedEmail.employee_id == employee_id_str
    )
    
    if status:
        try:
            status_enum = ExtractionStatus(status)
            query = query.filter(ExtractedEmail.extraction_status == status_enum)
        except ValueError:
            pass
    
    extractions = query.order_by(
        ExtractedEmail.received_at.desc()
    ).offset(skip).limit(limit).all()
    
    return extractions


@router.get("/email-extraction/extractions/{extraction_id}", response_model=ExtractedEmailResponse)
def get_extracted_email(
    extraction_id: UUID,
    db: Session = Depends(get_db)
):
    """Get specific extracted email with tasks"""
    extraction = db.query(ExtractedEmail).filter(
        ExtractedEmail.id == extraction_id
    ).first()
    
    if not extraction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Extraction not found"
        )
    
    return extraction


@router.get("/email-extraction/tasks", response_model=List[ExtractedTaskResponse])
def list_extracted_tasks(
    employee_id: UUID,
    approved: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List extracted tasks (the dataset)"""
    # Convert UUID to string for SQLite compatibility
    employee_id_str = str(employee_id)
    
    query = db.query(ExtractedTask).filter(
        ExtractedTask.employee_id == employee_id_str
    )
    
    if approved is not None:
        query = query.filter(ExtractedTask.approved == approved)
    
    tasks = query.order_by(
        ExtractedTask.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return tasks


@router.post("/email-extraction/approve/{extracted_task_id}")
def approve_extracted_task(
    extracted_task_id: UUID,
    request: TaskApprovalRequest,
    db: Session = Depends(get_db)
):
    """Approve extracted task and create actual Task"""
    extraction_service = EmailExtractionService(db)
    
    try:
        task = extraction_service.approve_and_create_task(
            extracted_task_id=extracted_task_id,
            assigned_to=request.assigned_to
        )
        
        return {
            "success": True,
            "message": "Task approved and created",
            "task_id": str(task.id)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve task: {str(e)}"
        )


@router.delete("/email-extraction/tasks/{extracted_task_id}")
def reject_extracted_task(
    extracted_task_id: UUID,
    db: Session = Depends(get_db)
):
    """Reject/delete extracted task"""
    task = db.query(ExtractedTask).filter(
        ExtractedTask.id == extracted_task_id
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
    
    db.delete(task)
    db.commit()
    
    return {"success": True, "message": "Task rejected and deleted"}


@router.get("/email-extraction/stats", response_model=EmailExtractionStats)
def get_extraction_statistics(
    employee_id: UUID,
    db: Session = Depends(get_db)
):
    """Get statistics about email extractions"""
    extraction_service = EmailExtractionService(db)
    
    stats = extraction_service.get_extraction_stats(employee_id)
    
    return EmailExtractionStats(**stats)


@router.get("/email-extraction/dataset/export")
def export_dataset(
    employee_id: UUID,
    format: str = Query("json", regex="^(json|csv)$"),
    db: Session = Depends(get_db)
):
    """Export extracted data as dataset"""
    extraction_service = EmailExtractionService(db)
    
    dataset = extraction_service.export_dataset(employee_id)
    
    if format == "json":
        return JSONResponse(content={
            "employee_id": str(employee_id),
            "export_date": datetime.now().isoformat(),
            "total_items": len(dataset),
            "items": dataset
        })
    
    elif format == "csv":
        # Convert to CSV
        import csv
        from io import StringIO
        
        output = StringIO()
        if dataset:
            writer = csv.DictWriter(output, fieldnames=dataset[0].keys())
            writer.writeheader()
            writer.writerows(dataset)
        
        from fastapi.responses import Response
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=email_extraction_dataset_{employee_id}.csv"
            }
        )


@router.get("/email-extraction/health")
def health_check():
    """Health check for email extraction service"""
    return {
        "status": "healthy",
        "service": "email_extraction",
        "features": [
            "gmail_oauth",
            "email_fetching",
            "gemini_extraction",
            "dataset_export"
        ]
    }

