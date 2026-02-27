"""Google Ads API payload translator."""
from typing import Dict, Any
from src.orchestration.translators.base import PlatformTranslator
from src.models.ticket import Ticket


class GoogleTranslator(PlatformTranslator):
    """
    Translator for Google Ads API payloads.
    
    Generates JSON payloads compliant with Google Ads API v14+.
    """
    
    def build_campaign_payload(self, ticket: Ticket) -> Dict[str, Any]:
        """
        Build Google Ads campaign creation payload.
        
        Args:
            ticket: Ticket with campaign and payload config
            
        Returns:
            Google Ads API JSON payload
        """
        config = ticket.payload_config
        campaign = ticket.campaign
        
        # Google Ads uses resource-based API
        payload = {
            "campaign": {
                "name": campaign.name,
                "status": "PAUSED",  # Always start paused
                "advertising_channel_type": config.get("channel_type", "SEARCH"),
                "campaign_budget": config.get("customer_id") + "/campaignBudgets/" + config.get("budget_id"),
            }
        }
        
        # Bidding strategy
        if config.get("bidding_strategy") == "TARGET_CPA":
            payload["campaign"]["target_cpa"] = {
                "target_cpa_micros": int(config.get("target_cpa", 10) * 1_000_000)
            }
        elif config.get("bidding_strategy") == "MAXIMIZE_CONVERSIONS":
            payload["campaign"]["maximize_conversions"] = {}
        
        # Networks
        if config.get("networks"):
            payload["campaign"]["network_settings"] = config["networks"]
        
        return payload
    
    def build_adset_payload(self, ticket: Ticket) -> Dict[str, Any]:
        """
        Build Google Ads ad group creation payload.
        
        Args:
            ticket: Ticket with targeting config
            
        Returns:
            Google Ads API JSON payload for ad group
        """
        config = ticket.payload_config
        campaign = ticket.campaign
        
        payload = {
            "ad_group": {
                "name": f"{campaign.name}_AdGroup",
                "campaign": config.get("customer_id") + "/campaigns/" + config.get("campaign_id"),
                "status": "ENABLED",
                "type": config.get("ad_group_type", "SEARCH_STANDARD"),
            }
        }
        
        # Bidding
        if config.get("cpc_bid_micros"):
            payload["ad_group"]["cpc_bid_micros"] = config["cpc_bid_micros"]
        
        return payload
    
    def build_ad_payload(self, ticket: Ticket) -> Dict[str, Any]:
        """
        Build Google Ads responsive search ad payload.
        
        Args:
            ticket: Ticket with ad creative config
            
        Returns:
            Google Ads API JSON payload for ad
        """
        config = ticket.payload_config
        
        payload = {
            "ad_group_ad": {
                "ad_group": config.get("customer_id") + "/adGroups/" + config.get("ad_group_id"),
                "status": "ENABLED",
                "ad": {
                    "responsive_search_ad": {
                        "headlines": [
                            {"text": h} for h in config.get("headlines", [])
                        ],
                        "descriptions": [
                            {"text": d} for d in config.get("descriptions", [])
                        ],
                        "path1": config.get("path1", ""),
                        "path2": config.get("path2", ""),
                    },
                    "final_urls": config.get("final_urls", []),
                }
            }
        }
        
        return payload
    
    def get_api_endpoint(self, resource_type: str) -> str:
        """
        Get Google Ads API endpoint for resource.
        
        Args:
            resource_type: Type of resource (campaign, ad_group, ad)
            
        Returns:
            API endpoint path
        """
        return f"https://googleads.googleapis.com/v14/customers/{{customer_id}}/{resource_type}:mutate"
