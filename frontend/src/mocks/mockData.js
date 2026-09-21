/**
 * Mock data schemas reflecting future backend responses from Azure AI / Multi-Agent orchestrator.
 * All API consumers access this via services/api.js.
 */

export const mockHealthStatus = {
  status: "ONLINE",
  provider: "Azure AI",
  latency_ms: 42,
  model: "nexus-manager-v1",
  orchestrator: "Multi-Agent Routing Mesh",
  active_agents: ["Manager Agent", "Sales Agent", "Inventory Agent", "People Management Agent"]
};

export const mockDashboardData = {
  metrics: {
    revenue: {
      value: "₹1,24,500",
      raw: 124500,
      change: "+12.4%",
      isPositive: true,
      timeframe: "vs last month"
    },
    orders: {
      value: "248",
      raw: 248,
      change: "+8.2%",
      isPositive: true,
      timeframe: "vs last month"
    },
    lowStock: {
      value: "4 products",
      count: 4,
      change: "Action needed",
      isWarning: true,
      timeframe: "below reorder level"
    },
    employees: {
      value: "36 active",
      count: 36,
      change: "3 on leave today",
      isNeutral: true,
      timeframe: "across 5 depts"
    }
  },
  businessSummary: {
    headline: "Sales performance is trending upward this month. Laptop Pro remains the strongest-selling product, while four products currently require inventory attention.",
    confidence: "98.4%",
    generatedAt: "Today at 08:30 AM",
    agentsInvolved: ["Manager", "Sales", "Inventory"]
  },
  recentActivity: [
    {
      id: "act-1",
      agent: "Sales Agent",
      action: "Analysed monthly revenue",
      timeAgo: "2 min ago",
      status: "success",
      icon: "TrendingUp"
    },
    {
      id: "act-2",
      agent: "Inventory Agent",
      action: "Checked low-stock products",
      timeAgo: "8 min ago",
      status: "success",
      icon: "Package"
    },
    {
      id: "act-3",
      agent: "Manager Agent",
      action: "Generated business summary",
      timeAgo: "12 min ago",
      status: "success",
      icon: "Brain"
    }
  ]
};

export const mockSalesData = {
  metrics: {
    monthlyRevenue: "₹1,24,500",
    unitsSold: "248",
    averageOrderValue: "₹5,020",
    growth: "+12.4%"
  },
  monthlyRevenueChart: [
    { month: "Apr", revenue: 82000, orders: 174 },
    { month: "May", revenue: 91000, orders: 195 },
    { month: "Jun", revenue: 88000, orders: 188 },
    { month: "Jul", revenue: 101000, orders: 215 },
    { month: "Aug", revenue: 110000, orders: 230 },
    { month: "Sep", revenue: 124500, orders: 248 }
  ],
  topProducts: [
    {
      id: "P101",
      name: "Laptop Pro",
      unitsSold: 27,
      revenue: "₹67,500",
      revenueRaw: 67500,
      share: "54.2%",
      trend: "+18%"
    },
    {
      id: "P102",
      name: "Wireless Headset",
      unitsSold: 42,
      revenue: "₹25,200",
      revenueRaw: 25200,
      share: "20.2%",
      trend: "+8%"
    },
    {
      id: "P103",
      name: "Mechanical Keyboard",
      unitsSold: 31,
      revenue: "₹21,700",
      revenueRaw: 21700,
      share: "17.4%",
      trend: "+12%"
    }
  ],
  recentSales: [
    { id: "ORD-7821", customer: "Apex Tech Labs", product: "Laptop Pro (x2)", amount: "₹5,000", date: "Today, 11:20", status: "Completed" },
    { id: "ORD-7820", customer: "Pinnacle Designs", product: "Wireless Headset (x4)", amount: "₹2,400", date: "Today, 10:45", status: "Completed" },
    { id: "ORD-7819", customer: "Quantix Global", product: "Mechanical Keyboard (x3)", amount: "₹2,100", date: "Today, 09:30", status: "Processing" },
    { id: "ORD-7818", customer: "Helix Software", product: "Monitor 27 (x1)", amount: "₹3,200", date: "Yesterday, 16:15", status: "Completed" },
    { id: "ORD-7817", customer: "Nexus AI Lab", product: "Laptop Pro (x1)", amount: "₹2,500", date: "Yesterday, 14:02", status: "Completed" }
  ]
};

