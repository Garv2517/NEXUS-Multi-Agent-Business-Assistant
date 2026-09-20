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
        has_top = any(w in q for w in ["top-selling", "top selling", "top products", "top 3", "top 5"]) or \
                  ("top" in q.split() and any(w in q for w in ["product", "products", "selling", "sellers"]))
        has_inv = any(w in q for w in ["stock", "inventory"])
        has_compare = "compare" in q

        if (has_compare and (has_inv or has_top or "product" in q)) or (has_top and has_inv):
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
            if "trend" in q:
                op = "sales.trend"
                params = {}
            elif "top" in q:
                op = "sales.top_products"
                params = {"limit": 3, "month": 9, "year": 2026}
            elif "month" in q:
                op = "sales.monthly"
                params = {"month": 9, "year": 2026}
            else:
                op = "sales.total"
                params = {"month": 9, "year": 2026}

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
            if any(w in q for w in ["low", "reorder", "depleted", "need"]):
                op = "inventory.low_stock"
                params = {}
            elif any(p in q for p in ["laptop", "mouse", "keyboard", "headset", "webcam", "p101", "p102", "p103"]):
                op = "inventory.product_stock"
                p_name = "Laptop Pro" if "laptop" in q else ("Wireless Headset" if "headset" in q else ("Mechanical Keyboard" if "keyboard" in q else None))
                p_id = "P101" if "p101" in q else ("P102" if "p102" in q else ("P103" if "p103" in q else None))
                params = {}
                if p_name:
                    params["product_name"] = p_name
                if p_id:
                    params["product_id"] = p_id
            else:
                op = "inventory.summary"
                params = {}

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
                        parameters=params,
                        description="Execute inventory specialist operation"
                    )
                ]
            )

        # 5. Single-Agent: HR
        if any(w in q for w in ["employee", "leave", "policy", "policies", "remote", "sick", "headcount", "staff", "profile"]):
            if any(w in q for w in ["all policies", "list policies", "all hr policies", "corporate policies", "company policies"]):
                op = "hr.policies"
                params = {}

            elif any(w in q for w in ["policy", "remote", "sick", "annual"]):
                op = "hr.policy"
                policy_title = "Remote Work" if "remote" in q else ("Sick Leave" if "sick" in q else "Annual Leave")
                params = {"title": policy_title}
            elif any(w in q for w in ["emp001", "emp002", "emp003", "profile", "employee details", "details for", "aarav", "priya"]):
                op = "hr.employee"
                emp_id = "EMP002" if "emp002" in q or "priya" in q else "EMP001"
                params = {"employee_id": emp_id}
            else:
                op = "hr.summary"
                params = {}

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
