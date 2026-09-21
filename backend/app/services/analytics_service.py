from typing import Optional, List
from ..repositories.analytics_repository import AnalyticsRepository, AnalyticsDatabaseNotFoundError
from ..models.analytics import (
    AnalyticsMetadata,
    CompanySummary,
    MonthlySalesPoint,
    MonthlySalesResponse,
    CategoryPerformanceItem,
    CategoryPerformanceResponse,
    ProductPerformanceItem,
    ProductPerformanceResponse,
    StorePerformanceItem,
    StorePerformanceResponse,
    LocationPerformanceItem,
    LocationPerformanceResponse,
    InventoryAnalyticsModel,
    InventoryProductItem,
    InventoryProductResponse
)


class AnalyticsService:
    """
    Business service layer for Kaggle retail analytics.
    Exposes typed, read-only analytics domain operations backed by AnalyticsRepository.
    Preserves USD metadata and integer-cents monetary precision.
    """

    def __init__(self, repository: Optional[AnalyticsRepository] = None):
        self.repository = repository or AnalyticsRepository()

    def get_metadata(self) -> AnalyticsMetadata:
        """Returns provenance and operational assumptions of the external dataset."""
        data = self.repository.get_metadata()
        if not data:
            raise AnalyticsDatabaseNotFoundError(
                "Analytics metadata record not found in nexus_analytics.db. "
                "Database may be corrupted or uninitialized."
            )
        return AnalyticsMetadata(**data)

    def get_company_summary(self) -> CompanySummary:
        """Returns executive company totals, gross profit, margin, and order metrics."""
        data = self.repository.get_company_summary()
        return CompanySummary(**data)

    def get_monthly_sales(self) -> MonthlySalesResponse:
        """Returns chronological monthly sales trend across the dataset window."""
        rows = self.repository.get_monthly_sales()
        points = [MonthlySalesPoint(**row) for row in rows]
        return MonthlySalesResponse(
            currency_code="USD",
            total_months=len(points),
            monthly_trend=points
        )

    def get_category_performance(self) -> CategoryPerformanceResponse:
        """Returns category-level revenue, unit volumes, and revenue share."""
        rows = self.repository.get_category_performance()
        items = [CategoryPerformanceItem(**row) for row in rows]
        return CategoryPerformanceResponse(
            currency_code="USD",
            categories=items
        )

    def get_product_performance(
        self,
        limit: Optional[int] = None,
        order_by: str = "revenue",
        category: Optional[str] = None
    ) -> ProductPerformanceResponse:
        """
        Returns SKU-level sales, gross revenue, and profitability metrics.
        Supported order_by: 'revenue', 'units', 'profit', 'margin'.
        """
        rows = self.repository.get_product_performance(
            limit=limit,
            order_by=order_by,
            category=category
        )
        items = [ProductPerformanceItem(**row) for row in rows]
        return ProductPerformanceResponse(
            currency_code="USD",
            total_products=len(items),
            products=items
        )

    def get_store_performance(
        self,
        limit: Optional[int] = None,
        order_by: str = "revenue",
        location: Optional[str] = None
    ) -> StorePerformanceResponse:
        """
        Returns store-level transaction counts, volume, and revenue rankings.
        Supported order_by: 'revenue', 'units', 'profit', 'transactions'.
        """
        rows = self.repository.get_store_performance(
            limit=limit,
            order_by=order_by,
            location=location
        )
        items = [StorePerformanceItem(**row) for row in rows]
        return StorePerformanceResponse(
            currency_code="USD",
            total_stores=len(items),
            stores=items
        )

    def get_location_performance(self) -> LocationPerformanceResponse:
        """Returns performance aggregated across commercial location zoning types."""
        rows = self.repository.get_location_performance()
        items = [LocationPerformanceItem(**row) for row in rows]
        return LocationPerformanceResponse(
            currency_code="USD",
            locations=items
        )

    def get_inventory_analytics(self) -> InventoryAnalyticsModel:
        """Returns point-in-time warehouse and store inventory valuation and health."""
        data = self.repository.get_inventory_analytics()
        return InventoryAnalyticsModel(**data)

    def get_inventory_by_product(
        self,
        limit: Optional[int] = 10,
        order_by: str = "stock_units",
        category: Optional[str] = None
    ) -> InventoryProductResponse:
        """Returns product-level inventory metrics across all store placements."""
        rows = self.repository.get_inventory_by_product(
            limit=limit,
            order_by=order_by,
            category=category
        )
        items = [InventoryProductItem(**row) for row in rows]
        return InventoryProductResponse(
            currency_code="USD",
            total_products=len(items),
            products=items
        )
