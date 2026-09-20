"""
Intent taxonomy and server-side trusted execution plan mapping for Phase B4B.
Enforces that Microsoft Foundry selects the intent enum only, while the server
constructs the trusted ExecutionPlan without dynamic code execution or tool injection.
"""

import uuid
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from ..agents.types import ExecutionPlan, PlanStep


class NexusIntent(str, Enum):
    """
    Nexus business intents matching existing B3 specialist capabilities.
    Reuses existing vocabulary covering sales, inventory, HR, compound workflows, and unsupported.
    """
    # Compound multi-agent workflows
    COMPOUND_SALES_INVENTORY = "compound_sales_inventory"
    BUSINESS_OVERVIEW = "business_overview"

    # Sales intents
    SALES_TOTAL = "sales_total"
    SALES_MONTHLY = "sales_monthly"
    SALES_TOP_PRODUCTS = "sales_top_products"
    SALES_TREND = "sales_trend"

    # Inventory intents
    INVENTORY_LOW_STOCK = "inventory_low_stock"
    INVENTORY_PRODUCT_STOCK = "inventory_product_stock"
    INVENTORY_SUMMARY = "inventory_summary"

    # HR intents
    HR_POLICY = "hr_policy"
    HR_POLICIES = "hr_policies"
    HR_EMPLOYEE = "hr_employee"
    HR_SUMMARY = "hr_summary"

    # Out-of-domain / Unsupported
    UNSUPPORTED = "unsupported"


class FoundryRoutingDecision(BaseModel):
    """
    Structured output schema for Microsoft Foundry Manager Router.
    Contains ONLY the validated intent enum and selector parameters.
    Does NOT contain chain-of-thought, reasoning, or analysis fields.
    Does NOT contain factual business values (e.g. revenue, stock, counts).
    """
    intent: NexusIntent = Field(
        ...,
        description="The classified Nexus business intent."
    )
    month: Optional[int] = Field(
        default=None,
        description="Target month (1-12) for monthly sales requests."
    )
    year: Optional[int] = Field(
        default=None,
        description="Target 4-digit year for monthly sales requests."
    )
    limit: Optional[int] = Field(
        default=None,
        description="Number of top products requested (e.g., 3, 5)."
    )
    product_name: Optional[str] = Field(
        default=None,
        description="Name of specific product for stock lookup (e.g. Laptop Pro)."
    )
    product_id: Optional[str] = Field(
        default=None,
        description="ID of specific product if mentioned (e.g. P101)."
    )
    employee_id: Optional[str] = Field(
        default=None,
        description="Employee ID for employee profile lookup (e.g. EMP001)."
    )
    employee_name: Optional[str] = Field(
        default=None,
        description="Employee name for employee profile lookup (e.g. Aarav Sharma)."
    )
    policy_name: Optional[str] = Field(
        default=None,
        description="Title or topic of specific HR policy (e.g. Annual Leave, Remote Work, Sick Leave)."
    )



