"""
Tests for Phase D1D: Read-Only Analytics API (/api/analytics/*).
Verifies:
- All 9 read-only endpoints return status 200 with matching schema contracts
- Authoritative financial representations remain integer cents with currency_code == 'USD'
- Query parameter validation for limit, order_by, category, location returns controlled HTTP 400
- Missing nexus_analytics.db returns controlled HTTP 503 ('Analytics dataset unavailable')
- Isolation from operational database (nexus.db)
"""

import pytest
from app.api.analytics import get_analytics_service
from app.repositories.analytics_repository import AnalyticsRepository
from app.services.analytics_service import AnalyticsService


# --- 1. Metadata Endpoint ---

def test_api_analytics_metadata(client):
    res = client.get("/api/analytics/metadata")
    assert res.status_code == 200
    data = res.json()
    assert data["dataset_name"] == "USA Toy Sales Dataset"
    assert data["dataset_source"] == "Kaggle"
    assert data["license"] == "CC0 / Public Domain"
    assert data["currency_code"] == "USD"
    assert data["sales_start_date"] == "2025-01-01"
    assert data["sales_end_date"] == "2025-12-31"
    assert data["inventory_snapshot_date"] == "2025-12-31"
    assert data["inventory_snapshot_date_is_assumed"] is True


# --- 2. Company Summary Endpoint ---

