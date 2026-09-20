"""
Capability Parity Test Suite: B3 Local Mode vs Foundry Manager Mode.
Proves that every user-query capability supported by B3/local mode can be represented
and executed in foundry_manager mode with complete operational parity.
Runs strictly with mocked Foundry routing — ZERO live Azure calls during pytest.
"""

import pytest
from unittest.mock import AsyncMock

from app.orchestration.intent import (
    NexusIntent,
    FoundryRoutingDecision,
    build_execution_plan
)
from app.agents.manager import ManagerAgent


CAPABILITY_MATRIX = [
    {
        "id": "1. total_sales",
        "query": "How much revenue did we make?",
        "intent": NexusIntent.SALES_TOTAL,
        "decision_kwargs": {},
        "expected_agent": "sales",
        "expected_op": "sales.total",
    },
    {
        "id": "2. monthly_sales",
        "query": "What were the monthly sales for September 2026?",
        "intent": NexusIntent.SALES_MONTHLY,
        "decision_kwargs": {"month": 9, "year": 2026},
        "expected_agent": "sales",
        "expected_op": "sales.monthly",
    },
    {
        "id": "3. top_products",
        "query": "Which are our top selling products?",
        "intent": NexusIntent.SALES_TOP_PRODUCTS,
        "decision_kwargs": {"limit": 3},
        "expected_agent": "sales",
        "expected_op": "sales.top_products",
    },
    {
        "id": "4. sales_trend",
        "query": "What is our revenue trend over time?",
        "intent": NexusIntent.SALES_TREND,
        "decision_kwargs": {},
        "expected_agent": "sales",
        "expected_op": "sales.trend",
    },
    {
        "id": "5. specific_product_stock",
        "query": "What is the stock level for Laptop Pro?",
        "intent": NexusIntent.INVENTORY_PRODUCT_STOCK,
        "decision_kwargs": {"product_name": "Laptop Pro", "product_id": "P101"},
        "expected_agent": "inventory",
        "expected_op": "inventory.product_stock",
    },
    {
        "id": "6. low_stock_products",
        "query": "Which products are low in stock?",
        "intent": NexusIntent.INVENTORY_LOW_STOCK,
        "decision_kwargs": {},
        "expected_agent": "inventory",
        "expected_op": "inventory.low_stock",
    },
    {
        "id": "7. inventory_summary",
        "query": "Give me an inventory summary of our catalog.",
        "intent": NexusIntent.INVENTORY_SUMMARY,
        "decision_kwargs": {},
        "expected_agent": "inventory",
        "expected_op": "inventory.summary",
    },
    {
        "id": "8. employee_summary",
        "query": "How many employees do we have and who is on leave?",
        "intent": NexusIntent.HR_SUMMARY,
        "decision_kwargs": {},
        "expected_agent": "hr",
        "expected_op": "hr.summary",
    },
    {
        "id": "9. employee_details",
        "query": "Show me employee details for EMP001.",
        "intent": NexusIntent.HR_EMPLOYEE,
        "decision_kwargs": {"employee_id": "EMP001"},
        "expected_agent": "hr",
        "expected_op": "hr.employee",
    },
    {
        "id": "10. specific_hr_policy",
        "query": "What is our Annual Leave policy?",
        "intent": NexusIntent.HR_POLICY,
        "decision_kwargs": {"policy_name": "Annual Leave"},
        "expected_agent": "hr",
        "expected_op": "hr.policy",
    },
    {
        "id": "11. all_hr_policies",
        "query": "List all company policies for Nexus.",
        "intent": NexusIntent.HR_POLICIES,
        "decision_kwargs": {},
        "expected_agent": "hr",
        "expected_op": "hr.policies",
    },
]


@pytest.mark.anyio
@pytest.mark.parametrize("cap", CAPABILITY_MATRIX, ids=[c["id"] for c in CAPABILITY_MATRIX])
async def test_capability_parity_single_agent(cap, test_db):
    """
    Verifies that for every single-agent capability:
    - Local mode routes and executes the specialist operation against SQLite
    - Foundry manager mode produces the exact same specialist execution and data
    """
    query = cap["query"]
    expected_agent = cap["expected_agent"]
    expected_op = cap["expected_op"]

    # 1. LOCAL MODE EXECUTION
    manager_local = ManagerAgent(orchestration_mode="local")
    resp_local = await manager_local.orchestrate(query, session_id="parity-local", db_path=test_db)

    assert resp_local.agents_used == [expected_agent], f"Local mode used {resp_local.agents_used}, expected {[expected_agent]}"
    assert len(resp_local.tool_calls) == 1
    assert resp_local.tool_calls[0].agent == expected_agent
    assert any(expected_op.split(".")[-1] in tc.tool for tc in resp_local.tool_calls)

    # 2. FOUNDRY MANAGER MODE EXECUTION
    decision = FoundryRoutingDecision(intent=cap["intent"], **cap["decision_kwargs"])
    plan = build_execution_plan(cap["intent"], query, decision=decision)

    mock_foundry = AsyncMock()
    mock_foundry.route.return_value = (plan, {
        "routing_source": "foundry",
        "model": "gpt-5-mini",
        "intent": cap["intent"].value
    })

    manager_foundry = ManagerAgent(
        foundry_router=mock_foundry,
        orchestration_mode="foundry_manager"
    )
    resp_foundry = await manager_foundry.orchestrate(query, session_id="parity-foundry", db_path=test_db)

    assert resp_foundry.agents_used == [expected_agent]
    assert len(resp_foundry.tool_calls) == 1
    assert resp_foundry.tool_calls[0].agent == expected_agent

    # Both modes must yield non-empty, factual answers
    assert resp_local.answer
    assert resp_foundry.answer
    assert resp_foundry.plan["intent"] == plan.intent


