"""Read-only Assistant tools backed by the unified Kaggle analytics dataset.

These tools preserve the specialist-agent tool vocabulary while sourcing Sales and
Inventory facts from ``nexus_analytics.db``. They intentionally avoid reorder-level
concepts because the external dataset does not provide them.
"""

from typing import Optional, Dict, Any

from ..repositories.analytics_repository import AnalyticsRepository
from ..core.risk_config import risk_config


def _repo(db_path: Optional[str]) -> AnalyticsRepository:
    return AnalyticsRepository(db_path=db_path)


def get_total_sales(analytics_db_path: Optional[str] = None) -> Dict[str, Any]:
    summary = _repo(analytics_db_path).get_company_summary()
    return {
        "data_source": "analytics",
        "dataset": "USA Toy Sales Dataset",
        "currency_code": "USD",
        "period": f"{summary['sales_start_date']} to {summary['sales_end_date']}",
        "revenue_cents": summary["total_revenue_cents"],
        "units_sold": summary["total_units_sold"],
        "orders": summary["transaction_count"],
        "gross_profit_cents": summary["gross_profit_cents"],
        "gross_margin_pct": summary["gross_margin_pct"],
    }


def get_monthly_sales(
    month: Optional[int] = None,
    year: Optional[int] = None,
    analytics_db_path: Optional[str] = None,
) -> Dict[str, Any]:
    if month is not None and (not isinstance(month, int) or not 1 <= month <= 12):
        raise ValueError("Month must be an integer between 1 and 12.")
    if year is not None and (not isinstance(year, int) or year < 2000):
        raise ValueError("Year must be an integer >= 2000.")

    points = _repo(analytics_db_path).get_monthly_sales()
    if not points:
        raise ValueError("No monthly sales data is available.")

    if month is None and year is None:
        point = points[-1]
    else:
        latest_year = int(points[-1]["year_month"][:4])
        latest_month = int(points[-1]["year_month"][5:7])
        target_year = year if year is not None else latest_year
        target_month = month if month is not None else latest_month
        target = f"{target_year:04d}-{target_month:02d}"
        point = next((p for p in points if p["year_month"] == target), None)
        if point is None:
            raise ValueError(
                f"No sales data is available for {target}. "
                "The external retail dataset covers Jan-Dec 2025."
            )

    return {
        "data_source": "analytics",
        "dataset": "USA Toy Sales Dataset",
        "currency_code": "USD",
        "period": point["year_month"],
        "revenue_cents": point["revenue_cents"],
        "units_sold": point["units_sold"],
        "orders": point["transaction_count"],
        "gross_profit_cents": point["profit_cents"],
        "gross_margin_pct": point["gross_margin_pct"],
    }


def get_top_products(limit: int = 3, analytics_db_path: Optional[str] = None) -> Dict[str, Any]:
    if not isinstance(limit, int) or not 1 <= limit <= 20:
        raise ValueError("Limit must be an integer between 1 and 20.")
    rows = _repo(analytics_db_path).get_product_performance(limit=limit, order_by="revenue")
    products = [
        {
            "id": p["product_id"],
            "name": p["product_name"],
            "category": p["product_category"],
            "units_sold": p["units_sold"],
            "revenue_cents": p["revenue_cents"],
            "gross_profit_cents": p["profit_cents"],
            "gross_margin_pct": p["gross_margin_pct"],
        }
        for p in rows
    ]
    return {
        "data_source": "analytics",
        "dataset": "USA Toy Sales Dataset",
        "currency_code": "USD",
        "ranking": "full-year revenue",
        "products": products,
    }


def get_sales_trend(analytics_db_path: Optional[str] = None) -> Dict[str, Any]:
    rows = _repo(analytics_db_path).get_monthly_sales()
    return {
        "data_source": "analytics",
        "dataset": "USA Toy Sales Dataset",
        "currency_code": "USD",
        "months": [
            {
                "period": p["year_month"],
                "revenue_cents": p["revenue_cents"],
                "units_sold": p["units_sold"],
                "gross_profit_cents": p["profit_cents"],
                "gross_margin_pct": p["gross_margin_pct"],
            }
            for p in rows
        ],
    }


