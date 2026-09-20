"""
Deterministic Router for Phase B3.
Maps user queries to discrete ExecutionPlans without LLMs or probabilistic routing.
Small, concise, and focused strictly on the supported business intents.
"""

import uuid
from typing import Dict, Any, List
from ..agents.types import ExecutionPlan, PlanStep


class DeterministicRouter:
    """Routes user queries deterministically to specialist agents."""

    @staticmethod
    def route(query: str) -> ExecutionPlan:
        q = query.strip().lower()
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"

        # 1. Compound: Compare top-selling products with inventory
        if ("compare" in q and ("product" in q or "stock" in q or "inventory" in q or "top" in q)) or \
           ("top" in q and ("inventory" in q or "stock" in q)):
            return ExecutionPlan(
                plan_id=plan_id,
                intent="compound_sales_inventory",
                query=query,
                agents=["sales", "inventory"],
                steps=[
                    PlanStep(
                        step=1,
                        agent="sales",
                        operation="sales.top_products",
                        parameters={"limit": 3},
                        description="Retrieve top 3 selling products"
                    ),
                    PlanStep(
                        step=2,
                        agent="inventory",
                        operation="inventory.product_stock",
                        parameters={},
                        depends_on=1,
                        description="Check current inventory stock for each top product"
                    )
                ]
            )

        # 2. Compound: Business Overview (Sales + Inventory + HR)
        if "overview" in q or "company status" in q or "business summary" in q:
            return ExecutionPlan(
                plan_id=plan_id,
                intent="business_overview",
                query=query,
                agents=["sales", "inventory", "hr"],
                steps=[
                    PlanStep(
                        step=1,
                        agent="sales",
                        operation="sales.total",
                        parameters={"month": 9, "year": 2026},
                        description="Retrieve current monthly sales performance"
                    ),
                    PlanStep(
                        step=2,
                        agent="inventory",
                        operation="inventory.summary",
                        parameters={},
                        description="Retrieve inventory health breakdown"
                    ),
                    PlanStep(
                        step=3,
                        agent="hr",
                        operation="hr.summary",
                        parameters={},
                        description="Retrieve workforce headcount and leave metrics"
                    )
                ]
            )

        # 3. Single-Agent: Sales
        if any(w in q for w in ["revenue", "sales", "top-selling", "top selling", "trend", "order", "units sold"]):
            op = "sales.trend" if "trend" in q else ("sales.top_products" if "top" in q else "sales.total")
            params = {"limit": 3} if op == "sales.top_products" else {"month": 9, "year": 2026}
            return ExecutionPlan(
                plan_id=plan_id,
                intent="sales",
                query=query,
                agents=["sales"],
                steps=[
                    PlanStep(
                        step=1,
                        agent="sales",
                        operation=op,
                        parameters=params,
                        description="Execute sales specialist operation"
                    )
                ]
            )

        # 4. Single-Agent: Inventory
        if any(w in q for w in ["stock", "inventory", "reorder", "depleted", "warehouse", "catalog"]):
            op = "inventory.low_stock" if any(w in q for w in ["low", "reorder", "depleted", "need"]) else "inventory.summary"
            return ExecutionPlan(
                plan_id=plan_id,
                intent="inventory",
                query=query,
                agents=["inventory"],
                steps=[
                    PlanStep(
                        step=1,
                        agent="inventory",
                        operation=op,
                        parameters={},
                        description="Execute inventory specialist operation"
                    )
                ]
            )

        # 5. Single-Agent: HR
        if any(w in q for w in ["employee", "leave", "policy", "remote", "sick", "headcount", "staff"]):
            op = "hr.policy" if any(w in q for w in ["policy", "remote", "sick", "annual"]) else "hr.summary"
            policy_title = "Remote Work" if "remote" in q else ("Sick Leave" if "sick" in q else "Annual Leave")
            params = {"title": policy_title} if op == "hr.policy" else {}
            return ExecutionPlan(
                plan_id=plan_id,
                intent="hr",
                query=query,
                agents=["hr"],
                steps=[
                    PlanStep(
                        step=1,
                        agent="hr",
                        operation=op,
                        parameters=params,
                        description="Execute HR specialist operation"
                    )
                ]
            )

        # 6. Unsupported / Out-of-Domain
        return ExecutionPlan(
            plan_id=plan_id,
            intent="unsupported",
            query=query,
            agents=[],
            steps=[]
        )
