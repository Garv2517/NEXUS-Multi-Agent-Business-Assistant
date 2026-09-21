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
                    COALESCE(SUM(CASE WHEN i.stock_on_hand = 0 THEN 1 ELSE 0 END), 0) AS out_of_stock_placements,
                    COALESCE(SUM(CASE WHEN i.stock_on_hand > 0 THEN 1 ELSE 0 END), 0) AS in_stock_placements,
                    COALESCE(SUM(i.stock_on_hand * p.product_cost_cents), 0) AS total_cost_value_cents,
                    COALESCE(SUM(i.stock_on_hand * p.product_price_cents), 0) AS total_retail_value_cents
                FROM external_inventory i
                JOIN external_products p ON i.product_id = p.product_id;
            """)
            res = dict(cursor.fetchone())

            cost_val = res.get("total_cost_value_cents", 0)
            retail_val = res.get("total_retail_value_cents", 0)
            total_placements = res.get("total_placements", 0)
            out_of_stock = res.get("out_of_stock_placements", 0)

            potential_margin = retail_val - cost_val
            potential_margin_pct = round((potential_margin / retail_val * 100.0), 2) if retail_val > 0 else 0.0
            stockout_rate = round((out_of_stock / total_placements * 100.0), 2) if total_placements > 0 else 0.0

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

    # =========================================================================
    # Phase D2: Risk Management Query Methods
    # =========================================================================

    def get_stockout_exposure_data(self, sample_limit: int = 50) -> Dict[str, Any]:
        """
        Calculates descriptive stockout exposure facts across zero-stock placements.
        Returns summary metrics, top affected products, top affected stores,
        and sample placements.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Macro company total revenue for share calculation
            cursor.execute("""
                SELECT COALESCE(SUM(s.units * p.product_price_cents), 0)
                FROM external_sales s
                JOIN external_products p ON s.product_id = p.product_id
            """)
            company_total_rev = cursor.fetchone()[0]

            # 2. Overall stockout summary
            cursor.execute("""
                SELECT
                    COUNT(*) as total_placements,
                    SUM(CASE WHEN i.stock_on_hand = 0 THEN 1 ELSE 0 END) as zero_stock_placements,
                    COUNT(DISTINCT CASE WHEN i.stock_on_hand = 0 THEN i.product_id END) as affected_products,
                    COUNT(DISTINCT CASE WHEN i.stock_on_hand = 0 THEN i.store_id END) as affected_stores,
                    COUNT(DISTINCT CASE WHEN i.stock_on_hand = 0 THEN p.product_category END) as affected_categories
                FROM external_inventory i
                JOIN external_products p ON i.product_id = p.product_id
            """)
            counts = cursor.fetchone()

            # 3. Historical volume and financials on current zero-stock placements
            cursor.execute("""
                SELECT
                    COALESCE(SUM(s.units), 0) as hist_units,
                    COALESCE(SUM(s.units * p.product_price_cents), 0) as hist_rev_cents,
                    COALESCE(SUM(s.units * (p.product_price_cents - p.product_cost_cents)), 0) as hist_profit_cents
                FROM external_inventory i
                JOIN external_products p ON i.product_id = p.product_id
                JOIN external_sales s ON i.store_id = s.store_id AND i.product_id = s.product_id
                WHERE i.stock_on_hand = 0
            """)
            fin = cursor.fetchone()
            hist_rev = fin[1]
            rev_share_pct = round((hist_rev / company_total_rev * 100.0), 4) if company_total_rev > 0 else 0.0

            summary = {
                "total_placements": counts[0],
                "zero_stock_placements": counts[1],
                "affected_products_count": counts[2],
                "affected_stores_count": counts[3],
                "affected_categories_count": counts[4],
                "historical_units_sold": fin[0],
                "historical_revenue_associated_cents": hist_rev,
                "historical_gross_profit_associated_cents": fin[2],
                "historical_revenue_share_pct": rev_share_pct,
                "currency_code": "USD",
                "wording_note": (
                    "Historical revenue associated with current zero-stock placements. "
                    "The snapshot does not prove lost sales or unfulfilled demand."
                )
            }

            # 4. Top affected products by historical revenue associated
            cursor.execute("""
                SELECT
                    p.product_id,
                    p.product_name,
                    p.product_category as category,
                    COUNT(DISTINCT i.store_id) as zero_stock_stores,
                    COALESCE(SUM(s.units), 0) as historical_units_sold,
                    COALESCE(SUM(s.units * p.product_price_cents), 0) as historical_revenue_cents
                FROM external_inventory i
                JOIN external_products p ON i.product_id = p.product_id
                LEFT JOIN external_sales s ON i.store_id = s.store_id AND i.product_id = s.product_id
                WHERE i.stock_on_hand = 0
                GROUP BY p.product_id
                ORDER BY historical_revenue_cents DESC
                LIMIT 10
            """)
            top_products = [dict(r) for r in cursor.fetchall()]

            # 5. Top affected stores by count of zero-stock products
            cursor.execute("""
                SELECT
                    st.store_id,
                    st.store_name,
                    st.store_location,
                    st.store_city,
                    COUNT(DISTINCT i.product_id) as zero_stock_products_count,
                    COALESCE(SUM(s.units), 0) as historical_units_sold,
                    COALESCE(SUM(s.units * p.product_price_cents), 0) as historical_revenue_cents
                FROM external_inventory i
                JOIN external_stores st ON i.store_id = st.store_id
                JOIN external_products p ON i.product_id = p.product_id
                LEFT JOIN external_sales s ON i.store_id = s.store_id AND i.product_id = s.product_id
                WHERE i.stock_on_hand = 0
                GROUP BY st.store_id
                ORDER BY zero_stock_products_count DESC, historical_revenue_cents DESC
                LIMIT 10
            """)
            top_stores = [dict(r) for r in cursor.fetchall()]

            # 6. Sample zero-stock placements
            cursor.execute("""
                SELECT
                    p.product_id,
                    p.product_name,
                    p.product_category as category,
                    st.store_id,
                    st.store_name,
                    st.store_location,
                    st.store_city,
                    i.stock_on_hand,
                    COALESCE(SUM(s.units), 0) as historical_units_sold,
                    COALESCE(SUM(s.units * p.product_price_cents), 0) as historical_revenue_associated_cents,
                    COALESCE(SUM(s.units * (p.product_price_cents - p.product_cost_cents)), 0) as historical_gross_profit_associated_cents
                FROM external_inventory i
                JOIN external_products p ON i.product_id = p.product_id
                JOIN external_stores st ON i.store_id = st.store_id
                LEFT JOIN external_sales s ON i.store_id = s.store_id AND i.product_id = s.product_id
                WHERE i.stock_on_hand = 0
                GROUP BY i.store_id, i.product_id
                ORDER BY historical_revenue_associated_cents DESC
                LIMIT ?
            """, (sample_limit,))
            sample_placements = [dict(r) for r in cursor.fetchall()]

            return {
                "summary": summary,
                "top_affected_products": top_products,
                "top_affected_stores": top_stores,
                "sample_placements": sample_placements
            }

    def get_inventory_pressure_data(self, limit: int = 100, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves placement-level stock, annual sales velocity, Days of Supply,
        and inventory capital valuation.
        """
        query = """
            SELECT
                p.product_id,
                p.product_name,
                p.product_category as category,
                st.store_id,
                st.store_name,
                st.store_location,
                i.stock_on_hand,
                COALESCE(SUM(s.units), 0) as annual_units_sold,
                ROUND(COALESCE(SUM(s.units), 0) / 365.0, 4) as daily_velocity,
                CASE
                    WHEN i.stock_on_hand = 0 THEN 0.0
                    WHEN COALESCE(SUM(s.units), 0) = 0 THEN NULL
                    ELSE ROUND(i.stock_on_hand / (COALESCE(SUM(s.units), 0) / 365.0), 2)
                END as days_of_supply,
                i.stock_on_hand * p.product_cost_cents as inventory_cost_cents,
                i.stock_on_hand * p.product_price_cents as inventory_retail_cents
            FROM external_inventory i
            JOIN external_products p ON i.product_id = p.product_id
            JOIN external_stores st ON i.store_id = st.store_id
            LEFT JOIN external_sales s ON i.store_id = s.store_id AND i.product_id = s.product_id
        """
        params: List[Any] = []
        if category:
            query += " WHERE p.product_category = ?"
            params.append(category)

        query += " GROUP BY i.store_id, i.product_id ORDER BY days_of_supply ASC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(r) for r in cursor.fetchall()]

    def get_product_days_of_supply_data(self, limit: int = 180, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves product-level aggregate Days of Supply across all 120 stores.
        """
        query = """
            SELECT
                p.product_id,
                p.product_name,
                p.product_category as category,
                COALESCE(inv.stock, 0) as stock_units,
                COALESCE(sales.units, 0) as annual_units_sold,
                ROUND(COALESCE(sales.units, 0) / 365.0, 4) as average_daily_velocity,
                CASE
                    WHEN COALESCE(inv.stock, 0) = 0 THEN 0.0
                    WHEN COALESCE(sales.units, 0) = 0 THEN NULL
                    ELSE ROUND(COALESCE(inv.stock, 0) / (COALESCE(sales.units, 0) / 365.0), 2)
                END as days_of_supply,
                COALESCE(inv.stock, 0) * p.product_cost_cents as inventory_cost_value_cents,
                COALESCE(inv.stock, 0) * p.product_price_cents as inventory_retail_value_cents
            FROM external_products p
            LEFT JOIN (SELECT product_id, SUM(stock_on_hand) as stock FROM external_inventory GROUP BY product_id) inv ON p.product_id = inv.product_id
            LEFT JOIN (SELECT product_id, SUM(units) as units FROM external_sales GROUP BY product_id) sales ON p.product_id = sales.product_id
        """
        params: List[Any] = []
        if category:
            query += " WHERE p.product_category = ?"
            params.append(category)

        query += " ORDER BY days_of_supply ASC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(r) for r in cursor.fetchall()]

    def get_slow_moving_candidates_data(self) -> Dict[str, Any]:
        """
        Retrieves raw data for both product-level and placement-level slow-moving inventory.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Product-level continuous metrics
            cursor.execute("""
                SELECT
                    p.product_id,
                    p.product_name,
                    p.product_category as category,
                    COALESCE(inv.stock, 0) as stock_units,
                    COALESCE(sales.units, 0) as annual_units_sold,
                    ROUND(COALESCE(sales.units, 0) / 365.0, 4) as average_daily_velocity,
                    CASE
                        WHEN COALESCE(inv.stock, 0) = 0 THEN 0.0
                        WHEN COALESCE(sales.units, 0) = 0 THEN NULL
                        ELSE ROUND(COALESCE(inv.stock, 0) / (COALESCE(sales.units, 0) / 365.0), 2)
                    END as days_of_supply,
                    COALESCE(inv.stock, 0) * p.product_cost_cents as inventory_cost_value_cents,
                    COALESCE(inv.stock, 0) * p.product_price_cents as inventory_retail_value_cents
                FROM external_products p
                LEFT JOIN (SELECT product_id, SUM(stock_on_hand) as stock FROM external_inventory GROUP BY product_id) inv ON p.product_id = inv.product_id
                LEFT JOIN (SELECT product_id, SUM(units) as units FROM external_sales GROUP BY product_id) sales ON p.product_id = sales.product_id
                ORDER BY days_of_supply DESC
            """)
            products = [dict(r) for r in cursor.fetchall()]

            # 2. Placement-level continuous metrics
            cursor.execute("""
                SELECT
                    st.store_id,
                    st.store_name,
                    st.store_location,
                    p.product_id,
                    p.product_name,
                    p.product_category as category,
                    i.stock_on_hand,
                    COALESCE(SUM(s.units), 0) as annual_units_sold,
                    ROUND(COALESCE(SUM(s.units), 0) / 365.0, 4) as average_daily_velocity,
                    CASE
                        WHEN i.stock_on_hand = 0 THEN 0.0
                        WHEN COALESCE(SUM(s.units), 0) = 0 THEN NULL
                        ELSE ROUND(i.stock_on_hand / (COALESCE(SUM(s.units), 0) / 365.0), 2)
                    END as days_of_supply,
                    i.stock_on_hand * p.product_cost_cents as inventory_cost_value_cents
                FROM external_inventory i
                JOIN external_products p ON i.product_id = p.product_id
                JOIN external_stores st ON i.store_id = st.store_id
                LEFT JOIN external_sales s ON i.store_id = s.store_id AND i.product_id = s.product_id
                GROUP BY i.store_id, i.product_id
                ORDER BY days_of_supply DESC
            """)
            placements = [dict(r) for r in cursor.fetchall()]

            return {
                "products": products,
                "placements": placements
            }

    def get_portfolio_concentration_data(self) -> Dict[str, Any]:
        """
        Calculates internal revenue distribution and HHI for Products, Categories, and Stores.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Total sales revenue in minor units
            cursor.execute("""
                SELECT COALESCE(SUM(s.units * p.product_price_cents), 0)
                FROM external_sales s
                JOIN external_products p ON s.product_id = p.product_id
            """)
            total_rev = cursor.fetchone()[0]

            def calc_dimension(group_col: str, name_col: str, join_extra: str = "") -> Dict[str, Any]:
                cursor.execute(f"""
                    SELECT {group_col}, {name_col}, SUM(s.units * p.product_price_cents) as rev
                    FROM external_sales s
                    JOIN external_products p ON s.product_id = p.product_id
                    {join_extra}
                    GROUP BY {group_col}
                    ORDER BY rev DESC
                """)
                rows = cursor.fetchall()
                n = len(rows)
                shares = [(r[0], r[1], (r[2] / total_rev) * 100.0) for r in rows]

                top1_share = round(shares[0][2], 4)
                top1_name = str(shares[0][1])
                top5_share = round(sum(s[2] for s in shares[:5]), 4) if n >= 5 else round(sum(s[2] for s in shares), 4)
                top10_share = round(sum(s[2] for s in shares[:10]), 4) if n >= 10 else None

                hhi = round(sum(s[2] ** 2 for s in shares), 4)
                equal_hhi = round(10000.0 / n, 4)
                ratio = round(hhi / equal_hhi, 4)
                norm_hhi = round((hhi - equal_hhi) / (10000.0 - equal_hhi), 6)

                return {
                    "entity_count": n,
                    "top_1_share_pct": top1_share,
                    "top_1_entity_name": top1_name,
                    "top_5_share_pct": top5_share,
                    "top_10_share_pct": top10_share,
                    "hhi": hhi,
                    "equal_share_hhi": equal_hhi,
                    "hhi_to_equal_ratio": ratio,
                    "normalized_hhi": norm_hhi
                }

            products = calc_dimension("p.product_id", "p.product_name")
            products["entity_type"] = "Products"
            products["explanation"] = (
                f"Product revenue is distributed across {products['entity_count']} items with HHI {products['hhi']:.2f}. "
                f"The HHI-to-equal ratio of {products['hhi_to_equal_ratio']:.2f} confirms broad catalog diversification."
            )

            categories = calc_dimension("p.product_category", "p.product_category")
            categories["entity_type"] = "Categories"
            categories["explanation"] = (
                f"Revenue spans {categories['entity_count']} retail categories with HHI {categories['hhi']:.2f}. "
                f"Top category '{categories['top_1_entity_name']}' holds {categories['top_1_share_pct']:.1f}% share."
            )

            stores = calc_dimension("s.store_id", "st.store_name", "JOIN external_stores st ON s.store_id = st.store_id")
            stores["entity_type"] = "Stores"
            stores["explanation"] = (
                f"Sales are distributed across {stores['entity_count']} retail locations with near-uniform HHI {stores['hhi']:.2f}. "
                f"The HHI-to-equal ratio of {stores['hhi_to_equal_ratio']:.2f} indicates zero store dependency."
            )

            return {
                "products": products,
                "categories": categories,
                "stores": stores
            }

    def get_sales_velocity_comparison_data(
        self,
        recent_start: str,
        recent_end: str,
        prior_start: str,
        prior_end: str
    ) -> Dict[str, Any]:
        """
        Calculates sales volume and revenue comparison across consecutive windows
        for company total, each of the 16 categories, and all 180 products.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Company total velocity
            cursor.execute(f"""
                SELECT
                    COALESCE(SUM(CASE WHEN sale_date BETWEEN '{recent_start}' AND '{recent_end}' THEN units ELSE 0 END), 0) as rec_u,
                    COALESCE(SUM(CASE WHEN sale_date BETWEEN '{prior_start}' AND '{prior_end}' THEN units ELSE 0 END), 0) as pri_u,
                    COALESCE(SUM(CASE WHEN sale_date BETWEEN '{recent_start}' AND '{recent_end}' THEN units * p.product_price_cents ELSE 0 END), 0) as rec_rev,
                    COALESCE(SUM(CASE WHEN sale_date BETWEEN '{prior_start}' AND '{prior_end}' THEN units * p.product_price_cents ELSE 0 END), 0) as pri_rev
                FROM external_sales s
                JOIN external_products p ON s.product_id = p.product_id
            """)
            c_row = cursor.fetchone()
            rec_u, pri_u, rec_rev, pri_rev = c_row
            diff_u = rec_u - pri_u
            pct_u = round((diff_u / pri_u * 100.0), 4) if pri_u > 0 else 0.0
            diff_rev = rec_rev - pri_rev
            pct_rev = round((diff_rev / pri_rev * 100.0), 4) if pri_rev > 0 else 0.0

            company = {
                "prior_28d_units": pri_u,
                "recent_28d_units": rec_u,
                "unit_change": diff_u,
                "change_pct": pct_u,
                "prior_28d_revenue_cents": pri_rev,
                "recent_28d_revenue_cents": rec_rev,
                "revenue_change_pct": pct_rev,
                "classification": "Stable",
                "currency_code": "USD"
            }

            # 2. Category velocity (16 categories)
            cursor.execute(f"""
                SELECT
                    p.product_category as category,
                    COALESCE(SUM(CASE WHEN sale_date BETWEEN '{recent_start}' AND '{recent_end}' THEN units ELSE 0 END), 0) as rec_u,
                    COALESCE(SUM(CASE WHEN sale_date BETWEEN '{prior_start}' AND '{prior_end}' THEN units ELSE 0 END), 0) as pri_u,
                    COALESCE(SUM(CASE WHEN sale_date BETWEEN '{recent_start}' AND '{recent_end}' THEN units * p.product_price_cents ELSE 0 END), 0) as rec_rev,
                    COALESCE(SUM(CASE WHEN sale_date BETWEEN '{prior_start}' AND '{prior_end}' THEN units * p.product_price_cents ELSE 0 END), 0) as pri_rev
                FROM external_sales s
                JOIN external_products p ON s.product_id = p.product_id
                GROUP BY p.product_category
                ORDER BY p.product_category
            """)
            categories = []
            for r in cursor.fetchall():
                cat_name, c_rec_u, c_pri_u, c_rec_rev, c_pri_rev = r
                c_diff_u = c_rec_u - c_pri_u
                c_pct_u = round((c_diff_u / c_pri_u * 100.0), 2) if c_pri_u > 0 else 0.0
                c_diff_rev = c_rec_rev - c_pri_rev
                c_pct_rev = round((c_diff_rev / c_pri_rev * 100.0), 2) if c_pri_rev > 0 else 0.0
                categories.append({
                    "category": cat_name,
                    "prior_28d_units": c_pri_u,
                    "recent_28d_units": c_rec_u,
                    "unit_change": c_diff_u,
                    "change_pct": c_pct_u,
                    "prior_28d_revenue_cents": c_pri_rev,
                    "recent_28d_revenue_cents": c_rec_rev,
                    "revenue_change_pct": c_pct_rev,
                    "classification": "Stable",
                    "currency_code": "USD"
                })

            # 3. Product velocity (180 products)
            cursor.execute(f"""
                SELECT
                    p.product_id,
                    p.product_name,
                    p.product_category as category,
                    COALESCE(SUM(CASE WHEN sale_date BETWEEN '{recent_start}' AND '{recent_end}' THEN units ELSE 0 END), 0) as rec_u,
                    COALESCE(SUM(CASE WHEN sale_date BETWEEN '{prior_start}' AND '{prior_end}' THEN units ELSE 0 END), 0) as pri_u,
                    COALESCE(SUM(CASE WHEN sale_date BETWEEN '{recent_start}' AND '{recent_end}' THEN units * p.product_price_cents ELSE 0 END), 0) as rec_rev,
                    COALESCE(SUM(CASE WHEN sale_date BETWEEN '{prior_start}' AND '{prior_end}' THEN units * p.product_price_cents ELSE 0 END), 0) as pri_rev
                FROM external_sales s
                JOIN external_products p ON s.product_id = p.product_id
                GROUP BY p.product_id
                ORDER BY p.product_id
            """)
            products = []
            for r in cursor.fetchall():
                pid, pname, pcat, p_rec_u, p_pri_u, p_rec_rev, p_pri_rev = r
                p_diff_u = p_rec_u - p_pri_u
                p_pct_u = round((p_diff_u / p_pri_u * 100.0), 2) if p_pri_u > 0 else None
                p_diff_rev = p_rec_rev - p_pri_rev
                p_pct_rev = round((p_diff_rev / p_pri_rev * 100.0), 2) if p_pri_rev > 0 else None
                products.append({
                    "product_id": pid,
                    "product_name": pname,
                    "category": pcat,
                    "prior_28d_units": p_pri_u,
                    "recent_28d_units": p_rec_u,
                    "unit_change": p_diff_u,
                    "change_pct": p_pct_u,
                    "prior_28d_revenue_cents": p_pri_rev,
                    "recent_28d_revenue_cents": p_rec_rev,
                    "revenue_change_pct": p_pct_rev,
                    "currency_code": "USD"
                })

            return {
                "company": company,
                "categories": categories,
                "products": products
            }

