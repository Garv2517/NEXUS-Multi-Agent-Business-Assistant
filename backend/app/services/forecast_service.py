"""Deterministic D3B forecasting service. No LLM or Azure calls."""
from collections import defaultdict
from datetime import date, timedelta
from typing import Dict, List, Optional, Sequence, Tuple

from ..core.forecast_config import (
    CATEGORY_MODELS,
    COMPANY_REVENUE,
    COMPANY_UNITS,
    forecast_config,
    reliability_label,
)
from ..models.forecast import (
    CategoryForecastResponse,
    CategoryForecastSeries,
    CompanyForecastResponse,
    DemandCoverageItem,
    DemandCoverageResponse,
    ForecastConfigResponse,
    ForecastPoint,
    ForecastSeries,
)
from ..repositories.forecast_repository import ForecastRepository


class ForecastService:
    def __init__(self, repository: Optional[ForecastRepository] = None):
        self.repository = repository or ForecastRepository()

    # -------------------- deterministic models --------------------
    @staticmethod
    def _naive(series: Sequence[float], horizon: int) -> List[float]:
        return [max(0.0, float(series[-1]))] * horizon

    @staticmethod
    def _moving_average(series: Sequence[float], window: int, horizon: int) -> List[float]:
        values = series[-window:] if len(series) >= window else series
        level = max(0.0, sum(values) / len(values))
        return [level] * horizon

    @staticmethod
    def _ols(series: Sequence[float], horizon: int) -> List[float]:
        n = len(series)
        if n < 2:
            return [float(series[-1])] * horizon
        mean_x = (n - 1) / 2.0
        mean_y = sum(series) / n
        denom = sum((x - mean_x) ** 2 for x in range(n))
        if denom == 0:
            return [float(mean_y)] * horizon
        slope = sum((x - mean_x) * (series[x] - mean_y) for x in range(n)) / denom
        intercept = mean_y - slope * mean_x
        return [intercept + slope * (n + i) for i in range(horizon)]

    @staticmethod
    def _ses(series: Sequence[float], horizon: int) -> List[float]:
        best_alpha = 0.3
        if len(series) > 5:
            best_sse = float("inf")
            for alpha in (0.1, 0.2, 0.3, 0.4, 0.5):
                level = float(series[0])
                sse = 0.0
                for y in series[1:]:
                    err = float(y) - level
                    sse += err * err
                    level = alpha * float(y) + (1.0 - alpha) * level
                if sse < best_sse:
                    best_sse = sse
                    best_alpha = alpha
        level = float(series[0])
        for y in series[1:]:
            level = best_alpha * float(y) + (1.0 - best_alpha) * level
        return [max(0.0, level)] * horizon

    def _run_model(self, model: str, series: Sequence[float], horizon: int) -> Tuple[List[float], Optional[str], str]:
        if model == "Naive":
            preds = self._naive(series, horizon)
        elif model == "MA4":
            preds = self._moving_average(series, 4, horizon)
        elif model == "MA8":
            preds = self._moving_average(series, 8, horizon)
        elif model == "OLS":
            preds = self._ols(series, horizon)
        elif model == "SES":
            preds = self._ses(series, horizon)
        else:
            raise ValueError(f"Unsupported forecast model '{model}'")

        fallback_reason = None
        model_used = model
        if any(p < 0 for p in preds):
            preds = self._moving_average(series, 4, horizon)
            model_used = "MA4"
            fallback_reason = f"{model} produced a negative forecast; deterministic MA4 fallback applied."
        return preds, fallback_reason, model_used

    # -------------------- verified series construction --------------------
    @staticmethod
    def _validate_complete_company_rows(rows: List[dict]) -> List[dict]:
        complete = [r for r in rows if int(r["distinct_sale_dates"]) == 7]
        if len(complete) != forecast_config.expected_complete_weeks:
            raise ValueError(
                f"Expected {forecast_config.expected_complete_weeks} complete weeks, got {len(complete)}"
            )
        if complete[0]["week_start"] != forecast_config.first_complete_week:
            raise ValueError("Unexpected first complete forecast week")
        if complete[-1]["week_start"] != forecast_config.last_complete_week:
            raise ValueError("Unexpected last complete forecast week")
        # Protect against hidden interior gaps.
        expected = date.fromisoformat(complete[0]["week_start"])
        for row in complete:
            if date.fromisoformat(row["week_start"]) != expected:
                raise ValueError("Missing or non-consecutive complete weekly bucket")
            expected += timedelta(days=7)
        return complete

    def _category_series(self, complete_weeks: List[str]) -> Dict[str, List[int]]:
        rows = self.repository.get_category_weekly_series()
        grouped: Dict[str, Dict[str, int]] = defaultdict(dict)
        for row in rows:
            # Week completeness is governed by the company calendar. A category
            # need not transact on every day inside an otherwise complete week.
            grouped[row["category"]][row["week_start"]] = int(row["units"])
        result = {}
        for category in sorted(CATEGORY_MODELS):
            values = [grouped.get(category, {}).get(week) for week in complete_weeks]
            if any(v is None for v in values):
                raise ValueError(f"Incomplete weekly series for category '{category}'")
            result[category] = [int(v) for v in values]
        return result

    @staticmethod
    def _future_weeks(last_week_start: str, horizon: int) -> List[str]:
        last = date.fromisoformat(last_week_start)
        return [(last + timedelta(weeks=i)).isoformat() for i in range(1, horizon + 1)]

    @staticmethod
    def _historical_points(weeks: List[str], values: Sequence[float], count: int = 12) -> List[ForecastPoint]:
        start = max(0, len(weeks) - count)
        return [
            ForecastPoint(week_start=weeks[i], value=int(round(values[i])), kind="historical")
            for i in range(start, len(weeks))
        ]

    # -------------------- public service --------------------
    def get_config(self) -> ForecastConfigResponse:
        return ForecastConfigResponse(
            horizon_weeks=forecast_config.horizon_weeks,
            min_training_weeks=forecast_config.min_training_weeks,
            complete_weeks=forecast_config.expected_complete_weeks,
            first_complete_week=forecast_config.first_complete_week,
            last_complete_week=forecast_config.last_complete_week,
            last_complete_week_end=forecast_config.last_complete_week_end,
            first_forecast_week=forecast_config.first_forecast_week,
            company_units_model=COMPANY_UNITS.model,
            company_revenue_model=COMPANY_REVENUE.model,
            reliability_strong_max_wape=forecast_config.reliability_strong_max_wape,
            reliability_moderate_max_wape=forecast_config.reliability_moderate_max_wape,
            snapshot_date=forecast_config.snapshot_date,
            snapshot_date_is_assumed=forecast_config.snapshot_date_is_assumed,
            partial_week_policy=(
                "Model training uses complete weeks through Dec 28, 2025. Partial source observations "
                "from Dec 29-31 are excluded from model training and full-week forecast comparison."
            ),
        )

    def get_company_forecast(self) -> CompanyForecastResponse:
        rows = self._validate_complete_company_rows(self.repository.get_company_weekly_series())
        weeks = [r["week_start"] for r in rows]
        units = [int(r["units"]) for r in rows]
        revenue = [int(r["revenue_cents"]) for r in rows]
        future_weeks = self._future_weeks(weeks[-1], forecast_config.horizon_weeks)

        unit_preds, unit_fallback, unit_model = self._run_model(
            COMPANY_UNITS.model, units, forecast_config.horizon_weeks
        )
        rev_preds, rev_fallback, rev_model = self._run_model(
            COMPANY_REVENUE.model, revenue, forecast_config.horizon_weeks
        )

        unit_points = self._historical_points(weeks, units) + [
            ForecastPoint(
                week_start=week,
                value=int(round(unit_preds[i])),
                kind="forecast",
                horizon=i + 1,
                historical_mae_reference=COMPANY_UNITS.horizon_mae[i],
            )
            for i, week in enumerate(future_weeks)
        ]
        revenue_points = self._historical_points(weeks, revenue) + [
            ForecastPoint(
                week_start=week,
                value=int(round(rev_preds[i])),
                kind="forecast",
                horizon=i + 1,
                historical_mae_reference=COMPANY_REVENUE.horizon_mae[i],
            )
            for i, week in enumerate(future_weeks)
        ]

        return CompanyForecastResponse(
            training_complete_weeks=len(rows),
            training_start_week=weeks[0],
            training_end_week=weeks[-1],
            training_end_date=forecast_config.last_complete_week_end,
            first_forecast_week=future_weeks[0],
            partial_week_disclosure=(
                "Model training uses complete weeks through Dec 28, 2025. Partial source observations "
                "from Dec 29-31 are excluded from model training and full-week forecast comparison."
            ),
            units=ForecastSeries(
                target="company_units",
                value_unit="units",
                model_used=unit_model,
                fallback_reason=unit_fallback,
                validation_wape=COMPANY_UNITS.aggregate_wape,
                validation_reliability=reliability_label(COMPANY_UNITS.aggregate_wape),
                historical_mae_by_horizon=list(COMPANY_UNITS.horizon_mae),
                points=unit_points,
                methodology_note=(
                    "SES selected by exhaustive 4-horizon rolling-origin validation over complete weekly data. "
                    "Historical MAE references are empirical errors, not confidence intervals."
                ),
            ),
            revenue=ForecastSeries(
                target="company_revenue_cents",
                value_unit="cents",
                model_used=rev_model,
                fallback_reason=rev_fallback,
                validation_wape=COMPANY_REVENUE.aggregate_wape,
                validation_reliability=reliability_label(COMPANY_REVENUE.aggregate_wape),
                historical_mae_by_horizon=list(COMPANY_REVENUE.horizon_mae),
                points=revenue_points,
                methodology_note=(
                    "SES selected by exhaustive 4-horizon rolling-origin validation over complete weekly data. "
                    "Revenue remains integer cents (USD). Historical MAE references are not probabilistic intervals."
                ),
            ),
        )

    def get_category_forecasts(self) -> CategoryForecastResponse:
        company_rows = self._validate_complete_company_rows(self.repository.get_company_weekly_series())
        weeks = [r["week_start"] for r in company_rows]
        future_weeks = self._future_weeks(weeks[-1], forecast_config.horizon_weeks)
        series_map = self._category_series(weeks)
        items: List[CategoryForecastSeries] = []

        for category in sorted(CATEGORY_MODELS):
            cfg = CATEGORY_MODELS[category]
            series = series_map[category]
            preds, fallback_reason, model_used = self._run_model(
                cfg.model, series, forecast_config.horizon_weeks
            )
            forecast_points = [
                ForecastPoint(
                    week_start=week,
                    value=int(round(preds[i])),
                    kind="forecast",
                    horizon=i + 1,
                )
                for i, week in enumerate(future_weeks)
            ]
            items.append(CategoryForecastSeries(
                category=category,
                model_used=model_used,
                fallback_reason=fallback_reason,
                validation_wape=cfg.aggregate_wape,
                validation_reliability=reliability_label(cfg.aggregate_wape),
                historical_points=self._historical_points(weeks, series, count=8),
                forecast_points=forecast_points,
                forecast_4w_units=sum(p.value for p in forecast_points),
            ))

        return CategoryForecastResponse(categories=items)

    def get_demand_coverage(self) -> DemandCoverageResponse:
        forecasts = self.get_category_forecasts()
        stock_rows = self.repository.get_category_inventory_stock()
        stock_map = {r["category"]: int(r["stock_units"]) for r in stock_rows}
        items = []
        for item in forecasts.categories:
            demand = max(item.forecast_4w_units, 1)
            stock = stock_map.get(item.category, 0)
            items.append(DemandCoverageItem(
                category=item.category,
                current_stock_units=stock,
                forecast_4w_units=item.forecast_4w_units,
                coverage_ratio=round(stock / demand, 3),
                forecast_coverage_weeks=round(stock / (demand / 4.0), 2),
                forecast_validation_wape=item.validation_wape,
                forecast_validation_reliability=item.validation_reliability,
            ))
        return DemandCoverageResponse(categories=items)