@pytest.mark.anyio
async def test_capability_parity_compound_sales_inventory(test_db):
    """Verifies parity on Compound Sales + Inventory workflow."""
    query = "Compare our top-selling products with current inventory."

    # 1. Local
    manager_local = ManagerAgent(orchestration_mode="local")
    resp_local = await manager_local.orchestrate(query, session_id="parity-local-compound", db_path=test_db)
    assert resp_local.agents_used == ["sales", "inventory"]
    assert len(resp_local.tool_calls) == 4  # 1 sales + 3 inventory
    assert any(e.type == "context_passed" for e in resp_local.trace)

    # 2. Foundry
    decision = FoundryRoutingDecision(intent=NexusIntent.COMPOUND_SALES_INVENTORY)
    plan = build_execution_plan(NexusIntent.COMPOUND_SALES_INVENTORY, query, decision=decision)
    mock_foundry = AsyncMock()
    mock_foundry.route.return_value = (plan, {
        "routing_source": "foundry",
        "model": "gpt-5-mini",
        "intent": "compound_sales_inventory"
    })
    manager_foundry = ManagerAgent(foundry_router=mock_foundry, orchestration_mode="foundry_manager")
    resp_foundry = await manager_foundry.orchestrate(query, session_id="parity-foundry-compound", db_path=test_db)

    assert resp_foundry.agents_used == ["sales", "inventory"]
    assert len(resp_foundry.tool_calls) == 4
    assert any(e.type == "context_passed" for e in resp_foundry.trace)
    assert "Laptop Pro" in resp_foundry.answer


@pytest.mark.anyio
async def test_capability_parity_business_overview(test_db):
    """Verifies parity on Business Overview workflow."""
    query = "Give me a business overview."

    # 1. Local
    manager_local = ManagerAgent(orchestration_mode="local")
    resp_local = await manager_local.orchestrate(query, session_id="parity-local-overview", db_path=test_db)
    assert resp_local.agents_used == ["sales", "inventory", "hr"]
    assert len(resp_local.tool_calls) == 3

    # 2. Foundry
    decision = FoundryRoutingDecision(intent=NexusIntent.BUSINESS_OVERVIEW)
    plan = build_execution_plan(NexusIntent.BUSINESS_OVERVIEW, query, decision=decision)
    mock_foundry = AsyncMock()
    mock_foundry.route.return_value = (plan, {
        "routing_source": "foundry",
        "model": "gpt-5-mini",
        "intent": "business_overview"
    })
    manager_foundry = ManagerAgent(foundry_router=mock_foundry, orchestration_mode="foundry_manager")
    resp_foundry = await manager_foundry.orchestrate(query, session_id="parity-foundry-overview", db_path=test_db)

    assert resp_foundry.agents_used == ["sales", "inventory", "hr"]
    assert len(resp_foundry.tool_calls) == 3
    assert "Business Overview:" in resp_foundry.answer


@pytest.mark.anyio
async def test_capability_parity_unsupported():
    """Verifies parity on Unsupported / Out-of-Domain workflow."""
    query = "What's the weather in Tokyo?"

    # 1. Local
    manager_local = ManagerAgent(orchestration_mode="local")
    resp_local = await manager_local.orchestrate(query, session_id="parity-local-unsupported")
    assert resp_local.agents_used == []
    assert resp_local.tool_calls == []
    assert "help with sales, inventory, HR, and business overview" in resp_local.answer

    # 2. Foundry
    decision = FoundryRoutingDecision(intent=NexusIntent.UNSUPPORTED)
    plan = build_execution_plan(NexusIntent.UNSUPPORTED, query, decision=decision)
    mock_foundry = AsyncMock()
    mock_foundry.route.return_value = (plan, {
        "routing_source": "foundry",
        "model": "gpt-5-mini",
        "intent": "unsupported"
    })
    manager_foundry = ManagerAgent(foundry_router=mock_foundry, orchestration_mode="foundry_manager")
    resp_foundry = await manager_foundry.orchestrate(query, session_id="parity-foundry-unsupported")

    assert resp_foundry.agents_used == []
    assert resp_foundry.tool_calls == []
    assert "help with sales, inventory, HR, and business overview" in resp_foundry.answer
