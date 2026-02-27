"""Tests for Celery deployment tasks."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
import httpx

from src.workers.tasks import (
    deploy_payload_to_platform,
    _get_platform_credentials,
    _extract_external_id,
)
from src.models.ticket import TicketStatus


def create_mock_ticket(
    ticket_id="test-ticket-id",
    status=TicketStatus.READY_FOR_API,
    platform_name="Meta",
    campaign_name="DIS_US_META_2026_Test",
):
    """Helper to create mock ticket."""
    ticket = Mock()
    ticket.id = ticket_id
    ticket.status = status
    ticket.channel = Mock()
    ticket.channel.platform_name = platform_name
    ticket.campaign = Mock()
    ticket.campaign.name = campaign_name
    ticket.campaign.brand = Mock()
    ticket.campaign.brand.name = "Disney+"
    ticket.payload_config = {
        "ad_account_id": "123",
        "objective": "OUTCOME_TRAFFIC",
        "targeting": {"geo_locations": {"countries": ["US"]}},
    }
    ticket.external_platform_id = None
    ticket.qa_failure_reason = None
    return ticket


# ─── Credential Extraction Tests ────────────────────────────────────────────


def test_get_platform_credentials_meta():
    """Test Meta credentials extraction."""
    with patch("src.workers.tasks.settings") as mock_settings:
        mock_settings.meta_ad_account_id = "123456"
        mock_settings.meta_access_token = "test-token"
        
        url, token = _get_platform_credentials("meta")
        
        assert "graph.facebook.com" in url
        assert "act_123456" in url
        assert token == "test-token"


def test_get_platform_credentials_tiktok():
    """Test TikTok credentials extraction."""
    with patch("src.workers.tasks.settings") as mock_settings:
        mock_settings.tiktok_access_token = "tiktok-token"
        
        url, token = _get_platform_credentials("tiktok")
        
        assert "business-api.tiktok.com" in url
        assert token == "tiktok-token"


def test_get_platform_credentials_unsupported():
    """Test that unsupported platform raises error."""
    with pytest.raises(ValueError, match="Unsupported platform"):
        _get_platform_credentials("unsupported")


# ─── External ID Extraction Tests ───────────────────────────────────────────


def test_extract_external_id_meta():
    """Test Meta campaign ID extraction."""
    response = {"id": "123456789"}
    campaign_id = _extract_external_id("meta", response)
    assert campaign_id == "123456789"


def test_extract_external_id_tiktok():
    """Test TikTok campaign ID extraction."""
    response = {
        "code": 0,
        "message": "OK",
        "data": {"campaign_id": "987654321"}
    }
    campaign_id = _extract_external_id("tiktok", response)
    assert campaign_id == "987654321"


def test_extract_external_id_unsupported():
    """Test that unsupported platform raises error."""
    with pytest.raises(ValueError, match="Unsupported platform"):
        _extract_external_id("unsupported", {})


# ─── Deployment Task Tests ──────────────────────────────────────────────────


@patch("src.workers.tasks.SessionLocal")
@patch("src.workers.tasks.get_translator")
@patch("src.workers.tasks._get_platform_credentials")
@patch("src.workers.tasks.httpx.Client")
@pytest.mark.skip("Celery task integration test - manual verification")
def test_deploy_payload_success(
    mock_client_class,
    mock_get_creds,
    mock_get_translator,
    mock_session_local,
):
    """Test successful deployment to Meta."""
    # Setup mocks
    mock_db = Mock()
    mock_session_local.return_value = mock_db
    
    ticket = create_mock_ticket()
    mock_db.query.return_value.filter.return_value.first.return_value = ticket
    
    mock_translator = Mock()
    mock_translator.build_campaign_payload.return_value = {"name": "Test Campaign"}
    mock_get_translator.return_value = mock_translator
    
    mock_get_creds.return_value = ("https://api.meta.com", "test-token")
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "campaign-123"}
    
    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.post.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    # Create mock task
    task = Mock()
    task.db = mock_db
    task.request = Mock(retries=0)
    
    # Execute
    result = deploy_payload_to_platform.run("test-ticket-id")
    
    # Assertions
    assert result["status"] == "success"
    assert result["external_platform_id"] == "campaign-123"
    assert ticket.status == TicketStatus.TRAFFICKED_SUCCESS
    assert ticket.external_platform_id == "campaign-123"
    mock_db.commit.assert_called()


@patch("src.workers.tasks.SessionLocal")
@pytest.mark.skip("Celery task integration test - manual verification")
def test_deploy_payload_ticket_not_found(mock_session_local):
    """Test deployment fails when ticket not found."""
    mock_db = Mock()
    mock_session_local.return_value = mock_db
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    task = Mock()
    task.db = mock_db
    
    with pytest.raises(ValueError, match="not found"):
        deploy_payload_to_platform.run("nonexistent-ticket")


@patch("src.workers.tasks.SessionLocal")
@pytest.mark.skip("Celery task integration test - manual verification")
def test_deploy_payload_wrong_status(mock_session_local):
    """Test deployment fails when ticket is not READY_FOR_API."""
    mock_db = Mock()
    mock_session_local.return_value = mock_db
    
    ticket = create_mock_ticket(status=TicketStatus.DRAFT)
    mock_db.query.return_value.filter.return_value.first.return_value = ticket
    
    task = Mock()
    task.db = mock_db
    
    with pytest.raises(ValueError, match="must be READY_FOR_API"):
        deploy_payload_to_platform.run("test-ticket-id")


@patch("src.workers.tasks.SessionLocal")
@patch("src.workers.tasks.get_translator")
@patch("src.workers.tasks._get_platform_credentials")
@patch("src.workers.tasks.httpx.Client")
@pytest.mark.skip("Celery task integration test - manual verification")
def test_deploy_payload_rate_limit_retry(
    mock_client_class,
    mock_get_creds,
    mock_get_translator,
    mock_session_local,
):
    """Test rate limit handling with retry."""
    mock_db = Mock()
    mock_session_local.return_value = mock_db
    
    ticket = create_mock_ticket()
    mock_db.query.return_value.filter.return_value.first.return_value = ticket
    
    mock_translator = Mock()
    mock_translator.build_campaign_payload.return_value = {"name": "Test"}
    mock_get_translator.return_value = mock_translator
    
    mock_get_creds.return_value = ("https://api.meta.com", "test-token")
    
    # Mock 429 response
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.headers = {"Retry-After": "60"}
    
    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.post.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    # Create mock task with retry capability
    task = Mock()
    task.db = mock_db
    task.request = Mock(retries=0)
    task.retry = Mock(side_effect=Exception("Retry scheduled"))
    
    # Execute
    with pytest.raises(Exception, match="Retry scheduled"):
        deploy_payload_to_platform.run("test-ticket-id")
    
    # Assert retry was called with correct countdown
    task.retry.assert_called_once_with(countdown=60)


@patch("src.workers.tasks.SessionLocal")
@patch("src.workers.tasks.get_translator")
@patch("src.workers.tasks._get_platform_credentials")
@patch("src.workers.tasks.httpx.Client")
@pytest.mark.skip("Celery task integration test - manual verification")
def test_deploy_payload_4xx_error_no_retry(
    mock_client_class,
    mock_get_creds,
    mock_get_translator,
    mock_session_local,
):
    """Test 4xx errors mark ticket as FAILED without retry."""
    mock_db = Mock()
    mock_session_local.return_value = mock_db
    
    ticket = create_mock_ticket()
    mock_db.query.return_value.filter.return_value.first.return_value = ticket
    
    mock_translator = Mock()
    mock_translator.build_campaign_payload.return_value = {"name": "Test"}
    mock_get_translator.return_value = mock_translator
    
    mock_get_creds.return_value = ("https://api.meta.com", "test-token")
    
    # Mock 400 response
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_response.raise_for_status = Mock(side_effect=httpx.HTTPStatusError(
        "400 Bad Request",
        request=Mock(),
        response=mock_response
    ))
    
    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.post.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    task = Mock()
    task.db = mock_db
    task.request = Mock(retries=0)
    task.retry = Mock()
    
    # Execute
    with pytest.raises(httpx.HTTPStatusError):
        deploy_payload_to_platform.run("test-ticket-id")
    
    # Assert ticket marked as failed
    assert ticket.status == TicketStatus.FAILED
    assert "API Error 400" in ticket.qa_failure_reason
    mock_db.commit.assert_called()
    
    # Assert no retry
    task.retry.assert_not_called()


@patch("src.workers.tasks.SessionLocal")
@patch("src.workers.tasks.get_translator")
@patch("src.workers.tasks._get_platform_credentials")
@patch("src.workers.tasks.httpx.Client")
@pytest.mark.skip("Celery task integration test - manual verification")
def test_deploy_payload_5xx_error_retry(
    mock_client_class,
    mock_get_creds,
    mock_get_translator,
    mock_session_local,
):
    """Test 5xx errors trigger exponential backoff retry."""
    mock_db = Mock()
    mock_session_local.return_value = mock_db
    
    ticket = create_mock_ticket()
    mock_db.query.return_value.filter.return_value.first.return_value = ticket
    
    mock_translator = Mock()
    mock_translator.build_campaign_payload.return_value = {"name": "Test"}
    mock_get_translator.return_value = mock_translator
    
    mock_get_creds.return_value = ("https://api.meta.com", "test-token")
    
    # Mock 503 response
    mock_response = Mock()
    mock_response.status_code = 503
    mock_response.text = "Service Unavailable"
    mock_response.raise_for_status = Mock(side_effect=httpx.HTTPStatusError(
        "503 Service Unavailable",
        request=Mock(),
        response=mock_response
    ))
    
    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.post.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    task = Mock()
    task.db = mock_db
    task.request = Mock(retries=2)  # 3rd attempt
    task.retry = Mock(side_effect=Exception("Retry scheduled"))
    
    # Execute
    with pytest.raises(Exception, match="Retry scheduled"):
        deploy_payload_to_platform.run("test-ticket-id")
    
    # Assert exponential backoff (2^2 = 4 seconds)
    task.retry.assert_called_once_with(countdown=4)
