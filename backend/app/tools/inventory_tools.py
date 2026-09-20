"""
Deterministic inventory business tools.
Queries stock levels, threshold warnings, and inventory summaries from SQLite.
"""

from typing import Optional, Dict, Any, List
from ..db.connection import get_db
from ..db.repositories import (
    get_all_products,
    get_product_by_id,
    get_product_by_name,
    get_low_stock_products_db,
    get_inventory_summary_db
)


def calculate_stock_status(stock: int, reorder_level: int) -> str:
    """Consistently calculates inventory status from physical stock and reorder point."""
    if stock == 0:
        return "out_of_stock"
    elif stock <= reorder_level:
        return "low"
    return "healthy"


def get_product_stock(
    product_id: Optional[str] = None,
    product_name: Optional[str] = None,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieves current physical inventory for a specific product.
    Requires at least one identifier (product_id or product_name).
    Calculates stock status dynamically.
    """
    if not product_id and not product_name:
        raise ValueError("At least one identifier (product_id or product_name) must be supplied.")

    with get_db(db_path) as conn:
        product = None
        if product_id:
            product = get_product_by_id(conn, product_id.strip())
        if not product and product_name:
            product = get_product_by_name(conn, product_name.strip())

        if not product:
            ident = product_id or product_name
            raise ValueError(f"Product '{ident}' not found in inventory catalog.")

        status = calculate_stock_status(product["stock"], product["reorder_level"])
        return {
            "id": product["id"],
            "name": product["name"],
            "category": product["category"],
            "unit_price": product["unit_price"],
            "stock": product["stock"],
            "reorder_level": product["reorder_level"],
            "status": status
        }


def get_low_stock_products(
    include_out_of_stock: bool = False,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Scans catalog for all SKUs with low stock (stock > 0 and stock <= reorder_level).
    Optionally includes completely out of stock items if include_out_of_stock=True.
    Returns count and list of depleted products.
    """
    with get_db(db_path) as conn:
        raw_products = get_low_stock_products_db(conn, include_out_of_stock=include_out_of_stock)
        products = []
        for p in raw_products:
            status = calculate_stock_status(p["stock"], p["reorder_level"])
            products.append({
                "id": p["id"],
                "name": p["name"],
                "category": p["category"],
                "stock": p["stock"],
                "reorder_level": p["reorder_level"],
                "status": status
            })
        return {
            "count": len(products),
            "products": products
        }


def get_inventory_summary(db_path: Optional[str] = None) -> Dict[str, int]:
    """
    Calculates total catalog size and health breakdown (healthy, low_stock, out_of_stock).
    """
    with get_db(db_path) as conn:
        summary = get_inventory_summary_db(conn)
        return summary


def get_all_products_inventory(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Returns full product catalog with dynamically verified status.
    """
    with get_db(db_path) as conn:
        raw_products = get_all_products(conn)
        results = []
        for p in raw_products:
            status = calculate_stock_status(p["stock"], p["reorder_level"])
            results.append({
                "id": p["id"],
                "name": p["name"],
                "category": p["category"],
                "unit_price": p["unit_price"],
                "stock": p["stock"],
                "reorder_level": p["reorder_level"],
                "status": status
            })
        return results
