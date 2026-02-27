"""Tests for the Taxonomy Engine."""
import pytest
from datetime import datetime
from src.services.taxonomy_engine import TaxonomyEngine


def test_generate_campaign_name_basic():
    """Test basic campaign name generation."""
    name = TaxonomyEngine.generate_campaign_name(
        brand_code="DIS",
        market_code="US",
        channel_platform="META",
        campaign_name="Moana Launch",
        year=2026,
    )
    assert name == "DIS_US_META_2026_MoanaLaunch"


def test_generate_campaign_name_current_year():
    """Test that year defaults to current year."""
    current_year = datetime.now().year
    name = TaxonomyEngine.generate_campaign_name(
        brand_code="HUL",
        market_code="UK",
        channel_platform="TIKTOK",
        campaign_name="Summer Sale",
    )
    assert name == f"HUL_UK_TIKTOK_{current_year}_SummerSale"


def test_generate_campaign_name_sanitizes_spaces():
    """Test that spaces are removed."""
    name = TaxonomyEngine.generate_campaign_name(
        brand_code="NAT",
        market_code="CA",
        channel_platform="GOOGLE",
        campaign_name="Holiday   Gift   Guide",
        year=2026,
    )
    assert name == "NAT_CA_GOOGLE_2026_HolidayGiftGuide"


def test_generate_campaign_name_removes_special_chars():
    """Test that special characters are removed."""
    name = TaxonomyEngine.generate_campaign_name(
        brand_code="DIS",
        market_code="US",
        channel_platform="META",
        campaign_name="Star-Wars: The Force!",
        year=2026,
    )
    assert name == "DIS_US_META_2026_StarWarsTheForce"


def test_generate_campaign_name_uppercase_codes():
    """Test that brand/market codes are uppercased."""
    name = TaxonomyEngine.generate_campaign_name(
        brand_code="dis",
        market_code="us",
        channel_platform="meta",
        campaign_name="test",
        year=2026,
    )
    assert name == "DIS_US_META_2026_test"


def test_generate_campaign_name_invalid_brand_code():
    """Test that invalid brand code raises ValueError."""
    with pytest.raises(ValueError, match="Invalid brand_code"):
        TaxonomyEngine.generate_campaign_name(
            brand_code="DIS-INVALID",
            market_code="US",
            channel_platform="META",
            campaign_name="test",
            year=2026,
        )


def test_generate_campaign_name_invalid_market_code():
    """Test that invalid market code raises ValueError."""
    with pytest.raises(ValueError, match="Invalid market_code"):
        TaxonomyEngine.generate_campaign_name(
            brand_code="DIS",
            market_code="US-CA",
            channel_platform="META",
            campaign_name="test",
            year=2026,
        )


def test_generate_campaign_name_empty_campaign_name():
    """Test that empty campaign name raises ValueError."""
    with pytest.raises(ValueError, match="must contain at least one alphanumeric character"):
        TaxonomyEngine.generate_campaign_name(
            brand_code="DIS",
            market_code="US",
            channel_platform="META",
            campaign_name="!!!",
            year=2026,
        )


def test_validate_taxonomy_valid():
    """Test that valid taxonomy passes validation."""
    assert TaxonomyEngine.validate_taxonomy("DIS_US_META_2026_MoanaLaunch")
    assert TaxonomyEngine.validate_taxonomy("HUL_UK_TIKTOK_2025_SummerSale")
    assert TaxonomyEngine.validate_taxonomy("NAT_CA_GOOGLE_2024_Test_Campaign")


def test_validate_taxonomy_invalid():
    """Test that invalid taxonomy fails validation."""
    assert not TaxonomyEngine.validate_taxonomy("dis_us_meta_2026_test")  # lowercase
    assert not TaxonomyEngine.validate_taxonomy("DIS_US_META_test")  # missing year
    assert not TaxonomyEngine.validate_taxonomy("DIS_US_2026_test")  # missing channel
    assert not TaxonomyEngine.validate_taxonomy("DIS-US-META-2026-test")  # hyphens
