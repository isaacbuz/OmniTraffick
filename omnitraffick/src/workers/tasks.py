"""Celery tasks for async API deployment."""
import time
import httpx
from typing import Optional
from celery import Task
from celery.utils.log import get_task_logger

from src.workers.celery_app import celery_app
from src.database import SessionLocal
from src.models.ticket import Ticket, TicketStatus
from src.orchestration.translators import get_translator
from src.config import settings

logger = get_task_logger(__name__)


class DatabaseTask(Task):
    """Base task with database session management."""
    
    _db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()


@celery_app.task(bind=True, base=DatabaseTask, max_retries=5)
def deploy_payload_to_platform(self, ticket_id: str) -> dict:
    """
    Deploy a trafficking payload to the ad platform API.
    
    Phase 4 Implementation:
    - Fetches ticket from database
    - Validates ticket is READY_FOR_API
    - Instantiates correct translator (Meta/TikTok)
    - Posts to platform Sandbox API
    - Captures external campaign_id and writes back to DB
    - Handles rate limits with exponential backoff
    
    Args:
        ticket_id: UUID of the ticket to deploy
        
    Returns:
        Dict with deployment status and external_platform_id
        
    Raises:
        Exception: If deployment fails after max retries
    """
    logger.info(f"Starting deployment for ticket {ticket_id}")
    
    # Fetch ticket
    ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    if not ticket:
        logger.error(f"Ticket {ticket_id} not found")
        raise ValueError(f"Ticket {ticket_id} not found")
    
    # Validate status
    if ticket.status != TicketStatus.READY_FOR_API:
        logger.error(f"Ticket {ticket_id} status is {ticket.status}, expected READY_FOR_API")
        raise ValueError(f"Ticket must be READY_FOR_API, current status: {ticket.status}")
    
    # Get platform details
    platform_name = ticket.channel.platform_name.lower()
    logger.info(f"Deploying to {platform_name}")
    
    # Get translator
    translator = get_translator(platform_name)
    
    # Build payload
    payload = translator.build_campaign_payload(ticket)
    logger.info(f"Generated payload: {payload}")
    
    # Get API endpoint and token
    api_url, api_token = _get_platform_credentials(platform_name)
    
    try:
        # Make API request
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                api_url,
                json=payload,
                headers=headers,
            )
            
            # Handle rate limiting with exponential backoff
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                logger.warning(f"Rate limited. Retrying after {retry_after}s")
                raise self.retry(countdown=retry_after)
            
            # Handle API errors
            response.raise_for_status()
            
            # Parse response
            response_data = response.json()
            external_id = _extract_external_id(platform_name, response_data)
            
            logger.info(f"Successfully deployed. External ID: {external_id}")
            
            # Update ticket with success
            ticket.status = TicketStatus.TRAFFICKED_SUCCESS
            ticket.external_platform_id = external_id
            ticket.qa_failure_reason = None
            self.db.commit()
            
            return {
                "status": "success",
                "ticket_id": str(ticket_id),
                "external_platform_id": external_id,
                "platform": platform_name,
            }
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
        
        # Retry on 5xx errors
        if 500 <= e.response.status_code < 600:
            logger.warning("Server error, retrying...")
            raise self.retry(countdown=2 ** self.request.retries)
        
        # Mark as failed on 4xx errors
        ticket.status = TicketStatus.FAILED
        ticket.qa_failure_reason = f"API Error {e.response.status_code}: {e.response.text[:200]}"
        self.db.commit()
        
        raise
    
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        
        # Retry on network errors
        logger.warning("Network error, retrying...")
        raise self.retry(countdown=2 ** self.request.retries)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        
        # Mark as failed
        ticket.status = TicketStatus.FAILED
        ticket.qa_failure_reason = f"Deployment error: {str(e)[:200]}"
        self.db.commit()
        
        raise


def _get_platform_credentials(platform_name: str) -> tuple[str, str]:
    """
    Get API endpoint and token for platform.
    
    Phase 4: Using sandbox endpoints.
    
    Returns:
        Tuple of (api_url, api_token)
    """
    if platform_name == "meta":
        return (
            f"https://graph.facebook.com/v18.0/act_{settings.meta_ad_account_id}/campaigns",
            settings.meta_access_token,
        )
    elif platform_name == "tiktok":
        return (
            "https://business-api.tiktok.com/open_api/v1.3/campaign/create/",
            settings.tiktok_access_token,
        )
    else:
        raise ValueError(f"Unsupported platform: {platform_name}")


def _extract_external_id(platform_name: str, response_data: dict) -> str:
    """
    Extract campaign ID from platform API response.
    
    Args:
        platform_name: Platform name (meta/tiktok)
        response_data: API response JSON
        
    Returns:
        External campaign ID
    """
    if platform_name == "meta":
        # Meta returns: {"id": "123456789"}
        return response_data.get("id")
    elif platform_name == "tiktok":
        # TikTok returns: {"code": 0, "data": {"campaign_id": "123456789"}}
        return response_data.get("data", {}).get("campaign_id")
    else:
        raise ValueError(f"Unsupported platform: {platform_name}")
