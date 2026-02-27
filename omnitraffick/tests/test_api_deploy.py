"""Tests for deployment API endpoints."""
import pytest
from unittest.mock import Mock, patch
from src.models.ticket import TicketStatus


def create_test_entities(client):
    """Create test market, brand, channel, campaign, ticket."""
    # Create market
    market_response = client.post(
        "/api/v1/markets",
        json={"code": "US", "country": "United States", "region": "North America"},
    )
    market_id = market_response.json()["id"]
    
    # Create brand
    brand_response = client.post(
        "/api/v1/brands",
        json={"name": "Disney+", "internal_code": "DIS"},
    )
    brand_id = brand_response.json()["id"]
    
    # Create channel
    channel_response = client.post(
        "/api/v1/channels",
        json={"platform_name": "Meta", "api_identifier": "meta_marketing_api"},
    )
    channel_id = channel_response.json()["id"]
    
    # Create campaign
    campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "campaign_name": "MoanaLaunch",
            "brand_id": brand_id,
            "market_id": market_id,
            "budget": 50000.00,
        },
    )
    campaign_id = campaign_response.json()["id"]
    
    # Create ticket
    ticket_response = client.post(
        "/api/v1/tickets",
        json={
            "campaign_id": campaign_id,
            "channel_id": channel_id,
            "request_type": "CREATE_CAMPAIGN",
            "payload_config": {
                "ad_account_id": "123",
                "objective": "OUTCOME_TRAFFIC",
                "targeting": {"geo_locations": {"countries": ["US"]}},
            },
        },
    )
    
    return ticket_response.json()


@pytest.mark.skip("FastAPI TestClient SQLite connection pooling issue")
def test_deploy_ticket_success(client):
    """Test successful deployment queue."""
    # Create test ticket
    ticket = create_test_entities(client)
    ticket_id = ticket["id"]
    
    # Update ticket to READY_FOR_API
    client.put(
        f"/api/v1/tickets/{ticket_id}",
        json={"status": "READY_FOR_API"},
    )
    
    # Mock Celery task
    with patch("src.api.v1.deploy.deploy_payload_to_platform") as mock_task:
        mock_task.delay.return_value = Mock(id="task-123")
        
        # Deploy
        response = client.post(
            "/api/v1/deploy",
            json={"ticket_id": ticket_id},
        )
        
        # Assertions
        assert response.status_code == 202
        data = response.json()
        assert data["task_id"] == "task-123"
        assert data["ticket_id"] == ticket_id
        assert data["status"] == "queued"
        
        # Verify task was queued
        mock_task.delay.assert_called_once_with(ticket_id)


@pytest.mark.skip("FastAPI TestClient SQLite connection pooling issue")
def test_deploy_ticket_not_found(client):
    """Test deployment fails for nonexistent ticket."""
    response = client.post(
        "/api/v1/deploy",
        json={"ticket_id": "nonexistent-id"},
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.skip("FastAPI TestClient SQLite connection pooling issue")
def test_deploy_ticket_wrong_status(client):
    """Test deployment fails when ticket is not READY_FOR_API."""
    # Create test ticket (status will be DRAFT)
    ticket = create_test_entities(client)
    ticket_id = ticket["id"]
    
    # Try to deploy without QA passing
    response = client.post(
        "/api/v1/deploy",
        json={"ticket_id": ticket_id},
    )
    
    assert response.status_code == 400
    assert "must be READY_FOR_API" in response.json()["detail"]


@pytest.mark.skip("Integration test - requires Celery worker")
def test_deployment_status_success():
    """Test deployment status check for successful task."""
    with patch("src.api.v1.deploy.AsyncResult") as mock_result_class:
        mock_task = Mock()
        mock_task.state = "SUCCESS"
        mock_task.result = {
            "status": "success",
            "external_platform_id": "campaign-123"
        }
        mock_result_class.return_value = mock_task
        
        from src.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/api/v1/deploy/status/task-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "task-123"
        assert data["status"] == "SUCCESS"
        assert data["result"]["external_platform_id"] == "campaign-123"


@pytest.mark.skip("Integration test - requires Celery worker")
def test_deployment_status_failure():
    """Test deployment status check for failed task."""
    with patch("src.api.v1.deploy.AsyncResult") as mock_result_class:
        mock_task = Mock()
        mock_task.state = "FAILURE"
        mock_task.info = Exception("API Error 400")
        mock_result_class.return_value = mock_task
        
        from src.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/api/v1/deploy/status/task-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "task-123"
        assert data["status"] == "FAILURE"
        assert "API Error" in data["error"]


@pytest.mark.skip("Integration test - requires Celery worker")
def test_deployment_status_pending():
    """Test deployment status check for pending task."""
    with patch("src.api.v1.deploy.AsyncResult") as mock_result_class:
        mock_task = Mock()
        mock_task.state = "PENDING"
        mock_result_class.return_value = mock_task
        
        from src.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/api/v1/deploy/status/task-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "task-123"
        assert data["status"] == "PENDING"
        assert "result" not in data
        assert "error" not in data
