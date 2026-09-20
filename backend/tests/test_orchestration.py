"""
Tests for Phase B3 Deterministic Router and ManagerAgent.
Validates routing logic, execution plans, context passing, and multi-agent synthesis.
"""

import pytest
from app.orchestration.router import DeterministicRouter
from app.agents.manager import ManagerAgent
from app.agents.registry import create_default_registry
from app.agents.base import BaseAgent
from app.agents.types import AgentTask, AgentResult


def test_router_sales_query():
    plan = DeterministicRouter.route("How much revenue did we make?")
    assert plan.intent == "sales"
    assert plan.agents == ["sales"]
    assert len(plan.steps) == 1
    assert plan.steps[0].operation == "sales.total"


def test_router_inventory_query():
    plan = DeterministicRouter.route("Which products are low in stock?")
    assert plan.intent == "inventory"
    assert plan.agents == ["inventory"]
    assert len(plan.steps) == 1
    assert plan.steps[0].operation == "inventory.low_stock"


def test_router_hr_query():
    plan = DeterministicRouter.route("What is our annual leave policy?")
    assert plan.intent == "hr"
    assert plan.agents == ["hr"]
    assert len(plan.steps) == 1
    assert plan.steps[0].operation == "hr.policy"
    assert plan.steps[0].parameters.get("title") == "Annual Leave"


def test_router_compound_sales_inventory_query():
    plan = DeterministicRouter.route("Compare our top-selling products with current inventory.")
    assert plan.intent == "compound_sales_inventory"
    assert set(plan.agents) == {"sales", "inventory"}
    assert len(plan.steps) == 2
    assert plan.steps[0].agent == "sales"
    assert plan.steps[0].operation == "sales.top_products"
    assert plan.steps[1].agent == "inventory"
    assert plan.steps[1].depends_on == 1


def test_router_business_overview_query():
    plan = DeterministicRouter.route("Give me a business overview.")
    assert plan.intent == "business_overview"
    assert set(plan.agents) == {"sales", "inventory", "hr"}
    assert len(plan.steps) == 3


def test_router_unsupported_query():
    plan = DeterministicRouter.route("What's the weather?")
    assert plan.intent == "unsupported"
    assert plan.agents == []
    assert plan.steps == []


@pytest.mark.anyio
async def test_manager_single_agent_sales(test_db):
    manager = ManagerAgent()
    resp = await manager.orchestrate("How much revenue did we make?", session_id="test-session", db_path=test_db)
    assert resp.session_id == "test-session"
    assert resp.agents_used == ["sales"]
    assert len(resp.tool_calls) == 1
    assert resp.tool_calls[0].tool == "get_total_sales"
    assert "₹124,500" in resp.answer
    assert any(e.type == "response_completed" for e in resp.trace)


@pytest.mark.anyio
async def test_manager_compound_query_checks_all_returned_products(test_db):
    """
    Asserts that:
    1. Sales agent retrieves top products.
    2. Context passed event contains all returned product IDs.
    3. Inventory agent is executed for EACH returned product ID.
    4. Response contains SQLite values.
    """
    manager = ManagerAgent()
    resp = await manager.orchestrate(
        "Compare our top-selling products with current inventory.",
        session_id="test-compound",
        db_path=test_db
    )

    assert resp.agents_used == ["sales", "inventory"]

    # Tool calls should have 1 get_top_products + 3 get_product_stock calls
    tools = [tc.tool for tc in resp.tool_calls]
    assert "get_top_products" in tools
    assert tools.count("get_product_stock") == 3

    # Context transfer event verification
    context_events = [e for e in resp.trace if e.type == "context_passed"]
    assert len(context_events) == 1
    passed_ids = context_events[0].metadata["product_ids"]
    assert len(passed_ids) == 3
    assert set(passed_ids) == {"P101", "P102", "P103"}

    # Final response verification: asserts all 3 returned products appear with factual data
    assert "Laptop Pro: 27 sold, 4 currently in stock, reorder level 10" in resp.answer
    assert "Wireless Headset: 42 sold, 31 currently in stock, reorder level 12" in resp.answer
    assert "Mechanical Keyboard: 31 sold, 8 currently in stock, reorder level 10" in resp.answer
    assert "Inventory attention is required for Laptop Pro" in resp.answer


@pytest.mark.anyio
async def test_manager_business_overview_invokes_all_three_specialists(test_db):
    manager = ManagerAgent()
    resp = await manager.orchestrate("Give me a business overview.", session_id="test-overview", db_path=test_db)

    assert set(resp.agents_used) == {"sales", "inventory", "hr"}
    tool_names = [tc.tool for tc in resp.tool_calls]
    assert "get_total_sales" in tool_names
    assert "get_inventory_summary" in tool_names
    assert "get_employee_summary" in tool_names

    # Assert factual database values are present
    assert "124,500" in resp.answer
    assert "13 products" in resp.answer
    assert "16 employees" in resp.answer


