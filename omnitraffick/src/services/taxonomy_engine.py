"""Taxonomy Engine - Generates standardized campaign naming."""
import re
from datetime import datetime


class TaxonomyEngine:
    """Generates standardized campaign names following strict taxonomy rules."""

    @staticmethod
    def generate_campaign_name(
        brand_code: str,
        market_code: str,
        channel_platform: str,
        campaign_name: str,
        year: int | None = None,
    ) -> str:
        """
        Generate a campaign name following the taxonomy rule:
        [BrandCode]_[MarketCode]_[ChannelPlatform]_[Year]_[CampaignName]

        Example: DIS_US_META_2026_MoanaLaunch

        Args:
            brand_code: Brand internal code (e.g., "DIS")
            market_code: Market code (e.g., "US")
            channel_platform: Channel platform name (e.g., "META")
            campaign_name: User-provided campaign name
            year: Year (defaults to current year)

        Returns:
            Formatted campaign name string

        Raises:
            ValueError: If any input contains invalid characters
        """
        # Use current year if not provided
        if year is None:
            year = datetime.now().year

        # Sanitize campaign_name (alphanumeric only, remove spaces)
        sanitized_name = TaxonomyEngine._sanitize_name(campaign_name)

        if not sanitized_name:
            raise ValueError("Campaign name must contain at least one alphanumeric character")

        # Validate brand_code and market_code format
        if not TaxonomyEngine._is_valid_code(brand_code):
            raise ValueError(f"Invalid brand_code: {brand_code}. Must be alphanumeric with underscores.")

        if not TaxonomyEngine._is_valid_code(market_code):
            raise ValueError(f"Invalid market_code: {market_code}. Must be alphanumeric with underscores.")

        # Build taxonomy string
        taxonomy = f"{brand_code.upper()}_{market_code.upper()}_{channel_platform.upper()}_{year}_{sanitized_name}"

        return taxonomy

    @staticmethod
    def _sanitize_name(name: str) -> str:
        """
        Sanitize campaign name: remove all non-alphanumeric characters (including spaces).

        Args:
            name: Raw campaign name

        Returns:
            Sanitized name (alphanumeric only)
        """
        # Remove all characters except alphanumeric
        sanitized = re.sub(r"[^A-Za-z0-9]", "", name)
        return sanitized

    @staticmethod
    def _is_valid_code(code: str) -> bool:
        """
        Validate that a code contains only alphanumeric characters and underscores.

        Args:
            code: Code to validate

        Returns:
            True if valid, False otherwise
        """
        return bool(re.match(r"^[A-Za-z0-9_]+$", code))

    @staticmethod
    def validate_taxonomy(taxonomy: str) -> bool:
        """
        Validate that a taxonomy string matches the expected pattern.

        Pattern: ^[A-Z0-9_]+_[A-Z0-9_]+_[A-Z0-9_]+_\\d{4}_[A-Za-z0-9_]+$

        Args:
            taxonomy: Taxonomy string to validate

        Returns:
            True if valid, False otherwise
        """
        pattern = r"^[A-Z0-9_]+_[A-Z0-9_]+_[A-Z0-9_]+_\d{4}_[A-Za-z0-9_]+$"
        return bool(re.match(pattern, taxonomy))
