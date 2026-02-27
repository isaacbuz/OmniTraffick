"""Tests for platform payload translators."""
import pytest
from decimal import Decimal
from unittest.mock import Mock
from src.orchestration.translators.meta import MetaTranslator
from src.orchestration.translators.tiktok import TikTokTranslator


# ─── Meta Translator Tests ──────────────────────────────────────────────────


def test_meta_build_campaign_payload_basic():
    """Test Meta campaign payload generation."""
    translator = MetaTranslator()
    
    # Mock ticket with campaign
    ticket = Mock()
    ticket.campaign = Mock()
    ticket.campaign.name = "DIS_US_META_2026_MoanaLaunch"
    ticket.payload_config = {
        "ad_account_id": "123456789",
        "objective": "OUTCOME_TRAFFIC",
        "special_ad_categories": [],
    }
    
    payload = translator.build_campaign_payload(ticket)
    
    assert payload["name"] == "DIS_US_META_2026_MoanaLaunch"
    assert payload["objective"] == "OUTCOME_TRAFFIC"
    assert payload["status"] == "PAUSED"
    assert payload["special_ad_categories"] == []


def test_meta_build_campaign_payload_with_spend_cap():
    """Test Meta campaign with spend cap."""
    translator = MetaTranslator()
    
    ticket = Mock()
    ticket.campaign = Mock()
    ticket.campaign.name = "TEST_CAMPAIGN"
    ticket.payload_config = {
        "ad_account_id": "123456789",
        "objective": "OUTCOME_SALES",
        "spend_cap": "10000.00",  # $10,000
    }
    
    payload = translator.build_campaign_payload(ticket)
    
    assert payload["spend_cap"] == 1000000  # Converted to cents


def test_meta_build_campaign_payload_missing_account_id():
    """Test that missing ad_account_id raises ValueError."""
    translator = MetaTranslator()
    
    ticket = Mock()
    ticket.campaign = Mock()
    ticket.campaign.name = "TEST"
    ticket.payload_config = {
        "objective": "OUTCOME_TRAFFIC",
    }
    
    with pytest.raises(ValueError, match="ad_account_id"):
        translator.build_campaign_payload(ticket)


def test_meta_build_adset_payload():
    """Test Meta adset payload generation."""
    translator = MetaTranslator()
    
    ticket = Mock()
    ticket.campaign = Mock()
    ticket.campaign.name = "DIS_US_META_2026_Test"
    ticket.payload_config = {
        "targeting": {
            "geo_locations": {"countries": ["US"]},
            "age_min": 18,
            "age_max": 65,
        },
        "optimization_goal": "REACH",
        "billing_event": "IMPRESSIONS",
        "daily_budget": "100.00",
    }
    
    payload = translator.build_adset_payload(ticket, campaign_id="123")
    
    assert payload["name"] == "DIS_US_META_2026_Test_AdSet"
    assert payload["campaign_id"] == "123"
    assert payload["optimization_goal"] == "REACH"
    assert payload["billing_event"] == "IMPRESSIONS"
    assert payload["daily_budget"] == 10000  # $100 in cents
    assert payload["status"] == "PAUSED"
    assert payload["targeting"]["geo_locations"]["countries"] == ["US"]


def test_meta_build_adset_payload_lifetime_budget():
    """Test Meta adset with lifetime budget."""
    translator = MetaTranslator()
    
    ticket = Mock()
    ticket.campaign = Mock()
    ticket.campaign.name = "TEST"
    ticket.payload_config = {
        "targeting": {"geo_locations": {"countries": ["US"]}},
        "optimization_goal": "LINK_CLICKS",
        "billing_event": "LINK_CLICKS",
        "lifetime_budget": "5000.00",
        "end_time": "2026-12-31",
    }
    
    payload = translator.build_adset_payload(ticket, campaign_id="123")
    
    assert payload["lifetime_budget"] == 500000
    assert payload["end_time"] == "2026-12-31"
    assert "daily_budget" not in payload


