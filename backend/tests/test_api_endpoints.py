def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["backend"] == "ready"
    assert data["foundry"] == "not_configured"
    assert data["mode"] == "local_orchestration"


def test_dashboard_endpoint_derived_values(client):
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "summary" in data

    # Revenue derived from real sales table
    assert data["metrics"]["revenue"]["value"] == 124500.0
    assert data["metrics"]["orders"]["value"] == 5

    # Inventory & HR counts derived from database
    assert data["metrics"]["lowStockProducts"]["value"] == 4
    assert data["metrics"]["employees"]["value"] == 180

    # Summary text generated dynamically with real numbers
    assert "₹124,500" in data["summary"]
    assert "Laptop Pro" in data["summary"]


def test_sales_endpoint_derived_values(client):
    response = client.get("/api/sales")
    assert response.status_code == 200
    data = response.json()
    assert data["revenue"] == 124500.0
    assert data["unitsSold"] == 248
    assert len(data["monthlyRevenue"]) == 6
    assert len(data["topProducts"]) >= 3
    assert data["topProducts"][0]["name"] == "Laptop Pro"
    assert data["topProducts"][0]["unitsSold"] == 27
    assert data["topProducts"][0]["revenue"] == 67500.0


def test_inventory_endpoint_derived_values(client):
    response = client.get("/api/inventory")
    assert response.status_code == 200
    data = response.json()
    assert data["totalProducts"] == 13
    assert data["lowStockCount"] == 4
    assert data["outOfStockCount"] == 1
    assert data["healthyStockCount"] == 8
    assert len(data["products"]) == 13


def test_hr_endpoint_derived_values(client):
    response = client.get("/api/hr")
    assert response.status_code == 200
    data = response.json()
    assert data["employeeCount"] == 180
    assert data["employeesOnLeave"] == 17
    assert data["departments"] == 12
    assert len(data["policies"]) == 3
    assert data["openRequests"] == 27
    assert len(data["employees"]) == 180


def test_activity_endpoint_records(client):
    response = client.get("/api/activity")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3
