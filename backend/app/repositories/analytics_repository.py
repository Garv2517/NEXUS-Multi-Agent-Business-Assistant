import contextlib
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any, Iterator
from ..core.config import settings


class AnalyticsDatabaseNotFoundError(FileNotFoundError):
    """Raised when the analytics SQLite database does not exist."""
    pass


class AnalyticsRepository:
    """
    Read-only repository for querying nexus_analytics.db.
    Guarantees strict read-only SQLite URI mode (?mode=ro) and parameterization.
    All mathematical aggregations are executed inside SQLite.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = Path(db_path).resolve()
        else:
            self.db_path = Path(settings.get_analytics_database_path()).resolve()

    def _ensure_db_exists(self) -> None:
        """Verifies analytics database file existence before attempting connection."""
        if not self.db_path.exists():
            raise AnalyticsDatabaseNotFoundError(
                f"Analytics database not found at '{self.db_path}'. "
                "Please run 'python scripts/import_kaggle_dataset.py' to generate it."
            )

    @contextlib.contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        """
        Creates a strictly read-only connection to SQLite using URI mode.
        Fails cleanly if the database file is missing.
        Guarantees connection is cleanly closed upon context manager exit.
        """
        self._ensure_db_exists()
        # Open in SQLite URI read-only mode (?mode=ro)
        uri = f"file:{self.db_path.as_posix()}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """Retrieves external dataset metadata and provenance record."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM analytics_metadata WHERE id = 1;")
            row = cursor.fetchone()
            if not row:
                return None
            return dict(row)

    def get_company_summary(self) -> Dict[str, Any]:
        """
        Calculates executive company metrics across the full dataset:
        revenue, COGS, gross profit, margin, units sold, transaction count,
        stores, products, categories, inventory units, and stockouts.
        Executes in a single query with zero N+1 overhead.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                WITH SalesAgg AS (
                    SELECT
                        COUNT(DISTINCT s.store_id) AS store_count,
                        COUNT(DISTINCT s.product_id) AS product_count,
                        COUNT(s.sale_id) AS transaction_count,
                        COALESCE(SUM(s.units), 0) AS total_units_sold,
                        COALESCE(SUM(s.units * p.product_price_cents), 0) AS total_revenue_cents,
                        COALESCE(SUM(s.units * p.product_cost_cents), 0) AS total_cogs_cents,
                        MIN(s.sale_date) AS sales_start_date,
                        MAX(s.sale_date) AS sales_end_date
                    FROM external_sales s
                    JOIN external_products p ON s.product_id = p.product_id
                ),
                ProdCatAgg AS (
                    SELECT COUNT(DISTINCT product_category) AS category_count
                    FROM external_products
                ),
                InvAgg AS (
                    SELECT
                        COALESCE(SUM(stock_on_hand), 0) AS inventory_units,
                        COALESCE(SUM(CASE WHEN stock_on_hand = 0 THEN 1 ELSE 0 END), 0) AS stockout_placement_count
                    FROM external_inventory
                )
                SELECT * FROM SalesAgg, ProdCatAgg, InvAgg;
            """)
            row = cursor.fetchone()
            res = dict(row)
            revenue_cents = res.get("total_revenue_cents", 0)
            cogs_cents = res.get("total_cogs_cents", 0)
            transactions = res.get("transaction_count", 0)

            profit_cents = revenue_cents - cogs_cents
            margin_pct = round((profit_cents / revenue_cents * 100.0), 2) if revenue_cents > 0 else 0.0
            aov_cents = round(revenue_cents / transactions) if transactions > 0 else 0

            res["gross_profit_cents"] = profit_cents
            res["total_profit_cents"] = profit_cents
            res["gross_margin_pct"] = margin_pct
            res["average_order_value_cents"] = aov_cents
            res["total_stores"] = res["store_count"]
            res["total_products"] = res["product_count"]
            res["total_transactions"] = res["transaction_count"]
            res["currency_code"] = "USD"
            return res

    def get_monthly_sales(self) -> List[Dict[str, Any]]:
        """
        Aggregates sales metrics grouped chronologically by month (YYYY-MM).
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    substr(s.sale_date, 1, 7) AS year_month,
                    COUNT(s.sale_id) AS transaction_count,
                    COALESCE(SUM(s.units), 0) AS units_sold,
                    COALESCE(SUM(s.units * p.product_price_cents), 0) AS revenue_cents,
                    COALESCE(SUM(s.units * p.product_cost_cents), 0) AS cogs_cents
                FROM external_sales s
                JOIN external_products p ON s.product_id = p.product_id
                GROUP BY substr(s.sale_date, 1, 7)
                ORDER BY year_month ASC;
            """)
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                rev = item["revenue_cents"]
                cogs = item["cogs_cents"]
                txs = item["transaction_count"]
                profit = rev - cogs
                item["profit_cents"] = profit
                item["gross_margin_pct"] = round((profit / rev * 100.0), 2) if rev > 0 else 0.0
                item["average_order_value_cents"] = round(rev / txs) if txs > 0 else 0
                results.append(item)
            return results

    def get_category_performance(self) -> List[Dict[str, Any]]:
        """
        Aggregates product category metrics:
        product counts, units sold, revenue, COGS, profit, and revenue share.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Calculate total revenue in subquery for accurate share calculation
            cursor.execute("""
                WITH TotalSales AS (
                    SELECT COALESCE(SUM(s.units * p.product_price_cents), 0) AS company_rev
                    FROM external_sales s
                    JOIN external_products p ON s.product_id = p.product_id
                )
                SELECT
                    p.product_category AS category,
                    COUNT(DISTINCT p.product_id) AS product_count,
                    COALESCE(SUM(s.units), 0) AS units_sold,
                    COALESCE(SUM(s.units * p.product_price_cents), 0) AS revenue_cents,
                    COALESCE(SUM(s.units * p.product_cost_cents), 0) AS cogs_cents,
                    ROUND(
                        (COALESCE(SUM(s.units * p.product_price_cents), 0) * 100.0) /
                        NULLIF((SELECT company_rev FROM TotalSales), 0),
                        2
                    ) AS revenue_share_pct
                FROM external_sales s
                JOIN external_products p ON s.product_id = p.product_id
                GROUP BY p.product_category
                ORDER BY revenue_cents DESC;
            """)
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                rev = item["revenue_cents"]
                cogs = item["cogs_cents"]
                profit = rev - cogs
                item["profit_cents"] = profit
                item["gross_margin_pct"] = round((profit / rev * 100.0), 2) if rev > 0 else 0.0
                results.append(item)
            return results

    def get_product_performance(
        self,
        limit: Optional[int] = None,
        order_by: str = "revenue",
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Returns SKU-level sales, unit volume, and profitability metrics.
        Supported order_by: 'revenue', 'units', 'profit', 'margin'.
        """
        order_clause_map = {
            "revenue": "revenue_cents DESC",
            "units": "units_sold DESC",
            "profit": "profit_cents DESC",
            "margin": "gross_margin_pct DESC"
        }
        clean_order_by = order_by.lower().strip()
        if clean_order_by not in order_clause_map:
            raise ValueError(f"Invalid order_by '{order_by}'. Allowed: {list(order_clause_map.keys())}")
        order_clause = order_clause_map[clean_order_by]

        if limit is not None:
            if not isinstance(limit, int) or limit <= 0 or limit > 1000:
                raise ValueError("Limit must be a positive integer between 1 and 1000")

        query = """
            SELECT
                p.product_id,
                p.product_name,
                p.product_category,
                p.product_cost_cents,
                p.product_price_cents,
                COALESCE(SUM(s.units), 0) AS units_sold,
                COALESCE(SUM(s.units * p.product_price_cents), 0) AS revenue_cents,
                COALESCE(SUM(s.units * p.product_cost_cents), 0) AS cogs_cents,
                COALESCE(SUM(s.units * (p.product_price_cents - p.product_cost_cents)), 0) AS profit_cents,
                ROUND(
                    ((p.product_price_cents - p.product_cost_cents) * 100.0) /
                    NULLIF(p.product_price_cents, 0),
                    2
                ) AS gross_margin_pct
            FROM external_products p
            LEFT JOIN external_sales s ON p.product_id = s.product_id
        """
        params: List[Any] = []

        if category:
            query += " WHERE p.product_category = ?"
            params.append(category)

        query += f" GROUP BY p.product_id ORDER BY {order_clause}"

        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(r) for r in cursor.fetchall()]

    def get_store_performance(
        self,
        limit: Optional[int] = None,
        order_by: str = "revenue",
        location: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Returns store-level transaction volume, units, and gross revenue.
        Supported order_by: 'revenue', 'units', 'profit', 'transactions'.
        """
        order_clause_map = {
            "revenue": "revenue_cents DESC",
            "units": "units_sold DESC",
            "profit": "profit_cents DESC",
            "transactions": "transaction_count DESC"
        }
        clean_order_by = order_by.lower().strip()
        if clean_order_by not in order_clause_map:
            raise ValueError(f"Invalid order_by '{order_by}'. Allowed: {list(order_clause_map.keys())}")
        order_clause = order_clause_map[clean_order_by]

        if limit is not None:
            if not isinstance(limit, int) or limit <= 0 or limit > 1000:
                raise ValueError("Limit must be a positive integer between 1 and 1000")

        query = """
            SELECT
                st.store_id,
                st.store_name,
                st.store_city,
                st.store_location,
                st.store_open_date,
                COUNT(s.sale_id) AS transaction_count,
                COALESCE(SUM(s.units), 0) AS units_sold,
                COALESCE(SUM(s.units * p.product_price_cents), 0) AS revenue_cents,
                COALESCE(SUM(s.units * (p.product_price_cents - p.product_cost_cents)), 0) AS profit_cents
            FROM external_stores st
            LEFT JOIN external_sales s ON st.store_id = s.store_id
            LEFT JOIN external_products p ON s.product_id = p.product_id
        """
        params: List[Any] = []

        if location:
            query += " WHERE st.store_location = ?"
            params.append(location)

        query += f" GROUP BY st.store_id ORDER BY {order_clause}"

        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                rev = item["revenue_cents"]
                txs = item["transaction_count"]
                item["average_order_value_cents"] = round(rev / txs) if txs > 0 else 0
                results.append(item)
            return results

    def get_location_performance(self) -> List[Dict[str, Any]]:
        """
        Aggregates performance by store location classification
        (e.g., Downtown, Mall, Commercial, Residential, Suburban, Airport).
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                WITH TotalSales AS (
                    SELECT COALESCE(SUM(s.units * p.product_price_cents), 0) AS company_rev
                    FROM external_sales s
                    JOIN external_products p ON s.product_id = p.product_id
                )
                SELECT
                    st.store_location,
                    COUNT(DISTINCT st.store_id) AS store_count,
                    COALESCE(SUM(s.units), 0) AS units_sold,
                    COALESCE(SUM(s.units * p.product_price_cents), 0) AS revenue_cents,
                    COALESCE(SUM(s.units * (p.product_price_cents - p.product_cost_cents)), 0) AS profit_cents,
                    ROUND(
                        (COALESCE(SUM(s.units * (p.product_price_cents - p.product_cost_cents)), 0) * 100.0) /
                        NULLIF(SUM(s.units * p.product_price_cents), 0),
                        2
                    ) AS gross_margin_pct,
                    ROUND(
                        (COALESCE(SUM(s.units * p.product_price_cents), 0) * 100.0) /
                        NULLIF((SELECT company_rev FROM TotalSales), 0),
                        2
                    ) AS revenue_share_pct
                FROM external_stores st
                LEFT JOIN external_sales s ON st.store_id = s.store_id
                LEFT JOIN external_products p ON s.product_id = p.product_id
                GROUP BY st.store_location
                ORDER BY revenue_cents DESC;
            """)
            return [dict(r) for r in cursor.fetchall()]

    def get_inventory_analytics(self) -> Dict[str, Any]:
        """
        Calculates snapshot inventory metrics:
        total units, cost basis, retail valuation, potential margin, and stockout counts.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    COUNT(*) AS total_placements,
                    COALESCE(SUM(i.stock_on_hand), 0) AS total_units_on_hand,
                    COALESCE(SUM(CASE WHEN i.stock_on_hand = 0 THEN 1 ELSE 0 END), 0) AS zero_stock_placements,
                    COALESCE(SUM(CASE WHEN i.stock_on_hand > 0 THEN 1 ELSE 0 END), 0) AS healthy_stock_placements,
                    COALESCE(SUM(i.stock_on_hand * p.product_cost_cents), 0) AS total_cost_value_cents,
                    COALESCE(SUM(i.stock_on_hand * p.product_price_cents), 0) AS total_retail_value_cents
                FROM external_inventory i
                JOIN external_products p ON i.product_id = p.product_id;
            """)
            res = dict(cursor.fetchone())

            cost_val = res.get("total_cost_value_cents", 0)
            retail_val = res.get("total_retail_value_cents", 0)
            total_placements = res.get("total_placements", 0)
            zero_stock = res.get("zero_stock_placements", 0)

            potential_margin = retail_val - cost_val
            potential_margin_pct = round((potential_margin / retail_val * 100.0), 2) if retail_val > 0 else 0.0
            stockout_rate = round((zero_stock / total_placements * 100.0), 2) if total_placements > 0 else 0.0

            res["potential_gross_margin_cents"] = potential_margin
            res["potential_gross_margin_pct"] = potential_margin_pct
            res["stockout_rate_pct"] = stockout_rate
            res["currency_code"] = "USD"

            # Fetch metadata snapshot date & assumption flag
            cursor.execute("SELECT inventory_snapshot_date, inventory_snapshot_date_is_assumed FROM analytics_metadata WHERE id = 1;")
            meta_row = cursor.fetchone()
            if meta_row:
                res["snapshot_date"] = meta_row["inventory_snapshot_date"]
                res["snapshot_date_is_assumed"] = bool(meta_row["inventory_snapshot_date_is_assumed"])
            else:
                res["snapshot_date"] = "2025-12-31"
                res["snapshot_date_is_assumed"] = True

            return res

    def get_inventory_by_product(
        self,
        limit: Optional[int] = 10,
        order_by: str = "stock_units",
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Returns product-level inventory aggregation across all store placements.
        Fields: product_id, product_name, category, store_placements, stock_units,
        inventory_cost_value_cents, inventory_retail_value_cents, zero_stock_store_count.
        Supported order_by: 'stock_units', 'cost_value', 'retail_value', 'placements', 'zero_stock'.
        """
        order_clause_map = {
            "stock_units": "stock_units DESC",
            "cost_value": "inventory_cost_value_cents DESC",
            "retail_value": "inventory_retail_value_cents DESC",
            "placements": "store_placements DESC",
            "zero_stock": "zero_stock_store_count DESC"
        }
        clean_order_by = order_by.lower().strip()
        if clean_order_by not in order_clause_map:
            raise ValueError(f"Invalid order_by '{order_by}'. Allowed: {list(order_clause_map.keys())}")
        order_clause = order_clause_map[clean_order_by]

        if limit is not None:
            if not isinstance(limit, int) or limit <= 0 or limit > 1000:
                raise ValueError("Limit must be a positive integer between 1 and 1000")

        query = """
            SELECT
                p.product_id,
                p.product_name,
                p.product_category AS category,
                COUNT(i.store_id) AS store_placements,
                COALESCE(SUM(i.stock_on_hand), 0) AS stock_units,
                COALESCE(SUM(i.stock_on_hand * p.product_cost_cents), 0) AS inventory_cost_value_cents,
                COALESCE(SUM(i.stock_on_hand * p.product_price_cents), 0) AS inventory_retail_value_cents,
                COALESCE(SUM(CASE WHEN i.stock_on_hand = 0 THEN 1 ELSE 0 END), 0) AS zero_stock_store_count
            FROM external_products p
            LEFT JOIN external_inventory i ON p.product_id = i.product_id
        """
        params: List[Any] = []

        if category:
            query += " WHERE p.product_category = ?"
            params.append(category)

        query += f" GROUP BY p.product_id ORDER BY {order_clause}"

        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(r) for r in cursor.fetchall()]
