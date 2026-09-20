"""
Deterministic sales business tools.
Calculates sales, revenues, top products, and trends directly from SQLite.
"""

from typing import Optional, Dict, Any, List
from ..db.connection import get_db
from ..db.repositories import (
    get_monthly_sales_db,
    get_top_selling_products_db,
    get_sales_trend_db,
    get_total_sales_all_time
)


def get_total_sales(
    month: Optional[int] = 9,
    year: Optional[int] = 2026,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculates total revenue, units sold, and order volume from SQLite.
    If month and year are specified, computes for that period; otherwise calculates all-time totals.
    """
    with get_db(db_path) as conn:
        if month is not None and year is not None:
            if not (1 <= month <= 12):
                raise ValueError(f"Invalid month: {month}. Month must be between 1 and 12.")
            if year < 2000:
                raise ValueError(f"Invalid year: {year}.")
            data = get_monthly_sales_db(conn, month, year)
            return {
                "revenue": data["revenue"],
                "units_sold": data["units_sold"],
                "orders": data["transactions"],
                "period": f"{year}-{month:02d}"
            }
        data = get_total_sales_all_time(conn)
        return {
            "revenue": data["revenue"],
            "units_sold": data["units_sold"],
            "orders": data["orders"],
            "period": "all_time"
        }


def get_monthly_sales(
    month: int,
    year: int,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculates monthly revenue, units sold, and transaction volume for a specific month and year.
    Validates month is between 1 and 12.
    """
    if not isinstance(month, int) or not (1 <= month <= 12):
        raise ValueError(f"Invalid month: {month}. Month must be an integer between 1 and 12.")
    if not isinstance(year, int) or year < 2000:
        raise ValueError(f"Invalid year: {year}. Year must be an integer >= 2000.")

    with get_db(db_path) as conn:
        result = get_monthly_sales_db(conn, month, year)
        return result


def get_top_products(
    limit: int = 5,
    month: Optional[int] = 9,
    year: Optional[int] = 2026,
    db_path: Optional[str] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Returns the top selling products ranked by revenue and units sold from SQLite.
    Validates limit is between 1 and 20.
    """
    if not isinstance(limit, int) or not (1 <= limit <= 20):
        raise ValueError(f"Invalid limit: {limit}. Limit must be an integer between 1 and 20.")

    if month is not None and not (1 <= month <= 12):
        raise ValueError(f"Invalid month: {month}. Month must be between 1 and 12.")

    with get_db(db_path) as conn:
        products = get_top_selling_products_db(conn, limit=limit, month=month, year=year)
        return {"products": products}


def get_sales_trend(db_path: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Computes monthly revenue grouped chronologically from SQLite sales transactions.
    """
    with get_db(db_path) as conn:
        trend = get_sales_trend_db(conn)
        return {"months": trend}
