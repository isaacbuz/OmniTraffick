"""Tests for QA Engine."""
import pytest
from unittest.mock import Mock
from decimal import Decimal
from src.qa.engine import QAEngine
from src.models.ticket import TicketStatus


@pytest.fixture
def mock_db():
    """Mock database session."""
    db = Mock()
    db.commit = Mock()
    return db


@pytest.fixture
def qa_engine(mock_db):
    """QA Engine instance."""
    return QAEngine(mock_db)


def create_mock_ticket(
    campaign_name="DIS_US_META_2026_MoanaLaunch",
    brand_name="Disney+",
    channel_name="Meta",
    payload_config=None,
):
    """Helper to create mock ticket."""
    ticket = Mock()
    ticket.campaign = Mock()
    ticket.campaign.name = campaign_name
    ticket.campaign.brand = Mock()
    ticket.campaign.brand.name = brand_name
    ticket.channel = Mock()
    ticket.channel.platform_name = channel_name
    ticket.payload_config = payload_config or {}
    ticket.status = TicketStatus.DRAFT
    ticket.qa_failure_reason = None
    return ticket


# ─── Rule 1: Taxonomy Validity ──────────────────────────────────────────────


def test_qa_taxonomy_valid(qa_engine):
    """Test that valid taxonomy passes QA."""
    ticket = create_mock_ticket(
        campaign_name="DIS_US_META_2026_MoanaLaunch",
        payload_config={
            "ad_account_id": "123",
            "objective": "OUTCOME_TRAFFIC",
            "targeting": {"geo_locations": {"countries": ["US"]}},
        },
    )
    passed, reason = qa_engine.evaluate(ticket)
    assert passed is True
    assert reason is None
    assert reason is None
    assert ticket.status == TicketStatus.READY_FOR_API


def test_qa_taxonomy_invalid_format(qa_engine):
    """Test that invalid taxonomy fails QA."""
    ticket = create_mock_ticket(campaign_name="invalid-campaign-name")
    passed, reason = qa_engine.evaluate(ticket)
    assert passed is False
    assert "does not match taxonomy pattern" in reason
    assert ticket.status == TicketStatus.QA_FAILED


def test_qa_taxonomy_lowercase(qa_engine):
    """Test that lowercase taxonomy fails QA."""
    ticket = create_mock_ticket(campaign_name="dis_us_meta_2026_test")
    passed, reason = qa_engine.evaluate(ticket)
    assert passed is False
    assert ticket.status == TicketStatus.QA_FAILED


# ─── Rule 2: Brand Safety ───────────────────────────────────────────────────


def test_qa_brand_safety_family_friendly_clean(qa_engine):
    """Test that family-friendly brand with clean targeting passes."""
    ticket = create_mock_ticket(
        brand_name="Disney+",
        payload_config={
            "ad_account_id": "123",
            "objective": "OUTCOME_TRAFFIC",
            "targeting": {
                "geo_locations": {"countries": ["US"]},
                "age_min": 18,
                "age_max": 65,
            },
        },
    )
    passed, reason = qa_engine.evaluate(ticket)
    assert passed is True


def test_qa_brand_safety_family_friendly_blocked_meta_interests(qa_engine):
    """Test that family-friendly brand with alcohol interests fails."""
    ticket = create_mock_ticket(
        brand_name="Disney Kids",
        payload_config={
            "ad_account_id": "123",
            "objective": "OUTCOME_TRAFFIC",
            "targeting": {
                "geo_locations": {"countries": ["US"]},
                "flexible_spec": [
                    {
                        "interests": [
                            {"id": "6003139266461", "name": "Alcohol"}  # Blocked
                        ]
                    }
                ],
            },
        },
    )
    passed, reason = qa_engine.evaluate(ticket)
    assert passed is False
    assert "adult/alcohol interests" in reason
    assert ticket.status == TicketStatus.QA_FAILED


def test_qa_brand_safety_family_friendly_blocked_tiktok_interests(qa_engine):
    """Test that family-friendly brand with gambling interests fails."""
    ticket = create_mock_ticket(
        brand_name="Family Channel",
        channel_name="TikTok",
        payload_config={
            "advertiser_id": "123",
            "objective_type": "TRAFFIC",
            "placements": ["PLACEMENT_TIKTOK"],
            "location_ids": ["6252001"],
            "interest_category_ids": ["100002"],  # Gambling (blocked)
        },
    )
    passed, reason = qa_engine.evaluate(ticket)
    assert passed is False
    assert "gambling" in reason.lower()


def test_qa_brand_safety_non_family_brand_allows_all(qa_engine):
    """Test that non-family brands can target any interests."""
    ticket = create_mock_ticket(
        brand_name="Corona Beer",
        payload_config={
            "ad_account_id": "123",
            "objective": "OUTCOME_SALES",
            "targeting": {
                "geo_locations": {"countries": ["US"]},
                "flexible_spec": [
                    {
                        "interests": [
                            {"id": "6003139266461", "name": "Alcohol"}  # Allowed for non-family brands
                        ]
                    }
                ],
            },
        },
    )
    passed, reason = qa_engine.evaluate(ticket)
    assert passed is True