def test_meta_build_adset_payload_missing_budget():
    """Test that missing budget raises ValueError."""
    translator = MetaTranslator()
    
    ticket = Mock()
    ticket.campaign = Mock()
    ticket.campaign.name = "TEST"
    ticket.payload_config = {
        "targeting": {"geo_locations": {"countries": ["US"]}},
        "optimization_goal": "REACH",
        "billing_event": "IMPRESSIONS",
    }
    
    with pytest.raises(ValueError, match="daily_budget or lifetime_budget"):
        translator.build_adset_payload(ticket, campaign_id="123")


def test_meta_build_ad_payload():
    """Test Meta ad payload generation."""
    translator = MetaTranslator()
    
    ticket = Mock()
    ticket.campaign = Mock()
    ticket.campaign.name = "DIS_US_META_2026_Test"
    ticket.payload_config = {
        "creative": {
            "image_hash": "abc123",
            "message": "Check out our new movie!",
            "link": "https://disney.com/moana",
            "call_to_action": {"type": "LEARN_MORE"},
        }
    }
    
    payload = translator.build_ad_payload(ticket, adset_id="456")
    
    assert payload["name"] == "DIS_US_META_2026_Test_Ad"
    assert payload["adset_id"] == "456"
    assert payload["status"] == "PAUSED"
    assert payload["creative"]["message"] == "Check out our new movie!"


def test_meta_validate_payload_config_valid():
    """Test Meta payload config validation (valid)."""
    translator = MetaTranslator()
    
    config = {
        "ad_account_id": "123",
        "objective": "OUTCOME_TRAFFIC",
        "targeting": {"geo_locations": {"countries": ["US"]}},
        "optimization_goal": "REACH",
        "billing_event": "IMPRESSIONS",
        "daily_budget": "100.00",
        "creative": {"image_hash": "abc"},
    }
    
    assert translator.validate_payload_config(config) is True


def test_meta_validate_payload_config_invalid():
    """Test Meta payload config validation (invalid)."""
    translator = MetaTranslator()
    
    config = {
        "ad_account_id": "123",
        "objective": "OUTCOME_TRAFFIC",
        # Missing targeting, optimization_goal, etc.
    }
    
    assert translator.validate_payload_config(config) is False


# ─── TikTok Translator Tests ────────────────────────────────────────────────


def test_tiktok_build_campaign_payload_basic():
    """Test TikTok campaign payload generation."""
    translator = TikTokTranslator()
    
    ticket = Mock()
    ticket.campaign = Mock()
    ticket.campaign.name = "DIS_US_TIKTOK_2026_Test"
    ticket.payload_config = {
        "advertiser_id": "987654321",
        "objective_type": "TRAFFIC",
        "budget_mode": "BUDGET_MODE_INFINITE",
    }
    
    payload = translator.build_campaign_payload(ticket)
    
    assert payload["advertiser_id"] == "987654321"
    assert payload["campaign_name"] == "DIS_US_TIKTOK_2026_Test"
    assert payload["objective_type"] == "TRAFFIC"
    assert payload["budget_mode"] == "BUDGET_MODE_INFINITE"


def test_tiktok_build_campaign_payload_with_budget():
    """Test TikTok campaign with total budget."""
    translator = TikTokTranslator()
    
    ticket = Mock()
    ticket.campaign = Mock()
    ticket.campaign.name = "TEST"
    ticket.payload_config = {
        "advertiser_id": "987654321",
        "objective_type": "CONVERSIONS",
        "budget_mode": "BUDGET_MODE_TOTAL",
        "budget": "50000.00",
    }
    
    payload = translator.build_campaign_payload(ticket)
    
    assert payload["budget"] == 50000.00


