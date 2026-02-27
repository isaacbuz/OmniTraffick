"""API endpoints for deployment operations."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.api.deps import get_db
from src.models.ticket import Ticket, TicketStatus
from src.workers.tasks import deploy_payload_to_platform

router = APIRouter()


class DeployRequest(BaseModel):
    """Request to deploy a ticket to platform."""
    ticket_id: str


class DeployResponse(BaseModel):
    """Response from deployment request."""
    task_id: str
    ticket_id: str
    status: str
    message: str


@router.post("/deploy", response_model=DeployResponse, status_code=status.HTTP_202_ACCEPTED)
def deploy_ticket(
    request: DeployRequest,
    db: Session = Depends(get_db),
):
    """
    Deploy a ticket to the advertising platform API.
    
    This endpoint queues the deployment as a Celery task for async processing.
    
    **Requirements:**
    - Ticket must exist
    - Ticket status must be READY_FOR_API
    
    **Process:**
    1. Validate ticket exists and is ready
    2. Queue Celery task for deployment
    3. Return task ID for status tracking
    
    Args:
        request: Deployment request with ticket_id
        db: Database session
        
    Returns:
        Task ID and status
        
    Raises:
        404: Ticket not found
        400: Ticket not in READY_FOR_API status
    """
    # Fetch ticket
    ticket = db.query(Ticket).filter(Ticket.id == request.ticket_id).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {request.ticket_id} not found"
        )
    
    # Validate status
    if ticket.status != TicketStatus.READY_FOR_API:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticket must be READY_FOR_API, current status: {ticket.status.value}"
        )
    
    # Queue Celery task
    task = deploy_payload_to_platform.delay(str(ticket.id))
    
    return DeployResponse(
        task_id=task.id,
        ticket_id=str(ticket.id),
        status="queued",
        message=f"Deployment queued for platform: {ticket.channel.platform_name}"
    )


@router.get("/deploy/status/{task_id}")
def get_deployment_status(task_id: str):
    """
    Get the status of a deployment task.
    
    Args:
        task_id: Celery task ID
        
    Returns:
        Task status and result
    """
    from celery.result import AsyncResult
    from src.workers.celery_app import celery_app
    
    task = AsyncResult(task_id, app=celery_app)
    
    response = {
        "task_id": task_id,
        "status": task.state,
    }
    
    if task.state == "SUCCESS":
        response["result"] = task.result
    elif task.state == "FAILURE":
        response["error"] = str(task.info)
    
    return response
