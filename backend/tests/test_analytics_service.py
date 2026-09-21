"""
Tests for Phase D1C: Read-Only Analytics Repository & Service for nexus_analytics.db.
Verifies clean error handling on missing DB, read-only guarantees, integer-cents precision,
Pydantic model validation, and SQL aggregations across all 8 supported analytical domains.
"""

import sqlite3
import pytest
from pathlib import Path

from app.repositories.analytics_repository import (
    AnalyticsRepository,
    AnalyticsDatabaseNotFoundError
)
from app.services.analytics_service import AnalyticsService
from app.core.config import settings, Settings
from app.models.analytics import (
    AnalyticsMetadata,
    CompanySummary,
    MonthlySalesResponse,
    CategoryPerformanceResponse,
    ProductPerformanceResponse,
    StorePerformanceResponse,
    LocationPerformanceResponse,
    InventoryAnalyticsModel,
    InventoryProductResponse,
    InventoryProductItem
)


@pytest.fixture
def analytics_service():
    """Provides an AnalyticsService connected to the verified nexus_analytics.db."""
    repo = AnalyticsRepository()
    return AnalyticsService(repository=repo)


# --- 1. Missing Database Clean Handling ---

def test_missing_database_fails_cleanly(tmp_path):
    """Verifies that accessing a non-existent database path raises AnalyticsDatabaseNotFoundError and does NOT create a file."""
    non_existent = tmp_path / "does_not_exist_analytics.db"
    assert not non_existent.exists()

    repo = AnalyticsRepository(db_path=str(non_existent))
    service = AnalyticsService(repository=repo)

    with pytest.raises(AnalyticsDatabaseNotFoundError, match="Analytics database not found"):
        service.get_company_summary()

    # Crucial rule: it must NOT create an empty file!
    assert not non_existent.exists()


# --- 2. Read-Only Protection ---

def test_read_only_protection(analytics_service):
    """Verifies SQLite engine enforces read-only access (URI mode ?mode=ro)."""
    with analytics_service.repository._get_connection() as conn:
        cursor = conn.cursor()

        # Attempting any write operation must fail at SQLite engine level
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            cursor.execute("CREATE TABLE should_fail (id INT);")

        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            cursor.execute("UPDATE external_stores SET store_name = 'Hacked' WHERE store_id = 1;")


# --- 3. Metadata Query ---

def test_get_metadata(analytics_service):
    meta = analytics_service.get_metadata()
    assert isinstance(meta, AnalyticsMetadata)
    assert meta.dataset_name == "USA Toy Sales Dataset"
    assert meta.dataset_source == "Kaggle"
    assert meta.license == "CC0 / Public Domain"
    assert meta.currency_code == "USD"
    assert meta.sales_start_date == "2025-01-01"
    assert meta.sales_end_date == "2025-12-31"
    assert meta.inventory_snapshot_date == "2025-12-31"
    assert meta.inventory_snapshot_date_is_assumed is True
    assert len(meta.stores_sha256) == 64
    assert len(meta.products_sha256) == 64
    assert len(meta.inventory_sha256) == 64
    assert len(meta.sales_sha256) == 64
    assert "synthetic" in meta.notes.lower()


# --- 4. Company Summary Query ---

def test_get_company_summary(analytics_service):
    summary = analytics_service.get_company_summary()
    assert isinstance(summary, CompanySummary)
    assert summary.currency_code == "USD"
    assert summary.store_count == 120
    assert summary.total_stores == 120
    assert summary.product_count == 180
    assert summary.total_products == 180
    assert summary.category_count == 16
    assert summary.transaction_count == 245800
    assert summary.total_transactions == 245800
    assert summary.total_units_sold == 567270
    assert summary.inventory_units == 338993
    assert summary.stockout_placement_count == 321

    # Exact integer cents
    assert summary.total_revenue_cents == 986293325
    assert summary.total_cogs_cents == 555682727
    assert summary.gross_profit_cents == 430610598
    assert summary.total_profit_cents == 430610598
    assert summary.total_revenue_cents - summary.total_cogs_cents == summary.gross_profit_cents

    # Decimal USD helper properties
    assert summary.revenue_usd == 9862933.25
    assert summary.cogs_usd == 5556827.27
    assert summary.profit_usd == 4306105.98
    assert summary.gross_margin_pct == 43.66
    assert summary.average_order_value_cents == 4013
    assert summary.aov_usd == 40.13


# --- 5. Monthly Sales Query ---

