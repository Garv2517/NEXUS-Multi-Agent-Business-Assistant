"""Read-only weekly forecasting queries over nexus_analytics.db."""
import contextlib
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from ..core.config import settings
from .analytics_repository import AnalyticsDatabaseNotFoundError


class ForecastRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or settings.get_analytics_database_path()).resolve()

    def _ensure_db_exists(self) -> None:
        if not self.db_path.exists():
            raise AnalyticsDatabaseNotFoundError("Analytics dataset unavailable")

    @contextlib.contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        self._ensure_db_exists()
        uri = f"file:{self.db_path.as_posix()}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    @staticmethod
    def _week_start_sql(date_column: str = "s.sale_date") -> str:
        # SQLite %w: Sunday=0 ... Saturday=6. Convert to Monday-based week.
        return (
            f"date({date_column}, '-' || "
            f"((CAST(strftime('%w', {date_column}) AS INTEGER) + 6) % 7) || ' days')"
        )

    def get_company_weekly_series(self) -> List[Dict[str, Any]]:
        week_expr = self._week_start_sql()
        with self._get_connection() as conn:
            rows = conn.execute(f"""
                SELECT
                    {week_expr} AS week_start,
                    MIN(s.sale_date) AS min_sale_date,
                    MAX(s.sale_date) AS max_sale_date,
                    COUNT(DISTINCT s.sale_date) AS distinct_sale_dates,
                    COUNT(*) AS transaction_count,
                    SUM(s.units) AS units,
                    SUM(s.units * p.product_price_cents) AS revenue_cents
                FROM external_sales s
                JOIN external_products p ON p.product_id = s.product_id
                GROUP BY week_start
                ORDER BY week_start
            """).fetchall()
        return [dict(r) for r in rows]

    def get_category_weekly_series(self) -> List[Dict[str, Any]]:
        week_expr = self._week_start_sql()
        with self._get_connection() as conn:
            rows = conn.execute(f"""
                SELECT
                    p.product_category AS category,
                    {week_expr} AS week_start,
                    COUNT(DISTINCT s.sale_date) AS distinct_sale_dates,
                    SUM(s.units) AS units,
                    SUM(s.units * p.product_price_cents) AS revenue_cents
                FROM external_sales s
                JOIN external_products p ON p.product_id = s.product_id
                GROUP BY p.product_category, week_start
                ORDER BY p.product_category, week_start
            """).fetchall()
        return [dict(r) for r in rows]

    def get_category_inventory_stock(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT
                    p.product_category AS category,
                    SUM(i.stock_on_hand) AS stock_units
                FROM external_inventory i
                JOIN external_products p ON p.product_id = i.product_id
                GROUP BY p.product_category
                ORDER BY p.product_category
            """).fetchall()
        return [dict(r) for r in rows]
