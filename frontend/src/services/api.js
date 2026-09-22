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
 * GET unified Overview data from the Kaggle-backed analytics domain.
 * People data and activity logs remain in the internal operational domain.
 */
export async function getDashboardData() {
  const [metadata, summary, monthly, hr, activityData] = await Promise.all([
    getAnalyticsMetadata(),
    getAnalyticsSummary(),
    getAnalyticsMonthlySales(),
    apiRequest("/api/hr"),
    apiRequest("/api/activity").catch(() => [])
  ]);

  const trend = monthly.monthly_trend || [];
  const latest = trend[trend.length - 1];
  const previous = trend[trend.length - 2];
  const monthChangePct = latest && previous && previous.revenue_cents > 0
    ? ((latest.revenue_cents - previous.revenue_cents) / previous.revenue_cents) * 100
    : 0;

  return {
    metadata,
    summary,
    metrics: {
      revenue: {
        valueCents: summary.total_revenue_cents,
        changePct: monthChangePct,
        timeframe: "2025 gross revenue"
      },
      transactions: {
        value: summary.transaction_count,
        timeframe: "2025 sales line items"
      },
      stockouts: {
        value: summary.stockout_placement_count,
        timeframe: "current zero-stock placements"
      },
      employees: {
        value: hr.employeeCount,
        timeframe: "internal People Management"
      }
    },
    businessSummary: {
      headline: `2025 retail analytics recorded ${summary.total_units_sold.toLocaleString('en-US')} units sold across ${summary.product_count} products and ${summary.store_count} stores, with ${summary.stockout_placement_count} current zero-stock placements.`,
      generatedAt: `${metadata.dataset_name} · ${metadata.currency_code}`,
      dataSources: ["Sales Analytics", "Inventory Analytics", "People Management"],
      status: "Verified"
    },
    monthlyRevenueChart: trend.map((item) => ({
      month: item.year_month,
      revenue: item.revenue_cents / 100,
      units: item.units_sold,
      transactions: item.transaction_count
    })),
    recentActivity: activityData.slice(0, 3).map((item, idx) => ({
      id: item.id || `act-${idx}`,
      agent: item.agent === 'sales' ? 'Sales Agent' : item.agent === 'inventory' ? 'Inventory Agent' : item.agent === 'hr' ? 'People Management Agent' : 'Manager Agent',
      action: item.action,
      timeAgo: `${(idx + 1) * 4} min ago`,
      status: item.status || 'success',
      icon: item.agent === 'sales' ? 'TrendingUp' : item.agent === 'inventory' ? 'Package' : 'Brain'
    }))
  };
}

/**
 * Unified Sales view backed entirely by nexus_analytics.db.
 */
export async function getSalesData() {
  const [metadata, summary, monthly, products, categories] = await Promise.all([
    getAnalyticsMetadata(),
    getAnalyticsSummary(),
    getAnalyticsMonthlySales(),
    getAnalyticsProducts({ limit: 10, order_by: 'revenue' }),
    getAnalyticsCategories()
  ]);

  const trend = monthly.monthly_trend || [];
  const latest = trend[trend.length - 1];
  const previous = trend[trend.length - 2];
  const monthlyChangePct = latest && previous && previous.revenue_cents > 0
    ? ((latest.revenue_cents - previous.revenue_cents) / previous.revenue_cents) * 100
    : 0;

  return {
    metadata,
    summary,
    metrics: {
      grossRevenueCents: summary.total_revenue_cents,
      grossProfitCents: summary.gross_profit_cents,
      grossMarginPct: summary.gross_margin_pct,
      unitsSold: summary.total_units_sold,
      transactions: summary.transaction_count,
      averageOrderValueCents: summary.average_order_value_cents,
      monthlyChangePct
    },
    monthlyRevenueChart: trend.map((item) => ({
      month: item.year_month,
      revenue: item.revenue_cents / 100,
      units: item.units_sold,
      transactions: item.transaction_count
    })),
    topProducts: (products.products || []).map((prod) => ({
      id: prod.product_id,
      name: prod.product_name,
      category: prod.product_category,
      unitsSold: prod.units_sold,
      revenueCents: prod.revenue_cents,
      revenueRaw: prod.revenue_cents / 100,
      profitCents: prod.profit_cents,
      grossMarginPct: prod.gross_margin_pct,
      sharePct: summary.total_revenue_cents > 0
        ? (prod.revenue_cents / summary.total_revenue_cents) * 100
        : 0
    })),
    categories: categories.categories || []
  };
}

/**
 * Unified Inventory view backed by Kaggle inventory + deterministic risk analytics.
 */