export const mockInventoryData = {
  metrics: {
    totalProducts: 52,
    lowStock: 4,
    outOfStock: 1,
    healthyStock: 47
  },
  products: [
    {
      id: "P101",
      name: "Laptop Pro",
      stock: 4,
      reorderLevel: 10,
      status: "Low",
      category: "Compute",
      warehouse: "North-Bay Facility",
      unitPrice: "₹2,500"
    },
    {
      id: "P102",
      name: "Wireless Headset",
      stock: 31,
      reorderLevel: 12,
      status: "Healthy",
      category: "Audio",
      warehouse: "North-Bay Facility",
      unitPrice: "₹600"
    },
    {
      id: "P103",
      name: "Mechanical Keyboard",
      stock: 8,
      reorderLevel: 10,
      status: "Low",
      category: "Peripherals",
      warehouse: "East Hub",
      unitPrice: "₹700"
    },
    {
      id: "P104",
      name: "Monitor 27\"",
      stock: 24,
      reorderLevel: 8,
      status: "Healthy",
      category: "Displays",
      warehouse: "West Hub",
      unitPrice: "₹3,200"
    },
    {
      id: "P105",
      name: "USB-C Multi-Hub 8-in-1",
      stock: 0,
      reorderLevel: 15,
      status: "Out of Stock",
      category: "Accessories",
      warehouse: "East Hub",
      unitPrice: "₹450"
    },
    {
      id: "P106",
      name: "Ergonomic Precision Mouse",
      stock: 6,
      reorderLevel: 10,
      status: "Low",
      category: "Peripherals",
      warehouse: "North-Bay Facility",
      unitPrice: "₹350"
    },
    {
      id: "P107",
      name: "Studio 4K Webcam",
      stock: 5,
      reorderLevel: 10,
      status: "Low",
      category: "Video",
      warehouse: "West Hub",
      unitPrice: "₹850"
    }
  ]
};

