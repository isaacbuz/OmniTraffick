"""TikTok Marketing API payload translator."""
from typing import Any
from src.orchestration.translators.base import PlatformTranslator


class TikTokTranslator(PlatformTranslator):
    """
    Translates OmniTraffick tickets into TikTok Marketing API payloads.
    
    Generates JSON structures compatible with:
    - Campaign Creation: /open_api/v1.3/campaign/create/
    - AdGroup Creation: /open_api/v1.3/adgroup/create/
    - Ad Creation: /open_api/v1.3/ad/create/
    
    Reference: https://business-api.tiktok.com/portal/docs
    """

    def build_campaign_payload(self, ticket: Any) -> dict[str, Any]:
        """
        Build TikTok campaign creation payload.
        
        Required payload_config fields:
        - advertiser_id: TikTok advertiser ID
        - objective_type: Campaign objective (e.g., "TRAFFIC", "CONVERSIONS")
        - budget_mode: Budget mode ("BUDGET_MODE_INFINITE" or "BUDGET_MODE_TOTAL")
        
        Returns:
            Dict matching TikTok Marketing API /campaign/create/ schema
        """
        config = ticket.payload_config
        campaign = ticket.campaign

        # Validate required fields
        if not config.get("advertiser_id"):
            raise ValueError("payload_config missing required field: advertiser_id")
        if not config.get("objective_type"):
            raise ValueError("payload_config missing required field: objective_type")

        payload = {
            "advertiser_id": config["advertiser_id"],
            "campaign_name": campaign.name,  # Taxonomy-generated name
            "objective_type": config["objective_type"],
            "budget_mode": config.get("budget_mode", "BUDGET_MODE_INFINITE"),
        }

        # Campaign budget (if finite budget mode)
        if config.get("budget_mode") == "BUDGET_MODE_TOTAL" and config.get("budget"):
            payload["budget"] = float(config["budget"])

        # Special ad category (e.g., credit, housing)
        if config.get("special_industries"):
            payload["special_industries"] = config["special_industries"]

        return payload

    def build_adset_payload(self, ticket: Any, campaign_id: str) -> dict[str, Any]:
        """
        Build TikTok adgroup (adset) creation payload.
        
        Required payload_config fields:
        - advertiser_id: TikTok advertiser ID
        - placements: List of placements (e.g., ["PLACEMENT_TIKTOK"])
        - location_ids: List of location IDs (geo-targeting)
        - age_groups: List of age groups (e.g., ["AGE_25_34"])
        - budget: Daily budget (minimum $20 USD)
        - bid_type: Bid type (e.g., "BID_TYPE_NO_BID", "BID_TYPE_MAX")
        - optimization_goal: Optimization goal (e.g., "CLICK", "CONVERT")
        
        Returns:
            Dict matching TikTok Marketing API /adgroup/create/ schema
        """
        config = ticket.payload_config
        campaign = ticket.campaign

        # Validate required fields
        required_fields = [
            "advertiser_id",
            "placements",
            "location_ids",
            "budget",
            "bid_type",
            "optimization_goal",
        ]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"payload_config missing required field: {field}")

        payload = {
            "advertiser_id": config["advertiser_id"],
            "campaign_id": campaign_id,
            "adgroup_name": f"{campaign.name}_AdGroup",
            "placement_type": "PLACEMENT_TYPE_NORMAL",
            "placements": config["placements"],
            "location_ids": config["location_ids"],
            "budget": float(config["budget"]),
            "budget_mode": "BUDGET_MODE_DAY",
            "bid_type": config["bid_type"],
            "optimization_goal": config["optimization_goal"],
        }

        # Age targeting
        if config.get("age_groups"):
            payload["age_groups"] = config["age_groups"]

        # Gender targeting
        if config.get("gender"):
            payload["gender"] = config["gender"]

        # Interest/behavior targeting
        if config.get("interest_category_ids"):
            payload["interest_category_ids"] = config["interest_category_ids"]

        # Bid amount (if manual bidding)
        if config.get("bid_price"):
            payload["bid_price"] = float(config["bid_price"])

        # Schedule (start/end time)
        if config.get("schedule_start_time"):
            payload["schedule_start_time"] = config["schedule_start_time"]
        if config.get("schedule_end_time"):
            payload["schedule_end_time"] = config["schedule_end_time"]

        # Pacing
        if config.get("pacing"):
            payload["pacing"] = config["pacing"]

        return payload

    def build_ad_payload(self, ticket: Any, adset_id: str) -> dict[str, Any]:
        """
        Build TikTok ad creation payload.
        
        Required payload_config fields:
        - advertiser_id: TikTok advertiser ID
        - creatives: List of creative objects (video_id, ad_text, call_to_action)
        - landing_page_url: Landing page URL
        
        Returns:
            Dict matching TikTok Marketing API /ad/create/ schema
        """
        config = ticket.payload_config
        campaign = ticket.campaign

        # Validate required fields
        if not config.get("creatives"):
            raise ValueError("payload_config missing required field: creatives")
        if not config.get("landing_page_url"):
            raise ValueError("payload_config missing required field: landing_page_url")

        payload = {
            "advertiser_id": config["advertiser_id"],
            "adgroup_id": adset_id,
            "ad_name": f"{campaign.name}_Ad",
            "ad_format": "SINGLE_VIDEO",  # Default to single video
            "creatives": config["creatives"],
            "landing_page_url": config["landing_page_url"],
        }

        # Display name (brand name shown in ad)
        if config.get("display_name"):
            payload["display_name"] = config["display_name"]

        # Tracking pixels
        if config.get("pixel_id"):
            payload["pixel_id"] = config["pixel_id"]

        # App install tracking
        if config.get("app_id"):
            payload["app_id"] = config["app_id"]

        return payload

    def validate_payload_config(self, payload_config: dict[str, Any]) -> bool:
        """
        Validate that payload_config contains minimum required fields for TikTok.
        
        Required:
        - advertiser_id
        - objective_type
        - placements
        - location_ids
        - budget
        - bid_type
        - optimization_goal
        - creatives
        - landing_page_url
        """
        required_fields = [
            "advertiser_id",
            "objective_type",
            "placements",
            "location_ids",
            "budget",
            "bid_type",
            "optimization_goal",
            "creatives",
            "landing_page_url",
        ]

        for field in required_fields:
            if field not in payload_config:
                return False

        return True
