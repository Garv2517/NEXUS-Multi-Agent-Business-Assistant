"""
Centralized mock data dictionary for Phase B1 of Nexus.
All mock data mirrors future real Azure AI / Microsoft Foundry responses.
"""

HEALTH_DATA = {
    "status": "online",
    "backend": "ready",
    "foundry": "not_configured",
    "model": "not_configured",
    "mode": "mock",
    "version": "0.1.0"
}

DASHBOARD_DATA = {
    "metrics": {
        "revenue": {
            "value": 124500.0,
            "currency": "INR",
            "change": 12.4
        },
        "orders": {
            "value": 248,
            "change": 8.2
        },
        "lowStockProducts": {
            "value": 4
        },
        "employees": {
            "value": 180
        }
    },
    "summary": "Sales performance is trending upward this month. Laptop Pro remains the strongest-selling product, while four products currently require inventory attention."
}

SALES_DATA = {
    "revenue": 124500.0,
    "monthlyChange": 12.4,
    "unitsSold": 248,
    "averageOrderValue": 5020.0,
    "monthlyRevenue": [
        {"month": "Apr", "value": 82000.0},
        {"month": "May", "value": 91000.0},
        {"month": "Jun", "value": 88000.0},
        {"month": "Jul", "value": 101000.0},
        {"month": "Aug", "value": 110000.0},
        {"month": "Sep", "value": 124500.0}
    ],
    "topProducts": [
        {
            "id": "P101",
            "name": "Laptop Pro",
            "unitsSold": 27,
            "revenue": 67500.0
        },
        {
            "id": "P102",
            "name": "Wireless Headset",
            "unitsSold": 42,
            "revenue": 25200.0
        },
        {
            "id": "P103",
            "name": "Mechanical Keyboard",
            "unitsSold": 31,
            "revenue": 21700.0
        }
    ]
}

INVENTORY_DATA = {
    "totalProducts": 52,
    "lowStockCount": 4,
    "outOfStockCount": 1,
    "healthyStockCount": 47,
    "products": [
        {
            "id": "P101",
            "name": "Laptop Pro",
            "stock": 4,
            "reorderLevel": 10,
            "status": "low"
        },
        {
            "id": "P102",
            "name": "Wireless Headset",
            "stock": 31,
            "reorderLevel": 12,
            "status": "healthy"
        },
        {
            "id": "P103",
            "name": "Mechanical Keyboard",
            "stock": 8,
            "reorderLevel": 10,
            "status": "low"
        },
        {
            "id": "P104",
            "name": "Monitor 27",
            "stock": 24,
            "reorderLevel": 8,
            "status": "healthy"
        }
    ]
}

HR_DATA = {
    "employeeCount": 180,
    "employeesOnLeave": 17,
    "departments": 12,
    "openRequests": 27,
    "policies": [
        {
            "id": "policy_01",
            "title": "Annual Leave",
            "summary": "18 days per year"
        },
        {
            "id": "policy_02",
            "title": "Remote Work",
            "summary": "Up to 2 days per week"
        },
        {
            "id": "policy_03",
            "title": "Sick Leave",
            "summary": "10 days per year"
        }
    ]
}

ACTIVITY_DATA = [
    {
        "id": "act_001",
        "timestamp": "10:42",
        "agent": "sales",
        "action": "Retrieved top products",
        "tool": "get_top_products",
        "status": "success",
        "duration_ms": 420
    },
    {
        "id": "act_002",
        "timestamp": "10:43",
        "agent": "inventory",
        "action": "Checked inventory",
        "tool": "get_product_stock",
        "status": "success",
        "duration_ms": 280
    },
    {
        "id": "act_003",
        "timestamp": "10:44",
        "agent": "manager",
        "action": "Generated final response",
        "tool": None,
        "status": "success",
        "duration_ms": 1200
    }
]

CHAT_WORKFLOW_DEMO = {
    "session_id": "session_demo",
    "answer": "Laptop Pro is currently your strongest-selling product with 27 units sold this month, but only 4 units remain in inventory. Based on current demand, restocking should be prioritised.",
    "agents_used": [
        "sales",
        "inventory"
    ],
    "tool_calls": [
        {
            "id": "tool_001",
            "agent": "sales",
            "tool": "get_top_products",
            "status": "success",
            "duration_ms": 420
        },
        {
            "id": "tool_002",
            "agent": "inventory",
            "tool": "get_product_stock",
            "status": "success",
            "duration_ms": 280
        }
    ],
    "trace": [
        {
            "id": "event_001",
            "type": "manager_started",
            "agent": "manager",
            "tool": None,
            "status": "running",
            "message": "Understanding request"
        },
        {
            "id": "event_002",
            "type": "route_selected",
            "agent": "manager",
            "tool": None,
            "status": "success",
            "message": "Routed request to Sales Agent"
        },
        {
            "id": "event_003",
            "type": "agent_started",
            "agent": "sales",
            "tool": None,
            "status": "running",
            "message": "Sales Agent started"
        },
        {
            "id": "event_004",
            "type": "tool_completed",
            "agent": "sales",
            "tool": "get_top_products",
            "status": "success",
            "message": "Retrieved top-selling products"
        },
        {
            "id": "event_005",
            "type": "route_selected",
            "agent": "manager",
            "tool": None,
            "status": "success",
            "message": "Routed request to Inventory Agent"
        },
        {
            "id": "event_006",
            "type": "agent_started",
            "agent": "inventory",
            "tool": None,
            "status": "running",
            "message": "Inventory Agent started"
        },
        {
            "id": "event_007",
            "type": "tool_completed",
            "agent": "inventory",
            "tool": "get_product_stock",
            "status": "success",
            "message": "Retrieved current stock"
        },
        {
            "id": "event_008",
            "type": "response_completed",
            "agent": "manager",
            "tool": None,
            "status": "success",
            "message": "Final response generated"
        }
    ]
}