def get_product_stock(
    product_id: Optional[Any] = None,
    product_name: Optional[str] = None,
    analytics_db_path: Optional[str] = None,
) -> Dict[str, Any]:
    if product_id is None and not product_name:
        raise ValueError("At least one product identifier is required.")

    normalized_id: Optional[int] = None
    if product_id is not None:
        try:
            normalized_id = int(str(product_id).strip().replace("Product ", "").replace("product ", ""))
        except ValueError as exc:
            raise ValueError(f"Invalid external product ID '{product_id}'. Expected a numeric ID.") from exc

    item = _repo(analytics_db_path).get_inventory_product_detail(
        product_id=normalized_id,
        product_name=product_name,
    )
    if not item:
        ident = normalized_id if normalized_id is not None else product_name
        raise ValueError(f"Product '{ident}' not found in external analytics inventory.")

    return {
        "data_source": "analytics",
        "dataset": "USA Toy Sales Dataset",
        "currency_code": "USD",
        "id": item["product_id"],
        "name": item["product_name"],
        "category": item["category"],
        "stock": item["stock_units"],
        "store_placements": item["store_placements"],
        "zero_stock_store_count": item["zero_stock_store_count"],
        "inventory_cost_value_cents": item["inventory_cost_value_cents"],
        "inventory_retail_value_cents": item["inventory_retail_value_cents"],
        "snapshot_date": "2025-12-31",
        "snapshot_date_is_assumed": True,
    }


def get_inventory_summary(analytics_db_path: Optional[str] = None) -> Dict[str, Any]:
    repo = _repo(analytics_db_path)
    inv = repo.get_inventory_analytics()
    company = repo.get_company_summary()
    return {
        "data_source": "analytics",
        "dataset": "USA Toy Sales Dataset",
        "currency_code": "USD",
        "total_products": company["product_count"],
        "total_units_on_hand": inv["total_units_on_hand"],
        "total_placements": inv["total_placements"],
        "in_stock_placements": inv["in_stock_placements"],
        "out_of_stock_placements": inv["out_of_stock_placements"],
        "stockout_rate_pct": inv["stockout_rate_pct"],
        "total_cost_value_cents": inv["total_cost_value_cents"],
        "total_retail_value_cents": inv["total_retail_value_cents"],
        "snapshot_date": inv["snapshot_date"],
        "snapshot_date_is_assumed": inv["snapshot_date_is_assumed"],
    }


def get_low_stock_products(
    include_out_of_stock: bool = True,
    limit: int = 10,
    analytics_db_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Return stockout / high-pressure placements using calibrated Days of Supply.

    The external dataset has no reorder level. "Low stock" is therefore interpreted
    as verified Stockout or empirically calibrated High Pressure inventory coverage.
    """
    if not isinstance(limit, int) or limit <= 0 or limit > 50:
        raise ValueError("Limit must be between 1 and 50.")

    raw = _repo(analytics_db_path).get_inventory_pressure_data(limit=500)
    items = []
    total_matching = 0
    allowed = {"High Pressure"}
    if include_out_of_stock:
        allowed.add("Stockout")

    for row in raw:
        tier = risk_config.classify_placement_coverage(row["stock_on_hand"], row["days_of_supply"])
        if tier not in allowed:
            continue
        total_matching += 1
        if len(items) < limit:
            dos = row["days_of_supply"]
            items.append({
                "id": row["product_id"],
                "name": row["product_name"],
                "category": row["category"],
                "store_id": row["store_id"],
                "store_name": row["store_name"],
                "stock": row["stock_on_hand"],
                "days_of_supply": dos,
                "status": tier,
            })

    return {
        "data_source": "analytics",
        "dataset": "USA Toy Sales Dataset",
        "currency_code": "USD",
        "count": total_matching,
        "returned": len(items),
        "products": items,
        "definition": "Stockout or dataset-calibrated High Pressure inventory coverage; no reorder levels are available.",
        "snapshot_date": risk_config.ASSUMED_SNAPSHOT_DATE,
        "snapshot_date_is_assumed": risk_config.SNAPSHOT_DATE_IS_ASSUMED,
    }
