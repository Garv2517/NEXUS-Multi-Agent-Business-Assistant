"""
Integration tests for /api/risk/* endpoints (NEXUS Phase D2: Risk Management).

Verifies:
- All 7 read-only routes return HTTP 200 with typed Pydantic payloads.
- Canonical ID fields are integer (product_id, store_id).
- Canonical monetary fields are integer cents (*_cents) with currency USD.
- Missing analytics database returns controlled HTTP 503 without leaking paths.
- Invalid query parameters return controlled HTTP 400 or 422.
"""
import pytest
from starlette.testclient import TestClient
from app.main import app
from app.api.risk import get_risk_service
from app.services.risk_service import RiskService
from app.repositories.analytics_repository import AnalyticsRepository


@pytest.fixture
def client():
    return TestClient(app)


def test_api_risk_config(client):
    res = client.get("/api/risk/config")
    assert res.status_code == 200
    data = res.json()
    assert data["assumed_snapshot_date"] == "2025-12-31"
    assert data["snapshot_date_is_assumed"] is True
    assert data["placement_dos_p10_days"] == 130.87
    assert data["placement_dos_p90_days"] == 392.04
    assert data["placement_material_capital_cents"] == 27554
    assert data["product_dos_p90_days"] == 241.34
    assert data["product_material_capital_cents"] == 2087756
    assert data["velocity_min_prior_units"] == 100
    assert data["velocity_severe_contraction_pct"] == -22.03


def test_api_risk_overview(client):
    res = client.get("/api/risk/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["currency_code"] == "USD"
    assert data["assumed_snapshot_date"] == "2025-12-31"
    assert data["snapshot_date_is_assumed"] is True
    assert len(data["domains"]) == 5

    # Verify domains
    domain_names = [d["domain"] for d in data["domains"]]
    assert "Stockout Exposure" in domain_names
    assert "Inventory Pressure" in domain_names
    assert "Slow-Moving Exposure" in domain_names
    assert "Sales Velocity" in domain_names
    assert "Portfolio Concentration" in domain_names

    # Check that no 0-100 overall score exists
    assert "No single 0-100 score" in data["governance_note"]


def test_api_risk_stockouts(client):
    res = client.get("/api/risk/stockouts?limit=10")
    assert res.status_code == 200
    data = res.json()
    s = data["summary"]

    assert s["total_placements"] == 14143
    assert s["zero_stock_placements"] == 321
    assert s["affected_products_count"] == 148
    assert s["affected_stores_count"] == 27
    assert s["affected_categories_count"] == 16
    assert s["historical_units_sold"] == 14936
    assert s["historical_revenue_associated_cents"] == 22884556
    assert s["historical_gross_profit_associated_cents"] == 9855306
    assert s["currency_code"] == "USD"

    # Verify terminology
    assert "Historical revenue associated with current zero-stock placements" in s["wording_note"]
    assert "lost revenue" not in s["wording_note"].lower()

    # Verify sample placements format
    assert len(data["sample_placements"]) <= 10
    if data["sample_placements"]:
        p0 = data["sample_placements"][0]
        assert isinstance(p0["product_id"], int)
        assert isinstance(p0["store_id"], int)
        assert isinstance(p0["historical_revenue_associated_cents"], int)


def test_api_risk_inventory_pressure(client):
    res = client.get("/api/risk/inventory-pressure?limit=25")
    assert res.status_code == 200
    data = res.json()
    assert data["currency_code"] == "USD"
    assert data["snapshot_date_is_assumed"] is True
    assert data["total_placements_evaluated"] == 25
    assert len(data["high_pressure_items"]) == 25

    item = data["high_pressure_items"][0]
    assert isinstance(item["product_id"], int)
    assert isinstance(item["store_id"], int)
    assert isinstance(item["inventory_cost_cents"], int)
    assert item["coverage_tier"] in [
        "Stockout", "High Pressure", "Moderate Pressure",
        "Typical", "Elevated Coverage", "Slow-Moving Candidate"
    ]
    assert "explanation" in item


def test_api_risk_slow_moving(client):
    res = client.get("/api/risk/slow-moving?limit=15")
    assert res.status_code == 200
    data = res.json()
    assert data["currency_code"] == "USD"
    assert "obsolete" not in data["terminology_note"].lower()

    # Product candidates
    for p in data["candidate_products"]:
        assert isinstance(p["product_id"], int)
        assert p["days_of_supply"] > 241.34
        assert p["inventory_cost_value_cents"] >= 2087756
        assert isinstance(p["inventory_cost_value_cents"], int)


def test_api_risk_concentration(client):
    res = client.get("/api/risk/concentration")
    assert res.status_code == 200
    data = res.json()
    assert data["currency_code"] == "USD"

    # Check products, categories, stores
    p = data["products"]
    assert p["entity_count"] == 180
    assert p["hhi"] == pytest.approx(66.35, rel=1e-2)
    assert p["hhi_to_equal_ratio"] == pytest.approx(1.19, rel=1e-2)

    c = data["categories"]
    assert c["entity_count"] == 16
    assert c["hhi"] == pytest.approx(701.76, rel=1e-2)
    assert c["hhi_to_equal_ratio"] == pytest.approx(1.12, rel=1e-2)

    s = data["stores"]
    assert s["entity_count"] == 120
    assert s["hhi"] == pytest.approx(85.26, rel=1e-2)
    assert s["hhi_to_equal_ratio"] == pytest.approx(1.02, rel=1e-2)

    # Confirm absence of regulatory / antitrust language
    assert "market concentration" not in data["methodology_note"].lower()
    assert "doj" not in data["methodology_note"].lower()


def test_api_risk_sales_velocity(client):
    res = client.get("/api/risk/sales-velocity?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert data["window_days"] == 28

    comp = data["company_momentum"]
    assert comp["recent_28d_units"] == 43701
    assert comp["prior_28d_units"] == 43245
    assert round(comp["change_pct"], 2) == 1.05

    assert len(data["categories_momentum"]) == 16
    assert len(data["top_contracting_products"]) <= 5
    assert len(data["top_growing_products"]) <= 5

    for prod in data["top_contracting_products"]:
        assert isinstance(prod["product_id"], int)
        assert isinstance(prod["prior_28d_revenue_cents"], int)
        assert prod["classification"] in ["Severe Contraction", "Moderate Contraction", "Stable"]


def test_api_risk_invalid_parameters(client):
    # Invalid limit (negative or 0)
    res = client.get("/api/risk/stockouts?limit=0")
    assert res.status_code == 422

    res = client.get("/api/risk/inventory-pressure?limit=-10")
    assert res.status_code == 422

    res = client.get("/api/risk/sales-velocity?limit=1000")
    assert res.status_code == 422


def test_api_risk_missing_database_returns_503(client, tmp_path):
    """Verifies that if analytics database is missing, risk API returns clean HTTP 503."""
    missing_db = tmp_path / "non_existent_nexus_analytics.db"

    def override_risk_service():
        repo = AnalyticsRepository(db_path=str(missing_db))
        return RiskService(repository=repo)

    app.dependency_overrides[get_risk_service] = override_risk_service

    try:
        res = client.get("/api/risk/overview")
        assert res.status_code == 503
        data = res.json()
        assert data["detail"] == "Analytics dataset unavailable"
        assert "non_existent" not in str(data)
    finally:
        app.dependency_overrides.clear()