def build_execution_plan(
    intent: NexusIntent,
    query: str,
    decision: Optional[FoundryRoutingDecision] = None,
    policy_name: Optional[str] = None
) -> ExecutionPlan:
    """
    Constructs a deterministic, trusted ExecutionPlan from a validated NexusIntent.
    SERVER-SIDE AUTHORITY: The model selects the intent; the server selects the actions.
    No tool names, arguments, or Python code from model text are dynamically executed.
    """
    plan_id = f"plan_{uuid.uuid4().hex[:8]}"

    # Extract clean selector parameters if decision is provided
    month = getattr(decision, "month", None) or 9
    year = getattr(decision, "year", None) or 2026
    limit = getattr(decision, "limit", None) or 3
    p_name = getattr(decision, "product_name", None)
    p_id = getattr(decision, "product_id", None)
    emp_id = getattr(decision, "employee_id", None)
    emp_name = getattr(decision, "employee_name", None)
    p_policy = getattr(decision, "policy_name", None) or policy_name

    # 1. Compound: Sales + Inventory
    if intent == NexusIntent.COMPOUND_SALES_INVENTORY:
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
                    parameters={"limit": limit, "month": month, "year": year},
                    description="Retrieve top selling products"
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
    if intent == NexusIntent.BUSINESS_OVERVIEW:
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
                    parameters={"month": month, "year": year},
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

    # 3. Sales Intents
    if intent == NexusIntent.SALES_TOTAL:
        return ExecutionPlan(
            plan_id=plan_id,
            intent="sales",
            query=query,
            agents=["sales"],
            steps=[
                PlanStep(
                    step=1,
                    agent="sales",
                    operation="sales.total",
                    parameters={"month": month, "year": year},
                    description="Execute sales total revenue operation"
                )
            ]
        )

    if intent == NexusIntent.SALES_MONTHLY:
        return ExecutionPlan(
            plan_id=plan_id,
            intent="sales",
            query=query,
            agents=["sales"],
            steps=[
                PlanStep(
                    step=1,
                    agent="sales",
                    operation="sales.monthly",
                    parameters={"month": month, "year": year},
                    description="Execute sales monthly performance operation"
                )
            ]
        )

    if intent == NexusIntent.SALES_TOP_PRODUCTS:
        return ExecutionPlan(
            plan_id=plan_id,
            intent="sales",
            query=query,
            agents=["sales"],
            steps=[
                PlanStep(
                    step=1,
                    agent="sales",
                    operation="sales.top_products",
                    parameters={"limit": limit, "month": month, "year": year},
                    description="Execute sales top products operation"
                )
            ]
        )

    if intent == NexusIntent.SALES_TREND:
        return ExecutionPlan(
            plan_id=plan_id,
            intent="sales",
            query=query,
            agents=["sales"],
            steps=[
                PlanStep(
                    step=1,
                    agent="sales",
                    operation="sales.trend",
                    parameters={},
                    description="Execute sales trend operation"
                )
            ]
        )

    # 4. Inventory Intents
    if intent == NexusIntent.INVENTORY_LOW_STOCK:
        return ExecutionPlan(
            plan_id=plan_id,
            intent="inventory",
            query=query,
            agents=["inventory"],
            steps=[
                PlanStep(
                    step=1,
                    agent="inventory",
                    operation="inventory.low_stock",
                    parameters={},
                    description="Execute inventory low stock operation"
                )
            ]
        )

    if intent == NexusIntent.INVENTORY_PRODUCT_STOCK:
        inv_params = {}
        if p_id:
            inv_params["product_id"] = p_id
        if p_name:
            inv_params["product_name"] = p_name
        return ExecutionPlan(
            plan_id=plan_id,
            intent="inventory",
            query=query,
            agents=["inventory"],
            steps=[
                PlanStep(
                    step=1,
                    agent="inventory",
                    operation="inventory.product_stock",
                    parameters=inv_params,
                    description="Execute inventory product stock lookup"
                )
            ]
        )

    if intent == NexusIntent.INVENTORY_SUMMARY:
        return ExecutionPlan(
            plan_id=plan_id,
            intent="inventory",
            query=query,
            agents=["inventory"],
            steps=[
                PlanStep(
                    step=1,
                    agent="inventory",
                    operation="inventory.summary",
                    parameters={},
                    description="Execute inventory summary operation"
                )
            ]
        )

    # 5. HR Intents
    if intent == NexusIntent.HR_POLICY:
        # Resolve policy title to known company policies safely
        title = "Annual Leave"
        check_str = f"{p_policy or ''} {query}".lower()
        if "remote" in check_str or "wfh" in check_str or "home" in check_str:
            title = "Remote Work"
        elif "sick" in check_str or "medical" in check_str:
            title = "Sick Leave"
        elif "annual" in check_str or "vacation" in check_str or "holiday" in check_str:
            title = "Annual Leave"

        return ExecutionPlan(
            plan_id=plan_id,
            intent="hr",
            query=query,
            agents=["hr"],
            steps=[
                PlanStep(
                    step=1,
                    agent="hr",
                    operation="hr.policy",
                    parameters={"title": title},
                    description="Execute HR policy lookup operation"
                )
            ]
        )

    if intent == NexusIntent.HR_POLICIES:
        return ExecutionPlan(
            plan_id=plan_id,
            intent="hr",
            query=query,
            agents=["hr"],
            steps=[
                PlanStep(
                    step=1,
                    agent="hr",
                    operation="hr.policies",
                    parameters={},
                    description="Execute HR all policies lookup operation"
                )
            ]
        )

    if intent == NexusIntent.HR_EMPLOYEE:
        hr_emp_params = {}
        if emp_id:
            hr_emp_params["employee_id"] = emp_id
        if emp_name:
            hr_emp_params["employee_name"] = emp_name
        return ExecutionPlan(
            plan_id=plan_id,
            intent="hr",
            query=query,
            agents=["hr"],
            steps=[
                PlanStep(
                    step=1,
                    agent="hr",
                    operation="hr.employee",
                    parameters=hr_emp_params,
                    description="Execute HR employee profile lookup operation"
                )
            ]
        )

    if intent == NexusIntent.HR_SUMMARY:
        return ExecutionPlan(
            plan_id=plan_id,
            intent="hr",
            query=query,
            agents=["hr"],
            steps=[
                PlanStep(
                    step=1,
                    agent="hr",
                    operation="hr.summary",
                    parameters={},
                    description="Execute HR workforce summary operation"
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

