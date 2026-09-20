"""
Tests for Phase B3 Specialist Agents and AgentRegistry.
Validates boundaries, tool restrictions, and error handling.
"""

import pytest
from app.agents.types import AgentTask
from app.agents.sales import SalesAgent
from app.agents.inventory import InventoryAgent
from app.agents.hr import HRAgent
from app.agents.registry import AgentRegistry, create_default_registry
from app.db.connection import get_db
from app.db.repositories import get_activity_logs_db


@pytest.mark.anyio
async def test_sales_agent_allowed_operations(test_db):
    agent = SalesAgent()

    # 1. sales.total
    task = AgentTask(task_id="t1", operation="sales.total", parameters={"db_path": test_db})
    res = await agent.execute(task)
    assert res.status == "success"
    assert res.data["revenue"] == 124500.0
    assert len(res.tool_calls) == 1
    assert res.tool_calls[0].tool == "get_total_sales"

    # 2. sales.top_products
    task = AgentTask(task_id="t2", operation="sales.top_products", parameters={"limit": 3, "db_path": test_db})
    res = await agent.execute(task)
    assert res.status == "success"
    assert len(res.data["products"]) == 3
    assert res.tool_calls[0].tool == "get_top_products"


@pytest.mark.anyio
async def test_sales_agent_invalid_operation():
    agent = SalesAgent()
    task = AgentTask(task_id="t_inv", operation="sales.unsupported", parameters={})
    res = await agent.execute(task)
    assert res.status == "error"
    assert res.error["code"] == "UNSUPPORTED_OPERATION"
    assert "not supported" in res.error["message"]


@pytest.mark.anyio
async def test_sales_agent_records_durable_activity(test_db):
    """Verifies that one tool execution creates exactly ONE durable activity entry."""
    with get_db(test_db) as conn:
        before_count = len(get_activity_logs_db(conn))

    agent = SalesAgent()
    task = AgentTask(task_id="t_act", operation="sales.total", parameters={"db_path": test_db})
    res = await agent.execute(task)
    assert res.status == "success"

    with get_db(test_db) as conn:
        after_count = len(get_activity_logs_db(conn))

    assert after_count == before_count + 1


@pytest.mark.anyio
async def test_get_top_products_activity_deduplication(test_db):
    """Proves get_top_products creates exactly 1 durable activity record."""
    with get_db(test_db) as conn:
        before = len(get_activity_logs_db(conn))

    agent = SalesAgent()
    task = AgentTask(task_id="t_top_act", operation="sales.top_products", parameters={"limit": 3, "db_path": test_db})
    res = await agent.execute(task)
    assert res.status == "success"

    with get_db(test_db) as conn:
        after = len(get_activity_logs_db(conn))
    assert after == before + 1


@pytest.mark.anyio
async def test_get_product_stock_activity_deduplication(test_db):
    """Proves get_product_stock creates exactly 1 durable activity record."""
    with get_db(test_db) as conn:
        before = len(get_activity_logs_db(conn))

    agent = InventoryAgent()
    task = AgentTask(task_id="t_stock_act", operation="inventory.product_stock", parameters={"product_id": "P101", "db_path": test_db})
    res = await agent.execute(task)
    assert res.status == "success"

    with get_db(test_db) as conn:
        after = len(get_activity_logs_db(conn))
    assert after == before + 1


@pytest.mark.anyio
async def test_inventory_agent_stock_operation(test_db):
    agent = InventoryAgent()
    task = AgentTask(task_id="t_stock", operation="inventory.product_stock", parameters={"product_id": "P101", "db_path": test_db})
    res = await agent.execute(task)
    assert res.status == "success"
    assert res.data["id"] == "P101"
    assert res.data["stock"] == 4
    assert res.data["status"] == "low"
    assert len(res.tool_calls) == 1
    assert res.tool_calls[0].tool == "get_product_stock"


@pytest.mark.anyio
async def test_inventory_agent_product_not_found(test_db):
    agent = InventoryAgent()
    task = AgentTask(task_id="t_missing", operation="inventory.product_stock", parameters={"product_id": "P9999", "db_path": test_db})
    res = await agent.execute(task)
    assert res.status == "error"
    assert res.error["code"] == "PRODUCT_NOT_FOUND"
    assert res.data is None


@pytest.mark.anyio
async def test_inventory_agent_invalid_operation():
    agent = InventoryAgent()
    task = AgentTask(task_id="t_bad", operation="inventory.unsupported", parameters={})
    res = await agent.execute(task)
    assert res.status == "error"
    assert res.error["code"] == "UNSUPPORTED_OPERATION"


@pytest.mark.anyio
async def test_hr_agent_summary_operation(test_db):
    agent = HRAgent()
    task = AgentTask(task_id="t_hr", operation="hr.summary", parameters={"db_path": test_db})
    res = await agent.execute(task)
    assert res.status == "success"
    assert res.data["employee_count"] == 16
    assert res.data["departments"] == 5
    assert len(res.tool_calls) == 1
    assert res.tool_calls[0].tool == "get_employee_summary"


@pytest.mark.anyio
async def test_hr_agent_policy_operation(test_db):
    agent = HRAgent()
    task = AgentTask(task_id="t_pol", operation="hr.policy", parameters={"title": "Remote Work", "db_path": test_db})
    res = await agent.execute(task)
    assert res.status == "success"
    assert res.data["title"] == "Remote Work"
    assert "2 days per week" in res.data["summary"]


@pytest.mark.anyio
async def test_hr_agent_policy_not_found(test_db):
    agent = HRAgent()
    task = AgentTask(task_id="t_none", operation="hr.policy", parameters={"title": "NonExistentPolicy", "db_path": test_db})
    res = await agent.execute(task)
    assert res.status == "error"
    assert res.error["code"] == "POLICY_NOT_FOUND"


@pytest.mark.anyio
async def test_hr_agent_invalid_operation():
    agent = HRAgent()
    task = AgentTask(task_id="t_bad_hr", operation="hr.unsupported", parameters={})
    res = await agent.execute(task)
    assert res.status == "error"
    assert res.error["code"] == "UNSUPPORTED_OPERATION"


def test_agent_registry_lookup():
    registry = create_default_registry()
    assert "sales" in registry.list_agents()
    assert "inventory" in registry.list_agents()
    assert "hr" in registry.list_agents()

    assert isinstance(registry.get("sales"), SalesAgent)
    assert isinstance(registry.get("inventory"), InventoryAgent)
    assert isinstance(registry.get("hr"), HRAgent)
    assert registry.get("unknown") is None
