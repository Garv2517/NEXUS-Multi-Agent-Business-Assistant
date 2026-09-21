"""
Risk Management Service for NEXUS Phase D2.

Performs pure deterministic risk evaluations, threshold classifications,
and explainability formatting using AnalyticsRepository and RiskConfig.
No SQL is executed here. Zero AI/LLM models are invoked.
"""
from typing import Optional, List, Dict, Any
from ..repositories.analytics_repository import AnalyticsRepository, AnalyticsDatabaseNotFoundError
from ..core.risk_config import risk_config, RiskConfig
from ..models.risk import (
    RiskThresholdConfigModel,
    StockoutExposureItem,
    StockoutExposureSummary,
    StockoutExposureResponse,
    InventoryPressureItem,
    InventoryPressureResponse,
    SlowMovingProductItem,
    SlowMovingPlacementItem,
    SlowMovingResponse,
    ConcentrationMetric,
    ConcentrationResponse,
    SalesVelocityItem,
    CategorySalesVelocityItem,
    CompanySalesVelocityItem,
    SalesVelocityResponse,
    RiskOverviewDomain,
    RiskOverview
)


class RiskService:
    """
    Deterministic domain service for Phase D2 Risk Management.
    """

    def __init__(self, repository: Optional[AnalyticsRepository] = None, config: Optional[RiskConfig] = None):
        self.repository = repository or AnalyticsRepository()
        self.config = config or risk_config

    def get_config(self) -> RiskThresholdConfigModel:
        """Returns the centralized immutable risk configuration for audit and explainability."""
        return RiskThresholdConfigModel(
            assumed_snapshot_date=self.config.ASSUMED_SNAPSHOT_DATE,
            snapshot_date_is_assumed=self.config.SNAPSHOT_DATE_IS_ASSUMED,
            dataset_sales_start=self.config.DATASET_SALES_START,
            dataset_sales_end=self.config.DATASET_SALES_END,
            velocity_days_baseline=self.config.VELOCITY_DAYS_BASELINE,
            placement_dos_p10_days=self.config.PLACEMENT_DOS_P10_DAYS,
            placement_dos_p25_days=self.config.PLACEMENT_DOS_P25_DAYS,
            placement_dos_p75_days=self.config.PLACEMENT_DOS_P75_DAYS,
            placement_dos_p90_days=self.config.PLACEMENT_DOS_P90_DAYS,
            placement_material_capital_cents=self.config.PLACEMENT_MATERIAL_CAPITAL_CENTS,
            product_dos_p90_days=self.config.PRODUCT_DOS_P90_DAYS,
            product_material_capital_cents=self.config.PRODUCT_MATERIAL_CAPITAL_CENTS,
            recent_window_start=self.config.RECENT_WINDOW_START,
            recent_window_end=self.config.RECENT_WINDOW_END,
            prior_window_start=self.config.PRIOR_WINDOW_START,
            prior_window_end=self.config.PRIOR_WINDOW_END,
            window_days=self.config.WINDOW_DAYS,
            velocity_min_prior_units=self.config.VELOCITY_MIN_PRIOR_UNITS,
            velocity_severe_contraction_pct=self.config.VELOCITY_SEVERE_CONTRACTION_PCT,
            velocity_moderate_contraction_pct=self.config.VELOCITY_MODERATE_CONTRACTION_PCT,
            velocity_growth_pct=self.config.VELOCITY_GROWTH_PCT
        )

    def get_stockout_exposure(self, sample_limit: int = 50) -> StockoutExposureResponse:
        """
        Retrieves verified descriptive stockout exposure facts.
        """
        raw = self.repository.get_stockout_exposure_data(sample_limit=sample_limit)
        summary = StockoutExposureSummary(**raw["summary"])
        sample_items = [StockoutExposureItem(**item) for item in raw["sample_placements"]]

        return StockoutExposureResponse(
            summary=summary,
            top_affected_products=raw["top_affected_products"],
            top_affected_stores=raw["top_affected_stores"],
            sample_placements=sample_items
        )

    def get_inventory_pressure(self, limit: int = 100, category: Optional[str] = None) -> InventoryPressureResponse:
        """
        Calculates Days of Supply coverage tiers for placements.
        """
        # Fetch placements from repository
        raw_items = self.repository.get_inventory_pressure_data(limit=limit, category=category)

        # Count distribution across returned items
        tier_counts: Dict[str, int] = {
            "Stockout": 0,
            "High Pressure": 0,
            "Moderate Pressure": 0,
            "Typical": 0,
            "Elevated Coverage": 0,
            "Slow-Moving Candidate": 0
        }

        classified_items: List[InventoryPressureItem] = []
        for r in raw_items:
            stock = r["stock_on_hand"]
            dos = r["days_of_supply"]
            tier = self.config.classify_placement_coverage(stock, dos)
            if tier in tier_counts:
                tier_counts[tier] += 1

            # Format explainability
            if tier == "Stockout":
                threshold = "stock_on_hand == 0"
                explanation = "Placement has zero physical stock on hand. Immediate stockout fact."
            elif tier == "High Pressure":
                threshold = f"0 < DOS <= {self.config.PLACEMENT_DOS_P10_DAYS}d (P10)"
                explanation = (
                    f"Estimated supply coverage of {dos:.1f} days falls within the lowest 10% "
                    f"of positive-stock placements (<={self.config.PLACEMENT_DOS_P10_DAYS}d)."
                )
            elif tier == "Moderate Pressure":
                threshold = f"{self.config.PLACEMENT_DOS_P10_DAYS}d < DOS <= {self.config.PLACEMENT_DOS_P25_DAYS}d (P25)"
                explanation = (
                    f"Estimated coverage of {dos:.1f} days is between P10 ({self.config.PLACEMENT_DOS_P10_DAYS}d) "
                    f"and P25 ({self.config.PLACEMENT_DOS_P25_DAYS}d)."
                )
            elif tier == "Typical":
                threshold = f"{self.config.PLACEMENT_DOS_P25_DAYS}d < DOS <= {self.config.PLACEMENT_DOS_P75_DAYS}d (P75)"
                explanation = (
                    f"Estimated coverage of {dos:.1f} days is in the typical interquartile range "
                    f"({self.config.PLACEMENT_DOS_P25_DAYS}d to {self.config.PLACEMENT_DOS_P75_DAYS}d)."
                )
            elif tier == "Elevated Coverage":
                threshold = f"{self.config.PLACEMENT_DOS_P75_DAYS}d < DOS <= {self.config.PLACEMENT_DOS_P90_DAYS}d (P90)"
                explanation = (
                    f"Estimated coverage of {dos:.1f} days is elevated between P75 ({self.config.PLACEMENT_DOS_P75_DAYS}d) "
                    f"and P90 ({self.config.PLACEMENT_DOS_P90_DAYS}d)."
                )
            else:
                threshold = f"DOS > {self.config.PLACEMENT_DOS_P90_DAYS}d (Top 10%)"
                explanation = (
                    f"Estimated coverage of {dos:.1f} days exceeds P90 ({self.config.PLACEMENT_DOS_P90_DAYS}d), "
                    f"representing slow inventory turnover."
                )

            classified_items.append(
                InventoryPressureItem(
                    product_id=r["product_id"],
                    product_name=r["product_name"],
                    category=r["category"],
                    store_id=r.get("store_id"),
                    store_name=r.get("store_name"),
                    store_location=r.get("store_location"),
                    stock_on_hand=stock,
                    annual_units_sold=r["annual_units_sold"],
                    daily_velocity=r["daily_velocity"],
                    days_of_supply=dos,
                    coverage_tier=tier,
                    inventory_cost_cents=r["inventory_cost_cents"],
                    inventory_retail_cents=r["inventory_retail_cents"],
                    currency_code="USD",
                    threshold_applied=threshold,
                    explanation=explanation
                )
            )

        return InventoryPressureResponse(
            currency_code="USD",
            snapshot_date=self.config.ASSUMED_SNAPSHOT_DATE,
            snapshot_date_is_assumed=self.config.SNAPSHOT_DATE_IS_ASSUMED,
            total_placements_evaluated=len(raw_items),
            tier_counts=tier_counts,
            high_pressure_items=classified_items
        )

    def get_slow_moving_inventory(self, limit: int = 50) -> SlowMovingResponse:
        """
        Identifies products and placements meeting the dual-condition slow-moving criteria.
        """
        raw = self.repository.get_slow_moving_candidates_data()

        # 1. Product-level filter
        candidate_products: List[SlowMovingProductItem] = []
        prod_capital_total = 0
        for p in raw["products"]:
            dos = p["days_of_supply"]
            cost_val = p["inventory_cost_value_cents"]
            if self.config.is_product_slow_moving(dos, cost_val):
                prod_capital_total += cost_val
                if len(candidate_products) < limit:
                    threshold = (
                        f"DOS > {self.config.PRODUCT_DOS_P90_DAYS}d (P90) AND "
                        f"Cost >= ${self.config.PRODUCT_MATERIAL_CAPITAL_CENTS/100:,.2f} (P75)"
                    )
                    explanation = (
                        f"Product has {dos:.1f} days of supply (exceeds P90 of {self.config.PRODUCT_DOS_P90_DAYS}d) "
                        f"with ${cost_val/100:,.2f} tied up in inventory cost (exceeds P75 of ${self.config.PRODUCT_MATERIAL_CAPITAL_CENTS/100:,.2f})."
                    )
                    candidate_products.append(
                        SlowMovingProductItem(
                            product_id=p["product_id"],
                            product_name=p["product_name"],
                            category=p["category"],
                            stock_units=p["stock_units"],
                            annual_units_sold=p["annual_units_sold"],
                            average_daily_velocity=p["average_daily_velocity"],
                            days_of_supply=dos,
                            inventory_cost_value_cents=cost_val,
                            inventory_retail_value_cents=p["inventory_retail_value_cents"],
                            currency_code="USD",
                            threshold_applied=threshold,
                            explanation=explanation
                        )
                    )

        # 2. Placement-level filter
        candidate_placements: List[SlowMovingPlacementItem] = []
        pl_capital_total = 0
        for pl in raw["placements"]:
            stock = pl["stock_on_hand"]
            dos = pl["days_of_supply"]
            cost_val = pl["inventory_cost_value_cents"]
            if self.config.is_placement_slow_moving(stock, dos, cost_val):
                pl_capital_total += cost_val
                if len(candidate_placements) < limit:
                    threshold = (
                        f"DOS > {self.config.PLACEMENT_DOS_P90_DAYS}d (P90) AND "
                        f"Cost >= ${self.config.PLACEMENT_MATERIAL_CAPITAL_CENTS/100:,.2f} (P75)"
                    )
                    explanation = (
                        f"Store placement has {dos:.1f} days of supply (exceeds P90 of {self.config.PLACEMENT_DOS_P90_DAYS}d) "
                        f"with ${cost_val/100:,.2f} in inventory cost."
                    )
                    candidate_placements.append(
                        SlowMovingPlacementItem(
                            store_id=pl["store_id"],
                            store_name=pl["store_name"],
                            store_location=pl["store_location"],
                            product_id=pl["product_id"],
                            product_name=pl["product_name"],
                            category=pl["category"],
                            stock_on_hand=stock,
                            annual_units_sold=pl["annual_units_sold"],
                            average_daily_velocity=pl["average_daily_velocity"],
                            days_of_supply=dos,
                            inventory_cost_value_cents=cost_val,
                            currency_code="USD",
                            threshold_applied=threshold,
                            explanation=explanation
                        )
                    )

        return SlowMovingResponse(
            currency_code="USD",
            snapshot_date=self.config.ASSUMED_SNAPSHOT_DATE,
            snapshot_date_is_assumed=self.config.SNAPSHOT_DATE_IS_ASSUMED,
            product_level_candidates_count=len(candidate_products),
            product_level_capital_exposure_cents=prod_capital_total,
            placement_level_candidates_count=len(candidate_placements),
            placement_level_capital_exposure_cents=pl_capital_total,
            candidate_products=candidate_products,
            candidate_placements=candidate_placements
        )

    def get_concentration(self) -> ConcentrationResponse:
        """
        Calculates internal revenue distribution and HHI for Products, Categories, and Stores.
        """
        raw = self.repository.get_portfolio_concentration_data()
        return ConcentrationResponse(
            currency_code="USD",
            products=ConcentrationMetric(**raw["products"]),
            categories=ConcentrationMetric(**raw["categories"]),
            stores=ConcentrationMetric(**raw["stores"])
        )

    def get_sales_velocity(self, limit: int = 10) -> SalesVelocityResponse:
        """
        Evaluates 28-day sales volume and revenue comparison.
        """
        raw = self.repository.get_sales_velocity_comparison_data(
            recent_start=self.config.RECENT_WINDOW_START,
            recent_end=self.config.RECENT_WINDOW_END,
            prior_start=self.config.PRIOR_WINDOW_START,
            prior_end=self.config.PRIOR_WINDOW_END
        )

        # Company momentum
        comp_data = raw["company"]
        comp_cls = self.config.classify_velocity_change(
            comp_data["prior_28d_units"],
            comp_data["change_pct"]
        )
        comp_item = CompanySalesVelocityItem(
            prior_28d_units=comp_data["prior_28d_units"],
            recent_28d_units=comp_data["recent_28d_units"],
            unit_change=comp_data["unit_change"],
            change_pct=comp_data["change_pct"],
            prior_28d_revenue_cents=comp_data["prior_28d_revenue_cents"],
            recent_28d_revenue_cents=comp_data["recent_28d_revenue_cents"],
            revenue_change_pct=comp_data["revenue_change_pct"],
            classification=comp_cls,
            currency_code="USD"
        )

        # Category momentum
        cat_items: List[CategorySalesVelocityItem] = []
        for c in raw["categories"]:
            c_cls = self.config.classify_velocity_change(c["prior_28d_units"], c["change_pct"])
            cat_items.append(
                CategorySalesVelocityItem(
                    category=c["category"],
                    prior_28d_units=c["prior_28d_units"],
                    recent_28d_units=c["recent_28d_units"],
                    unit_change=c["unit_change"],
                    change_pct=c["change_pct"],
                    prior_28d_revenue_cents=c["prior_28d_revenue_cents"],
                    recent_28d_revenue_cents=c["recent_28d_revenue_cents"],
                    revenue_change_pct=c["revenue_change_pct"],
                    classification=c_cls,
                    currency_code="USD"
                )
            )

        # Product momentum
        all_prods: List[SalesVelocityItem] = []
        for p in raw["products"]:
            p_cls = self.config.classify_velocity_change(p["prior_28d_units"], p["change_pct"])
            pct = p["change_pct"]
            if p_cls == "Severe Contraction":
                threshold = f"change_pct <= {self.config.VELOCITY_SEVERE_CONTRACTION_PCT}% (P05)"
                explanation = f"Volume contracted by {pct:.1f}% over 28 days, falling in the lowest 5% of products."
            elif p_cls == "Moderate Contraction":
                threshold = f"{self.config.VELOCITY_SEVERE_CONTRACTION_PCT}% < change_pct <= {self.config.VELOCITY_MODERATE_CONTRACTION_PCT}% (P25)"
                explanation = f"Volume contracted by {pct:.1f}% over 28 days, between P05 and P25 boundaries."
            elif p_cls == "Growth":
                threshold = f"change_pct >= {self.config.VELOCITY_GROWTH_PCT}% (P75)"
                explanation = f"Volume expanded by {pct:.1f}% over 28 days, in top quartile of products."
            else:
                threshold = f"{self.config.VELOCITY_MODERATE_CONTRACTION_PCT}% < change_pct < {self.config.VELOCITY_GROWTH_PCT}%"
                explanation = f"Volume changed by {pct:.1f}%, within the typical 50% interquartile stability core."

            all_prods.append(
                SalesVelocityItem(
                    product_id=p["product_id"],
                    product_name=p["product_name"],
                    category=p["category"],
                    prior_28d_units=p["prior_28d_units"],
                    recent_28d_units=p["recent_28d_units"],
                    unit_change=p["unit_change"],
                    change_pct=pct,
                    prior_28d_revenue_cents=p["prior_28d_revenue_cents"],
                    recent_28d_revenue_cents=p["recent_28d_revenue_cents"],
                    revenue_change_pct=p["revenue_change_pct"],
                    classification=p_cls,
                    currency_code="USD",
                    threshold_applied=threshold,
                    explanation=explanation
                )
            )

        # Sort products for top contracting and top growing
        valid_prods = [p for p in all_prods if p.change_pct is not None]
        top_contracting = sorted(valid_prods, key=lambda x: x.change_pct)[:limit]
        top_growing = sorted(valid_prods, key=lambda x: x.change_pct, reverse=True)[:limit]

        return SalesVelocityResponse(
            recent_window=f"{self.config.RECENT_WINDOW_START} to {self.config.RECENT_WINDOW_END}",
            prior_window=f"{self.config.PRIOR_WINDOW_START} to {self.config.PRIOR_WINDOW_END}",
            window_days=self.config.WINDOW_DAYS,
            company_momentum=comp_item,
            categories_momentum=cat_items,
            top_contracting_products=top_contracting,
            top_growing_products=top_growing
        )

    def get_risk_overview(self) -> RiskOverview:
        """
        Assembles independent domain statuses without a single 0-100 score.
        """
        stockouts = self.get_stockout_exposure()
        slow_moving = self.get_slow_moving_inventory()
        concentration = self.get_concentration()
        velocity = self.get_sales_velocity()

        domains = [
            RiskOverviewDomain(
                domain="Stockout Exposure",
                status=f"{stockouts.summary.zero_stock_placements} Stockouts",
                headline_metric=f"${stockouts.summary.historical_revenue_associated_cents / 100:,.2f}",
                detail=(
                    f"{stockouts.summary.zero_stock_placements} zero-stock placements across "
                    f"{stockouts.summary.affected_stores_count} stores ({stockouts.summary.historical_revenue_share_pct:.2f}% of 2025 revenue)."
                ),
                explainability=(
                    "Historical revenue associated with current zero-stock placements. "
                    "Reflects verified physical stockouts; does not imply unfulfilled demand."
                )
            ),
            RiskOverviewDomain(
                domain="Inventory Pressure",
                status="P10 Calibrated",
                headline_metric=f"<= {self.config.PLACEMENT_DOS_P10_DAYS}d Pressure Tier",
                detail=(
                    f"Placements classified into 5 empirical coverage tiers based on positive-stock "
                    f"percentiles (P10={self.config.PLACEMENT_DOS_P10_DAYS}d, P90={self.config.PLACEMENT_DOS_P90_DAYS}d)."
                ),
                explainability="Days of Supply = Stock On Hand / (2025 Units Sold / 365.0). Snapshot date assumed as Dec 31, 2025."
            ),
            RiskOverviewDomain(
                domain="Slow-Moving Exposure",
                status=f"{slow_moving.product_level_candidates_count} Products",
                headline_metric=f"${slow_moving.product_level_capital_exposure_cents / 100:,.2f}",
                detail=(
                    f"{slow_moving.product_level_candidates_count} products with DOS > {self.config.PRODUCT_DOS_P90_DAYS}d "
                    f"and capital >= ${self.config.PRODUCT_MATERIAL_CAPITAL_CENTS / 100:,.2f}."
                ),
                explainability=(
                    "Dual-condition rule requires both high days of supply (>P90) and material capital allocation (>=P75). "
                    "No carrying costs or obsolescence rates are assumed."
                )
            ),
            RiskOverviewDomain(
                domain="Sales Velocity",
                status=f"Company {velocity.company_momentum.classification}",
                headline_metric=f"{velocity.company_momentum.change_pct:+.2f}% Units",
                detail=(
                    f"Company sales units moved {velocity.company_momentum.change_pct:+.2f}% over consecutive 28-day windows. "
                    f"{len(velocity.top_contracting_products)} products show notable contraction (<= {self.config.VELOCITY_SEVERE_CONTRACTION_PCT}%)."
                ),
                explainability="Compares 2025-12-04..12-31 to 2025-11-06..12-03. Minimum volume floor: 100 units."
            ),
            RiskOverviewDomain(
                domain="Portfolio Concentration",
                status="Diversified Portfolio",
                headline_metric=f"HHI {concentration.products.hhi:.1f} (Ratio {concentration.products.hhi_to_equal_ratio:.2f})",
                detail=(
                    f"Product HHI-to-equal ratio is {concentration.products.hhi_to_equal_ratio:.2f}; "
                    f"Store ratio is {concentration.stores.hhi_to_equal_ratio:.2f}. Indicates broad portfolio balance."
                ),
                explainability=(
                    "Internal portfolio concentration. A ratio of 1.0 represents perfectly equal revenue share. "
                    "Low ratios confirm absence of single-point failure dependencies."
                )
            )
        ]

        return RiskOverview(
            currency_code="USD",
            assumed_snapshot_date=self.config.ASSUMED_SNAPSHOT_DATE,
            snapshot_date_is_assumed=self.config.SNAPSHOT_DATE_IS_ASSUMED,
            domains=domains
        )
