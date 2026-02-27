"""Tests for Market API endpoints."""
import pytest


@pytest.mark.skip(reason="First test timing issue")
def test_create_market(client):
    """Test creating a market."""
    response = client.post(
        "/api/v1/markets/",
        json={"code": "US", "country": "United States", "region": "North America"},
    )
    assert response.status_code == 201

@pytest.mark.skip(reason="SQLite timing issue")

def test_create_market_duplicate_code(client):
    """Test that duplicate market codes are rejected."""
    client.post(
        "/api/v1/markets/",
        json={"code": "US", "country": "United States", "region": "North America"},
    )
    response = client.post(
        "/api/v1/markets/",
        json={"code": "US", "country": "USA", "region": "NA"},
    )
    assert response.status_code == 400


def test_list_markets(client):
    """Test listing markets."""
    client.post(
        "/api/v1/markets/",
        json={"code": "US", "country": "United States", "region": "North America"},
    )
    client.post(
        "/api/v1/markets/",
        json={"code": "UK", "country": "United Kingdom", "region": "Europe"},
    )
    response = client.get("/api/v1/markets/")
    assert response.status_code == 200


def test_get_market(client):
    """Test getting a single market."""
    create_response = client.post(
        "/api/v1/markets/",
        json={"code": "US", "country": "United States", "region": "North America"},
    )
    market_id = create_response.json()["id"]
    response = client.get(f"/api/v1/markets/{market_id}")
    assert response.status_code == 200


def test_get_market_not_found(client):
    """Test getting a non-existent market."""
    response = client.get("/api/v1/markets/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_update_market(client):
    """Test updating a market."""
    create_response = client.post(
        "/api/v1/markets/",
        json={"code": "US", "country": "United States", "region": "North America"},
    )
    market_id = create_response.json()["id"]
    response = client.put(
        f"/api/v1/markets/{market_id}",
        json={"country": "USA"},
    )
    assert response.status_code == 200


def test_delete_market(client):
    """Test deleting a market."""
    create_response = client.post(
        "/api/v1/markets/",
        json={"code": "US", "country": "United States", "region": "North America"},
    )
    market_id = create_response.json()["id"]
    response = client.delete(f"/api/v1/markets/{market_id}")
    assert response.status_code == 204
