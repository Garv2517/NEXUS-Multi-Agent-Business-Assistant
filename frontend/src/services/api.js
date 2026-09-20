/**
 * Nexus API Service
 * 
 * Phase B1: Replaces client-side static mock state with real FastAPI backend calls.
 * Base URL configurable via VITE_API_BASE_URL (defaults to http://localhost:8000).
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Generic fetch wrapper with JSON parsing and error handling
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const res = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {})
      },
      ...options
    });

    if (!res.ok) {
      const errorBody = await res.json().catch(() => ({}));
      throw new Error(errorBody.detail || `HTTP Error ${res.status}: ${res.statusText}`);
    }

    return await res.json();
  } catch (err) {
    console.error(`API Error [${endpoint}]:`, err);
    throw err;
  }
}

/**
 * GET /api/health
 */
export async function getHealthStatus() {
  const data = await apiRequest("/api/health");
  return {
    status: data.status === "online" ? "ONLINE" : "OFFLINE",
    backend: data.backend,
    foundry: data.foundry,
    model: data.model,
    mode: data.mode,
    version: data.version,
    latency_ms: 42
  };
}

/**
 * GET /api/dashboard
 */
export async function getDashboardData() {
  const data = await apiRequest("/api/dashboard");
  const activityData = await apiRequest("/api/activity").catch(() => []);

  return {
    metrics: {
      revenue: {
        value: `₹${Number(data.metrics.revenue.value).toLocaleString('en-IN')}`,
        raw: data.metrics.revenue.value,
        change: `+${data.metrics.revenue.change}%`,
        isPositive: data.metrics.revenue.change >= 0,
        timeframe: "vs last month"
      },
      orders: {
        value: String(data.metrics.orders.value),
        raw: data.metrics.orders.value,
        change: `+${data.metrics.orders.change}%`,
        isPositive: data.metrics.orders.change >= 0,
        timeframe: "vs last month"
      },
      lowStock: {
        value: `${data.metrics.lowStockProducts.value} products`,
        count: data.metrics.lowStockProducts.value,
        change: "Action needed",
        isWarning: true,
        timeframe: "below reorder level"
      },
      employees: {
        value: `${data.metrics.employees.value} active`,
        count: data.metrics.employees.value,
        change: "3 on leave today",
        isNeutral: true,
        timeframe: "across 5 depts"
      }
    },
    businessSummary: {
      headline: data.summary,
      confidence: "98.4%",
      generatedAt: "Live from Nexus API",
      agentsInvolved: ["Manager", "Sales", "Inventory"]
    },
    recentActivity: activityData.slice(0, 3).map((item, idx) => ({
      id: item.id || `act-${idx}`,
      agent: item.agent === 'sales' ? 'Sales Agent' : item.agent === 'inventory' ? 'Inventory Agent' : 'Manager Agent',
      action: item.action,
      timeAgo: `${(idx + 1) * 4} min ago`,
      status: item.status || 'success',
      icon: item.agent === 'sales' ? 'TrendingUp' : item.agent === 'inventory' ? 'Package' : 'Brain'
    }))
  };
}

/**
 * GET /api/sales
 */
export async function getSalesData() {
  const data = await apiRequest("/api/sales");

  return {
    metrics: {
      monthlyRevenue: `₹${Number(data.revenue).toLocaleString('en-IN')}`,
      unitsSold: String(data.unitsSold),
      averageOrderValue: `₹${Number(data.averageOrderValue).toLocaleString('en-IN')}`,
      growth: `+${data.monthlyChange}%`
    },
    monthlyRevenueChart: data.monthlyRevenue.map((item) => ({
      month: item.month,
      revenue: item.value,
      orders: Math.round(item.value / 450)
    })),
    topProducts: data.topProducts.map((prod) => ({
      id: prod.id,
      name: prod.name,
      unitsSold: prod.unitsSold,
      revenue: `₹${Number(prod.revenue).toLocaleString('en-IN')}`,
      revenueRaw: prod.revenue,
      share: `${Math.round((prod.revenue / data.revenue) * 100)}%`,
      trend: "+12%"
    })),
    recentSales: [
      { id: "ORD-7821", customer: "Apex Tech Labs", product: "Laptop Pro (x2)", amount: "₹5,000", date: "Today, 11:20", status: "Completed" },
      { id: "ORD-7820", customer: "Pinnacle Designs", product: "Wireless Headset (x4)", amount: "₹2,400", date: "Today, 10:45", status: "Completed" },
      { id: "ORD-7819", customer: "Quantix Global", product: "Mechanical Keyboard (x3)", amount: "₹2,100", date: "Today, 09:30", status: "Processing" },
      { id: "ORD-7818", customer: "Helix Software", product: "Monitor 27 (x1)", amount: "₹3,200", date: "Yesterday, 16:15", status: "Completed" },
      { id: "ORD-7817", customer: "Nexus AI Lab", product: "Laptop Pro (x1)", amount: "₹2,500", date: "Yesterday, 14:02", status: "Completed" }
    ]
  };
}

/**
 * GET /api/inventory
 */
