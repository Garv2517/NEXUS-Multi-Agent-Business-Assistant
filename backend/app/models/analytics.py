from decimal import Decimal
from typing import List, Optional, Any
from pydantic import BaseModel, Field, model_validator


# --- Metadata Model ---
class AnalyticsMetadata(BaseModel):
    dataset_name: str = Field(..., description="Name of external dataset")
    dataset_source: str = Field(..., description="Origin platform or source")
    dataset_nature: str = Field(..., description="Synthetic or operational categorization")
    license: str = Field(..., description="Dataset usage license")
    currency_code: str = Field(default="USD", description="Canonical monetary ISO code")
    sales_start_date: str = Field(..., description="Earliest recorded sales date (YYYY-MM-DD)")
    sales_end_date: str = Field(..., description="Latest recorded sales date (YYYY-MM-DD)")
    inventory_snapshot_date: str = Field(..., description="Point-in-time inventory date (YYYY-MM-DD)")
    inventory_snapshot_date_is_assumed: bool = Field(..., description="Whether inventory date is an analytical assumption")
    stores_sha256: str = Field(..., description="SHA-256 hash of stores source file")
    products_sha256: str = Field(..., description="SHA-256 hash of products source file")
    inventory_sha256: str = Field(..., description="SHA-256 hash of inventory source file")
    sales_sha256: str = Field(..., description="SHA-256 hash of sales source file")
    loaded_at: str = Field(..., description="UTC ISO-8601 ingestion timestamp")
    notes: Optional[str] = Field(default=None, description="Analytical limitations and dataset notes")


# --- Company Performance Summary Model ---
class CompanySummary(BaseModel):
    currency_code: str = Field(default="USD", description="Currency code")
    total_revenue_cents: int = Field(..., description="Total sales gross revenue in minor currency units (cents)")
    total_cogs_cents: int = Field(..., description="Total cost of goods sold in minor currency units (cents)")
    gross_profit_cents: int = Field(..., description="Total gross profit in minor currency units (cents)")
    total_profit_cents: Optional[int] = Field(default=None, description="Alias for gross_profit_cents")
    total_units_sold: int = Field(..., description="Total quantity of products sold")
    transaction_count: int = Field(..., description="Total number of transaction line items")
    total_transactions: Optional[int] = Field(default=None, description="Alias for transaction_count")
    gross_margin_pct: float = Field(..., description="Gross margin percentage (profit / revenue * 100)")
    average_order_value_cents: int = Field(..., description="Average order value in cents")
    store_count: int = Field(..., description="Count of distinct selling stores")
    total_stores: Optional[int] = Field(default=None, description="Alias for store_count")
    product_count: int = Field(..., description="Count of distinct selling products")
    total_products: Optional[int] = Field(default=None, description="Alias for product_count")
    category_count: int = Field(..., description="Count of distinct product categories")
    inventory_units: int = Field(..., description="Total units of inventory currently on hand")
    stockout_placement_count: int = Field(..., description="Total store-product placements currently at zero stock")
    sales_start_date: str = Field(..., description="Start date of dataset sales window")
    sales_end_date: str = Field(..., description="End date of dataset sales window")

    @model_validator(mode="before")
    @classmethod
    def sync_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "total_stores" in data and "store_count" not in data:
                data["store_count"] = data["total_stores"]
            elif "store_count" in data and "total_stores" not in data:
                data["total_stores"] = data["store_count"]

            if "total_products" in data and "product_count" not in data:
                data["product_count"] = data["total_products"]
            elif "product_count" in data and "total_products" not in data:
                data["total_products"] = data["product_count"]

            if "total_transactions" in data and "transaction_count" not in data:
                data["transaction_count"] = data["total_transactions"]
            elif "transaction_count" in data and "total_transactions" not in data:
                data["total_transactions"] = data["transaction_count"]

            if "total_profit_cents" in data and "gross_profit_cents" not in data:
                data["gross_profit_cents"] = data["total_profit_cents"]
            elif "gross_profit_cents" in data and "total_profit_cents" not in data:
                data["total_profit_cents"] = data["gross_profit_cents"]
        return data

    @property
    def revenue_usd(self) -> float:
        return round(self.total_revenue_cents / 100.0, 2)

    @property
    def cogs_usd(self) -> float:
        return round(self.total_cogs_cents / 100.0, 2)

    @property
    def profit_usd(self) -> float:
        return round(self.gross_profit_cents / 100.0, 2)

    @property
    def aov_usd(self) -> float:
        return round(self.average_order_value_cents / 100.0, 2)


