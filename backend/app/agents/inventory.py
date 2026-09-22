"""Inventory Specialist Agent.

Live Assistant requests use the unified Kaggle analytics/risk data source when an
``analytics_db_path`` is supplied. Legacy B3 behavior remains available for isolated
regression tests and is not used by the production chat endpoint.
"""

import time
import uuid
from .base import BaseAgent
from .types import AgentTask, AgentResult, ToolCallRecord
from ..tools.inventory_tools import (
    get_inventory_summary as legacy_get_inventory_summary,
    get_low_stock_products as legacy_get_low_stock_products,
    get_product_stock as legacy_get_product_stock,
)
from ..tools.analytics_business_tools import (
    get_inventory_summary as analytics_get_inventory_summary,
    get_low_stock_products as analytics_get_low_stock_products,
    get_product_stock as analytics_get_product_stock,
)


class InventoryAgent(BaseAgent):
    name = "inventory"
    description = "Specialist agent responsible for inventory positions, stockouts, and calibrated inventory pressure."

    ALLOWED_OPERATIONS = {
        "inventory.product_stock",
        "inventory.low_stock",
        "inventory.summary",
    }

    async def execute(self, task: AgentTask) -> AgentResult:
        if task.operation not in self.ALLOWED_OPERATIONS:
            return AgentResult(
                task_id=task.task_id,
                agent=self.name,
                status="error",
                error={
                    "code": "UNSUPPORTED_OPERATION",
                    "message": f"Operation '{task.operation}' is not supported by InventoryAgent.",
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
            if task.operation == "inventory.product_stock":
                tool_name = "get_product_stock"
                p_id = task.parameters.get("product_id")
                p_name = task.parameters.get("product_name")
                if use_analytics:
                    result_data = analytics_get_product_stock(
                        product_id=p_id,
                        product_name=p_name,
                        analytics_db_path=analytics_db_path,
                    )
                    summary = (
                        f"Stock for {result_data.get('name', p_id or p_name)}: "
                        f"{result_data.get('stock', 0):,} units across "
                        f"{result_data.get('store_placements', 0)} store placements"
                    )
                else:
                    result_data = legacy_get_product_stock(product_id=p_id, product_name=p_name, db_path=db_path)
                    summary = f"Stock for {result_data.get('name', p_id or p_name)}: {result_data.get('stock')} units ({result_data.get('status')})"

            elif task.operation == "inventory.low_stock":
                tool_name = "get_low_stock_products"
                include_oos = task.parameters.get("include_out_of_stock", True if use_analytics else False)
                if use_analytics:
                    result_data = analytics_get_low_stock_products(
                        include_out_of_stock=include_oos,
                        limit=task.parameters.get("limit", 10),
                        analytics_db_path=analytics_db_path,
                    )
                    summary = f"Found {result_data.get('count', 0)} high-pressure/stockout placements"
                else:
                    result_data = legacy_get_low_stock_products(include_out_of_stock=include_oos, db_path=db_path)
                    summary = f"Found {result_data.get('count', 0)} low stock items"

            elif task.operation == "inventory.summary":
                tool_name = "get_inventory_summary"
                if use_analytics:
                    result_data = analytics_get_inventory_summary(analytics_db_path=analytics_db_path)
                    summary = (
                        f"Inventory summary: {result_data.get('total_units_on_hand', 0):,} units, "
                        f"{result_data.get('out_of_stock_placements', 0)} zero-stock placements"
                    )
                else:
                    result_data = legacy_get_inventory_summary(db_path=db_path)
                    summary = f"Inventory summary: {result_data.get('total_products')} products ({result_data.get('healthy')} healthy, {result_data.get('low_stock')} low)"

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

        except ValueError as exc:
            duration_ms = max(1, int((time.perf_counter() - t0) * 1000))
            err_record = ToolCallRecord(
                id=f"tool_{uuid.uuid4().hex[:8]}",
                agent=self.name,
                tool=tool_name or "get_product_stock",
                arguments={k: v for k, v in task.parameters.items() if k not in {"db_path", "analytics_db_path"}},
                status="error",
                duration_ms=duration_ms,
                result_summary="Product/data lookup failed",
                error=str(exc),
            )
            return AgentResult(
                task_id=task.task_id,
                agent=self.name,
                status="error",
                data=None,
                tool_calls=[err_record],
                error={"code": "PRODUCT_NOT_FOUND", "message": str(exc)},
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
