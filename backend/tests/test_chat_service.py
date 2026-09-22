import uuid


def test_chat_compare_query_uses_unified_analytics(client):
    response = client.post("/api/chat", json={"message": "Compare our top-selling products with current inventory."})
    assert response.status_code == 200
    data = response.json()

    parsed_uuid = uuid.UUID(data["session_id"])
    assert str(parsed_uuid) == data["session_id"]

    assert data["agents_used"] == ["sales", "inventory"]
    tool_names = [t["tool"] for t in data["tool_calls"]]
    assert tool_names.count("get_top_products") == 1
    assert tool_names.count("get_product_stock") == 3

    # Unified Kaggle analytics facts, not legacy Laptop/Headset/Keyboard seed data.
    assert "Mega Board Game" in data["answer"]
    assert "City Board Game" in data["answer"]
    assert "Pro Science Lab" in data["answer"]
    assert "$231,910.47" in data["answer"]
    assert "421 units currently in stock" in data["answer"]
    assert "reorder levels" in data["answer"].lower()
    assert "Laptop Pro" not in data["answer"]
    assert "₹" not in data["answer"]

    context_events = [e for e in data["trace"] if e["type"] == "context_passed"]
    assert len(context_events) == 1
    assert set(context_events[0]["metadata"]["product_ids"]) == {130, 97, 153}


def test_chat_total_sales_uses_external_usd_dataset(client):
    response = client.post("/api/chat", json={"message": "What are our total sales?"})
    assert response.status_code == 200
    data = response.json()
    assert data["agents_used"] == ["sales"]
    assert any(t["tool"] == "get_total_sales" for t in data["tool_calls"])
    assert "$9,862,933.25" in data["answer"]
    assert "567,270" in data["answer"]
    assert "245,800" in data["answer"]
    assert "₹124,500" not in data["answer"]


def test_chat_top_products_uses_external_catalog(client):
    response = client.post("/api/chat", json={"message": "Show me the top 3 selling products."})
    assert response.status_code == 200
    data = response.json()
    assert data["agents_used"] == ["sales"]
    assert "Mega Board Game" in data["answer"]
    assert "Product 130" in data["answer"]
    assert "Laptop Pro" not in data["answer"]


def test_chat_inventory_summary_uses_external_snapshot(client):
    response = client.post("/api/chat", json={"message": "How many out-of-stock placements do we have?"})
    assert response.status_code == 200
    data = response.json()
    assert data["agents_used"] == ["inventory"]
    assert "338,993" in data["answer"]
    assert "14,143" in data["answer"]
    assert "321 zero-stock placements" in data["answer"]
    assert "assumed as Dec 31, 2025" in data["answer"]


def test_chat_hr_remains_internal_people_domain(client):
    response = client.post("/api/chat", json={"message": "How many employees do we have?"})
    assert response.status_code == 200
    data = response.json()
    assert data["agents_used"] == ["hr"]
    assert "180 active employees" in data["answer"]
    assert "12 departments" in data["answer"]
    assert "17 on leave" in data["answer"]


def test_chat_business_overview_combines_analytics_and_people(client):
    response = client.post("/api/chat", json={"message": "Give me a business overview."})
    assert response.status_code == 200
    data = response.json()
    assert set(data["agents_used"]) == {"sales", "inventory", "hr"}
    assert "$9,862,933.25" in data["answer"]
    assert "338,993 units" in data["answer"]
    assert "321 zero-stock placements" in data["answer"]
    assert "180 synthetic internal employees" in data["answer"]


def test_chat_empty_message_validation_error(client):
    response = client.post("/api/chat", json={"message": ""})
    assert response.status_code == 422


def test_chat_whitespace_message_validation_error(client):
    response = client.post("/api/chat", json={"message": "    "})
    assert response.status_code == 422
