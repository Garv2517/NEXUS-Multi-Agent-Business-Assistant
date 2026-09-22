"""Pydantic contracts for NEXUS D3B Forecasting & Demand Planning."""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class ForecastPoint(BaseModel):
    week_start: str
    value: int
    kind: Literal["historical", "forecast"]
    horizon: Optional[int] = None
    historical_mae_reference: Optional[float] = None


class ForecastSeries(BaseModel):
    target: str
    value_unit: Literal["units", "cents"]
    model_used: str
    fallback_reason: Optional[str] = None
    validation_wape: float
    validation_reliability: str
    historical_mae_by_horizon: List[float]
    points: List[ForecastPoint]
    methodology_note: str


class CompanyForecastResponse(BaseModel):
    currency_code: str = Field("USD")
    horizon_weeks: int = Field(4)
    training_complete_weeks: int
    training_start_week: str
    training_end_week: str
    training_end_date: str
    first_forecast_week: str
    partial_week_disclosure: str
    units: ForecastSeries
    revenue: ForecastSeries


class CategoryForecastSeries(BaseModel):
    category: str
    model_used: str
    fallback_reason: Optional[str] = None
    validation_wape: float
    validation_reliability: str
    historical_points: List[ForecastPoint]
    forecast_points: List[ForecastPoint]
    forecast_4w_units: int


class CategoryForecastResponse(BaseModel):
    horizon_weeks: int = Field(4)
    categories: List[CategoryForecastSeries]
    reliability_note: str = Field(
        "Forecast Validation Reliability is project-defined from aggregate 4-horizon WAPE: "
        "Strong <= 0.10, Moderate <= 0.20, Limited > 0.20. It is not a confidence probability."
    )


class DemandCoverageItem(BaseModel):
    category: str
    current_stock_units: int
    forecast_4w_units: int
    coverage_ratio: float
    forecast_coverage_weeks: float
    forecast_validation_wape: float
    forecast_validation_reliability: str


class DemandCoverageResponse(BaseModel):
    snapshot_date: str = Field("2025-12-31")
    snapshot_date_is_assumed: bool = Field(True)
    horizon_weeks: int = Field(4)
    categories: List[DemandCoverageItem]
    methodology_note: str = Field(
        "coverage_ratio = current_stock / forecast_4w_units. "
        "forecast_coverage_weeks = current_stock / (forecast_4w_units / 4). "
        "These are planning indicators only and do not trigger replenishment orders."
    )


class ForecastConfigResponse(BaseModel):
    horizon_weeks: int
    min_training_weeks: int
    complete_weeks: int
    first_complete_week: str
    last_complete_week: str
    last_complete_week_end: str
    first_forecast_week: str
    company_units_model: str
    company_revenue_model: str
    reliability_strong_max_wape: float
    reliability_moderate_max_wape: float
    snapshot_date: str
    snapshot_date_is_assumed: bool
    partial_week_policy: str
