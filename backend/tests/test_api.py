import pytest
from fastapi.testclient import TestClient
from main import app
from services.data_collector import DataCollector
from services.scoring_engine import ScoringEngine

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    # Now serves the frontend HTML
    assert "text/html" in response.headers.get("content-type", "")

def test_analyze_market_valid_country():
    # This might fail if external APIs are down or rate limited, so we should mock ideally.
    # For now, we'll test with a known country.
    response = client.post("/api/markets/analyze", json={"country_name": "Brazil"})
    assert response.status_code == 200
    data = response.json()
    assert data["country"] == "Brazil"
    assert "score" in data["analysis"]
    assert data["data"]["lat"] != 0
    assert data["data"]["lng"] != 0

def test_analyze_market_invalid_country():
    response = client.post("/api/markets/analyze", json={"country_name": "InvalidCountryName123"})
    assert response.status_code == 404

def test_data_collector_geocoding():
    collector = DataCollector()
    # Test with Brazil (BR)
    data = collector.get_country_data("BR")
    assert data["lat"] is not None
    assert data["lng"] is not None
    # Brazil is roughly -14, -51
    assert -35 < data["lat"] < 5
    assert -75 < data["lng"] < -30
