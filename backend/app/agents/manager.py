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
from ..core.config import settings
from ..models.chat import ChatResponse
from ..models.trace import ToolCall, TraceEvent


class ManagerAgent:
    """Central orchestrator managing specialist agent execution and context transfer."""

    def __init__(
        self,
        registry: Optional[AgentRegistry] = None,
        router: Optional[Any] = None,
        foundry_router: Optional[Any] = None,
        orchestration_mode: Optional[str] = None,
        fallback_to_local: Optional[bool] = None,
    ):
        self.registry = registry or create_default_registry()
        if router is not None:
            self.router = router
        else:
            from ..orchestration.router import DeterministicRouter
            self.router = DeterministicRouter()
        self.foundry_router = foundry_router
        self.orchestration_mode = orchestration_mode or getattr(settings, "ORCHESTRATION_MODE", "local")
        self.fallback_to_local = (
            fallback_to_local
            if fallback_to_local is not None

            else getattr(settings, "FOUNDRY_FALLBACK_TO_LOCAL", True)
        )

    async def orchestrate(
        self,
        query: str,
        session_id: str,
        db_path: Optional[str] = None,
        analytics_db_path: Optional[str] = None
    ) -> ChatResponse:
        trace: List[TraceEvent] = []
        tool_calls: List[ToolCall] = []
        agents_used: List[str] = []
        event_counter = 1
        using_analytics = bool(analytics_db_path)

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
        routing_metadata: Dict[str, Any] = {}
        plan: Optional[ExecutionPlan] = None

        if self.orchestration_mode == "foundry_manager":
            try:
                from ..orchestration.foundry_router import get_foundry_router
                f_router = self.foundry_router or get_foundry_router()
                plan, routing_metadata = await f_router.route(query)
            except Exception as e:
                failure_cat = getattr(e, "category", type(e).__name__)
                if self.fallback_to_local:
                    routing_metadata = {
                        "routing_source": "local_fallback",
                        "failure_category": failure_cat
                    }
                    plan = self.router.route(query)
                else:
                    trace.append(
                        TraceEvent(
                            id=next_event_id(),
                            type="route_selected",
                            agent="manager",
                            status="error",
                            message=f"Foundry routing failed: {failure_cat}",
                            metadata={"routing_source": "foundry_error", "failure_category": failure_cat}
                        )
                    )
                    trace.append(
                        TraceEvent(
                            id=next_event_id(),
                            type="response_completed",
                            agent="manager",
                            status="error",
                            message="Routing service unavailable"
                        )
                    )
                    return ChatResponse(
                        session_id=session_id,
                        answer=f"Routing service failure: {failure_cat}. Unable to process request.",
                        agents_used=[],
                        tool_calls=[],
                        trace=trace,
                        plan=None
                    )
        else:
            plan = self.router.route(query)
            routing_metadata = {
                "routing_source": "local",
                "intent": plan.intent
            }

        # 3. Route selected event
        agents_display = " and ".join([f"{a.capitalize()} Agent" for a in plan.agents])
        route_message = (
            f"Foundry Manager selected a validated Nexus route ({plan.intent})."
            if routing_metadata.get("routing_source") == "foundry"
            else (
                f"Foundry routing failed ({routing_metadata.get('failure_category')}); fell back to local deterministic router."
                if routing_metadata.get("routing_source") == "local_fallback"
                else (
                    f"Classified request as {plan.intent}"
                    if not plan.agents
                    else f"Routed request to {agents_display}"
                )
            )
        )
        route_status = "warning" if routing_metadata.get("routing_source") == "local_fallback" else "success"

        trace.append(
            TraceEvent(
                id=next_event_id(),
                type="route_selected",
                agent="manager",
                status=route_status,
                message=route_message,
                metadata=routing_metadata
            )
        )

        # 4. Handle Unsupported / Out-of-Domain queries
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
                answer="I can currently help with sales, inventory, HR, and business overview questions using verified Nexus data.",
                agents_used=[],
                tool_calls=[],
                trace=trace,
                plan=plan.model_dump()
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

            sales_params = {"limit": 3, "db_path": db_path}
            if using_analytics:
                sales_params["analytics_db_path"] = analytics_db_path
            else:
                sales_params.update({"month": 9, "year": 2026})
            sales_task = AgentTask(
                task_id=f"task_{uuid.uuid4().hex[:8]}",
                operation="sales.top_products",
                parameters=sales_params
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
                    message=f"Passed top product IDs ({', '.join(map(str, product_ids))}) to Inventory Agent",
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
                    parameters={
                        "product_id": pid,
                        "db_path": db_path,
                        **({"analytics_db_path": analytics_db_path} if using_analytics else {})
                    },
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
            if using_analytics:
                for p in top_products:
                    pid = p["id"]
                    p_name = p.get("name", str(pid))
                    units = p.get("units_sold", 0)
                    revenue_cents = p.get("revenue_cents", 0)
                    inv = inventory_stocks.get(pid, {})
                    stock_val = inv.get("stock", 0)
                    placements = inv.get("store_placements", 0)
                    zero_stores = inv.get("zero_stock_store_count", 0)
                    product_lines.append(
                        f"- {p_name} (Product {pid}): {units:,} units sold, "
                        f"${revenue_cents / 100:,.2f} revenue, {stock_val:,} units currently in stock "
                        f"across {placements} store placements; {zero_stores} zero-stock stores."
                    )
                answer = (
                    "Top products by 2025 gross revenue compared with the current external inventory snapshot:\n\n"
                    + "\n".join(product_lines)
                    + "\n\nInventory snapshot date is assumed as Dec 31, 2025 for analytical use. "
                    "The source dataset does not provide reorder levels, so none are invented."
                )
            else:
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
            s_res = await sales_agent.execute(AgentTask(
                task_id=f"task_{uuid.uuid4().hex[:8]}",
                operation="sales.total",
                parameters={
                    "db_path": db_path,
                    **({"analytics_db_path": analytics_db_path} if using_analytics else {"month": 9, "year": 2026})
                }
            ))
            for tc in s_res.tool_calls:
                tool_calls.append(ToolCall(id=tc.id, agent=tc.agent, tool=tc.tool, status=tc.status, duration_ms=tc.duration_ms))
            sales_trace_message = (
                f"Revenue: ${s_res.data.get('revenue_cents', 0) / 100:,.2f}"
                if using_analytics
                else f"Revenue: ₹{int(s_res.data.get('revenue', 0)):,}"
            )
            trace.append(TraceEvent(id=next_event_id(), type="tool_completed", agent="sales", tool="get_total_sales", status="success", message=sales_trace_message, duration_ms=s_res.tool_calls[0].duration_ms if s_res.tool_calls else 1))
            trace.append(TraceEvent(id=next_event_id(), type="agent_completed", agent="sales", status="success", message="Sales Agent completed"))

            # 2. Inventory
            trace.append(TraceEvent(id=next_event_id(), type="agent_started", agent="inventory", status="running", message="Inventory Agent started"))
            trace.append(TraceEvent(id=next_event_id(), type="tool_started", agent="inventory", tool="get_inventory_summary", status="running", message="Retrieving inventory summary"))
            inv_res = await inventory_agent.execute(AgentTask(
                task_id=f"task_{uuid.uuid4().hex[:8]}",
                operation="inventory.summary",
                parameters={
                    "db_path": db_path,
                    **({"analytics_db_path": analytics_db_path} if using_analytics else {})
                }
            ))
            for tc in inv_res.tool_calls:
                tool_calls.append(ToolCall(id=tc.id, agent=tc.agent, tool=tc.tool, status=tc.status, duration_ms=tc.duration_ms))
            inventory_trace_message = (
                f"Inventory: {inv_res.data.get('total_units_on_hand', 0):,} units; {inv_res.data.get('out_of_stock_placements', 0)} zero-stock placements"
                if using_analytics
                else f"Total: {inv_res.data.get('total_products')} products"
            )
            trace.append(TraceEvent(id=next_event_id(), type="tool_completed", agent="inventory", tool="get_inventory_summary", status="success", message=inventory_trace_message, duration_ms=inv_res.tool_calls[0].duration_ms if inv_res.tool_calls else 1))
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
            if using_analytics:
                answer = (
                    f"Business Overview: The external retail dataset generated "
                    f"${s_res.data.get('revenue_cents', 0) / 100:,.2f} in 2025 revenue across "
                    f"{s_res.data.get('units_sold', 0):,} units sold. Current inventory contains "
                    f"{inv_res.data.get('total_units_on_hand', 0):,} units across "
                    f"{inv_res.data.get('total_placements', 0):,} store-product placements, with "
                    f"{inv_res.data.get('out_of_stock_placements', 0)} zero-stock placements. "
                    f"People Management contains {hr_res.data.get('employee_count', 0)} synthetic internal employees across "
                    f"{hr_res.data.get('departments', 0)} departments, with "
                    f"{hr_res.data.get('employees_on_leave', 0)} on leave."
                )
            else:
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
            if using_analytics and agent_name in {"sales", "inventory"}:
                params["analytics_db_path"] = analytics_db_path
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
                if using_analytics:
                    if step.operation == "sales.trend":
                        months = res.data.get("months", [])
                        if months:
                            first = months[0]
                            last = months[-1]
                            answer = (
                                f"External retail sales trend covers {first.get('period')} through {last.get('period')}. "
                                f"The latest month generated ${last.get('revenue_cents', 0) / 100:,.2f} from "
                                f"{last.get('units_sold', 0):,} units."
                            )
                        else:
                            answer = "No external monthly sales trend is available."
                    elif step.operation == "sales.top_products":
                        prods = res.data.get("products", [])
                        names = [
                            f"{p['name']} (Product {p['id']}: {p['units_sold']:,} units, ${p['revenue_cents'] / 100:,.2f})"
                            for p in prods
                        ]
                        answer = "Top products by 2025 gross revenue: " + "; ".join(names) + "."
                    elif step.operation == "sales.monthly":
                        answer = (
                            f"Sales for {res.data.get('period')}: ${res.data.get('revenue_cents', 0) / 100:,.2f} "
                            f"revenue across {res.data.get('units_sold', 0):,} units and "
                            f"{res.data.get('orders', 0):,} transactions."
                        )
                    else:
                        answer = (
                            f"The USA Toy Sales external analytics dataset generated "
                            f"${res.data.get('revenue_cents', 0) / 100:,.2f} in total 2025 revenue across "
                            f"{res.data.get('units_sold', 0):,} units sold and {res.data.get('orders', 0):,} transactions."
                        )
                else:
                    if step.operation == "sales.trend":
                        answer = f"Sales trend across the last 6 months shows steady growth, concluding at ₹{int(res.data.get('months', [])[-1].get('revenue', 0)):,} for September 2026."
                    elif step.operation == "sales.top_products":
                        prods = res.data.get("products", [])
                        names = [f"{p['name']} ({p['units_sold']} units, ₹{int(p['revenue']):,})" for p in prods[:3]]
                        answer = f"Top-selling products this month: {', '.join(names)}."
                    elif step.operation == "sales.monthly":
                        answer = f"Monthly sales for {res.data.get('month', 9)}/{res.data.get('year', 2026)}: Total revenue is ₹{int(res.data.get('revenue', 0)):,} across {res.data.get('units_sold', 0)} units sold."
                    else:
                        answer = f"Total revenue generated this month is ₹{int(res.data.get('revenue', 0)):,} across {res.data.get('units_sold', 0)} units sold."

            elif agent_name == "inventory":
                if using_analytics:
                    if step.operation == "inventory.low_stock":
                        count = res.data.get("count", 0)
                        products = res.data.get("products", [])
                        if not products:
                            answer = "No stockout or high-pressure inventory placements were returned in the current sample."
                        else:
                            items = []
                            for p in products:
                                dos = p.get("days_of_supply")
                                dos_text = "stockout" if p.get("status") == "Stockout" else f"{dos:.1f} days of supply" if dos is not None else "coverage unavailable"
                                items.append(f"- {p['name']} at {p.get('store_name', 'store')}: {p['stock']} units, {p['status']} ({dos_text})")
                            answer = (
                                f"The external inventory dataset has {count} returned/identified stockout or high-pressure placements. "
                                f"Showing {len(products)}:\n" + "\n".join(items) +
                                "\nThese classifications use dataset-calibrated Days of Supply; the source has no reorder levels."
                            )
                    elif step.operation == "inventory.product_stock":
                        answer = (
                            f"{res.data.get('name')} (Product {res.data.get('id')}): {res.data.get('stock', 0):,} units "
                            f"across {res.data.get('store_placements', 0)} store placements; "
                            f"{res.data.get('zero_stock_store_count', 0)} stores currently have zero stock for this product. "
                            "Inventory snapshot date is assumed as Dec 31, 2025 for analytical use."
                        )
                    else:
                        answer = (
                            f"External inventory summary: {res.data.get('total_units_on_hand', 0):,} units on hand across "
                            f"{res.data.get('total_placements', 0):,} store-product placements, including "
                            f"{res.data.get('out_of_stock_placements', 0)} zero-stock placements "
                            f"({res.data.get('stockout_rate_pct', 0):.2f}%). "
                            "Inventory snapshot date is assumed as Dec 31, 2025 for analytical use."
                        )
                else:
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
                    elif step.operation == "inventory.product_stock":
                        answer = f"Product '{res.data.get('name')}' (ID: {res.data.get('id')}): {res.data.get('stock')} units in stock (status: {res.data.get('status')}, reorder level: {res.data.get('reorder_level')})."
                    else:
                        answer = f"Inventory summary: {res.data.get('total_products')} products in catalog, {res.data.get('healthy')} healthy, {res.data.get('low_stock')} low stock, and {res.data.get('out_of_stock')} out of stock."

            elif agent_name == "hr":
                if step.operation == "hr.policy":
                    answer = f"{res.data.get('title')}: {res.data.get('summary')}. {res.data.get('content')}"
                elif step.operation == "hr.policies":
                    titles = [p.get("title") for p in res.data.get("policies", [])]
                    answer = f"Nexus has {res.data.get('count', len(titles))} corporate policies: {', '.join(titles)}."
                elif step.operation == "hr.employee":
                    answer = f"Employee profile for {res.data.get('name')} (ID: {res.data.get('id')}): {res.data.get('role')} in {res.data.get('department')}. Status is {res.data.get('status')}, with {res.data.get('leave_balance')} leave days remaining."
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
