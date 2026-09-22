"""Sales Specialist Agent.

Legacy B3 tool behavior remains available for isolated regression tests, while live
Assistant requests can explicitly select the unified Kaggle analytics source via
``analytics_db_path``. The agent itself never queries SQLite directly.
"""

import time
import uuid
from .base import BaseAgent
from .types import AgentTask, AgentResult, ToolCallRecord
from ..tools.sales_tools import (
    get_total_sales as legacy_get_total_sales,
    get_monthly_sales as legacy_get_monthly_sales,
    get_top_products as legacy_get_top_products,
    get_sales_trend as legacy_get_sales_trend,
)
from ..tools.analytics_business_tools import (
    get_total_sales as analytics_get_total_sales,
    get_monthly_sales as analytics_get_monthly_sales,
    get_top_products as analytics_get_top_products,
    get_sales_trend as analytics_get_sales_trend,
)


class SalesAgent(BaseAgent):
    name = "sales"
    description = "Specialist agent responsible for sales metrics, monthly revenue, trends, and top-selling products."

    ALLOWED_OPERATIONS = {
        "sales.total",
        "sales.monthly",
        "sales.top_products",
        "sales.trend",
    }

    async def execute(self, task: AgentTask) -> AgentResult:
        if task.operation not in self.ALLOWED_OPERATIONS:
            return AgentResult(
                task_id=task.task_id,
                agent=self.name,
                status="error",
                error={
                    "code": "UNSUPPORTED_OPERATION",
                    "message": f"Operation '{task.operation}' is not supported by SalesAgent.",
                },
            )

        db_path = task.parameters.get("db_path") or task.context.get("db_path")
        analytics_db_path = task.parameters.get("analytics_db_path") or task.context.get("analytics_db_path")
        use_analytics = bool(analytics_db_path)

        t0 = time.perf_counter()
        tool_name = ""
        result_data = {}
        summary = ""

        try:
            if task.operation == "sales.total":
                tool_name = "get_total_sales"
                if use_analytics:
                    result_data = analytics_get_total_sales(analytics_db_path=analytics_db_path)
                    summary = (
                        f"External retail revenue: ${result_data.get('revenue_cents', 0) / 100:,.2f} "
                        f"across {result_data.get('units_sold', 0):,} units"
                    )
                else:
                    month = task.parameters.get("month", 9)
                    year = task.parameters.get("year", 2026)
                    result_data = legacy_get_total_sales(month=month, year=year, db_path=db_path)
                    summary = f"Total revenue: ₹{int(result_data.get('revenue', 0)):,} across {result_data.get('units_sold', 0)} units"

            elif task.operation == "sales.monthly":
                tool_name = "get_monthly_sales"
                month = task.parameters.get("month")
                year = task.parameters.get("year")
                if use_analytics:
                    result_data = analytics_get_monthly_sales(
                        month=month,
                        year=year,
                        analytics_db_path=analytics_db_path,
                    )
                    summary = f"Monthly sales for {result_data.get('period')}: ${result_data.get('revenue_cents', 0) / 100:,.2f}"
                else:
                    month = month if month is not None else 9
                    year = year if year is not None else 2026
                    result_data = legacy_get_monthly_sales(month=month, year=year, db_path=db_path)
                    summary = f"Monthly sales for {month}/{year}: ₹{int(result_data.get('revenue', 0)):,}"

            elif task.operation == "sales.top_products":
                tool_name = "get_top_products"
                limit = task.parameters.get("limit", 3)
                if use_analytics:
                    result_data = analytics_get_top_products(limit=limit, analytics_db_path=analytics_db_path)
                else:
                    month = task.parameters.get("month", 9)
                    year = task.parameters.get("year", 2026)
                    result_data = legacy_get_top_products(limit=limit, month=month, year=year, db_path=db_path)
                prods = result_data.get("products", [])
                summary = f"Retrieved top {len(prods)} products"

            elif task.operation == "sales.trend":
                tool_name = "get_sales_trend"
                if use_analytics:
                    result_data = analytics_get_sales_trend(analytics_db_path=analytics_db_path)
                else:
                    result_data = legacy_get_sales_trend(db_path=db_path)
                summary = f"Retrieved sales trend across {len(result_data.get('months', []))} months"

            duration_ms = max(1, int((time.perf_counter() - t0) * 1000))
            call_record = ToolCallRecord(
                id=f"tool_{uuid.uuid4().hex[:8]}",
                agent=self.name,
                tool=tool_name,
                arguments={k: v for k, v in task.parameters.items() if k not in {"db_path", "analytics_db_path"}},
                status="success",
                duration_ms=duration_ms,
                result_summary=summary,
            )

            from ..services.business_service import BusinessService
            BusinessService.record_activity(
                agent=self.name,
                action=summary,
                tool=tool_name,
                status="success",
                duration_ms=duration_ms,
                db_path=db_path,
            )

            return AgentResult(
                task_id=task.task_id,
                agent=self.name,
                status="success",
                data=result_data,
                tool_calls=[call_record],
            )

        except Exception as exc:
            duration_ms = max(1, int((time.perf_counter() - t0) * 1000))
            err_record = ToolCallRecord(
                id=f"tool_{uuid.uuid4().hex[:8]}",
                agent=self.name,
                tool=tool_name or "unknown",
                arguments={k: v for k, v in task.parameters.items() if k not in {"db_path", "analytics_db_path"}},
                status="error",
                duration_ms=duration_ms,
                result_summary="Execution failed",
                error=str(exc),
            )
            return AgentResult(
                task_id=task.task_id,
                agent=self.name,
                status="error",
                tool_calls=[err_record],
                error={"code": "TOOL_EXECUTION_ERROR", "message": str(exc)},
            )