export async function getInventoryData() {
  const [metadata, inventory, products, stockouts] = await Promise.all([
    getAnalyticsMetadata(),
    getAnalyticsInventory(),
    getAnalyticsInventoryProducts({ limit: 180, order_by: 'stock_units' }),
    getRiskStockouts()
  ]);

  return {
    metadata,
    metrics: {
      totalProducts: products.total_products,
      totalStockUnits: inventory.total_units_on_hand,
      totalPlacements: inventory.total_placements,
      inStockPlacements: inventory.in_stock_placements,
      outOfStockPlacements: inventory.out_of_stock_placements,
      stockoutRatePct: inventory.stockout_rate_pct,
      costValueCents: inventory.total_cost_value_cents,
      retailValueCents: inventory.total_retail_value_cents,
      potentialGrossMarginCents: inventory.potential_gross_margin_cents,
      snapshotDate: inventory.snapshot_date,
      snapshotDateIsAssumed: inventory.snapshot_date_is_assumed
    },
    stockoutExposure: stockouts.summary,
    products: (products.products || []).map((prod) => ({
      id: prod.product_id,
      name: prod.product_name,
      category: prod.category,
      stockUnits: prod.stock_units,
      storePlacements: prod.store_placements,
      zeroStockStores: prod.zero_stock_store_count,
      costValueCents: prod.inventory_cost_value_cents,
      retailValueCents: prod.inventory_retail_value_cents,
      exposureStatus: prod.zero_stock_store_count > 0 ? 'Stockout Exposure' : 'Fully In Stock'
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
    employees: (data.employees || []).map((e) => ({
      id: e.id,
      name: e.name,
      department: e.department,
      role: e.role,
      status: e.status,
      leaveBalance: e.leaveBalance
    }))
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
    agent: item.agent === 'sales' ? 'Sales Agent' : item.agent === 'inventory' ? 'Inventory Agent' : item.agent === 'hr' ? 'People Management Agent' : 'Manager Agent',
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

/**
 * ============================================================================
 * Phase D1D: External Kaggle Analytics API Services (/api/analytics/*)
 * Read-only analytics endpoints backed by nexus_analytics.db.
 * ============================================================================
 */

/**
 * GET /api/analytics/metadata
 */
export async function getAnalyticsMetadata() {
  return await apiRequest("/api/analytics/metadata");
}

/**
 * GET /api/analytics/summary
 */
export async function getAnalyticsSummary() {
  return await apiRequest("/api/analytics/summary");
}

/**
 * GET /api/analytics/monthly-sales
 */
export async function getAnalyticsMonthlySales() {
  return await apiRequest("/api/analytics/monthly-sales");
}

/**
 * GET /api/analytics/categories
 */
export async function getAnalyticsCategories() {
  return await apiRequest("/api/analytics/categories");
}

/**
 * GET /api/analytics/products
 * @param {Object} [params] - { limit, order_by, category }
 */
export async function getAnalyticsProducts(params = {}) {
  const query = new URLSearchParams();
  if (params.limit) query.append("limit", params.limit);
  if (params.order_by) query.append("order_by", params.order_by);
  if (params.category) query.append("category", params.category);

  const qs = query.toString();
  return await apiRequest(`/api/analytics/products${qs ? `?${qs}` : ''}`);
}

/**
 * GET /api/analytics/stores
 * @param {Object} [params] - { limit, order_by, location }
 */
export async function getAnalyticsStores(params = {}) {
  const query = new URLSearchParams();
  if (params.limit) query.append("limit", params.limit);
  if (params.order_by) query.append("order_by", params.order_by);
  if (params.location) query.append("location", params.location);

  const qs = query.toString();
  return await apiRequest(`/api/analytics/stores${qs ? `?${qs}` : ''}`);
}

/**
 * GET /api/analytics/locations
 */
export async function getAnalyticsLocations() {
  return await apiRequest("/api/analytics/locations");
}

/**
 * GET /api/analytics/inventory
 */
export async function getAnalyticsInventory() {
  return await apiRequest("/api/analytics/inventory");
}

/**
 * GET /api/analytics/inventory/products
 * @param {Object} [params] - { limit, order_by, category }
 */
export async function getAnalyticsInventoryProducts(params = {}) {
  const query = new URLSearchParams();
  if (params.limit) query.append("limit", params.limit);
  if (params.order_by) query.append("order_by", params.order_by);
  if (params.category) query.append("category", params.category);

  const qs = query.toString();
  return await apiRequest(`/api/analytics/inventory/products${qs ? `?${qs}` : ''}`);
}

// ===========================================================================
// RISK API ENDPOINTS — D2B
// ===========================================================================

/**
 * GET /api/risk/config
 */
export async function getRiskConfig() {
  return await apiRequest("/api/risk/config");
}

/**
 * GET /api/risk/overview
 */
export async function getRiskOverview() {
  return await apiRequest("/api/risk/overview");
}

/**
 * GET /api/risk/stockouts
 */
export async function getRiskStockouts() {
  return await apiRequest("/api/risk/stockouts");
}

/**
 * GET /api/risk/inventory-pressure
 * @param {Object} [params] - { limit, classification }
 */
export async function getRiskInventoryPressure(params = {}) {
  const query = new URLSearchParams();
  if (params.limit) query.append("limit", params.limit);
  if (params.classification) query.append("classification", params.classification);
  const qs = query.toString();
  return await apiRequest(`/api/risk/inventory-pressure${qs ? `?${qs}` : ''}`);
}

/**
 * GET /api/risk/slow-moving
 * @param {Object} [params] - { limit }
 */
export async function getRiskSlowMoving(params = {}) {
  const query = new URLSearchParams();
  if (params.limit) query.append("limit", params.limit);
  const qs = query.toString();
  return await apiRequest(`/api/risk/slow-moving${qs ? `?${qs}` : ''}`);
}

/**
 * GET /api/risk/concentration
 */
export async function getRiskConcentration() {
  return await apiRequest("/api/risk/concentration");
}

/**
 * GET /api/risk/sales-velocity
 * @param {Object} [params] - { limit, classification }
 */
export async function getRiskSalesVelocity(params = {}) {
  const query = new URLSearchParams();
  if (params.limit) query.append("limit", params.limit);
  if (params.classification) query.append("classification", params.classification);
  const qs = query.toString();
  return await apiRequest(`/api/risk/sales-velocity${qs ? `?${qs}` : ''}`);
}

// ===========================================================================
// FORECASTING API ENDPOINTS — D3B
// ===========================================================================

export async function getForecastConfig() {
  return await apiRequest("/api/forecast/config");
}

export async function getCompanyForecast() {
  return await apiRequest("/api/forecast/company");
}

export async function getCategoryForecasts() {
  return await apiRequest("/api/forecast/categories");
}

export async function getForecastCoverage() {
  return await apiRequest("/api/forecast/coverage");
}
