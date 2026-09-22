"""Deterministic fallback router for Nexus.

Foundry remains the preferred live routing source when enabled. This router provides
safe local/fallback intent selection using the same server-approved operations.
"""

import re
import uuid
from typing import Dict, Any

from ..agents.types import ExecutionPlan, PlanStep


_MONTHS = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}


def _sales_selectors(q: str) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    for token, month in _MONTHS.items():
        if re.search(rf"\b{re.escape(token)}\b", q):
            params["month"] = month
            break
    year_match = re.search(r"\b(20\d{2})\b", q)
    if year_match:
        params["year"] = int(year_match.group(1))
    return params


def _product_selectors(q: str) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    # External product IDs are numeric (e.g. "product 130", "product id 130").
    pid_match = re.search(r"\bproduct(?:\s+id)?\s*#?\s*(\d{1,4})\b", q)
    if pid_match:
        params["product_id"] = pid_match.group(1)
        return params

    # Conservative phrase extraction for fallback mode only.
    for prefix in ("stock level for ", "stock level of ", "current stock for ", "stock for ", "stock of ", "inventory for ", "inventory of "):
        idx = q.find(prefix)
        if idx >= 0:
            candidate = q[idx + len(prefix):].strip(" ?.!")
            if candidate and len(candidate) <= 80 and candidate not in {"products", "product", "each product"}:
                params["product_name"] = candidate
                break
    return params


class DeterministicRouter:
    """Routes supported business queries to trusted specialist operations."""

    @staticmethod
    def route(query: str) -> ExecutionPlan:
        q = query.strip().lower()
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"

        # 1. Compound: compare top-selling products with current inventory.
        has_top = any(w in q for w in ["top-selling", "top selling", "top products", "top 3", "top 5"]) or (
            "top" in q.split() and any(w in q for w in ["product", "products", "selling", "sellers"])
        )
        has_inv = any(w in q for w in ["stock", "inventory"])
        has_compare = "compare" in q
        if (has_compare and (has_inv or has_top or "product" in q)) or (has_top and has_inv):
            return ExecutionPlan(
                plan_id=plan_id,
                intent="compound_sales_inventory",
                query=query,
                agents=["sales", "inventory"],
                steps=[
                    PlanStep(step=1, agent="sales", operation="sales.top_products", parameters={"limit": 3}, description="Retrieve top 3 selling products"),
                    PlanStep(step=2, agent="inventory", operation="inventory.product_stock", parameters={}, depends_on=1, description="Check current inventory stock for each top product"),
                ],
            )

        # 2. Business overview combines unified retail analytics + internal people data.
        if "overview" in q or "company status" in q or "business summary" in q:
            return ExecutionPlan(
                plan_id=plan_id,
                intent="business_overview",
                query=query,
                agents=["sales", "inventory", "hr"],
                steps=[
                    PlanStep(step=1, agent="sales", operation="sales.total", parameters={}, description="Retrieve full-period sales performance"),
                    PlanStep(step=2, agent="inventory", operation="inventory.summary", parameters={}, description="Retrieve inventory snapshot summary"),
                    PlanStep(step=3, agent="hr", operation="hr.summary", parameters={}, description="Retrieve workforce headcount and leave metrics"),
                ],
            )

        # 3. Sales.
        if any(w in q for w in ["revenue", "sales", "selling", "top products", "top-selling", "top selling", "trend", "order", "units sold"]):
            if "trend" in q:
                op, params = "sales.trend", {}
            elif "top" in q:
                limit_match = re.search(r"\btop\s+(\d{1,2})\b", q)
                limit = min(max(int(limit_match.group(1)), 1), 20) if limit_match else 3
                op, params = "sales.top_products", {"limit": limit}
            elif "month" in q or any(re.search(rf"\b{m}\b", q) for m in _MONTHS):
                op, params = "sales.monthly", _sales_selectors(q)
            else:
                op, params = "sales.total", {}

            return ExecutionPlan(
                plan_id=plan_id,
                intent="sales",
                query=query,
                agents=["sales"],
                steps=[PlanStep(step=1, agent="sales", operation=op, parameters=params, description="Execute sales specialist operation")],
            )

        # 4. Inventory. The external dataset has no reorder levels; "low stock" maps
        # to calibrated inventory pressure / stockout analysis in live analytics mode.
        if any(w in q for w in ["stock", "inventory", "reorder", "depleted", "warehouse", "catalog"]):
            if any(w in q for w in ["low", "reorder", "depleted", "need", "out of stock", "stockout", "pressure"]):
                op, params = "inventory.low_stock", {}
            else:
                selectors = _product_selectors(q)
                if selectors:
                    op, params = "inventory.product_stock", selectors
                else:
                    op, params = "inventory.summary", {}

            return ExecutionPlan(
                plan_id=plan_id,
                intent="inventory",
                query=query,
                agents=["inventory"],
                steps=[PlanStep(step=1, agent="inventory", operation=op, parameters=params, description="Execute inventory specialist operation")],
            )

        # 5. HR / People Management.
        if any(w in q for w in ["employee", "leave", "policy", "policies", "remote", "sick", "headcount", "staff", "profile"]):
            if any(w in q for w in ["all policies", "list policies", "all hr policies", "corporate policies", "company policies"]):
                op, params = "hr.policies", {}
            elif any(w in q for w in ["policy", "remote", "sick", "annual"]):
                op = "hr.policy"
                policy_title = "Remote Work" if "remote" in q else ("Sick Leave" if "sick" in q else "Annual Leave")
                params = {"title": policy_title}
            elif any(w in q for w in ["emp001", "emp002", "emp003", "profile", "employee details", "details for", "aarav", "priya"]):
                op = "hr.employee"
                emp_id = "EMP002" if "emp002" in q or "priya" in q else "EMP001"
                params = {"employee_id": emp_id}
            else:
                op, params = "hr.summary", {}

            return ExecutionPlan(
                plan_id=plan_id,
                intent="hr",
                query=query,
                agents=["hr"],
                steps=[PlanStep(step=1, agent="hr", operation=op, parameters=params, description="Execute HR specialist operation")],
            )

        return ExecutionPlan(plan_id=plan_id, intent="unsupported", query=query, agents=[], steps=[])
