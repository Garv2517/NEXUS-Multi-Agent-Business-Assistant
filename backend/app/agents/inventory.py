"""
Inventory Specialist Agent for Phase B3.
Responsible for stock levels, replenishment alerts, and catalog health.
Restricted exclusively to inventory tools. No direct database or repository access.
"""

import time
import uuid
from typing import Optional
from .base import BaseAgent
from .types import AgentTask, AgentResult, ToolCallRecord
from ..tools.inventory_tools import (
    get_product_stock,
    get_low_stock_products,
    get_inventory_summary
)
from ..services.business_service import BusinessService


class InventoryAgent(BaseAgent):
    name = "inventory"
    description = "Specialist agent responsible for product stock levels, low-stock thresholds, and catalog health."

    ALLOWED_OPERATIONS = {
        "inventory.product_stock",
        "inventory.low_stock",
        "inventory.summary"
    }

    async def execute(self, task: AgentTask) -> AgentResult:
        if task.operation not in self.ALLOWED_OPERATIONS:
            return AgentResult(
                task_id=task.task_id,
                agent=self.name,
                status="error",
                error={
                    "code": "UNSUPPORTED_OPERATION",
                    "message": f"Operation '{task.operation}' is not supported by InventoryAgent."
                }
            )

        db_path = task.parameters.get("db_path") or task.context.get("db_path")

        try:
            t0 = time.perf_counter()
            tool_name = ""
            result_data = {}
            summary = ""

            if task.operation == "inventory.product_stock":
                tool_name = "get_product_stock"
                p_id = task.parameters.get("product_id")
                p_name = task.parameters.get("product_name")
                result_data = get_product_stock(product_id=p_id, product_name=p_name, db_path=db_path)
                summary = f"Stock for {result_data.get('name', p_id or p_name)}: {result_data.get('stock')} units ({result_data.get('status')})"

            elif task.operation == "inventory.low_stock":
                tool_name = "get_low_stock_products"
                include_oos = task.parameters.get("include_out_of_stock", False)
                result_data = get_low_stock_products(include_out_of_stock=include_oos, db_path=db_path)
                summary = f"Found {result_data.get('count', 0)} low stock items"

            elif task.operation == "inventory.summary":
                tool_name = "get_inventory_summary"
                result_data = get_inventory_summary(db_path=db_path)
                summary = f"Inventory summary: {result_data.get('total_products')} products ({result_data.get('healthy')} healthy, {result_data.get('low_stock')} low)"

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

        except ValueError as ve:
            t1 = time.perf_counter()
            duration_ms = max(1, int((t1 - t0) * 1000))
            err_record = ToolCallRecord(
                id=f"tool_{uuid.uuid4().hex[:8]}",
                agent=self.name,
                tool=tool_name or "get_product_stock",
                arguments=task.parameters,
                status="error",
                duration_ms=duration_ms,
                result_summary="Product not found",
                error=str(ve)
            )
            return AgentResult(
                task_id=task.task_id,
                agent=self.name,
                status="error",
                data=None,
                tool_calls=[err_record],
                error={
                    "code": "PRODUCT_NOT_FOUND",
                    "message": str(ve)
                }
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
