"""Meta Conversions API (CAPI) - Server-Side Tracking."""
import hashlib
import time
from typing import Dict, Any, List
import httpx
from src.config import settings


class CAPIService:
    """
    Meta Conversions API Service.
    
    Implements server-to-server event tracking to bypass:
    - Ad blockers
    - iOS 14+ App Tracking Transparency (ATT)
    - Cookie restrictions (ITP)
    
    Benefits:
    - Higher match rates (hashed PII sent directly to Meta)
    - Event deduplication with browser pixel
    - More reliable attribution
    """
    
    def __init__(self, access_token: str | None = None, pixel_id: str | None = None):
        """
        Initialize CAPI service.
        
        Args:
            access_token: Meta access token
            pixel_id: Meta Pixel ID
        """
        self.access_token = access_token or settings.meta_access_token
        self.pixel_id = pixel_id or getattr(settings, 'meta_pixel_id', None)
        
        if not self.access_token or not self.pixel_id:
            raise ValueError("META_ACCESS_TOKEN and META_PIXEL_ID required for CAPI")
        
        self.api_url = f"https://graph.facebook.com/v18.0/{self.pixel_id}/events"
    
    def send_event(
        self,
        event_name: str,
        event_id: str,
        user_data: Dict[str, Any],
        custom_data: Dict[str, Any] | None = None,
        event_source_url: str | None = None,
        action_source: str = "website",
    ) -> Dict[str, Any]:
        """
        Send conversion event to Meta CAPI.
        
        Args:
            event_name: Event name (e.g., "PageView", "Purchase", "Lead")
            event_id: Unique event ID (must match browser pixel for deduplication)
            user_data: User information for matching (email, phone, IP, user agent)
            custom_data: Custom event parameters (value, currency, content_ids)
            event_source_url: URL where event occurred
            action_source: Event source (website/app/email)
            
        Returns:
            API response with events_received count
        """
        # Hash user data (required for privacy)
        hashed_user_data = self._hash_user_data(user_data)
        
        # Build event payload
        event = {
            "event_name": event_name,
            "event_time": int(time.time()),
            "event_id": event_id,
            "event_source_url": event_source_url,
            "action_source": action_source,
            "user_data": hashed_user_data,
        }
        
        if custom_data:
            event["custom_data"] = custom_data
        
        # Send to Meta CAPI
        payload = {
            "data": [event],
            "access_token": self.access_token,
        }
        
        response = httpx.post(self.api_url, json=payload, timeout=10.0)
        response.raise_for_status()
        
        return response.json()
    
    def send_batch_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send multiple events in a single batch request.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            API response
        """
        # Hash user data for all events
        processed_events = []
        for event in events:
            user_data = event.pop("user_data")
            hashed_user_data = self._hash_user_data(user_data)
            event["user_data"] = hashed_user_data
            event["event_time"] = event.get("event_time", int(time.time()))
            processed_events.append(event)
        
        payload = {
            "data": processed_events,
            "access_token": self.access_token,
        }
        
        response = httpx.post(self.api_url, json=payload, timeout=10.0)
        response.raise_for_status()
        
        return response.json()
    
    def _hash_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hash user data according to Meta specifications.
        
        Hashes:
        - email: SHA-256 of lowercase, trimmed email
        - phone: SHA-256 of E.164 format (no spaces/dashes)
        - first_name: SHA-256 of lowercase
        - last_name: SHA-256 of lowercase
        - city: SHA-256 of lowercase
        - state: SHA-256 of lowercase 2-letter code
        - zip: SHA-256 of 5-digit ZIP
        - country: SHA-256 of lowercase 2-letter ISO code
        
        Does NOT hash:
        - client_ip_address
        - client_user_agent
        - fbc (Meta click ID)
        - fbp (Meta browser ID)
        """
        hashed = {}
        
        # Hash fields
        hash_fields = [
            "email", "phone", "first_name", "last_name",
            "city", "state", "zip", "country", "gender", "date_of_birth"
        ]
        
        for field in hash_fields:
            if field in user_data:
                value = str(user_data[field]).lower().strip()
                hashed[field] = self._sha256(value)
        
        # Pass through non-hashed fields
        passthrough_fields = [
            "client_ip_address", "client_user_agent", "fbc", "fbp"
        ]
        
        for field in passthrough_fields:
            if field in user_data:
                hashed[field] = user_data[field]
        
        return hashed
    
    def _sha256(self, value: str) -> str:
        """SHA-256 hash."""
        return hashlib.sha256(value.encode()).hexdigest()
    
    @staticmethod
    def generate_event_id() -> str:
        """
        Generate unique event ID for deduplication.
        
        Must be shared between:
        1. Frontend pixel event
        2. Backend CAPI event
        
        Returns:
            Unique event ID (UUID or timestamp-based)
        """
        import uuid
        return str(uuid.uuid4())


# Example usage
"""
from src.tracking.capi import CAPIService

capi = CAPIService()

# On backend when user signs up
capi.send_event(
    event_name="Lead",
    event_id="unique-event-id-123",  # Must match frontend pixel
    user_data={
        "email": "user@example.com",
        "phone": "+15555551234",
        "client_ip_address": "192.168.1.1",
        "client_user_agent": "Mozilla/5.0...",
        "fbc": "fb.1.1234567890.AbCdEfG",  # From _fbc cookie
        "fbp": "fb.1.1234567890.1234567890",  # From _fbp cookie
    },
    custom_data={
        "value": 99.99,
        "currency": "USD",
    },
    event_source_url="https://example.com/signup",
)
"""
