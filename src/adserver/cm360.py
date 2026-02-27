"""Campaign Manager 360 (CM360) Ad Server Client."""
import httpx
from typing import Dict, Any, Tuple
from src.config import settings


class CM360Client:
    """
    Campaign Manager 360 API client for generating tracking tags.
    
    Before deploying DSP campaigns, OmniTraffick must:
    1. Create a Campaign Shell in CM360
    2. Create a Placement
    3. Generate 1x1 impression pixel + click tracker
    4. Inject these tags into DSP payloads (Meta/TikTok)
    """
    
    def __init__(self, access_token: str | None = None, profile_id: str | None = None):
        """
        Initialize CM360 client.
        
        Args:
            access_token: OAuth2 access token for CM360 API
            profile_id: CM360 profile (network) ID
        """
        self.access_token = access_token or getattr(settings, 'cm360_access_token', None)
        self.profile_id = profile_id or getattr(settings, 'cm360_profile_id', None)
        
        if not self.access_token or not self.profile_id:
            raise ValueError("CM360_ACCESS_TOKEN and CM360_PROFILE_ID required")
        
        self.base_url = "https://dfareporting.googleapis.com/dfareporting/v4"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
    
    def create_campaign_shell(self, campaign_name: str, advertiser_id: str) -> Dict[str, Any]:
        """
        Create a Campaign Shell in CM360.
        
        Args:
            campaign_name: Campaign name (taxonomy)
            advertiser_id: CM360 advertiser ID
            
        Returns:
            Campaign object with id
        """
        url = f"{self.base_url}/userprofiles/{self.profile_id}/campaigns"
        
        payload = {
            "name": campaign_name,
            "advertiserId": advertiser_id,
            "archived": False,
            "startDate": "2026-01-01",  # Should be dynamic
            "endDate": "2026-12-31",
        }
        
        response = httpx.post(url, json=payload, headers=self.headers, timeout=30.0)
        response.raise_for_status()
        
        return response.json()
    
    def create_placement(
        self,
        campaign_id: str,
        site_id: str,
        placement_name: str,
    ) -> Dict[str, Any]:
        """
        Create a Placement in CM360.
        
        Args:
            campaign_id: CM360 campaign ID
            site_id: CM360 site ID
            placement_name: Placement name
            
        Returns:
            Placement object with id
        """
        url = f"{self.base_url}/userprofiles/{self.profile_id}/placements"
        
        payload = {
            "name": placement_name,
            "campaignId": campaign_id,
            "siteId": site_id,
            "compatibility": "DISPLAY",
            "paymentSource": "PLACEMENT_AGENCY_PAID",
            "size": {
                "width": 1,
                "height": 1,
            },
            "tagFormats": ["PLACEMENT_TAG_STANDARD"],
            "pricingSchedule": {
                "startDate": "2026-01-01",
                "endDate": "2026-12-31",
                "pricingType": "PRICING_TYPE_CPM",
            }
        }
        
        response = httpx.post(url, json=payload, headers=self.headers, timeout=30.0)
        response.raise_for_status()
        
        return response.json()
    
    def generate_placement_tags(self, placement_id: str) -> Tuple[str, str]:
        """
        Generate tracking tags for a placement.
        
        Args:
            placement_id: CM360 placement ID
            
        Returns:
            Tuple of (impression_pixel, click_tracker)
        """
        url = f"{self.base_url}/userprofiles/{self.profile_id}/placements/{placement_id}/generatetags"
        
        response = httpx.post(url, headers=self.headers, timeout=30.0)
        response.raise_for_status()
        
        tags = response.json()
        
        # Extract 1x1 pixel and click tracker
        impression_pixel = self._extract_impression_pixel(tags)
        click_tracker = self._extract_click_tracker(tags)
        
        return impression_pixel, click_tracker
    
    def _extract_impression_pixel(self, tags_response: Dict[str, Any]) -> str:
        """
        Extract 1x1 impression pixel from tags response.
        
        Args:
            tags_response: CM360 generatetags API response
            
        Returns:
            Impression pixel URL
        """
        # Example: https://ad.doubleclick.net/ddm/ad/N123.456/B789;sz=1x1;ord=[timestamp]
        for tag in tags_response.get("placementTags", []):
            if "PLACEMENT_TAG_STANDARD" in tag.get("tagFormats", []):
                tag_string = tag.get("tagString", "")
                # Parse the img src URL
                if 'src="' in tag_string:
                    start = tag_string.find('src="') + 5
                    end = tag_string.find('"', start)
                    return tag_string[start:end]
        
        # Fallback: construct manually
        return f"https://ad.doubleclick.net/ddm/trackimp/N{self.profile_id};sz=1x1;ord=[timestamp]"
    
    def _extract_click_tracker(self, tags_response: Dict[str, Any]) -> str:
        """
        Extract click tracker from tags response.
        
        Args:
            tags_response: CM360 generatetags API response
            
        Returns:
            Click tracker URL
        """
        # Example: https://ad.doubleclick.net/ddm/clk/N123.456;ord=[timestamp]
        for tag in tags_response.get("placementTags", []):
            if "PLACEMENT_TAG_CLICK_COMMANDS" in tag.get("tagFormats", []):
                return tag.get("tagString", "")
        
        # Fallback
        return f"https://ad.doubleclick.net/ddm/clk/N{self.profile_id};ord=[timestamp]"
    
    def create_campaign_with_tracking(
        self,
        campaign_name: str,
        advertiser_id: str,
        site_id: str,
    ) -> Dict[str, Any]:
        """
        Full workflow: Create campaign shell, placement, and generate tags.
        
        Args:
            campaign_name: Campaign name (taxonomy)
            advertiser_id: CM360 advertiser ID
            site_id: CM360 site ID
            
        Returns:
            Dict with campaign_id, placement_id, impression_pixel, click_tracker
        """
        # Step 1: Create campaign shell
        campaign = self.create_campaign_shell(campaign_name, advertiser_id)
        campaign_id = campaign["id"]
        
        # Step 2: Create placement
        placement = self.create_placement(
            campaign_id=campaign_id,
            site_id=site_id,
            placement_name=f"{campaign_name}_1x1_Tracking",
        )
        placement_id = placement["id"]
        
        # Step 3: Generate tags
        impression_pixel, click_tracker = self.generate_placement_tags(placement_id)
        
        return {
            "campaign_id": campaign_id,
            "placement_id": placement_id,
            "impression_pixel": impression_pixel,
            "click_tracker": click_tracker,
        }
