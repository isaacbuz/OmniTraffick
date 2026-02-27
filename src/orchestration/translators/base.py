"""Abstract base class for platform translators."""
from abc import ABC, abstractmethod
from typing import Any


class PlatformTranslator(ABC):
    """
    Abstract base class for translating OmniTraffick tickets into platform-specific payloads.
    
    Each platform (Meta, TikTok, Google Ads) implements this interface to generate
    the exact JSON structure required by their respective APIs.
    """

    @abstractmethod
    def build_campaign_payload(self, ticket: Any) -> dict[str, Any]:
        """
        Build a campaign creation payload for the platform.
        
        Args:
            ticket: Ticket model instance with campaign, channel, and payload_config data
            
        Returns:
            Platform-specific JSON payload for campaign creation
            
        Raises:
            ValueError: If required data is missing or invalid
        """
        pass

    @abstractmethod
    def build_adset_payload(self, ticket: Any, campaign_id: str) -> dict[str, Any]:
        """
        Build an adset/ad group creation payload for the platform.
        
        Args:
            ticket: Ticket model instance
            campaign_id: External platform campaign ID
            
        Returns:
            Platform-specific JSON payload for adset creation
            
        Raises:
            ValueError: If required data is missing or invalid
        """
        pass

    @abstractmethod
    def build_ad_payload(self, ticket: Any, adset_id: str) -> dict[str, Any]:
        """
        Build an ad creation payload for the platform.
        
        Args:
            ticket: Ticket model instance
            adset_id: External platform adset ID
            
        Returns:
            Platform-specific JSON payload for ad creation
            
        Raises:
            ValueError: If required data is missing or invalid
        """
        pass

    @abstractmethod
    def validate_payload_config(self, payload_config: dict[str, Any]) -> bool:
        """
        Validate that the ticket's payload_config contains all required fields.
        
        Args:
            payload_config: The ticket's payload_config JSON
            
        Returns:
            True if valid, False otherwise
        """
        pass