def test_get_monthly_sales(analytics_service):
    res = analytics_service.get_monthly_sales()
    assert isinstance(res, MonthlySalesResponse)
    assert res.currency_code == "USD"
    assert res.total_months == 12
    assert len(res.monthly_trend) == 12

    # Check chronological ordering
    months = [p.year_month for p in res.monthly_trend]
    assert months == [
        "2025-01", "2025-02", "2025-03", "2025-04",
        "2025-05", "2025-06", "2025-07", "2025-08",
        "2025-09", "2025-10", "2025-11", "2025-12"
    ]

    # Verify sum of monthly revenue equals company total
    sum_monthly_rev = sum(p.revenue_cents for p in res.monthly_trend)
    sum_monthly_units = sum(p.units_sold for p in res.monthly_trend)
    assert sum_monthly_rev == 986293325
    assert sum_monthly_units == 567270

    # January exact check
    jan = res.monthly_trend[0]
    assert jan.year_month == "2025-01"
    assert jan.transaction_count == 20761
    assert jan.units_sold == 48099
    assert jan.revenue_cents == 83507993


# --- 6. Category Performance Query ---

def test_get_category_performance(analytics_service):
    res = analytics_service.get_category_performance()
    assert isinstance(res, CategoryPerformanceResponse)
    assert len(res.categories) == 16

    # Top category must be Action Figures
    top_cat = res.categories[0]
    assert top_cat.category == "Action Figures"
    assert top_cat.product_count == 17
    assert top_cat.units_sold == 52714
    assert top_cat.revenue_cents == 106052161
    assert top_cat.revenue_usd == 1060521.61
    assert top_cat.revenue_share_pct == 10.75

    # Sum of category revenue equals company revenue
    total_cat_rev = sum(c.revenue_cents for c in res.categories)
    assert total_cat_rev == 986293325


# --- 7. Product Performance Query ---

def test_get_product_performance_ranking(analytics_service):
    # Top 5 by revenue
    res = analytics_service.get_product_performance(limit=5, order_by="revenue")
    assert isinstance(res, ProductPerformanceResponse)
    assert res.total_products == 5

    # Top product is Product 130 (Mega Board Game)
    top_p = res.products[0]
    assert top_p.product_id == 130
    assert top_p.product_name == "Mega Board Game"
    assert top_p.product_category == "Action Figures"
    assert top_p.units_sold == 1623
    assert top_p.revenue_cents == 23191047
    assert top_p.revenue_usd == 231910.47


def test_get_product_performance_with_category_filter(analytics_service):
    res = analytics_service.get_product_performance(category="Board Games", order_by="revenue")
    assert res.total_products == 11
    for p in res.products:
        assert p.product_category == "Board Games"


def test_get_product_performance_by_units(analytics_service):
    res = analytics_service.get_product_performance(limit=3, order_by="units")
    assert len(res.products) == 3
    # Verify descending units order
    assert res.products[0].units_sold >= res.products[1].units_sold >= res.products[2].units_sold


# --- 8. Store Performance Query ---

def test_get_store_performance_ranking(analytics_service):
    res = analytics_service.get_store_performance(limit=5, order_by="revenue")
    assert isinstance(res, StorePerformanceResponse)
    assert res.total_stores == 5

    # Top store is Store 34
    top_s = res.stores[0]
    assert top_s.store_id == 34
    assert top_s.revenue_cents == 10382410
    assert top_s.revenue_usd == 103824.10
    assert top_s.units_sold == 5796


def test_get_store_performance_location_filter(analytics_service):
    res = analytics_service.get_store_performance(location="Airport")
    assert res.total_stores == 4
    for s in res.stores:
        assert s.store_location == "Airport"


# --- 9. Location Performance Query ---

def test_get_location_performance(analytics_service):
    res = analytics_service.get_location_performance()
    assert isinstance(res, LocationPerformanceResponse)
    assert len(res.locations) == 6

    # Locations present: Downtown, Mall, Commercial, Residential, Suburban, Airport
    loc_names = {l.store_location for l in res.locations}
    assert loc_names == {"Downtown", "Mall", "Commercial", "Residential", "Suburban", "Airport"}

    # Total stores across locations must be 120
    assert sum(l.store_count for l in res.locations) == 120

    # Total revenue across locations must equal company revenue
    assert sum(l.revenue_cents for l in res.locations) == 986293325


# --- 10. Inventory Analytics Query ---