@pytest.mark.anyio
async def test_manager_unsupported_query_invokes_zero_agents():
    manager = ManagerAgent()
    resp = await manager.orchestrate("What's the weather?", session_id="test-unsupported")

    assert resp.agents_used == []
    assert resp.tool_calls == []
    assert "help with sales, inventory, HR, and business overview" in resp.answer


@pytest.mark.anyio
async def test_manager_specialist_failure_isolation(test_db):
    """
    If Sales succeeds but Inventory fails, ManagerAgent should not crash
    and should return safe partial response with agent_failed in trace.
    """
    registry = create_default_registry()

    # Create a broken inventory agent simulating specialist error
    class FailingInventoryAgent(BaseAgent):
        name = "inventory"
        description = "Failing agent"
        async def execute(self, task: AgentTask) -> AgentResult:
            return AgentResult(
                task_id=task.task_id,
                agent=self.name,
                status="error",
                error={"code": "SERVICE_UNAVAILABLE", "message": "Warehouse node unreachable"}
            )

    registry.register("inventory", FailingInventoryAgent())
    manager = ManagerAgent(registry=registry)

    resp = await manager.orchestrate(
        "Compare our top-selling products with current inventory.",
        session_id="test-fail",
        db_path=test_db
    )

    # Handled gracefully without crash
    assert "inventory data could not be retrieved" in resp.answer
    trace_types = [e.type for e in resp.trace]
    assert "agent_failed" in trace_types
    assert any(e.agent == "inventory" and e.type == "agent_failed" for e in resp.trace)


@pytest.mark.anyio
async def test_manager_compound_query_activity_deduplication(test_db):
    """
    Proves that for the compound query (1 top_products + 3 product_stock),
    exactly 4 durable activity records are created in SQLite with zero duplicates from Manager.
    """
    from app.db.connection import get_db
    from app.db.repositories import get_activity_logs_db

    with get_db(test_db) as conn:
        before = len(get_activity_logs_db(conn))

    manager = ManagerAgent()
    resp = await manager.orchestrate(
        "Compare our top-selling products with current inventory.",
        session_id="test-dedup",
        db_path=test_db
    )

    with get_db(test_db) as conn:
        after = len(get_activity_logs_db(conn))

    # Exactly 4 durable records: 1 sales tool + 3 inventory tool calls
    assert after == before + 4
    assert len(resp.tool_calls) == 4


@pytest.mark.anyio
async def test_manager_low_stock_query_enumerates_every_tool_product(test_db):
    """
    Consistency Test 4 & 5:
    Assistant low-stock response contains every product returned by the tool,
    matches tool count, reports correct stock counts, and contains no duplicates.
    """
    from app.tools.inventory_tools import get_low_stock_products

    manager = ManagerAgent()
    resp = await manager.orchestrate(
        "Which products are low in stock?",
        session_id="test-low-stock",
        db_path=test_db
    )

    assert resp.agents_used == ["inventory"]
    assert len(resp.tool_calls) == 1
    assert resp.tool_calls[0].tool == "get_low_stock_products"

    tool_res = get_low_stock_products(db_path=test_db)
    count = tool_res["count"]
    products = tool_res["products"]

    # 1. Answer count matches tool count
    assert f"There are currently {count} products low in stock:" in resp.answer

    # 2. Every product returned by the tool is enumerated in the answer
    for p in products:
        assert p["name"] in resp.answer, f"Product {p['name']} missing from assistant answer."
        assert f"({p['stock']} left)" in resp.answer, f"Stock quantity for {p['name']} missing from answer."

    # 3. No product appears twice in the assistant answer
    for p in products:
        occurrences = resp.answer.count(p["name"])
        assert occurrences == 1, f"Product {p['name']} appears {occurrences} times in answer: {resp.answer}"


@pytest.mark.anyio
async def test_manager_low_stock_consistency_with_inventory_summary(test_db):
    """
    Consistency Test 6:
    Proves assistant low-stock count matches get_inventory_summary()["low_stock"].
    """
    from app.tools.inventory_tools import get_inventory_summary

    summary = get_inventory_summary(db_path=test_db)
    manager = ManagerAgent()
    resp = await manager.orchestrate(
        "Which products are low in stock?",
        session_id="test-low-stock-summary",
        db_path=test_db
    )

    assert f"{summary['low_stock']} products low in stock" in resp.answer
