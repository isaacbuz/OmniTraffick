"""QA Rules Engine - Pre-flight validation for campaign payloads."""
import re
from typing import Any
from decimal import Decimal
from sqlalchemy.orm import Session

from src.models.ticket import Ticket, TicketStatus
from src.models.brand import Brand
from src.services.taxonomy_engine import TaxonomyEngine


class QAEngine:
    """
    Pre-flight QA engine that validates campaign payloads before API trafficking.
    
    Rules are evaluated in order. If any rule fails, the ticket status is updated
    to QA_FAILED with a failure reason, and the payload is blocked from API submission.
    """

    def __init__(self, db: Session):
        """
        Initialize QA Engine.
        
        Args:
            db: Database session for querying brand/campaign data
        """
        self.db = db

    def evaluate(self, ticket: Ticket) -> tuple[bool, str | None]:
        """
        Evaluate all QA rules for a ticket.
        
        Args:
            ticket: Ticket to evaluate
            
        Returns:
            Tuple of (passed: bool, failure_reason: str | None)
            If passed=True, failure_reason is None
            If passed=False, failure_reason contains the error message
        """
        rules = [
            self._rule_taxonomy_validity,
            self._rule_brand_safety,
            self._rule_budget_limits,
            self._rule_payload_schema,
        ]

        for rule in rules:
            passed, reason = rule(ticket)
            if not passed:
                # Update ticket status to QA_FAILED
                ticket.status = TicketStatus.QA_FAILED
                ticket.qa_failure_reason = reason
                self.db.commit()
                return False, reason

        # All rules passed
        ticket.status = TicketStatus.READY_FOR_API
        ticket.qa_failure_reason = None
        self.db.commit()
        return True, None

    def _rule_taxonomy_validity(self, ticket: Ticket) -> tuple[bool, str | None]:
        """
        Rule 1: Taxonomy Validity
        
        Validates that the campaign name strictly matches our taxonomy pattern:
        [BrandCode]_[MarketCode]_[ChannelPlatform]_[Year]_[CampaignName]
        
        Example: DIS_US_META_2026_MoanaLaunch
        """
        campaign_name = ticket.campaign.name

        if not TaxonomyEngine.validate_taxonomy(campaign_name):
            return False, f"Campaign name '{campaign_name}' does not match taxonomy pattern"

        return True, None

    def _rule_brand_safety(self, ticket: Ticket) -> tuple[bool, str | None]:
        """
        Rule 2: Brand Safety
        
        If the brand is marked "family_friendly", verify that the payload does NOT
        contain targeting IDs for adult content or alcohol interests.
        
        Platform-specific blocked interest IDs:
        - Meta: 6003139266461 (alcohol), 6004854404172 (adult content)
        - TikTok: 100001 (alcohol), 100002 (gambling), 100003 (adult content)
        """
        brand = ticket.campaign.brand
        config = ticket.payload_config

        # Check if brand has family_friendly flag (assume stored in brand metadata)
        # For Phase 3, we'll add a boolean field to Brand model in Phase 4
        # For now, check if brand name contains "Disney" or "Kids" as placeholder
        is_family_friendly = any(
            keyword in brand.name.lower() for keyword in ["disney", "kids", "family", "children"]
        )

        if not is_family_friendly:
            return True, None  # No restrictions

        # Check Meta targeting
        if config.get("targeting", {}).get("flexible_spec"):
            interests = config["targeting"]["flexible_spec"]
            blocked_meta_interests = ["6003139266461", "6004854404172"]
            for interest_set in interests:
                for interest in interest_set.get("interests", []):
                    if interest.get("id") in blocked_meta_interests:
                        return False, f"Family-friendly brand cannot target adult/alcohol interests (Meta interest ID: {interest['id']})"

        # Check TikTok targeting
        if config.get("interest_category_ids"):
            blocked_tiktok_interests = ["100001", "100002", "100003"]
            for interest_id in config["interest_category_ids"]:
                if str(interest_id) in blocked_tiktok_interests:
                    return False, f"Family-friendly brand cannot target adult/alcohol/gambling interests (TikTok interest ID: {interest_id})"

        return True, None

    def _rule_budget_limits(self, ticket: Ticket) -> tuple[bool, str | None]:
        """
        Rule 3: Budget Limits
        
        Reject any request where daily budget > $100,000.
        
        This is a safety mechanism to prevent accidental overspend.
        """
        config = ticket.payload_config

        # Check Meta daily_budget (in config as string dollars, stored as cents in payload)
        if config.get("daily_budget"):
            daily_budget = Decimal(config["daily_budget"])
            if daily_budget > Decimal("100000.00"):
                return False, f"Daily budget ${daily_budget} exceeds maximum allowed ($100,000)"

        # Check TikTok budget (stored as string dollars)
        if config.get("budget"):
            budget = Decimal(config["budget"])
            # TikTok uses daily budget by default
            if budget > Decimal("100000.00"):
                return False, f"Daily budget ${budget} exceeds maximum allowed ($100,000)"

        # Check lifetime budget (Meta)
        if config.get("lifetime_budget"):
            lifetime_budget = Decimal(config["lifetime_budget"])
            # Allow higher lifetime budgets (e.g., $1M over 30 days = $33k/day average)
            if lifetime_budget > Decimal("1000000.00"):
                return False, f"Lifetime budget ${lifetime_budget} exceeds maximum allowed ($1,000,000)"

        return True, None

    def _rule_payload_schema(self, ticket: Ticket) -> tuple[bool, str | None]:
        """
        Rule 4: Payload Schema Validation
        
        Verify that the payload_config contains all required fields for the channel.
        
        This prevents incomplete payloads from reaching the API.
        """
        channel_name = ticket.channel.platform_name.lower()
        config = ticket.payload_config

        # Basic validation: ensure critical fields are present
        if channel_name == "meta":
            required_fields = ["ad_account_id", "objective", "targeting"]
            for field in required_fields:
                if field not in config:
                    return False, f"Missing required field for Meta: {field}"

        elif channel_name == "tiktok":
            required_fields = ["advertiser_id", "objective_type", "placements", "location_ids"]
            for field in required_fields:
                if field not in config:
                    return False, f"Missing required field for TikTok: {field}"

        # Ensure targeting has geo data
        if config.get("targeting") and not config["targeting"].get("geo_locations") and channel_name != "tiktok":
            if channel_name == "tiktok" and not config.get("location_ids"):
                return False, "TikTok targeting must include location_ids"

        # Ensure targeting has geo data (platform-specific)
        if channel_name == "meta":
            if config.get("targeting") and not config["targeting"].get("geo_locations"):
                return False, "Meta targeting must include geo_locations"
        elif channel_name == "tiktok":
            if not config.get("location_ids"):
                return False, "TikTok payload must include location_ids"

        return True, None
