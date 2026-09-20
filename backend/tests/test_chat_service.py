import uuid
from app.tools.sales_tools import get_top_products
from app.tools.inventory_tools import get_product_stock


def test_chat_compare_query_executes_real_tools(client, test_db):
    """
    Tests that POST /api/chat executes real tools against SQLite
    via ManagerAgent and dynamically produces answer with factual database numbers.
    """
    # Fetch expected values directly from tools
    top_prods = get_top_products(limit=3, month=9, year=2026, db_path=test_db)["products"]
    top = top_prods[0]
    stock = get_product_stock(product_id=top["id"], db_path=test_db)

    payload = {
        "message": "Compare our top-selling products with current inventory."
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Verify session UUID is dynamic and valid (not hardcoded session_demo)
    assert data["session_id"] != "session_demo"
    parsed_uuid = uuid.UUID(data["session_id"])
    assert str(parsed_uuid) == data["session_id"]

    # Verify agent routing
    assert "sales" in data["agents_used"]
    assert "inventory" in data["agents_used"]

    # Verify real tools executed: get_top_products + get_product_stock for all 3 products
    assert len(data["tool_calls"]) == 4
    tool_names = [t["tool"] for t in data["tool_calls"]]
    assert "get_top_products" in tool_names
    assert tool_names.count("get_product_stock") == 3

    # Verify context_passed event is present in trace with product IDs
    context_events = [e for e in data["trace"] if e["type"] == "context_passed"]
    assert len(context_events) == 1
    assert context_events[0]["metadata"]["source"] == "sales"
    assert context_events[0]["metadata"]["target"] == "inventory"
    assert set(context_events[0]["metadata"]["product_ids"]) == {p["id"] for p in top_prods}

    # Verify measured durations are actual numbers, not hard-coded 420/280
    for t in data["tool_calls"]:
        assert isinstance(t["duration_ms"], int)
        assert t["duration_ms"] >= 0

    # Verify that ALL returned top products appear in the final synthesis with exact tool numbers
    for p in top_prods:
        p_stock = get_product_stock(product_id=p["id"], db_path=test_db)
        assert p["name"] in data["answer"]
        assert str(p["units_sold"]) in data["answer"]
        assert str(p_stock["stock"]) in data["answer"]
        assert str(p_stock["reorder_level"]) in data["answer"]


def test_chat_empty_message_validation_error(client):
    """Verifies that an empty message raises a 422 validation error."""
    response = client.post("/api/chat", json={"message": ""})
    assert response.status_code == 422


def test_chat_whitespace_message_validation_error(client):
    """Verifies that whitespace-only message raises a 422 validation error."""
    response = client.post("/api/chat", json={"message": "    "})
    assert response.status_code == 422


def test_chat_low_stock_query(client, test_db):
    """Verifies low stock query executes get_low_stock_products and enumerates all products."""
    from app.tools.inventory_tools import get_low_stock_products
    tool_res = get_low_stock_products(db_path=test_db)

    response = client.post("/api/chat", json={"message": "Which products are low in stock?"})
    assert response.status_code == 200
    data = response.json()
    assert "inventory" in data["agents_used"]
    assert any(t["tool"] == "get_low_stock_products" for t in data["tool_calls"])
    assert f"{tool_res['count']} products low in stock" in data["answer"].lower()
    for p in tool_res["products"]:
        assert p["name"] in data["answer"]
        assert f"({p['stock']} left)" in data["answer"]