# ─── Rule 3: Budget Limits ──────────────────────────────────────────────────


def test_qa_budget_limits_daily_budget_within_limit(qa_engine):
    """Test that daily budget within limits passes."""
    ticket = create_mock_ticket(
        payload_config={
            "ad_account_id": "123",
            "objective": "OUTCOME_TRAFFIC",
            "targeting": {"geo_locations": {"countries": ["US"]}},
            "daily_budget": "50000.00",  # $50k - within limit
        },
    )
    passed, reason = qa_engine.evaluate(ticket)
    assert passed is True


def test_qa_budget_limits_daily_budget_exceeds(qa_engine):
    """Test that daily budget > $100k fails."""
    ticket = create_mock_ticket(
        payload_config={
            "ad_account_id": "123",
            "objective": "OUTCOME_TRAFFIC",
            "targeting": {"geo_locations": {"countries": ["US"]}},
            "daily_budget": "150000.00",  # $150k - exceeds limit
        },
    )
    passed, reason = qa_engine.evaluate(ticket)
    assert passed is False
    assert "exceeds maximum allowed" in reason
    assert ticket.status == TicketStatus.QA_FAILED


def test_qa_budget_limits_lifetime_budget_within_limit(qa_engine):
    """Test that lifetime budget within limits passes."""
    ticket = create_mock_ticket(
        payload_config={
            "ad_account_id": "123",
            "objective": "OUTCOME_TRAFFIC",
            "targeting": {"geo_locations": {"countries": ["US"]}},
            "lifetime_budget": "500000.00",  # $500k - within limit
        },
    )
    passed, reason = qa_engine.evaluate(ticket)
    assert passed is True


def test_qa_budget_limits_lifetime_budget_exceeds(qa_engine):
    """Test that lifetime budget > $1M fails."""
    ticket = create_mock_ticket(
        payload_config={
            "ad_account_id": "123",
            "objective": "OUTCOME_TRAFFIC",
            "targeting": {"geo_locations": {"countries": ["US"]}},
            "lifetime_budget": "1500000.00",  # $1.5M - exceeds limit
        },
    )
    passed, reason = qa_engine.evaluate(ticket)
    assert passed is False
    assert "exceeds maximum allowed" in reason


def test_qa_budget_limits_tiktok_budget(qa_engine):
    """Test TikTok budget limits."""
    ticket = create_mock_ticket(
        channel_name="TikTok",
        payload_config={
            "advertiser_id": "123",
            "objective_type": "TRAFFIC",
            "placements": ["PLACEMENT_TIKTOK"],
            "location_ids": ["6252001"],
            "budget": "200000.00",  # $200k - exceeds limit
        },
    )
    passed, reason = qa_engine.evaluate(ticket)
    assert passed is False
    assert "exceeds maximum allowed" in reason


# ─── Rule 4: Payload Schema ─────────────────────────────────────────────────


def test_qa_payload_schema_meta_valid(qa_engine):
    """Test that valid Meta payload passes schema check."""
    ticket = create_mock_ticket(
        payload_config={
            "ad_account_id": "123",
            "objective": "OUTCOME_TRAFFIC",
            "targeting": {"geo_locations": {"countries": ["US"]}},
        },
    )
    passed, reason = qa_engine.evaluate(ticket)
    assert passed is True


def test_qa_payload_schema_meta_missing_ad_account(qa_engine):
    """Test that Meta payload missing ad_account_id fails."""
    ticket = create_mock_ticket(
        payload_config={
            "objective": "OUTCOME_TRAFFIC",
            "targeting": {"geo_locations": {"countries": ["US"]}},
        },
    )
    passed, reason = qa_engine.evaluate(ticket)
    assert passed is False
    assert "ad_account_id" in reason


def test_qa_payload_schema_tiktok_valid(qa_engine):
    """Test that valid TikTok payload passes schema check."""
    ticket = create_mock_ticket(
        channel_name="TikTok",
        payload_config={
            "advertiser_id": "123",
            "objective_type": "TRAFFIC",
            "placements": ["PLACEMENT_TIKTOK"],
            "location_ids": ["6252001"],
        },
    )
    passed, reason = qa_engine.evaluate(ticket)
    assert passed is True


def test_qa_payload_schema_tiktok_missing_placements(qa_engine):
    """Test that TikTok payload missing placements fails."""
    ticket = create_mock_ticket(
        channel_name="TikTok",
        payload_config={
            "advertiser_id": "123",
            "objective_type": "TRAFFIC",
            "location_ids": ["6252001"],
        },
    )
    passed, reason = qa_engine.evaluate(ticket)
    assert passed is False
    assert "placements" in reason


def test_qa_payload_schema_missing_geo_targeting(qa_engine):
    """Test that payload without geo targeting fails."""
    ticket = create_mock_ticket(
        payload_config={
            "ad_account_id": "123",
            "objective": "OUTCOME_TRAFFIC",
            "targeting": {},  # No geo_locations
        },
    )
    passed, reason = qa_engine.evaluate(ticket)
    assert passed is False
    assert "geographic locations" in reason
