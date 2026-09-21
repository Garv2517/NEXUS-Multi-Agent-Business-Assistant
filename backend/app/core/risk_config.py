"""
Centralized Risk Management Configuration for NEXUS Phase D2.

Empirically calibrated to the external Kaggle retail analytics dataset
(nexus_analytics.db) as verified in Phase D2A.
All thresholds, percentiles, and eligibility floors are immutable and explicit.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RiskConfig:
    # --- Dataset Temporal and Assumption Metadata ---
    ASSUMED_SNAPSHOT_DATE: str = "2025-12-31"
    SNAPSHOT_DATE_IS_ASSUMED: bool = True
    DATASET_SALES_START: str = "2025-01-01"
    DATASET_SALES_END: str = "2025-12-31"
    VELOCITY_DAYS_BASELINE: float = 365.0

    # --- Placement-Level Days of Supply (DOS) Percentile Boundaries ---
    # Derived from positive-stock placement distribution (n=13,822) in D2A:
    # P10 = 130.87 days, P25 = 171.76 days, P75 = 298.64 days, P90 = 392.04 days
    PLACEMENT_DOS_P10_DAYS: float = 130.87
    PLACEMENT_DOS_P25_DAYS: float = 171.76
    PLACEMENT_DOS_P75_DAYS: float = 298.64
    PLACEMENT_DOS_P90_DAYS: float = 392.04

    # Placement Capital Exposure Threshold (P75 from D2A: $275.54)
    PLACEMENT_MATERIAL_CAPITAL_CENTS: int = 27554

    # --- Product-Level Slow-Moving Inventory Boundaries ---
    # Derived from product-level aggregate distribution (n=180) in D2A:
    # P90 DOS = 241.34 days; P75 Inventory Cost = 2,087,756 cents ($20,877.56)
    PRODUCT_DOS_P90_DAYS: float = 241.34
    PRODUCT_MATERIAL_CAPITAL_CENTS: int = 2087756

    # --- Sales Velocity Windows & Decline Boundaries ---
    # Consecutive 28-day windows
    RECENT_WINDOW_START: str = "2025-12-04"
    RECENT_WINDOW_END: str = "2025-12-31"
    PRIOR_WINDOW_START: str = "2025-11-06"
    PRIOR_WINDOW_END: str = "2025-12-03"
    WINDOW_DAYS: int = 28

    # Minimum volume eligibility floor for percentage change
    VELOCITY_MIN_PRIOR_UNITS: int = 100

    # Product-level percentage change percentiles from D2A:
    # P05 = -22.03%, P25 = -9.35%, P75 = +11.60%
    VELOCITY_SEVERE_CONTRACTION_PCT: float = -22.03
    VELOCITY_MODERATE_CONTRACTION_PCT: float = -9.35
    VELOCITY_GROWTH_PCT: float = 11.60

    # --- Helper Classification Methods ---

    def classify_placement_coverage(self, stock_on_hand: int, dos: Optional[float]) -> str:
        """
        Classifies placement inventory coverage into mutually exclusive, exhaustive tiers.
        """
        if stock_on_hand == 0 or (dos is not None and dos == 0.0):
            return "Stockout"
        if dos is None:
            return "Undefined"
        if 0 < dos <= self.PLACEMENT_DOS_P10_DAYS:
            return "High Pressure"
        if self.PLACEMENT_DOS_P10_DAYS < dos <= self.PLACEMENT_DOS_P25_DAYS:
            return "Moderate Pressure"
        if self.PLACEMENT_DOS_P25_DAYS < dos <= self.PLACEMENT_DOS_P75_DAYS:
            return "Typical"
        if self.PLACEMENT_DOS_P75_DAYS < dos <= self.PLACEMENT_DOS_P90_DAYS:
            return "Elevated Coverage"
        return "Slow-Moving Candidate"

    def is_placement_slow_moving(self, stock_on_hand: int, dos: Optional[float], cost_value_cents: int) -> bool:
        """
        Dual-condition placement slow-moving candidate:
        DOS > 392.04 AND placement_inventory_cost_cents >= 27554
        """
        if stock_on_hand <= 0 or dos is None:
            return False
        return dos > self.PLACEMENT_DOS_P90_DAYS and cost_value_cents >= self.PLACEMENT_MATERIAL_CAPITAL_CENTS

    def is_product_slow_moving(self, dos: Optional[float], cost_value_cents: int) -> bool:
        """
        Dual-condition product slow-moving candidate:
        product_days_of_supply > 241.34 AND inventory_cost_value_cents >= 2087756
        """
        if dos is None:
            return False
        return dos > self.PRODUCT_DOS_P90_DAYS and cost_value_cents >= self.PRODUCT_MATERIAL_CAPITAL_CENTS

    def classify_velocity_change(self, prior_units: int, change_pct: Optional[float]) -> str:
        """
        Classifies sales velocity change over consecutive 28-day windows.
        """
        if prior_units < self.VELOCITY_MIN_PRIOR_UNITS:
            return "Low Volume Baseline"
        if change_pct is None:
            return "Undefined"
        if change_pct <= self.VELOCITY_SEVERE_CONTRACTION_PCT:
            return "Severe Contraction"
        if self.VELOCITY_SEVERE_CONTRACTION_PCT < change_pct <= self.VELOCITY_MODERATE_CONTRACTION_PCT:
            return "Moderate Contraction"
        if self.VELOCITY_MODERATE_CONTRACTION_PCT < change_pct < self.VELOCITY_GROWTH_PCT:
            return "Stable"
        return "Growth"


# Global singleton configuration
risk_config = RiskConfig()
