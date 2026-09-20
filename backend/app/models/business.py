from typing import List, Optional
from pydantic import BaseModel, Field


# --- Health Models ---
class HealthResponse(BaseModel):
    status: str = Field(default="online")
    backend: str = Field(default="ready")
    foundry: str = Field(default="not_configured")
    model: str = Field(default="not_configured")
    mode: str = Field(default="mock")
    version: str = Field(default="0.1.0")


# --- Dashboard Models ---
class RevenueMetric(BaseModel):
    value: float = Field(..., description="Total monthly revenue")
    currency: str = Field(default="INR", description="Currency code")
    change: float = Field(..., description="Percentage change compared to previous month")


class OrdersMetric(BaseModel):
    value: int = Field(..., description="Total order volume")
    change: float = Field(..., description="Percentage change compared to previous month")


class CountMetric(BaseModel):
    value: int = Field(..., description="Count of items/employees")


class DashboardMetrics(BaseModel):
    revenue: RevenueMetric
    orders: OrdersMetric
    lowStockProducts: CountMetric
    employees: CountMetric


class DashboardResponse(BaseModel):
    metrics: DashboardMetrics
    summary: str = Field(..., description="Synthesized executive business summary")


# --- Sales Models ---
class MonthlyRevenuePoint(BaseModel):
    month: str = Field(..., description="Abbreviated month name (e.g. Apr)")
    value: float = Field(..., description="Revenue generated in that month")


class TopProduct(BaseModel):
    id: str = Field(..., description="Product SKU ID")
    name: str = Field(..., description="Product name")
    unitsSold: int = Field(..., description="Quantity sold")
    revenue: float = Field(..., description="Gross revenue generated")


class SalesResponse(BaseModel):
    revenue: float
    monthlyChange: float
    unitsSold: int
    averageOrderValue: float
    monthlyRevenue: List[MonthlyRevenuePoint]
    topProducts: List[TopProduct]


# --- Inventory Models ---
class InventoryProduct(BaseModel):
    id: str
    name: str
    stock: int
    reorderLevel: int
    status: str


class InventoryResponse(BaseModel):
    totalProducts: int
    lowStockCount: int
    outOfStockCount: int
    healthyStockCount: int
    products: List[InventoryProduct]


# --- HR Models ---
class HRPolicy(BaseModel):
    id: str
    title: str
    summary: str


class HRResponse(BaseModel):
    employeeCount: int
    employeesOnLeave: int
    departments: int
    openRequests: int
    policies: List[HRPolicy]


# --- Activity Models ---
class ActivityLogItem(BaseModel):
    id: str
    timestamp: str
    agent: str
    action: str
    tool: Optional[str] = None
    status: str = "success"
    duration_ms: Optional[int] = None
