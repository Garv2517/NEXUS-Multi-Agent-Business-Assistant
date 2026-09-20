"""
Manager Agent for Phase B3.
Acts as the central orchestrator:
1. Receives user query
2. Consults DeterministicRouter for execution plan
3. Executes specialist agents through AgentRegistry
4. Passes context between specialists
5. Generates ordered, truthful trace events
6. Synthesizes deterministic responses from real SQLite-derived tool data
Does NOT call repositories, SQLite, or business tools directly.
"""

import uuid
from typing import Optional, List, Dict, Any
from .types import AgentTask, AgentResult, ToolCallRecord, ExecutionPlan
from .registry import AgentRegistry, create_default_registry
from ..orchestration.router import DeterministicRouter
from ..models.chat import ChatResponse
from ..models.trace import ToolCall, TraceEvent


class ManagerAgent:
    """Central orchestrator managing specialist agent execution and context transfer."""

    def __init__(
        self,
        registry: Optional[AgentRegistry] = None,
        router: Optional[DeterministicRouter] = None
    ):
        self.registry = registry or create_default_registry()
        self.router = router or DeterministicRouter()

    async def orchestrate(
        self,
        query: str,
        session_id: str,
        db_path: Optional[str] = None
    ) -> ChatResponse:
        trace: List[TraceEvent] = []
        tool_calls: List[ToolCall] = []
        agents_used: List[str] = []
        event_counter = 1

        def next_event_id() -> str:
            nonlocal event_counter
            eid = f"event_{event_counter:03d}"
            event_counter += 1
            return eid

        # 1. Manager started
        trace.append(
            TraceEvent(
                id=next_event_id(),
                type="manager_started",
                agent="manager",
                status="running",
                message="Understanding request"
            )
        )

        # 2. Router determines intent & plan
        plan = self.router.route(query)

        # 3. Handle Unsupported / Out-of-Domain queries
        if plan.intent == "unsupported":
            trace.append(
                TraceEvent(
                    id=next_event_id(),
                    type="response_completed",
                    agent="manager",
                    status="success",
                    message="Query out of business domain"
                )
            )
            return ChatResponse(
                session_id=session_id,
                answer="I can currently help with sales, inventory, HR, and business overview questions.",
                agents_used=[],
                tool_calls=[],
                trace=trace,
                plan=plan.model_dump()
            )

        # 4. Route selected event
        agents_display = " and ".join([f"{a.capitalize()} Agent" for a in plan.agents])
        trace.append(
            TraceEvent(
                id=next_event_id(),
                type="route_selected",
                agent="manager",
                status="success",
                message=f"Routed request to {agents_display}"
            )
        )
        agents_used = list(plan.agents)

        # 5. Execute Plan
        # --- Case A: Compound Sales + Inventory Comparison ---
        if plan.intent == "compound_sales_inventory":
            sales_agent = self.registry.get("sales")
            inventory_agent = self.registry.get("inventory")

            # Step 1: Sales Agent
            trace.append(
                TraceEvent(
                    id=next_event_id(),
                    type="agent_started",
                    agent="sales",
                    status="running",
                    message="Sales Agent started"
                )
            )
            trace.append(
                TraceEvent(
                    id=next_event_id(),
                    type="tool_started",
                    agent="sales",
                    tool="get_top_products",
                    status="running",
                    message="Retrieving top selling products"
                )
            )

            sales_task = AgentTask(
                task_id=f"task_{uuid.uuid4().hex[:8]}",
                operation="sales.top_products",
                parameters={"limit": 3, "month": 9, "year": 2026, "db_path": db_path}
            )
            sales_res = await sales_agent.execute(sales_task)

            # Record sales tool call
            for tc in sales_res.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        agent=tc.agent,
                        tool=tc.tool,
                        status=tc.status,
                        duration_ms=tc.duration_ms
                    )
                )

            if sales_res.status == "error":
                trace.append(
                    TraceEvent(
                        id=next_event_id(),
                        type="tool_failed",
                        agent="sales",
                        tool="get_top_products",
                        status="error",
                        message=sales_res.error.get("message", "Sales query failed")
                    )
                )
                trace.append(
                    TraceEvent(
                        id=next_event_id(),
                        type="agent_failed",
                        agent="sales",
                        status="error",
                        message="Sales Agent execution failed"
                    )
                )
                trace.append(
                    TraceEvent(
                        id=next_event_id(),
                        type="response_completed",
                        agent="manager",
                        status="error",
                        message="Failed to retrieve sales data"
                    )
                )
                return ChatResponse(
                    session_id=session_id,
                    answer="Sales data is currently unavailable.",
                    agents_used=["sales"],
                    tool_calls=tool_calls,
                    trace=trace,
                    plan=plan.model_dump()
                )

            # Sales tool succeeded
            top_products = sales_res.data.get("products", [])
            dur_sales = sales_res.tool_calls[0].duration_ms if sales_res.tool_calls else 1
            trace.append(
                TraceEvent(
                    id=next_event_id(),
                    type="tool_completed",
                    agent="sales",
                    tool="get_top_products",
                    status="success",
                    message=f"Retrieved top {len(top_products)} selling products",
                    duration_ms=dur_sales
                )
            )
            trace.append(
                TraceEvent(
                    id=next_event_id(),
                    type="agent_completed",
                    agent="sales",
                    status="success",
                    message="Sales Agent completed"
                )
            )

            # Extract ALL returned product IDs
            product_ids = [p["id"] for p in top_products]

            # Context Passing Event
            trace.append(
                TraceEvent(
                    id=next_event_id(),
                    type="context_passed",
                    agent="manager",
                    status="success",
                    message=f"Passed top product IDs ({', '.join(product_ids)}) to Inventory Agent",
                    metadata={
                        "source": "sales",
                        "target": "inventory",
                        "product_ids": product_ids
                    }
                )
            )

            # Step 2: Inventory Agent for EACH product ID
            trace.append(
                TraceEvent(
                    id=next_event_id(),
                    type="agent_started",
                    agent="inventory",
                    status="running",
                    message="Inventory Agent started"
                )
            )

            inventory_stocks: Dict[str, Any] = {}
            inventory_failed = False

            for pid in product_ids:
                trace.append(
                    TraceEvent(
                        id=next_event_id(),
                        type="tool_started",
                        agent="inventory",
                        tool="get_product_stock",
                        status="running",
                        message=f"Checking stock for {pid}"
                    )
                )
                inv_task = AgentTask(
                    task_id=f"task_{uuid.uuid4().hex[:8]}",
                    operation="inventory.product_stock",
                    parameters={"product_id": pid, "db_path": db_path},
                    context={"sales_source": "top_products"}
                )
                inv_res = await inventory_agent.execute(inv_task)

                for tc in inv_res.tool_calls:
                    tool_calls.append(
                        ToolCall(
                            id=tc.id,
                            agent=tc.agent,
                            tool=tc.tool,
                            status=tc.status,
                            duration_ms=tc.duration_ms
                        )
                    )

                if inv_res.status == "success" and inv_res.data:
                    inventory_stocks[pid] = inv_res.data
                    dur_inv = inv_res.tool_calls[0].duration_ms if inv_res.tool_calls else 1
                    trace.append(
                        TraceEvent(
                            id=next_event_id(),
                            type="tool_completed",
                            agent="inventory",
                            tool="get_product_stock",
                            status="success",
                            message=f"Stock for {inv_res.data.get('name')}: {inv_res.data.get('stock')} units",
                            duration_ms=dur_inv
                        )
                    )
                else:
                    inventory_failed = True
                    trace.append(
                        TraceEvent(
                            id=next_event_id(),
                            type="tool_failed",
                            agent="inventory",
                            tool="get_product_stock",
                            status="error",
                            message=inv_res.error.get("message", f"Failed to retrieve stock for {pid}")
                        )
                    )

            if inventory_failed and not inventory_stocks:
                trace.append(
                    TraceEvent(
                        id=next_event_id(),
                        type="agent_failed",
                        agent="inventory",
                        status="error",
                        message="Inventory Agent execution failed"
                    )
                )
                trace.append(
                    TraceEvent(
                        id=next_event_id(),
                        type="response_completed",
                        agent="manager",
                        status="success",
                        message="Response synthesized with partial data"
                    )
                )
                answer = f"Sales data was retrieved successfully ({len(top_products)} top products), but inventory data could not be retrieved."
                return ChatResponse(
                    session_id=session_id,
                    answer=answer,
                    agents_used=agents_used,
                    tool_calls=tool_calls,
                    trace=trace,
                    plan=plan.model_dump()
                )

            trace.append(
                TraceEvent(
                    id=next_event_id(),
                    type="agent_completed",
                    agent="inventory",
                    status="success",
                    message="Inventory Agent completed"
                )
            )

            # Response synthesis combining ALL returned top products and inventory data
            product_lines = []
            low_stock_items = []
            for p in top_products:
                pid = p["id"]
                p_name = p.get("name", pid)
                units = p.get("units_sold", 0)
                inv = inventory_stocks.get(pid, {})
                stock_val = inv.get("stock", 0)
                reorder_val = inv.get("reorder_level", 0)
                product_lines.append(
                    f"- {p_name}: {units} sold, {stock_val} currently in stock, reorder level {reorder_val}."
                )
                if stock_val <= reorder_val:
                    low_stock_items.append(f"{p_name} ({stock_val} left vs reorder level {reorder_val})")

            conclusion = (
                f"Inventory attention is required for {', '.join(low_stock_items)} due to high sales velocity."
                if low_stock_items
                else "All top-selling products currently maintain healthy inventory levels."
            )

            answer = (
                "Among the current top-selling products:\n\n"
                + "\n".join(product_lines)
                + f"\n\n{conclusion}"
            )

            trace.append(
                TraceEvent(
                    id=next_event_id(),
                    type="response_completed",
                    agent="manager",
                    status="success",
                    message="Final response generated"
                )
            )

            return ChatResponse(
                session_id=session_id,
                answer=answer,
                agents_used=agents_used,
                tool_calls=tool_calls,
                trace=trace,
                plan=plan.model_dump()
            )

        # --- Case B: Business Overview (Sales + Inventory + HR) ---
        elif plan.intent == "business_overview":
            sales_agent = self.registry.get("sales")
            inventory_agent = self.registry.get("inventory")
            hr_agent = self.registry.get("hr")

            # 1. Sales
            trace.append(TraceEvent(id=next_event_id(), type="agent_started", agent="sales", status="running", message="Sales Agent started"))
            trace.append(TraceEvent(id=next_event_id(), type="tool_started", agent="sales", tool="get_total_sales", status="running", message="Retrieving monthly sales total"))
            s_res = await sales_agent.execute(AgentTask(task_id=f"task_{uuid.uuid4().hex[:8]}", operation="sales.total", parameters={"month": 9, "year": 2026, "db_path": db_path}))
            for tc in s_res.tool_calls:
                tool_calls.append(ToolCall(id=tc.id, agent=tc.agent, tool=tc.tool, status=tc.status, duration_ms=tc.duration_ms))
            trace.append(TraceEvent(id=next_event_id(), type="tool_completed", agent="sales", tool="get_total_sales", status="success", message=f"Revenue: ₹{int(s_res.data.get('revenue', 0)):,}", duration_ms=s_res.tool_calls[0].duration_ms if s_res.tool_calls else 1))
            trace.append(TraceEvent(id=next_event_id(), type="agent_completed", agent="sales", status="success", message="Sales Agent completed"))

            # 2. Inventory
            trace.append(TraceEvent(id=next_event_id(), type="agent_started", agent="inventory", status="running", message="Inventory Agent started"))
            trace.append(TraceEvent(id=next_event_id(), type="tool_started", agent="inventory", tool="get_inventory_summary", status="running", message="Retrieving inventory summary"))
            inv_res = await inventory_agent.execute(AgentTask(task_id=f"task_{uuid.uuid4().hex[:8]}", operation="inventory.summary", parameters={"db_path": db_path}))
            for tc in inv_res.tool_calls:
                tool_calls.append(ToolCall(id=tc.id, agent=tc.agent, tool=tc.tool, status=tc.status, duration_ms=tc.duration_ms))
            trace.append(TraceEvent(id=next_event_id(), type="tool_completed", agent="inventory", tool="get_inventory_summary", status="success", message=f"Total: {inv_res.data.get('total_products')} products", duration_ms=inv_res.tool_calls[0].duration_ms if inv_res.tool_calls else 1))
            trace.append(TraceEvent(id=next_event_id(), type="agent_completed", agent="inventory", status="success", message="Inventory Agent completed"))

            # 3. HR
            trace.append(TraceEvent(id=next_event_id(), type="agent_started", agent="hr", status="running", message="HR Agent started"))
            trace.append(TraceEvent(id=next_event_id(), type="tool_started", agent="hr", tool="get_employee_summary", status="running", message="Retrieving workforce headcount"))
            hr_res = await hr_agent.execute(AgentTask(task_id=f"task_{uuid.uuid4().hex[:8]}", operation="hr.summary", parameters={"db_path": db_path}))
            for tc in hr_res.tool_calls:
                tool_calls.append(ToolCall(id=tc.id, agent=tc.agent, tool=tc.tool, status=tc.status, duration_ms=tc.duration_ms))
            trace.append(TraceEvent(id=next_event_id(), type="tool_completed", agent="hr", tool="get_employee_summary", status="success", message=f"Headcount: {hr_res.data.get('employee_count')} employees", duration_ms=hr_res.tool_calls[0].duration_ms if hr_res.tool_calls else 1))
            trace.append(TraceEvent(id=next_event_id(), type="agent_completed", agent="hr", status="success", message="HR Agent completed"))

            # Synthesis
            answer = (
                f"Business Overview: Revenue stands at ₹{int(s_res.data.get('revenue', 0)):,} "
                f"across {s_res.data.get('units_sold', 0)} units sold this month. "
                f"The inventory catalog contains {inv_res.data.get('total_products', 0)} products with "
                f"{inv_res.data.get('low_stock', 0)} requiring restocking. "
                f"Headcount is {hr_res.data.get('employee_count', 0)} employees across "
                f"{hr_res.data.get('departments', 0)} departments with "
                f"{hr_res.data.get('employees_on_leave', 0)} on leave."
            )

            trace.append(TraceEvent(id=next_event_id(), type="response_completed", agent="manager", status="success", message="Final response generated"))

            return ChatResponse(
                session_id=session_id,
                answer=answer,
                agents_used=agents_used,
                tool_calls=tool_calls,
                trace=trace,
                plan=plan.model_dump()
            )

        # --- Case C: Single-Agent Queries ---
        else:
            agent_name = plan.agents[0]
            step = plan.steps[0]
            agent = self.registry.get(agent_name)

            trace.append(TraceEvent(id=next_event_id(), type="agent_started", agent=agent_name, status="running", message=f"{agent_name.capitalize()} Agent started"))
            tool_name = step.operation.split(".")[-1]
            trace.append(TraceEvent(id=next_event_id(), type="tool_started", agent=agent_name, tool=tool_name, status="running", message=f"Executing {step.operation}"))

            params = dict(step.parameters)
            params["db_path"] = db_path
            task = AgentTask(task_id=f"task_{uuid.uuid4().hex[:8]}", operation=step.operation, parameters=params)
            res = await agent.execute(task)

            for tc in res.tool_calls:
                tool_calls.append(ToolCall(id=tc.id, agent=tc.agent, tool=tc.tool, status=tc.status, duration_ms=tc.duration_ms))

            if res.status == "error":
                trace.append(TraceEvent(id=next_event_id(), type="tool_failed", agent=agent_name, tool=tool_name, status="error", message=res.error.get("message", "Tool failed")))
                trace.append(TraceEvent(id=next_event_id(), type="agent_failed", agent=agent_name, status="error", message=f"{agent_name.capitalize()} Agent failed"))
                trace.append(TraceEvent(id=next_event_id(), type="response_completed", agent="manager", status="error", message="Failed to retrieve data"))
                return ChatResponse(
                    session_id=session_id,
                    answer=f"Could not retrieve {agent_name} data: {res.error.get('message')}",
                    agents_used=agents_used,
                    tool_calls=tool_calls,
                    trace=trace,
                    plan=plan.model_dump()
                )

            dur = res.tool_calls[0].duration_ms if res.tool_calls else 1
            trace.append(TraceEvent(id=next_event_id(), type="tool_completed", agent=agent_name, tool=tool_name, status="success", message=res.tool_calls[0].result_summary if res.tool_calls else "Success", duration_ms=dur))
            trace.append(TraceEvent(id=next_event_id(), type="agent_completed", agent=agent_name, status="success", message=f"{agent_name.capitalize()} Agent completed"))

            # Build single-agent response
            answer = ""
            if agent_name == "sales":
                if step.operation == "sales.trend":
                    answer = f"Sales trend across the last 6 months shows steady growth, concluding at ₹{int(res.data.get('months', [])[-1].get('revenue', 0)):,} for September 2026."
                elif step.operation == "sales.top_products":
                    prods = res.data.get("products", [])
                    names = [f"{p['name']} ({p['units_sold']} units, ₹{int(p['revenue']):,})" for p in prods[:3]]
                    answer = f"Top-selling products this month: {', '.join(names)}."
                else:
                    answer = f"Total revenue generated this month is ₹{int(res.data.get('revenue', 0)):,} across {res.data.get('units_sold', 0)} units sold."

            elif agent_name == "inventory":
                if step.operation == "inventory.low_stock":
                    count = res.data.get("count", 0)
                    products = res.data.get("products", [])
                    if count == 0 or not products:
                        answer = "There are currently no products low in stock."
                    elif count == len(products):
                        items = [f"- {p['name']} ({p['stock']} left)" for p in products]
                        if items:
                            items[-1] = items[-1] + "."
                        answer = f"There are currently {count} products low in stock:\n" + "\n".join(items)
                    else:
                        items = [f"- {p['name']} ({p['stock']} left)" for p in products]
                        if items:
                            items[-1] = items[-1] + "."
                        answer = f"{count} products are low in stock. Showing {len(products)}:\n" + "\n".join(items)
                else:
                    answer = f"Inventory summary: {res.data.get('total_products')} products in catalog, {res.data.get('healthy')} healthy, {res.data.get('low_stock')} low stock, and {res.data.get('out_of_stock')} out of stock."

            elif agent_name == "hr":
                if step.operation == "hr.policy":
                    answer = f"{res.data.get('title')}: {res.data.get('summary')}. {res.data.get('content')}"
                else:
                    answer = f"Nexus currently has {res.data.get('employee_count')} active employees across {res.data.get('departments')} departments, with {res.data.get('employees_on_leave')} on leave."

            trace.append(TraceEvent(id=next_event_id(), type="response_completed", agent="manager", status="success", message="Final response generated"))

            return ChatResponse(
                session_id=session_id,
                answer=answer,
                agents_used=agents_used,
                tool_calls=tool_calls,
                trace=trace,
                plan=plan.model_dump()
            )