# --- Monthly Sales Models ---
class MonthlySalesPoint(BaseModel):
    year_month: str = Field(..., description="Period identifier (YYYY-MM)")
    revenue_cents: int = Field(..., description="Gross monthly sales in cents")
    cogs_cents: int = Field(..., description="Total monthly COGS in cents")
    profit_cents: int = Field(..., description="Total monthly gross profit in cents")
    units_sold: int = Field(..., description="Total units sold in period")
    transaction_count: int = Field(..., description="Count of transactions in period")
    gross_margin_pct: float = Field(..., description="Gross margin percentage")
    average_order_value_cents: int = Field(..., description="Average order value in cents")

    @property
    def revenue_usd(self) -> float:
        return round(self.revenue_cents / 100.0, 2)

    @property
    def profit_usd(self) -> float:
        return round(self.profit_cents / 100.0, 2)


class MonthlySalesResponse(BaseModel):
    currency_code: str = Field(default="USD")
    total_months: int = Field(...)
    monthly_trend: List[MonthlySalesPoint] = Field(default_factory=list)


# --- Category Performance Models ---
class CategoryPerformanceItem(BaseModel):
    category: str = Field(..., description="Product category name")
    product_count: int = Field(..., description="Number of unique products in category")
    units_sold: int = Field(..., description="Total units sold in category")
    revenue_cents: int = Field(..., description="Total category revenue in cents")
    cogs_cents: int = Field(..., description="Total category COGS in cents")
    profit_cents: int = Field(..., description="Total category gross profit in cents")
    gross_margin_pct: float = Field(..., description="Gross margin percentage")
    revenue_share_pct: float = Field(..., description="Share of total company revenue")

    @property
    def revenue_usd(self) -> float:
        return round(self.revenue_cents / 100.0, 2)

    @property
    def profit_usd(self) -> float:
        return round(self.profit_cents / 100.0, 2)


class CategoryPerformanceResponse(BaseModel):
    currency_code: str = Field(default="USD")
    categories: List[CategoryPerformanceItem] = Field(default_factory=list)


# --- Product Performance Models ---
class ProductPerformanceItem(BaseModel):
    product_id: int = Field(..., description="Product identifier")
    product_name: str = Field(..., description="Product title")
    product_category: str = Field(..., description="Product category")
    product_cost_cents: int = Field(..., description="Unit cost in cents")
    product_price_cents: int = Field(..., description="Unit retail price in cents")
    units_sold: int = Field(..., description="Total units sold")
    revenue_cents: int = Field(..., description="Total revenue generated in cents")
    cogs_cents: int = Field(..., description="Total cost of goods sold in cents")
    profit_cents: int = Field(..., description="Total gross profit in cents")
    gross_margin_pct: float = Field(..., description="Gross margin percentage")

    @property
    def price_usd(self) -> float:
        return round(self.product_price_cents / 100.0, 2)

    @property
    def cost_usd(self) -> float:
        return round(self.product_cost_cents / 100.0, 2)

    @property
    def revenue_usd(self) -> float:
        return round(self.revenue_cents / 100.0, 2)

    @property
    def profit_usd(self) -> float:
        return round(self.profit_cents / 100.0, 2)


class ProductPerformanceResponse(BaseModel):
    currency_code: str = Field(default="USD")
    total_products: int = Field(...)
    products: List[ProductPerformanceItem] = Field(default_factory=list)


