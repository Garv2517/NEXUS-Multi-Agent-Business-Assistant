"""
Sales Specialist Agent for Phase B3.
Responsible for revenue, monthly performance, trends, and top products.
Restricted exclusively to sales tools. No direct database or repository access.
"""

import time
import uuid
from typing import Optional
from .base import BaseAgent
from .types import AgentTask, AgentResult, ToolCallRecord
from ..tools.sales_tools import (
    get_total_sales,
    get_monthly_sales,
    get_top_products,
    get_sales_trend
)



class SalesAgent(BaseAgent):
    name = "sales"
    description = "Specialist agent responsible for sales metrics, monthly revenue, trends, and top-selling products."

    ALLOWED_OPERATIONS = {
        "sales.total",
        "sales.monthly",
        "sales.top_products",
        "sales.trend"
    }

    async def execute(self, task: AgentTask) -> AgentResult:
        if task.operation not in self.ALLOWED_OPERATIONS:
            return AgentResult(
                task_id=task.task_id,
                agent=self.name,
                status="error",
                error={
                    "code": "UNSUPPORTED_OPERATION",
                    "message": f"Operation '{task.operation}' is not supported by SalesAgent."
                }
            )

        db_path = task.parameters.get("db_path") or task.context.get("db_path")

        try:
            t0 = time.perf_counter()
            tool_name = ""
            result_data = {}
            summary = ""

            if task.operation == "sales.total":
                tool_name = "get_total_sales"
                month = task.parameters.get("month", 9)
                year = task.parameters.get("year", 2026)
                result_data = get_total_sales(month=month, year=year, db_path=db_path)
                summary = f"Total revenue: ₹{int(result_data.get('revenue', 0)):,} across {result_data.get('units_sold', 0)} units"

            elif task.operation == "sales.monthly":
                tool_name = "get_monthly_sales"
                month = task.parameters.get("month", 9)
                year = task.parameters.get("year", 2026)
                result_data = get_monthly_sales(month=month, year=year, db_path=db_path)
                summary = f"Monthly sales for {month}/{year}: ₹{int(result_data.get('revenue', 0)):,}"

            elif task.operation == "sales.top_products":
                tool_name = "get_top_products"
                limit = task.parameters.get("limit", 3)
                month = task.parameters.get("month", 9)
                year = task.parameters.get("year", 2026)
                result_data = get_top_products(limit=limit, month=month, year=year, db_path=db_path)
                prods = result_data.get("products", [])
                summary = f"Retrieved top {len(prods)} products"

            elif task.operation == "sales.trend":
                tool_name = "get_sales_trend"
                result_data = get_sales_trend(db_path=db_path)
                summary = f"Retrieved sales trend across {len(result_data.get('months', []))} months"

            t1 = time.perf_counter()
            duration_ms = max(1, int((t1 - t0) * 1000))

            call_record = ToolCallRecord(
                id=f"tool_{uuid.uuid4().hex[:8]}",
                agent=self.name,
                tool=tool_name,
                arguments=task.parameters,
                status="success",
                duration_ms=duration_ms,
                result_summary=summary
            )

            # Exactly one durable activity record per tool execution
            from ..services.business_service import BusinessService
            BusinessService.record_activity(
                agent=self.name,
                action=summary,
                tool=tool_name,
                status="success",
                duration_ms=duration_ms,
                db_path=db_path
            )

            return AgentResult(
                task_id=task.task_id,
                agent=self.name,
                status="success",
                data=result_data,
                tool_calls=[call_record]
            )

        except Exception as e:
            t1 = time.perf_counter()
            duration_ms = max(1, int((t1 - t0) * 1000))
            err_record = ToolCallRecord(
                id=f"tool_{uuid.uuid4().hex[:8]}",
                agent=self.name,
                tool=tool_name or "unknown",
                arguments=task.parameters,
                status="error",
                duration_ms=duration_ms,
                result_summary="Execution failed",
                error=str(e)
            )
            return AgentResult(
                task_id=task.task_id,
                agent=self.name,
                status="error",
                tool_calls=[err_record],
                error={
                    "code": "TOOL_EXECUTION_ERROR",
                    "message": str(e)
                }
            )
