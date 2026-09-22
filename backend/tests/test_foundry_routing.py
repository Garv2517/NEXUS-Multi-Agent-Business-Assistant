"""
Unit tests for Phase B4B: Microsoft Foundry Manager Routing.
Strictly adheres to Section 27 requirements:
- Zero live Azure/Foundry calls during pytest (mocked FoundryChatClient/Agent/Router)
- Covers all 20 required verification scenarios
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import ValidationError

from app.core.config import settings
from app.agents.types import ExecutionPlan, PlanStep
from app.orchestration.intent import (
    NexusIntent,
    FoundryRoutingDecision,
    build_execution_plan
)
from app.orchestration.foundry_router import (
    FoundryManagerRouter,
    FoundryRoutingError
)
from app.agents.manager import ManagerAgent
from app.orchestration.router import DeterministicRouter


# =====================================================================
# 1. Local mode still uses DeterministicRouter
# =====================================================================
@pytest.mark.anyio
async def test_local_mode_uses_deterministic_router():
    with patch.object(settings, "ORCHESTRATION_MODE", "local"):
        mock_foundry = AsyncMock()
        manager = ManagerAgent(
            foundry_router=mock_foundry,
            orchestration_mode="local"
        )
        resp = await manager.orchestrate("How much revenue did we make?", session_id="test-local")

        # Foundry router should NOT have been called
        mock_foundry.route.assert_not_called()
        # Trace should identify local routing
        route_event = next(e for e in resp.trace if e.type == "route_selected")
        assert route_event.metadata.get("routing_source") == "local"
        assert resp.plan["intent"] == "sales"


# =====================================================================
# 2. Foundry_manager mode uses FoundryManagerRouter
# =====================================================================
@pytest.mark.anyio
async def test_foundry_manager_mode_uses_foundry_router():
    mock_foundry = AsyncMock()
    mock_plan = build_execution_plan(NexusIntent.SALES_TOTAL, "How much revenue did we make?")
    mock_foundry.route.return_value = (mock_plan, {
        "routing_source": "foundry",
        "model": "gpt-5-mini",
        "intent": "sales_total"
    })

    manager = ManagerAgent(
        foundry_router=mock_foundry,
        orchestration_mode="foundry_manager"
    )
    resp = await manager.orchestrate("How much revenue did we make?", session_id="test-fm")

    mock_foundry.route.assert_called_once_with("How much revenue did we make?")
    route_event = next(e for e in resp.trace if e.type == "route_selected")
    assert route_event.metadata.get("routing_source") == "foundry"
    assert route_event.metadata.get("model") == "gpt-5-mini"


# =====================================================================
# 3. Structured sales route maps to existing trusted plan
# =====================================================================
def test_structured_sales_route_maps_to_trusted_plan():
    plan = build_execution_plan(NexusIntent.SALES_TOTAL, "revenue check")
    assert plan.intent == "sales"
    assert plan.agents == ["sales"]
    assert len(plan.steps) == 1
    assert plan.steps[0].operation == "sales.total"


# =====================================================================
# 4. Structured inventory route maps to existing trusted plan
# =====================================================================
def test_structured_inventory_route_maps_to_trusted_plan():
    plan = build_execution_plan(NexusIntent.INVENTORY_LOW_STOCK, "low stock check")
    assert plan.intent == "inventory"
    assert plan.agents == ["inventory"]
    assert len(plan.steps) == 1
    assert plan.steps[0].operation == "inventory.low_stock"


# =====================================================================
# 5. Structured HR route maps to existing trusted plan
# =====================================================================
def test_structured_hr_route_maps_to_trusted_plan():
    plan = build_execution_plan(NexusIntent.HR_POLICY, "leave policy", policy_name="Annual Leave")
    assert plan.intent == "hr"
    assert plan.agents == ["hr"]
    assert len(plan.steps) == 1
    assert plan.steps[0].operation == "hr.policy"
    assert plan.steps[0].parameters.get("title") == "Annual Leave"


# =====================================================================
# 6. Structured business overview route maps correctly
# =====================================================================
def test_structured_business_overview_route_maps_correctly():
    plan = build_execution_plan(NexusIntent.BUSINESS_OVERVIEW, "overview")
    assert plan.intent == "business_overview"
    assert plan.agents == ["sales", "inventory", "hr"]
    assert len(plan.steps) == 3
    assert [s.agent for s in plan.steps] == ["sales", "inventory", "hr"]


# =====================================================================
# 7. Structured compound sales/inventory route maps correctly
# =====================================================================
def test_structured_compound_sales_inventory_route_maps_correctly():
    plan = build_execution_plan(NexusIntent.COMPOUND_SALES_INVENTORY, "compare top products with stock")
    assert plan.intent == "compound_sales_inventory"
    assert plan.agents == ["sales", "inventory"]
    assert len(plan.steps) == 2
    assert plan.steps[0].operation == "sales.top_products"
    assert plan.steps[0].parameters["limit"] == 3
    assert plan.steps[1].operation == "inventory.product_stock"
    assert plan.steps[1].depends_on == 1


# =====================================================================
# 8. Unsupported route invokes zero specialists/tools
# =====================================================================
@pytest.mark.anyio
async def test_unsupported_route_invokes_zero_specialists_and_tools():
    mock_foundry = AsyncMock()
    mock_plan = build_execution_plan(NexusIntent.UNSUPPORTED, "What's the weather?")
    mock_foundry.route.return_value = (mock_plan, {
        "routing_source": "foundry",
        "model": "gpt-5-mini",
        "intent": "unsupported"
    })

    manager = ManagerAgent(
        foundry_router=mock_foundry,
        orchestration_mode="foundry_manager"
    )
    resp = await manager.orchestrate("What's the weather?", session_id="test-unsupported")

    assert resp.agents_used == []
    assert resp.tool_calls == []
    assert "help with sales, inventory, HR, and business overview" in resp.answer
    assert any(e.type == "route_selected" and e.metadata.get("intent") == "unsupported" for e in resp.trace)


# =====================================================================
# 9. Invalid enum / malformed structured response is rejected
# =====================================================================
def test_invalid_enum_rejected_by_pydantic():
    with pytest.raises(ValidationError):
        FoundryRoutingDecision.model_validate({"intent": "arbitrary_custom_code"})


# =====================================================================
# 10. response.value absent is treated as routing failure
# =====================================================================
@pytest.mark.anyio
async def test_response_value_absent_treated_as_routing_failure():
    mock_agent = AsyncMock()
    mock_response = MagicMock()
    mock_response.value = None  # Missing structured output
    mock_agent.run.return_value = mock_response

    mock_client = MagicMock()
    router = FoundryManagerRouter(client=mock_client, model="gpt-5-mini")

    with patch("app.orchestration.foundry_router.Agent", return_value=mock_agent):
        with pytest.raises(FoundryRoutingError) as exc_info:
            await router.route("some query")
        assert exc_info.value.category == "INVALID_STRUCTURED_OUTPUT"


# =====================================================================
# 11. Foundry exception falls back locally when enabled
# =====================================================================
@pytest.mark.anyio
async def test_foundry_exception_falls_back_locally_when_enabled():
    mock_foundry = AsyncMock()
    mock_foundry.route.side_effect = FoundryRoutingError("NETWORK_ERROR", "Connection refused")

    manager = ManagerAgent(
        foundry_router=mock_foundry,
        orchestration_mode="foundry_manager",
        fallback_to_local=True
    )
    resp = await manager.orchestrate("How much revenue did we make?", session_id="test-fallback")

    # Fell back to local DeterministicRouter
    route_event = next(e for e in resp.trace if e.type == "route_selected")
    assert route_event.metadata.get("routing_source") == "local_fallback"
    assert route_event.metadata.get("failure_category") == "NETWORK_ERROR"
    assert resp.plan["intent"] == "sales"
    assert len(resp.agents_used) > 0


# =====================================================================
# 12. Timeout falls back locally when enabled
# =====================================================================
@pytest.mark.anyio
async def test_foundry_timeout_falls_back_locally_when_enabled():
    mock_foundry = AsyncMock()
    mock_foundry.route.side_effect = FoundryRoutingError("TIMEOUT", "Foundry routing timed out after 15s.")

    manager = ManagerAgent(
        foundry_router=mock_foundry,
        orchestration_mode="foundry_manager",
        fallback_to_local=True
    )
    resp = await manager.orchestrate("Which products are low in stock?", session_id="test-timeout")

    route_event = next(e for e in resp.trace if e.type == "route_selected")
    assert route_event.metadata.get("routing_source") == "local_fallback"
    assert route_event.metadata.get("failure_category") == "TIMEOUT"
    assert resp.plan["intent"] == "inventory"


# =====================================================================
# 13. Fallback-disabled failure does not route locally
# =====================================================================
@pytest.mark.anyio
async def test_fallback_disabled_failure_does_not_route_locally():
    mock_foundry = AsyncMock()
    mock_foundry.route.side_effect = FoundryRoutingError("AUTHENTICATION_FAILED", "Azure login required")

    manager = ManagerAgent(
        foundry_router=mock_foundry,
        orchestration_mode="foundry_manager",
        fallback_to_local=False
    )
    resp = await manager.orchestrate("How much revenue did we make?", session_id="test-nofallback")

    # Controlled error response, 0 agents used
    assert resp.agents_used == []
    assert resp.tool_calls == []
    assert resp.plan is None
    assert "Routing service failure: AUTHENTICATION_FAILED" in resp.answer
    error_event = next(e for e in resp.trace if e.type == "route_selected")
    assert error_event.status == "error"
    assert error_event.metadata.get("routing_source") == "foundry_error"


# =====================================================================
# 14. Route trace identifies Foundry source
# =====================================================================
@pytest.mark.anyio
async def test_route_trace_identifies_foundry_source():
    mock_foundry = AsyncMock()
    mock_plan = build_execution_plan(NexusIntent.INVENTORY_LOW_STOCK, "low stock")
    mock_foundry.route.return_value = (mock_plan, {
        "routing_source": "foundry",
        "model": "gpt-5-mini",
        "intent": "inventory_low_stock"
    })

    manager = ManagerAgent(
        foundry_router=mock_foundry,
        orchestration_mode="foundry_manager"
    )
    resp = await manager.orchestrate("Which products are low in stock?", session_id="test-source")

    route_event = next(e for e in resp.trace if e.type == "route_selected")
    assert route_event.status == "success"
    assert route_event.metadata["routing_source"] == "foundry"
    assert route_event.metadata["model"] == "gpt-5-mini"
    assert route_event.metadata["intent"] == "inventory_low_stock"


# =====================================================================
# 15. Fallback trace identifies local_fallback
# =====================================================================
@pytest.mark.anyio
async def test_fallback_trace_identifies_local_fallback():
    mock_foundry = AsyncMock()
    mock_foundry.route.side_effect = FoundryRoutingError("QUOTA_OR_RATE_LIMIT", "Rate limit exceeded")

    manager = ManagerAgent(
        foundry_router=mock_foundry,
        orchestration_mode="foundry_manager",
        fallback_to_local=True
    )
    resp = await manager.orchestrate("Give me a business overview.", session_id="test-fb-trace")

    route_event = next(e for e in resp.trace if e.type == "route_selected")
    assert route_event.status == "warning"
    assert route_event.metadata["routing_source"] == "local_fallback"
    assert route_event.metadata["failure_category"] == "QUOTA_OR_RATE_LIMIT"


# =====================================================================
# 16. Model output cannot inject arbitrary tool/function names
# =====================================================================
def test_model_output_cannot_inject_arbitrary_tool_names():
    # Only NexusIntent enum values are accepted; arbitrary strings fail validation
    with pytest.raises(ValidationError):
        FoundryRoutingDecision.model_validate({"intent": "system.drop_database"})

    # Even if someone bypassed Pydantic and passed an invalid intent to build_execution_plan,
    # it safely falls back to unsupported with 0 agents and 0 steps
    unsupported_plan = build_execution_plan("arbitrary_intent", "malicious query")  # type: ignore
    assert unsupported_plan.intent == "unsupported"
    assert unsupported_plan.agents == []
    assert unsupported_plan.steps == []


# =====================================================================
# 17. Model output cannot inject business values into execution
# =====================================================================
def test_model_output_cannot_inject_business_values():
    # FoundryRoutingDecision has NO fields for factual data (revenue, stock counts, leave balances)
    assert "revenue" not in FoundryRoutingDecision.model_fields
    assert "stock" not in FoundryRoutingDecision.model_fields
    assert "units_sold" not in FoundryRoutingDecision.model_fields
    assert "employee_count" not in FoundryRoutingDecision.model_fields
    assert "leave_balance" not in FoundryRoutingDecision.model_fields
    assert "reorder_level" not in FoundryRoutingDecision.model_fields



# =====================================================================
# 18. Existing compound context passing still passes all expected IDs
# =====================================================================
@pytest.mark.anyio
async def test_compound_context_passing_with_foundry_route(test_db):
    mock_foundry = AsyncMock()
    mock_plan = build_execution_plan(
        NexusIntent.COMPOUND_SALES_INVENTORY,
        "Compare our top-selling products with current inventory."
    )
    mock_foundry.route.return_value = (mock_plan, {
        "routing_source": "foundry",
        "model": "gpt-5-mini",
        "intent": "compound_sales_inventory"
    })

    manager = ManagerAgent(
        foundry_router=mock_foundry,
        orchestration_mode="foundry_manager"
    )
    resp = await manager.orchestrate(
        "Compare our top-selling products with current inventory.",
        session_id="test-compound-context"
    )

    # Verify context_passed event contains top 3 product IDs from SalesAgent
    context_events = [e for e in resp.trace if e.type == "context_passed"]
    assert len(context_events) == 1
    assert context_events[0].metadata["source"] == "sales"
    assert context_events[0].metadata["target"] == "inventory"
    passed_product_ids = context_events[0].metadata.get("product_ids", [])
    assert len(passed_product_ids) == 3


# =====================================================================
# 19. Existing deterministic business answers remain unchanged
# =====================================================================
@pytest.mark.anyio
async def test_deterministic_business_answers_remain_unchanged(test_db):
    mock_foundry = AsyncMock()
    mock_plan = build_execution_plan(NexusIntent.SALES_TOTAL, "How much revenue did we make?")
    mock_foundry.route.return_value = (mock_plan, {
        "routing_source": "foundry",
        "model": "gpt-5-mini",
        "intent": "sales_total"
    })

    manager = ManagerAgent(
        foundry_router=mock_foundry,
        orchestration_mode="foundry_manager"
    )
    resp = await manager.orchestrate(
        "How much revenue did we make?",
        session_id="test-factual",
        analytics_db_path=settings.get_analytics_database_path(),
    )

    # Foundry chooses the route only; factual business values come from the verified analytics DB.
    assert "$9,862,933.25" in resp.answer
    assert "567,270" in resp.answer
    assert "245,800" in resp.answer
    assert "₹" not in resp.answer


# =====================================================================
# 20. No live Azure calls occur during ordinary pytest
# =====================================================================
def test_no_live_azure_calls_during_pytest():
    # Attempting to initialize FoundryChatClient without real Azure calls in tests
    # Verify that FoundryManagerRouter accepts an injected client for isolation
    mock_client = MagicMock()
    router = FoundryManagerRouter(client=mock_client, model="gpt-5-mini")
    assert router._client is mock_client
    assert router.model_name == "gpt-5-mini"
