"""Meta Graph API payload translator."""
from typing import Any
from src.orchestration.translators.base import PlatformTranslator


class MetaTranslator(PlatformTranslator):
    """
    Translates OmniTraffick tickets into Meta Graph API payloads.
    
    Generates JSON structures compatible with:
    - Campaign Creation: /act_{ad_account_id}/campaigns
    - AdSet Creation: /act_{ad_account_id}/adsets
    - Ad Creation: /act_{ad_account_id}/ads
    
    Reference: https://developers.facebook.com/docs/marketing-api/reference/
    """

    def build_campaign_payload(self, ticket: Any) -> dict[str, Any]:
        """
        Build Meta campaign creation payload.
        
        Required payload_config fields:
        - ad_account_id: Meta ad account ID (e.g., "123456789")
        - objective: Campaign objective (e.g., "OUTCOME_TRAFFIC", "OUTCOME_SALES")
        - special_ad_categories: List of special ad categories (default: [])
        
        Returns:
            Dict matching Meta Graph API /campaigns endpoint schema
        """
        config = ticket.payload_config
        campaign = ticket.campaign

        # Validate required fields
        if not config.get("ad_account_id"):
            raise ValueError("payload_config missing required field: ad_account_id")
        if not config.get("objective"):
            raise ValueError("payload_config missing required field: objective")

        payload = {
            "name": campaign.name,  # Taxonomy-generated name
            "objective": config["objective"],
            "status": "PAUSED",  # Always create paused for safety
            "special_ad_categories": config.get("special_ad_categories", []),
        }

        # Optional fields
        if config.get("spend_cap"):
            payload["spend_cap"] = int(float(config["spend_cap"]) * 100)  # Convert to cents

        if config.get("buying_type"):
            payload["buying_type"] = config["buying_type"]

        return payload

    def build_adset_payload(self, ticket: Any, campaign_id: str) -> dict[str, Any]:
        """
        Build Meta adset creation payload.
        
        Required payload_config fields:
        - ad_account_id: Meta ad account ID
        - targeting: Targeting spec (geo, age, gender, interests)
        - optimization_goal: Optimization goal (e.g., "REACH", "LINK_CLICKS")
        - billing_event: Billing event (e.g., "IMPRESSIONS", "LINK_CLICKS")
        - bid_amount: Bid amount in cents
        - daily_budget: Daily budget in cents
        
        Returns:
            Dict matching Meta Graph API /adsets endpoint schema
        """
        config = ticket.payload_config
        campaign = ticket.campaign

        # Validate required fields
        required_fields = ["targeting", "optimization_goal", "billing_event"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"payload_config missing required field: {field}")

        payload = {
            "name": f"{campaign.name}_AdSet",
            "campaign_id": campaign_id,
            "optimization_goal": config["optimization_goal"],
            "billing_event": config["billing_event"],
            "status": "PAUSED",
            "targeting": config["targeting"],
        }

        # Budget (daily or lifetime)
        if config.get("daily_budget"):
            payload["daily_budget"] = int(float(config["daily_budget"]) * 100)
        elif config.get("lifetime_budget"):
            payload["lifetime_budget"] = int(float(config["lifetime_budget"]) * 100)
            if config.get("end_time"):
                payload["end_time"] = config["end_time"]
        else:
            raise ValueError("payload_config must include either daily_budget or lifetime_budget")

        # Bid amount (if manual bidding)
        if config.get("bid_amount"):
            payload["bid_amount"] = int(float(config["bid_amount"]) * 100)

        # Promoted object (for traffic/conversions)
        if config.get("promoted_object"):
            payload["promoted_object"] = config["promoted_object"]

        return payload

    def build_ad_payload(self, ticket: Any, adset_id: str) -> dict[str, Any]:
        """
        Build Meta ad creation payload.
        
        Required payload_config fields:
        - creative: Creative spec (image_hash/video_id, message, link, call_to_action)
        
        Returns:
            Dict matching Meta Graph API /ads endpoint schema
        """
        config = ticket.payload_config
        campaign = ticket.campaign

        # Validate required fields
        if "creative" not in config:
            raise ValueError("payload_config missing required field: creative")

        payload = {
            "name": f"{campaign.name}_Ad",
            "adset_id": adset_id,
            "status": "PAUSED",
            "creative": config["creative"],
        }

        # Tracking specs (for conversion tracking)
        if config.get("tracking_specs"):
            payload["tracking_specs"] = config["tracking_specs"]

        return payload

    def validate_payload_config(self, payload_config: dict[str, Any]) -> bool:
        """
        Validate that payload_config contains minimum required fields for Meta.
        
        Required:
        - ad_account_id
        - objective
        - targeting
        - optimization_goal
        - billing_event
        - daily_budget OR lifetime_budget
        - creative
        """
        required_fields = [
            "ad_account_id",
            "objective",
            "targeting",
            "optimization_goal",
            "billing_event",
            "creative",
        ]

        for field in required_fields:
            if field not in payload_config:
                return False

        # Must have either daily_budget or lifetime_budget
        if "daily_budget" not in payload_config and "lifetime_budget" not in payload_config:
            return False

        return True