def test_get_inventory_analytics(analytics_service):
    inv = analytics_service.get_inventory_analytics()
    assert isinstance(inv, InventoryAnalyticsModel)
    assert inv.currency_code == "USD"
    assert inv.snapshot_date == "2025-12-31"
    assert inv.snapshot_date_is_assumed is True
    assert inv.total_placements == 14143
    assert inv.out_of_stock_placements == 321
    assert inv.in_stock_placements == 13822  # 14143 - 321
    assert inv.in_stock_placements + inv.out_of_stock_placements == inv.total_placements
    assert not hasattr(inv, "healthy_stock_placements")
    assert not hasattr(inv, "healthy_placements")
    assert inv.stockout_rate_pct == 2.27

    # Exact valuation in cents
    assert inv.total_cost_value_cents == 312121493
    assert inv.total_retail_value_cents == 557626331
    assert inv.potential_gross_margin_cents == 245504838
    assert inv.potential_gross_margin_pct == 44.03

    # USD helpers
    assert inv.cost_value_usd == 3121214.93
    assert inv.retail_value_usd == 5576263.31
    assert inv.potential_margin_usd == 2455048.38


# --- 11. Operational nexus.db Remains Untouched ---

def test_operational_nexus_db_unaffected():
    """Confirms operational nexus.db contains zero external tables and remains untouched."""
    nexus_db_path = Path("data/nexus.db")
    if nexus_db_path.exists():
        conn = sqlite3.connect(str(nexus_db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'external_%';")
        assert len(cursor.fetchall()) == 0
        conn.close()


# --- 12. ANALYTICS_DATABASE_PATH Configuration ---

def test_analytics_database_path_configuration(monkeypatch, tmp_path):
    """Verifies that ANALYTICS_DATABASE_PATH setting resolves custom and relative paths correctly."""
    custom_db = tmp_path / "custom_analytics.db"
    monkeypatch.setenv("ANALYTICS_DATABASE_PATH", str(custom_db))
    custom_settings = Settings()
    resolved = custom_settings.get_analytics_database_path()
    assert Path(resolved).resolve() == custom_db.resolve()

    # Relative path resolution
    monkeypatch.setenv("ANALYTICS_DATABASE_PATH", "data/nexus_analytics.db")
    rel_settings = Settings()
    rel_resolved = rel_settings.get_analytics_database_path()
    assert Path(rel_resolved).name == "nexus_analytics.db"
    assert Path(rel_resolved).exists()


# --- 13. Inventory By Product Aggregation ---

def test_get_inventory_by_product_aggregation(analytics_service):
    """Verifies product-level inventory aggregation across store placements."""
    res = analytics_service.get_inventory_by_product(limit=10, order_by="stock_units")
    assert isinstance(res, InventoryProductResponse)
    assert res.currency_code == "USD"
    assert res.total_products == 10
    assert len(res.products) == 10

    # Top product by stock units is Product 61 ("Mini Robot")
    top_item = res.products[0]
    assert isinstance(top_item, InventoryProductItem)
    assert top_item.product_id == 61
    assert top_item.product_name == "Mini Robot"
    assert top_item.category == "Arts & Crafts"
    assert top_item.store_placements == 92
    assert top_item.stock_units == 2659
    assert top_item.inventory_cost_value_cents == 1100826
    assert top_item.inventory_retail_value_cents == 1598059
    assert top_item.zero_stock_store_count == 1

    # Exact integer cents and USD display properties
    assert top_item.cost_value_usd == 11008.26
    assert top_item.retail_value_usd == 15980.59


def test_get_inventory_by_product_category_filter(analytics_service):
    """Verifies category filtering in product-level inventory aggregation."""
    res = analytics_service.get_inventory_by_product(category="Building Blocks", limit=5)
    assert len(res.products) <= 5
    for item in res.products:
        assert item.category == "Building Blocks"


# --- 14. Inventory Product Limit Validation ---

def test_inventory_product_limit_validation(analytics_service):
    """Verifies limit bounds enforcement (must be positive integer <= 1000)."""
    with pytest.raises(ValueError, match="Limit must be a positive integer"):
        analytics_service.get_inventory_by_product(limit=0)

    with pytest.raises(ValueError, match="Limit must be a positive integer"):
        analytics_service.get_inventory_by_product(limit=-1)

    with pytest.raises(ValueError, match="Limit must be a positive integer"):
        analytics_service.get_inventory_by_product(limit=1001)


# --- 15. Invalid Sort Field Rejection ---

def test_invalid_sort_field_rejection(analytics_service):
    """Verifies strict whitelist validation rejects invalid/malicious order_by fields."""
    with pytest.raises(ValueError, match="Invalid order_by"):
        analytics_service.get_product_performance(order_by="unsupported_field")

    with pytest.raises(ValueError, match="Invalid order_by"):
        analytics_service.get_store_performance(order_by="store_location; DROP TABLE external_stores")

    with pytest.raises(ValueError, match="Invalid order_by"):
        analytics_service.get_inventory_by_product(order_by="invalid_sort")