export const mockHRData = {
  metrics: {
    employees: 36,
    onLeave: 3,
    departments: 5,
    openRequests: 4
  },
  policies: [
    {
      title: "Annual Leave",
      description: "18 days per year with up to 5 days rollover allowed into Q1.",
      category: "Time Off",
      code: "POL-HR-01"
    },
    {
      title: "Remote Work",
      description: "Up to 2 days per week with manager coordination and core hours sync.",
      category: "Workplace",
      code: "POL-HR-02"
    },
    {
      title: "Sick Leave",
      description: "10 days per year. Medical certificate requested for 3+ consecutive days.",
      category: "Health",
      code: "POL-HR-03"
    }
  ],
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

export const mockActivityLogs = [
  {
    id: "act-101",
    timestamp: "10:42",
    agent: "Sales Agent",
    action: "Retrieved top products",
    tool: "get_top_products",
    status: "Success",
    duration: "420ms",
    meta: { timeframe: "current_month", count: 3 }
  },
  {
    id: "act-102",
    timestamp: "10:43",
    agent: "Inventory Agent",
    action: "Checked inventory",
    tool: "get_product_stock",
    status: "Success",
    duration: "280ms",
    meta: { sku: "NX-LP-01", remaining: 4 }
  },
  {
    id: "act-103",
    timestamp: "10:44",
    agent: "Manager Agent",
    action: "Generated final response",
    tool: "-",
    status: "Success",
    duration: "1.2s",
    meta: { agents_used: ["sales", "inventory"] }
  },
  {
    id: "act-104",
    timestamp: "09:15",
    agent: "People Management Agent",
    action: "Looked up leave policies",
    tool: "get_hr_policy",
    status: "Success",
    duration: "310ms",
    meta: { policy: "POL-HR-01" }
  },
  {
    id: "act-105",
    timestamp: "08:30",
    agent: "Manager Agent",
    action: "Generated business summary",
    tool: "aggregate_kpis",
    status: "Success",
    duration: "2.1s",
    meta: { modules: ["sales", "inventory", "hr"] }
  },
  {
    id: "act-106",
    timestamp: "08:02",
    agent: "Inventory Agent",
    action: "Scanned stock threshold alerts",
    tool: "scan_low_stock",
    status: "Success",
    duration: "540ms",
    meta: { flagged: 4 }
  }
];

/**
 * Pre-defined canned multi-agent orchestration traces for assistant queries.
 */
export const mockAgentWorkflows = {
  compare_top_products_vs_inventory: {
    answer: "Laptop Pro is currently your strongest-selling product with 27 units sold this month, but only 4 units remain in inventory. Based on current demand, restocking should be prioritised.",
    session_id: "session_001",
    agents_used: ["sales", "inventory"],
    tool_calls: [
      {
        agent: "sales",
        tool: "get_top_products",
        status: "success",
        duration: "420ms",
        params: { limit: 3, timeframe: "current_month" },
        result: [
          { name: "Laptop Pro", unitsSold: 27, revenue: "₹67,500" },
          { name: "Wireless Headset", unitsSold: 42, revenue: "₹25,200" }
        ]
      },
      {
        agent: "inventory",
        tool: "get_product_stock",
        status: "success",
        duration: "280ms",
        params: { sku: "P101", product: "Laptop Pro" },
        result: { stock: 4, reorderLevel: 10, status: "Low" }
      }
    ],
    // The exact stepped sequence of streaming events
    events: [
      {
        id: "evt-1",
        type: "manager_started",
        agent: "Manager Agent",
        tool: null,
        status: "running",
        message: "Understanding request"
      },
      {
        id: "evt-2",
        type: "route_selected",
        agent: "Manager Agent",
        tool: null,
        status: "success",
        message: "Routed request to Sales Agent"
      },
      {
        id: "evt-3",
        type: "agent_started",
        agent: "Sales Agent",
        tool: null,
        status: "running",
        message: "Analyzing sales performance"
      },
      {
        id: "evt-4",
        type: "tool_started",
        agent: "Sales Agent",
        tool: "get_top_products()",
        status: "running",
        message: "Executing get_top_products(limit=3)"
      },
      {
        id: "evt-5",
        type: "tool_completed",
        agent: "Sales Agent",
        tool: "get_top_products()",
        status: "success",
        duration: "420ms",
        message: "Identified top product: Laptop Pro (27 units)"
      },
      {
        id: "evt-6",
        type: "agent_completed",
        agent: "Sales Agent",
        tool: null,
        status: "success",
        duration: "420ms",
        message: "Sales Agent completed"
      },
      {
        id: "evt-7",
        type: "route_selected",
        agent: "Manager Agent",
        tool: null,
        status: "success",
        message: "Routed request to Inventory Agent"
      },
      {
        id: "evt-8",
        type: "agent_started",
        agent: "Inventory Agent",
        tool: null,
        status: "running",
        message: "Checking stock levels"
      },
      {
        id: "evt-9",
        type: "tool_started",
        agent: "Inventory Agent",
        tool: "get_product_stock()",
        status: "running",
        message: "Executing get_product_stock('P101')"
      },
      {
        id: "evt-10",
        type: "tool_completed",
        agent: "Inventory Agent",
        tool: "get_product_stock()",
        status: "success",
        duration: "280ms",
        message: "Stock level critical: 4 units remaining (reorder level: 10)"
      },
      {
        id: "evt-11",
        type: "agent_completed",
        agent: "Inventory Agent",
        tool: null,
        status: "success",
        duration: "280ms",
        message: "Inventory Agent completed"
      },
      {
        id: "evt-12",
        type: "response_completed",
        agent: "Manager Agent",
        tool: null,
        status: "success",
        duration: "1.2s",
        message: "Final response generated"
      }
    ]
  },

  sales_performance: {
    answer: "Monthly revenue currently stands at ₹1,24,500 (+12.4% vs last month) with 248 units sold. Average order value is ₹5,020, led by sustained demand for Laptop Pro and high-margin accessories.",
    session_id: "session_002",
    agents_used: ["sales"],
    tool_calls: [
      {
        agent: "sales",
        tool: "get_monthly_revenue",
        status: "success",
        duration: "340ms",
        params: { month: "September" }
      }
    ],
    events: [
      { id: "sp-1", type: "manager_started", agent: "Manager Agent", status: "running", message: "Evaluating revenue query" },
      { id: "sp-2", type: "route_selected", agent: "Manager Agent", status: "success", message: "Routed to Sales Agent" },
      { id: "sp-3", type: "agent_started", agent: "Sales Agent", status: "running", message: "Querying financial registers" },
      { id: "sp-4", type: "tool_started", agent: "Sales Agent", tool: "get_monthly_revenue()", status: "running", message: "Fetching September figures" },
      { id: "sp-5", type: "tool_completed", agent: "Sales Agent", tool: "get_monthly_revenue()", status: "success", duration: "340ms", message: "Revenue confirmed at ₹1,24,500" },
      { id: "sp-6", type: "response_completed", agent: "Manager Agent", status: "success", message: "Summary prepared" }
    ]
  },

  low_stock_products: {
    answer: "Four products currently need restocking: Laptop Pro (4 units, reorder at 10), Mechanical Keyboard (8 units, reorder at 10), Ergonomic Mouse (6 units, reorder at 10), and USB-C Multi-Hub is completely Out of Stock.",
    session_id: "session_003",
    agents_used: ["inventory"],
    tool_calls: [
      {
        agent: "inventory",
        tool: "scan_low_stock",
        status: "success",
        duration: "310ms",
        params: { threshold: "reorderLevel" }
      }
    ],
    events: [
      { id: "ls-1", type: "manager_started", agent: "Manager Agent", status: "running", message: "Scanning inventory thresholds" },
      { id: "ls-2", type: "route_selected", agent: "Manager Agent", status: "success", message: "Routed to Inventory Agent" },
      { id: "ls-3", type: "agent_started", agent: "Inventory Agent", status: "running", message: "Executing warehouse scan" },
      { id: "ls-4", type: "tool_started", agent: "Inventory Agent", tool: "scan_low_stock()", status: "running", message: "Querying active catalog" },
      { id: "ls-5", type: "tool_completed", agent: "Inventory Agent", tool: "scan_low_stock()", status: "success", duration: "310ms", message: "4 SKUs flagged below threshold" },
      { id: "ls-6", type: "response_completed", agent: "Manager Agent", status: "success", message: "Low-stock warning ready" }
    ]
  },

  business_overview: {
    answer: "Business health is strong overall. Revenue is up +12.4% (₹1,24,500), orders reached 248, and People Management reports 36 active team members with 3 on approved leave. The immediate operational priority is restocking 4 depleted hardware lines.",
    session_id: "session_004",
    agents_used: ["sales", "inventory", "hr"],
    tool_calls: [
      { agent: "sales", tool: "get_monthly_revenue", status: "success", duration: "320ms" },
      { agent: "inventory", tool: "scan_low_stock", status: "success", duration: "290ms" },
      { agent: "hr", tool: "get_employee_summary", status: "success", duration: "210ms" }
    ],
    events: [
      { id: "bo-1", type: "manager_started", agent: "Manager Agent", status: "running", message: "Decomposing full business inquiry" },
      { id: "bo-2", type: "route_selected", agent: "Manager Agent", status: "success", message: "Dispatched parallel queries to Sales, Inventory, and People Management" },
      { id: "bo-3", type: "agent_started", agent: "Sales Agent", status: "running", message: "Sales audit active" },
      { id: "bo-4", type: "tool_completed", agent: "Sales Agent", tool: "get_monthly_revenue()", status: "success", duration: "320ms", message: "Revenue calculated" },
      { id: "bo-5", type: "agent_started", agent: "Inventory Agent", status: "running", message: "Warehouse audit active" },
      { id: "bo-6", type: "tool_completed", agent: "Inventory Agent", tool: "scan_low_stock()", status: "success", duration: "290ms", message: "Stock status compiled" },
      { id: "bo-7", type: "agent_started", agent: "People Management Agent", status: "running", message: "Staff census active" },
      { id: "bo-8", type: "tool_completed", agent: "People Management Agent", tool: "get_employee_summary()", status: "success", duration: "210ms", message: "36 active verified" },
      { id: "bo-9", type: "response_completed", agent: "Manager Agent", status: "success", message: "Executive synthesis complete" }
    ]
  }
};
