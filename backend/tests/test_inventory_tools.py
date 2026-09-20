import pytest
from app.tools.inventory_tools import (
    get_product_stock,
    get_low_stock_products,
    get_inventory_summary,
    get_all_products_inventory
)
from app.services.business_service import BusinessService


def test_get_product_stock_by_id(test_db):
    """Verifies stock lookup by product ID."""
    prod = get_product_stock(product_id="P101", db_path=test_db)
    assert prod["id"] == "P101"
    assert prod["name"] == "Laptop Pro"
    assert prod["stock"] == 4
    assert prod["reorder_level"] == 10
    assert prod["status"] == "low"
    assert prod["unit_price"] == 2500.0


def test_get_product_stock_by_name(test_db):
    """Verifies stock lookup by product name (case-insensitive)."""
    prod = get_product_stock(product_name="wireless headset", db_path=test_db)
    assert prod["id"] == "P102"
    assert prod["stock"] == 31
    assert prod["status"] == "healthy"


def test_get_product_stock_unknown_raises_error(test_db):
    """Verifies that unknown product raises ValueError."""
    with pytest.raises(ValueError, match="not found"):
        get_product_stock(product_id="P999_NON_EXISTENT", db_path=test_db)


def test_get_product_stock_missing_both_args(test_db):
    """Verifies that calling without id or name raises ValueError."""
    with pytest.raises(ValueError, match="At least one identifier"):
        get_product_stock(db_path=test_db)


def test_low_stock_products_calculation(test_db):
    """Verifies low stock calculation filters stock > 0 and stock <= reorder_level."""
    res = get_low_stock_products(db_path=test_db)
    count = res["count"]
    products = res["products"]
    assert count == 4  # 4 low (P101, P103, P106, P107), out of stock (P105) excluded
    assert count == len(products)
    for p in products:
        assert p["stock"] > 0
        assert p["stock"] <= p["reorder_level"]
        assert p["status"] == "low"


def test_low_stock_count_equals_product_list_length(test_db):
    """Consistency Test 1: get_low_stock_products()['count'] == len(get_low_stock_products()['products'])."""
    res = get_low_stock_products(db_path=test_db)
    assert res["count"] == len(res["products"])


def test_every_product_satisfies_documented_low_stock_rule(test_db):
    """
    Consistency Test 2: Every product returned by get_low_stock_products() satisfies
    the documented low-stock rule: stock > 0 AND stock <= reorder_level.
    """
    res = get_low_stock_products(db_path=test_db)
    assert len(res["products"]) > 0
    for p in res["products"]:
        assert p["stock"] > 0, f"Product {p['name']} has stock {p['stock']} <= 0; out-of-stock items must be excluded from low stock."
        assert p["stock"] <= p["reorder_level"], f"Product {p['name']} has stock {p['stock']} > reorder_level {p['reorder_level']}."
        assert p["status"] == "low"


def test_inventory_summary_category_counts_partition(test_db):
    """
    Consistency Test 3: Inventory summary category counts partition the catalog:
    total_products == healthy + low_stock + out_of_stock.
    """
    summary = get_inventory_summary(db_path=test_db)
    total = summary["total_products"]
    healthy = summary["healthy"]
    low = summary["low_stock"]
    out_of_stock = summary["out_of_stock"]

    assert total == 13
    assert low == 4
    assert out_of_stock == 1
    assert healthy == 8
    assert healthy + low + out_of_stock == total


def test_no_duplicate_products_in_low_stock(test_db):
    """Consistency Test 5: No product appears twice in low stock result."""
    res = get_low_stock_products(db_path=test_db)
    ids = [p["id"] for p in res["products"]]
    names = [p["name"] for p in res["products"]]
    assert len(ids) == len(set(ids)), f"Duplicate product IDs found: {ids}"
    assert len(names) == len(set(names)), f"Duplicate product names found: {names}"


def test_dashboard_and_inventory_kpi_semantics_match_tool(test_db):
    """
    Consistency Test 6: Dashboard and Inventory KPI semantics match the underlying tool semantics.
    """
    summary = get_inventory_summary(db_path=test_db)
    low_tool = get_low_stock_products(db_path=test_db)

    # Tool low stock count matches summary low_stock count
    assert low_tool["count"] == summary["low_stock"]

    # Dashboard lowStockProducts matches summary low_stock
    dashboard = BusinessService.get_dashboard(db_path=test_db)
    assert dashboard.metrics.lowStockProducts.value == summary["low_stock"]
    assert dashboard.metrics.lowStockProducts.value == low_tool["count"]

    # Inventory page metrics match summary
    inventory = BusinessService.get_inventory(db_path=test_db)
    assert inventory.lowStockCount == summary["low_stock"]
    assert inventory.outOfStockCount == summary["out_of_stock"]
    assert inventory.healthyStockCount == summary["healthy"]
    assert inventory.totalProducts == summary["total_products"]
    assert inventory.totalProducts == inventory.healthyStockCount + inventory.lowStockCount + inventory.outOfStockCount


def test_low_stock_optional_include_out_of_stock(test_db):
    """Verifies that optional include_out_of_stock=True includes stock==0 items."""
    res_with_oos = get_low_stock_products(include_out_of_stock=True, db_path=test_db)
    assert res_with_oos["count"] == 5
    assert len(res_with_oos["products"]) == 5
    statuses = [p["status"] for p in res_with_oos["products"]]
    assert "out_of_stock" in statuses
    assert "low" in statuses


def test_get_all_products_inventory(test_db):
    """Verifies all products list has dynamic status."""
    all_prods = get_all_products_inventory(db_path=test_db)
    assert len(all_prods) == 13
    p105 = next(p for p in all_prods if p["id"] == "P105")
    assert p105["status"] == "out_of_stock"