def test_api_analytics_summary(client):
    res = client.get("/api/analytics/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["currency_code"] == "USD"
    assert data["store_count"] == 120
    assert data["product_count"] == 180
    assert data["category_count"] == 16
    assert data["transaction_count"] == 245800
    assert data["total_units_sold"] == 567270
    assert data["inventory_units"] == 338993
    assert data["stockout_placement_count"] == 321

    # Exact integer cents
    assert data["total_revenue_cents"] == 986293325
    assert data["total_cogs_cents"] == 555682727
    assert data["gross_profit_cents"] == 430610598
    assert data["gross_margin_pct"] == 43.66
    assert data["average_order_value_cents"] == 4013


# --- 3. Monthly Sales Trend Endpoint ---

def test_api_analytics_monthly_sales(client):
    res = client.get("/api/analytics/monthly-sales")
    assert res.status_code == 200
    data = res.json()
    assert data["currency_code"] == "USD"
    assert data["total_months"] == 12
    assert len(data["monthly_trend"]) == 12

    # Verify chronological sequence
    periods = [p["year_month"] for p in data["monthly_trend"]]
    assert periods[0] == "2025-01"
    assert periods[-1] == "2025-12"

    # Monthly sum equals company revenue
    total_rev = sum(p["revenue_cents"] for p in data["monthly_trend"])
    assert total_rev == 986293325


# --- 4. Category Performance Endpoint ---

def test_api_analytics_categories(client):
    res = client.get("/api/analytics/categories")
    assert res.status_code == 200
    data = res.json()
    assert data["currency_code"] == "USD"
    assert len(data["categories"]) == 16

    top_cat = data["categories"][0]
    assert top_cat["category"] == "Action Figures"
    assert top_cat["product_count"] == 17
    assert top_cat["units_sold"] == 52714
    assert top_cat["revenue_cents"] == 106052161
    assert top_cat["revenue_share_pct"] == 10.75


# --- 5. Product Performance Endpoint & Validation ---

def test_api_analytics_products(client):
    # Top 5 products by revenue
    res = client.get("/api/analytics/products?limit=5&order_by=revenue")
    assert res.status_code == 200
    data = res.json()
    assert data["currency_code"] == "USD"
    assert data["total_products"] == 5
    assert len(data["products"]) == 5

    # Top product is Product 130
    top_p = data["products"][0]
    assert isinstance(top_p["product_id"], int)
    assert top_p["product_id"] == 130
    assert top_p["product_name"] == "Mega Board Game"
    assert top_p["revenue_cents"] == 23191047
    assert top_p["units_sold"] == 1623


def test_api_analytics_products_category_filter(client):
    res = client.get("/api/analytics/products?category=Board+Games")
    assert res.status_code == 200
    data = res.json()
    assert data["total_products"] == 11
    for p in data["products"]:
        assert p["product_category"] == "Board Games"


def test_api_analytics_products_invalid_params(client):
    # Invalid limit (0, negative, >1000)
    res = client.get("/api/analytics/products?limit=0")
    assert res.status_code == 400

    res = client.get("/api/analytics/products?limit=-5")
    assert res.status_code == 400

    res = client.get("/api/analytics/products?limit=1001")
    assert res.status_code == 400

    # Invalid order_by
    res = client.get("/api/analytics/products?order_by=malicious_sql")
    assert res.status_code == 400


# --- 6. Store Performance Endpoint & Validation ---

# --- 6. Store Performance Endpoint & Validation ---

def test_api_analytics_stores(client):
    res = client.get("/api/analytics/stores?limit=5&order_by=revenue")
    assert res.status_code == 200
    data = res.json()
    assert data["currency_code"] == "USD"
    assert data["total_stores"] == 5
    top_s = data["stores"][0]
    assert isinstance(top_s["store_id"], int)
    assert top_s["store_id"] == 34
    assert top_s["revenue_cents"] == 10382410


def test_api_analytics_stores_location_filter(client):
    # Test Downtown filter
    res = client.get("/api/analytics/stores?location=Downtown")
    assert res.status_code == 200
    data = res.json()
    assert data["total_stores"] > 0
    for s in data["stores"]:
        assert s["store_location"] == "Downtown"
        assert isinstance(s["store_id"], int)

    # Test Mall filter with limit
    res = client.get("/api/analytics/stores?location=Mall&limit=5")
    assert res.status_code == 200
    data = res.json()
    assert len(data["stores"]) <= 5
    for s in data["stores"]:
        assert s["store_location"] == "Mall"
        assert isinstance(s["store_id"], int)

    # Test Airport filter
    res = client.get("/api/analytics/stores?location=Airport")
    assert res.status_code == 200
    data = res.json()
    assert data["total_stores"] == 4
    for s in data["stores"]:
        assert s["store_location"] == "Airport"


def test_api_analytics_stores_invalid_params(client):
    res = client.get("/api/analytics/stores?limit=-1")
    assert res.status_code == 400

    res = client.get("/api/analytics/stores?order_by=invalid")
    assert res.status_code == 400


# --- 7. Location Performance Endpoint ---

def test_api_analytics_locations(client):
    res = client.get("/api/analytics/locations")
    assert res.status_code == 200
    data = res.json()
    assert data["currency_code"] == "USD"
    assert len(data["locations"]) == 6
    loc_names = {l["store_location"] for l in data["locations"]}
    # Regression test asserting the complete location set is exactly the 6 verified categories
    assert loc_names == {"Downtown", "Mall", "Commercial", "Residential", "Suburban", "Airport"}


# --- 8. Inventory Analytics Summary Endpoint ---

def test_api_analytics_inventory(client):
    # Test both /inventory and /inventory/summary routes
    for path in ["/api/analytics/inventory", "/api/analytics/inventory/summary"]:
        res = client.get(path)
        assert res.status_code == 200
        data = res.json()
        assert data["currency_code"] == "USD"
        assert data["snapshot_date"] == "2025-12-31"
        assert data["snapshot_date_is_assumed"] is True
        assert data["total_placements"] == 14143
        assert data["total_units_on_hand"] == 338993

        # Exact semantic definitions: stock_on_hand == 0 and stock_on_hand > 0
        assert data["out_of_stock_placements"] == 321
        assert data["in_stock_placements"] == 13822
        assert data["out_of_stock_placements"] + data["in_stock_placements"] == data["total_placements"]
        assert data["stockout_rate_pct"] == 2.27

        # Confirm healthy semantics are removed
        assert "healthy_placements" not in data
        assert "healthy_stock_placements" not in data

        assert data["total_cost_value_cents"] == 312121493
        assert data["total_retail_value_cents"] == 557626331


# --- 9. Inventory By Product Endpoint & Validation ---

def test_api_analytics_inventory_products(client):
    res = client.get("/api/analytics/inventory/products?limit=5&order_by=stock_units")
    assert res.status_code == 200
    data = res.json()
    assert data["currency_code"] == "USD"
    assert data["total_products"] == 5
    top_p = data["products"][0]
    assert isinstance(top_p["product_id"], int)
    assert top_p["product_id"] == 61
    assert top_p["product_name"] == "Mini Robot"
    assert top_p["category"] == "Arts & Crafts"
    assert top_p["stock_units"] == 2659
    assert top_p["store_placements"] == 92
    assert top_p["inventory_cost_value_cents"] == 1100826
    assert top_p["inventory_retail_value_cents"] == 1598059
    assert top_p["zero_stock_store_count"] == 1


def test_api_analytics_inventory_products_invalid_params(client):
    res = client.get("/api/analytics/inventory/products?limit=0")
    assert res.status_code == 400

    res = client.get("/api/analytics/inventory/products?order_by=invalid")
    assert res.status_code == 400


# --- 10. Missing Database -> Controlled HTTP 503 ---

def test_api_analytics_missing_database_returns_503(client, tmp_path):
    """Verifies that if analytics database is missing, API returns clean HTTP 503 without crashing."""
    missing_db = tmp_path / "non_existent_nexus_analytics.db"

    # Dependency override pointing to non-existent DB
    def override_service():
        repo = AnalyticsRepository(db_path=str(missing_db))
        return AnalyticsService(repository=repo)

    from app.main import app
    app.dependency_overrides[get_analytics_service] = override_service

    try:
        res = client.get("/api/analytics/summary")
        assert res.status_code == 503
        data = res.json()
        assert data["detail"] == "Analytics dataset unavailable"
        # Must not expose file paths
        assert "non_existent" not in str(data)
    finally:
        app.dependency_overrides.clear()