# --- Store Performance Models ---
class StorePerformanceItem(BaseModel):
    store_id: int = Field(..., description="Store identifier")
    store_name: str = Field(..., description="Commercial title")
    store_city: str = Field(..., description="City location")
    store_location: str = Field(..., description="Commercial zoning type")
    store_open_date: str = Field(..., description="Recorded opening date (YYYY-MM-DD)")
    units_sold: int = Field(..., description="Total units sold")
    revenue_cents: int = Field(..., description="Total gross revenue in cents")
    profit_cents: int = Field(..., description="Total gross profit in cents")
    transaction_count: int = Field(..., description="Number of sales transactions")
    average_order_value_cents: int = Field(..., description="Average order value in cents")

    @property
    def revenue_usd(self) -> float:
        return round(self.revenue_cents / 100.0, 2)

    @property
    def profit_usd(self) -> float:
        return round(self.profit_cents / 100.0, 2)


class StorePerformanceResponse(BaseModel):
    currency_code: str = Field(default="USD")
    total_stores: int = Field(...)
    stores: List[StorePerformanceItem] = Field(default_factory=list)


# --- Location Performance Models ---
class LocationPerformanceItem(BaseModel):
    store_location: str = Field(..., description="Location category (e.g. Downtown, Mall)")
    store_count: int = Field(..., description="Number of stores in location type")
    units_sold: int = Field(..., description="Total units sold across location")
    revenue_cents: int = Field(..., description="Total revenue generated in cents")
    profit_cents: int = Field(..., description="Total profit generated in cents")
    gross_margin_pct: float = Field(..., description="Gross margin percentage")
    revenue_share_pct: float = Field(..., description="Share of total company revenue")

    @property
    def revenue_usd(self) -> float:
        return round(self.revenue_cents / 100.0, 2)

    @property
    def profit_usd(self) -> float:
        return round(self.profit_cents / 100.0, 2)


class LocationPerformanceResponse(BaseModel):
    currency_code: str = Field(default="USD")
    locations: List[LocationPerformanceItem] = Field(default_factory=list)


# --- Inventory Analytics Models ---
class InventoryAnalyticsModel(BaseModel):
    currency_code: str = Field(default="USD")
    snapshot_date: str = Field(..., description="Effective snapshot date (YYYY-MM-DD)")
    snapshot_date_is_assumed: bool = Field(..., description="Whether snapshot date is an analytical assumption")
    total_units_on_hand: int = Field(..., description="Total stock count across all placements")
    total_cost_value_cents: int = Field(..., description="Cost valuation of inventory in cents")
    total_retail_value_cents: int = Field(..., description="Retail selling valuation of inventory in cents")
    potential_gross_margin_cents: int = Field(..., description="Potential margin (retail - cost) in cents")
    potential_gross_margin_pct: float = Field(..., description="Potential margin percentage")
    total_placements: int = Field(..., description="Total store-SKU inventory placements")
    zero_stock_placements: int = Field(..., description="Placements with stock_on_hand = 0")
    healthy_stock_placements: int = Field(..., description="Placements with stock_on_hand > 0")
    stockout_rate_pct: float = Field(..., description="Percentage of placements out of stock")

    @property
    def cost_value_usd(self) -> float:
        return round(self.total_cost_value_cents / 100.0, 2)

    @property
    def retail_value_usd(self) -> float:
        return round(self.total_retail_value_cents / 100.0, 2)

    @property
    def potential_margin_usd(self) -> float:
        return round(self.potential_gross_margin_cents / 100.0, 2)


# --- Inventory-By-Product Models ---
class InventoryProductItem(BaseModel):
    product_id: int = Field(..., description="Product identifier")
    product_name: str = Field(..., description="Product title")
    category: str = Field(..., description="Product category")
    store_placements: int = Field(..., description="Number of stores carrying this product")
    stock_units: int = Field(..., description="Total units of stock across all stores")
    inventory_cost_value_cents: int = Field(..., description="Total cost value of current stock in cents")
    inventory_retail_value_cents: int = Field(..., description="Total retail value of current stock in cents")
    zero_stock_store_count: int = Field(default=0, description="Count of stores with zero stock for this product")

    @property
    def cost_value_usd(self) -> float:
        return round(self.inventory_cost_value_cents / 100.0, 2)

    @property
    def retail_value_usd(self) -> float:
        return round(self.inventory_retail_value_cents / 100.0, 2)


class InventoryProductResponse(BaseModel):
    currency_code: str = Field(default="USD", description="Currency ISO code")
    total_products: int = Field(..., description="Number of products returned")
    products: List[InventoryProductItem] = Field(default_factory=list)
