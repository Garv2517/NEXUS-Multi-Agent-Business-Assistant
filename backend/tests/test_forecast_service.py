"""Tests for deterministic D3B forecasting service."""
import pytest

from app.repositories.forecast_repository import ForecastRepository
from app.services.forecast_service import ForecastService


@pytest.fixture
def service():
    return ForecastService()


def test_company_forecast_contract(service):
    data = service.get_company_forecast()
    assert data.currency_code == "USD"
    assert data.horizon_weeks == 4
    assert data.training_complete_weeks == 51
    assert data.training_start_week == "2025-01-06"
    assert data.training_end_week == "2025-12-22"
    assert data.training_end_date == "2025-12-28"
    assert data.first_forecast_week == "2025-12-29"
    assert data.units.model_used == "SES"
    assert data.revenue.model_used == "SES"
    assert data.units.validation_wape == pytest.approx(0.0139)
    assert data.revenue.validation_wape == pytest.approx(0.0143)


def test_company_forecast_dates_and_nonnegative(service):
    data = service.get_company_forecast()
    unit_forecasts = [p for p in data.units.points if p.kind == "forecast"]
    revenue_forecasts = [p for p in data.revenue.points if p.kind == "forecast"]
    expected = ["2025-12-29", "2026-01-05", "2026-01-12", "2026-01-19"]
    assert [p.week_start for p in unit_forecasts] == expected
    assert [p.week_start for p in revenue_forecasts] == expected
    assert all(p.value >= 0 for p in unit_forecasts)
    assert all(p.value >= 0 for p in revenue_forecasts)
    assert [p.horizon for p in unit_forecasts] == [1, 2, 3, 4]


def test_partial_week_not_in_training_history(service):
    data = service.get_company_forecast()
    hist = [p.week_start for p in data.units.points if p.kind == "historical"]
    assert "2025-12-29" not in hist
    assert hist[-1] == "2025-12-22"
    assert "Partial source observations from Dec 29-31" in data.partial_week_disclosure


def test_category_forecasts_all_16(service):
    data = service.get_category_forecasts()
    assert len(data.categories) == 16
    names = {c.category for c in data.categories}
    assert "Action Figures" in names
    assert "Collectibles" in names
    assert all(len(c.forecast_points) == 4 for c in data.categories)
    assert all(c.forecast_4w_units > 0 for c in data.categories)


def test_collectibles_reliability_is_metric_driven(service):
    data = service.get_category_forecasts()
    collectibles = next(c for c in data.categories if c.category == "Collectibles")
    assert collectibles.model_used == "MA8"
    assert collectibles.validation_wape == pytest.approx(0.2177)
    assert collectibles.validation_reliability == "Limited"


def test_demand_coverage_formula(service):
    data = service.get_demand_coverage()
    assert data.snapshot_date == "2025-12-31"
    assert data.snapshot_date_is_assumed is True
    assert len(data.categories) == 16
    item = data.categories[0]
    expected_ratio = round(item.current_stock_units / max(item.forecast_4w_units, 1), 3)
    expected_weeks = round(item.current_stock_units / (max(item.forecast_4w_units, 1) / 4.0), 2)
    assert item.coverage_ratio == expected_ratio
    assert item.forecast_coverage_weeks == expected_weeks


def test_weekly_repository_calendar_integrity():
    repo = ForecastRepository()
    rows = repo.get_company_weekly_series()
    assert len(rows) == 53
    complete = [r for r in rows if r["distinct_sale_dates"] == 7]
    partial = [r for r in rows if r["distinct_sale_dates"] != 7]
    assert len(complete) == 51
    assert [(r["week_start"], r["distinct_sale_dates"]) for r in partial] == [
        ("2024-12-30", 5),
        ("2025-12-29", 3),
    ]


def test_config_is_transparent(service):
    cfg = service.get_config()
    assert cfg.company_units_model == "SES"
    assert cfg.company_revenue_model == "SES"
    assert cfg.reliability_strong_max_wape == 0.10
    assert cfg.reliability_moderate_max_wape == 0.20
    assert cfg.snapshot_date_is_assumed is True