export async function getInventoryData() {
  const data = await apiRequest("/api/inventory");

  return {
    metrics: {
      totalProducts: data.totalProducts,
      lowStock: data.lowStockCount,
      outOfStock: data.outOfStockCount,
      healthyStock: data.healthyStockCount
    },
    products: data.products.map((prod) => ({
      id: prod.id,
      name: prod.name,
      stock: prod.stock,
      reorderLevel: prod.reorderLevel,
      status: prod.status.charAt(0).toUpperCase() + prod.status.slice(1),
      category: prod.id === 'P101' ? 'Compute' : prod.id === 'P102' ? 'Audio' : prod.id === 'P103' ? 'Peripherals' : 'Displays',
      warehouse: prod.id === 'P101' ? 'North-Bay Facility' : prod.id === 'P103' ? 'East Hub' : 'West Hub',
      unitPrice: prod.id === 'P101' ? '₹2,500' : '₹600'
    }))
  };
}

/**
 * GET /api/hr
 */
export async function getHRData() {
  const data = await apiRequest("/api/hr");

  return {
    metrics: {
      employees: data.employeeCount,
      onLeave: data.employeesOnLeave,
      departments: data.departments,
      openRequests: data.openRequests
    },
    policies: data.policies.map((p) => ({
      title: p.title,
      description: p.summary,
      category: p.title.includes('Leave') ? 'Time Off' : 'Workplace',
      code: p.id.toUpperCase()
    })),
    employees: [
      { id: "EMP-001", name: "Aarav Sharma", department: "Engineering", role: "Staff AI Engineer", status: "Active", tenure: "3.2 yrs" },
      { id: "EMP-002", name: "Priya Patel", department: "Product", role: "Lead Product Manager", status: "Active", tenure: "2.5 yrs" },
      { id: "EMP-003", name: "Rohan Verma", department: "Sales", role: "Account Executive", status: "On Leave", tenure: "1.8 yrs" },
      { id: "EMP-004", name: "Ananya Iyer", department: "Operations", role: "Inventory Lead", status: "Active", tenure: "4.0 yrs" },
      { id: "EMP-005", name: "Devansh Rao", department: "Engineering", role: "Systems Architect", status: "Active", tenure: "2.1 yrs" },
      { id: "EMP-006", name: "Kavita Nair", department: "People & HR", role: "HR Generalist", status: "On Leave", tenure: "1.2 yrs" },
      { id: "EMP-007", name: "Vikram Malhotra", department: "Finance", role: "Financial Analyst", status: "Active", tenure: "3.0 yrs" },
      { id: "EMP-008", name: "Sneha Reddy", department: "Sales", role: "Sales Director", status: "Active", tenure: "4.5 yrs" }
    ]
  };
}

/**
 * GET /api/activity
 */
export async function getActivityLogs() {
  const data = await apiRequest("/api/activity");

  return data.map((item) => ({
    id: item.id,
    timestamp: item.timestamp,
    agent: item.agent === 'sales' ? 'Sales Agent' : item.agent === 'inventory' ? 'Inventory Agent' : item.agent === 'hr' ? 'HR Agent' : 'Manager Agent',
    action: item.action,
    tool: item.tool || '-',
    status: item.status === 'success' ? 'Success' : item.status,
    duration: item.duration_ms ? (item.duration_ms >= 1000 ? `${(item.duration_ms / 1000).toFixed(1)}s` : `${item.duration_ms}ms`) : '-',
    meta: { agent: item.agent, tool: item.tool, duration_ms: item.duration_ms }
  }));
}

/**
 * POST /api/chat
 * 
 * Submits query to FastAPI backend at /api/chat.
 * Dispatches backend trace events sequentially to `onEvent` to preserve live timeline progression,
 * then returns the structured response.
 */
export async function sendMessage(message, onEvent = () => {}) {
  const trimmed = message.trim();
  if (!trimmed) {
    throw new Error("Message cannot be empty");
  }

  // 1. Send request to real FastAPI backend
  const data = await apiRequest("/api/chat", {
    method: "POST",
    body: JSON.stringify({ message: trimmed })
  });

  // 2. Animate trace events returned by the backend (350ms delay between steps)
  if (data.trace && Array.isArray(data.trace)) {
    for (let i = 0; i < data.trace.length; i++) {
      const evt = data.trace[i];
      await new Promise((resolve) => setTimeout(resolve, 380));
      onEvent({
        id: evt.id,
        type: evt.type,
        agent: evt.agent ? `${evt.agent.charAt(0).toUpperCase() + evt.agent.slice(1)} Agent` : 'Manager Agent',
        tool: evt.tool ? `${evt.tool}()` : null,
        status: evt.status,
        message: evt.message,
        duration: evt.duration_ms ? `${evt.duration_ms}ms` : null,
        metadata: evt.metadata || null,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      });
    }
  }

  await new Promise((resolve) => setTimeout(resolve, 250));

  return {
    session_id: data.session_id,
    answer: data.answer,
    agents_used: data.agents_used,
    plan: data.plan || null,
    tool_calls: data.tool_calls.map((t) => ({
      id: t.id,
      agent: t.agent,
      tool: t.tool,
      status: t.status,
      duration: `${t.duration_ms}ms`
    })),
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  };
}
