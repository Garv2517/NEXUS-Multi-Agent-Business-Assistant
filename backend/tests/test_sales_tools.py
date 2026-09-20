import pytest
from app.tools.sales_tools import (
    get_total_sales,
    get_monthly_sales,
    get_top_products,
    get_sales_trend
)


def test_get_total_sales_september(test_db):
    """Verifies that September 2026 sales values are correctly computed from SQLite."""
    data = get_total_sales(month=9, year=2026, db_path=test_db)
    assert data["revenue"] == 124500.0
    assert data["units_sold"] == 248
    assert data["orders"] == 5
    assert data["period"] == "2026-09"


def test_get_total_sales_all_time(test_db):
    """Verifies all-time sales aggregate computation."""
    data = get_total_sales(month=None, year=None, db_path=test_db)
    assert data["revenue"] > 124500.0
    assert data["units_sold"] > 248
    assert data["period"] == "all_time"


def test_get_monthly_sales_valid(test_db):
    """Verifies monthly sales for April 2026."""
    data = get_monthly_sales(month=4, year=2026, db_path=test_db)
    assert data["month"] == 4
    assert data["year"] == 2026
    assert data["revenue"] == 82000.0
    assert data["transactions"] == 4


def test_get_monthly_sales_invalid_month(test_db):
    """Verifies that invalid month throws ValueError."""
    with pytest.raises(ValueError, match="Invalid month"):
        get_monthly_sales(month=13, year=2026, db_path=test_db)
    with pytest.raises(ValueError, match="Invalid month"):
        get_monthly_sales(month=0, year=2026, db_path=test_db)


def test_get_monthly_sales_invalid_year(test_db):
    """Verifies that invalid year throws ValueError."""
    with pytest.raises(ValueError, match="Invalid year"):
        get_monthly_sales(month=5, year=1998, db_path=test_db)


def test_get_top_products_ordering_and_values(test_db):
    """Verifies that top products are properly ordered by revenue descending."""
    res = get_top_products(limit=5, month=9, year=2026, db_path=test_db)
    products = res["products"]
    assert len(products) >= 3

    # Top product must be Laptop Pro (P101) with 27 units and ₹67,500 revenue
    p1 = products[0]
    assert p1["id"] == "P101"
    assert p1["name"] == "Laptop Pro"
    assert p1["units_sold"] == 27
    assert p1["revenue"] == 67500.0

    # Second product must be Wireless Headset (P102) with 42 units and ₹25,200 revenue
    p2 = products[1]
    assert p2["id"] == "P102"
    assert p2["name"] == "Wireless Headset"
    assert p2["units_sold"] == 42
    assert p2["revenue"] == 25200.0

    # Ensure strictly descending revenue
    for i in range(len(products) - 1):
        assert products[i]["revenue"] >= products[i + 1]["revenue"]


def test_get_top_products_invalid_limit(test_db):
    """Verifies that invalid limits raise ValueError."""
    with pytest.raises(ValueError, match="Invalid limit"):
        get_top_products(limit=0, db_path=test_db)
    with pytest.raises(ValueError, match="Invalid limit"):
        get_top_products(limit=25, db_path=test_db)


def test_get_sales_trend(test_db):
    """Verifies sales trend contains 6 months of historical data."""
    trend = get_sales_trend(db_path=test_db)
    months = trend["months"]
    assert len(months) == 6
    months_labels = [m["month"] for m in months]
    assert "Apr" in months_labels
    assert "Sep" in months_labels
