"""Conversion tracking API endpoints."""
from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class TrackingEventRequest(BaseModel):
    """Tracking event from frontend."""
    event_name: str
    event_id: str
    user_data: dict
    custom_data: dict | None = None
    event_source_url: str | None = None


@router.post("/tracking/event")
async def track_event(event: TrackingEventRequest, request: Request):
    """
    Track conversion event via Meta CAPI.
    
    Receives event from frontend pixel, enriches with server-side data,
    and sends to Meta Conversions API for deduplication.
    
    Args:
        event: Event data from pixel
        request: FastAPI request (for IP extraction)
        
    Returns:
        Success status
    """
    try:
        from src.tracking.capi import CAPIService
        
        # Initialize CAPI
        capi = CAPIService()
        
        # Enrich user data with server-side info
        user_data = event.user_data.copy()
        
        # Get client IP from request
        client_ip = request.client.host if request.client else None
        if client_ip:
            user_data["client_ip_address"] = client_ip
        
        # Send to Meta CAPI
        response = capi.send_event(
            event_name=event.event_name,
            event_id=event.event_id,
            user_data=user_data,
            custom_data=event.custom_data,
            event_source_url=event.event_source_url,
        )
        
        return {
            "success": True,
            "events_received": response.get("events_received", 0),
        }
    
    except ImportError:
        return {
            "success": False,
            "error": "CAPI service not configured. Set META_ACCESS_TOKEN and META_PIXEL_ID.",
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
