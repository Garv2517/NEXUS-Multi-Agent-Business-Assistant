"""Centralized, immutable forecasting configuration for NEXUS D3B.

All locked model selections and validation metrics come from the D3A.2
exhaustive 4-horizon rolling-origin audit over the 51 complete 2025 weeks.
"""
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class ForecastTargetConfig:
    model: str
    aggregate_wape: float
    horizon_mae: Tuple[float, float, float, float]


@dataclass(frozen=True)
class ForecastConfig:
    horizon_weeks: int = 4
    min_training_weeks: int = 20
    expected_complete_weeks: int = 51
    first_complete_week: str = "2025-01-06"
    last_complete_week: str = "2025-12-22"
    last_complete_week_end: str = "2025-12-28"
    first_forecast_week: str = "2025-12-29"
    partial_start_week: str = "2024-12-30"
    partial_end_week: str = "2025-12-29"
    partial_end_observed_days: int = 3
    reliability_strong_max_wape: float = 0.10
    reliability_moderate_max_wape: float = 0.20
    snapshot_date: str = "2025-12-31"
    snapshot_date_is_assumed: bool = True


forecast_config = ForecastConfig()

COMPANY_UNITS = ForecastTargetConfig(
    model="SES",
    aggregate_wape=0.0139,
    horizon_mae=(147.09, 143.32, 150.97, 161.62),
)

COMPANY_REVENUE = ForecastTargetConfig(
    model="SES",
    aggregate_wape=0.0143,
    horizon_mae=(256122.0, 260317.0, 285655.0, 272384.0),
)

# Exact D3A.2 exhaustive-origin winners. Aggregate WAPE remains the primary
# selection metric; these are deterministic, dataset-specific model choices.
CATEGORY_MODELS: Dict[str, ForecastTargetConfig] = {
    "Action Figures": ForecastTargetConfig("OLS", 0.0509, (0.0, 0.0, 0.0, 0.0)),
    "Arts & Crafts": ForecastTargetConfig("OLS", 0.0436, (0.0, 0.0, 0.0, 0.0)),
    "Baby & Toddler": ForecastTargetConfig("OLS", 0.0429, (0.0, 0.0, 0.0, 0.0)),
    "Board Games": ForecastTargetConfig("MA8", 0.0437, (0.0, 0.0, 0.0, 0.0)),
    "Building Blocks": ForecastTargetConfig("SES", 0.0574, (0.0, 0.0, 0.0, 0.0)),
    "Card Games": ForecastTargetConfig("SES", 0.0662, (0.0, 0.0, 0.0, 0.0)),
    "Collectibles": ForecastTargetConfig("MA8", 0.2177, (0.0, 0.0, 0.0, 0.0)),
    "Dolls": ForecastTargetConfig("SES", 0.0617, (0.0, 0.0, 0.0, 0.0)),
    "Educational": ForecastTargetConfig("MA4", 0.0645, (0.0, 0.0, 0.0, 0.0)),
    "Model Kits": ForecastTargetConfig("OLS", 0.0794, (0.0, 0.0, 0.0, 0.0)),
    "Outdoor Play": ForecastTargetConfig("MA8", 0.0388, (0.0, 0.0, 0.0, 0.0)),
    "Plush": ForecastTargetConfig("MA8", 0.0708, (0.0, 0.0, 0.0, 0.0)),
    "Pretend Play": ForecastTargetConfig("OLS", 0.0599, (0.0, 0.0, 0.0, 0.0)),
    "Puzzles": ForecastTargetConfig("SES", 0.0390, (0.0, 0.0, 0.0, 0.0)),
    "STEM Kits": ForecastTargetConfig("SES", 0.0666, (0.0, 0.0, 0.0, 0.0)),
    "Toy Vehicles": ForecastTargetConfig("MA8", 0.0473, (0.0, 0.0, 0.0, 0.0)),
}


def reliability_label(aggregate_wape: float) -> str:
    """Project-defined validation reliability label; not a confidence level."""
    if aggregate_wape <= forecast_config.reliability_strong_max_wape:
        return "Strong"
    if aggregate_wape <= forecast_config.reliability_moderate_max_wape:
        return "Moderate"
    return "Limited"