def test_tiktok_build_adset_payload():
    """Test TikTok adgroup payload generation."""
    translator = TikTokTranslator()
    
    ticket = Mock()
    ticket.campaign = Mock()
    ticket.campaign.name = "DIS_US_TIKTOK_2026_Test"
    ticket.payload_config = {
        "advertiser_id": "987654321",
        "placements": ["PLACEMENT_TIKTOK"],
        "location_ids": ["6252001"],  # USA
        "age_groups": ["AGE_25_34", "AGE_35_44"],
        "budget": "100.00",
        "bid_type": "BID_TYPE_NO_BID",
        "optimization_goal": "CLICK",
    }
    
    payload = translator.build_adset_payload(ticket, campaign_id="123")
    
    assert payload["advertiser_id"] == "987654321"
    assert payload["campaign_id"] == "123"
    assert payload["adgroup_name"] == "DIS_US_TIKTOK_2026_Test_AdGroup"
    assert payload["placements"] == ["PLACEMENT_TIKTOK"]
    assert payload["location_ids"] == ["6252001"]
    assert payload["age_groups"] == ["AGE_25_34", "AGE_35_44"]
    assert payload["budget"] == 100.00
    assert payload["budget_mode"] == "BUDGET_MODE_DAY"
    assert payload["bid_type"] == "BID_TYPE_NO_BID"
    assert payload["optimization_goal"] == "CLICK"


def test_tiktok_build_adset_payload_with_bid_price():
    """Test TikTok adgroup with manual bid."""
    translator = TikTokTranslator()
    
    ticket = Mock()
    ticket.campaign = Mock()
    ticket.campaign.name = "TEST"
    ticket.payload_config = {
        "advertiser_id": "987654321",
        "placements": ["PLACEMENT_TIKTOK"],
        "location_ids": ["6252001"],
        "budget": "200.00",
        "bid_type": "BID_TYPE_MAX",
        "bid_price": "0.50",
        "optimization_goal": "CONVERT",
    }
    
    payload = translator.build_adset_payload(ticket, campaign_id="123")
    
    assert payload["bid_price"] == 0.50


def test_tiktok_build_ad_payload():
    """Test TikTok ad payload generation."""
    translator = TikTokTranslator()
    
    ticket = Mock()
    ticket.campaign = Mock()
    ticket.campaign.name = "DIS_US_TIKTOK_2026_Test"
    ticket.payload_config = {
        "advertiser_id": "987654321",
        "creatives": [
            {
                "video_id": "v123",
                "ad_text": "Watch Moana now!",
                "call_to_action": "LEARN_MORE",
            }
        ],
        "landing_page_url": "https://disney.com/moana",
        "display_name": "Disney+",
    }
    
    payload = translator.build_ad_payload(ticket, adset_id="456")
    
    assert payload["advertiser_id"] == "987654321"
    assert payload["adgroup_id"] == "456"
    assert payload["ad_name"] == "DIS_US_TIKTOK_2026_Test_Ad"
    assert payload["ad_format"] == "SINGLE_VIDEO"
    assert payload["landing_page_url"] == "https://disney.com/moana"
    assert payload["display_name"] == "Disney+"
    assert len(payload["creatives"]) == 1


def test_tiktok_validate_payload_config_valid():
    """Test TikTok payload config validation (valid)."""
    translator = TikTokTranslator()
    
    config = {
        "advertiser_id": "987654321",
        "objective_type": "TRAFFIC",
        "placements": ["PLACEMENT_TIKTOK"],
        "location_ids": ["6252001"],
        "budget": "100.00",
        "bid_type": "BID_TYPE_NO_BID",
        "optimization_goal": "CLICK",
        "creatives": [{"video_id": "v123"}],
        "landing_page_url": "https://example.com",
    }
    
    assert translator.validate_payload_config(config) is True


def test_tiktok_validate_payload_config_invalid():
    """Test TikTok payload config validation (invalid)."""
    translator = TikTokTranslator()
    
    config = {
        "advertiser_id": "987654321",
        "objective_type": "TRAFFIC",
        # Missing placements, location_ids, etc.
    }
    
    assert translator.validate_payload_config(config) is False
