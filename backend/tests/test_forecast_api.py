"""Integration tests for /api/forecast/* endpoints."""
from starlette.testclient import TestClient

from app.api.forecast import get_forecast_service
from app.main import app
from app.repositories.forecast_repository import ForecastRepository
from app.services.forecast_service import ForecastService


def test_forecast_config_endpoint():
    with TestClient(app) as client:
        res = client.get("/api/forecast/config")
        assert res.status_code == 200
        body = res.json()
        assert body["horizon_weeks"] == 4
        assert body["company_units_model"] == "SES"
        assert body["company_revenue_model"] == "SES"


def test_forecast_company_endpoint():
    with TestClient(app) as client:
        res = client.get("/api/forecast/company")
        assert res.status_code == 200
        body = res.json()
        assert body["currency_code"] == "USD"
        assert body["training_complete_weeks"] == 51
        assert body["first_forecast_week"] == "2025-12-29"
        assert len([p for p in body["units"]["points"] if p["kind"] == "forecast"]) == 4


def test_forecast_categories_and_coverage_endpoints():
    with TestClient(app) as client:
        cats = client.get("/api/forecast/categories")
        cov = client.get("/api/forecast/coverage")
        assert cats.status_code == 200
        assert cov.status_code == 200
        assert len(cats.json()["categories"]) == 16
        assert len(cov.json()["categories"]) == 16
        assert cov.json()["snapshot_date_is_assumed"] is True


def test_forecast_missing_database_returns_503(tmp_path):
    missing = tmp_path / "missing_analytics.db"

    def override():
        return ForecastService(ForecastRepository(db_path=str(missing)))

    app.dependency_overrides[get_forecast_service] = override
    try:
        with TestClient(app) as client:
            res = client.get("/api/forecast/company")
            assert res.status_code == 503
            assert res.json() == {"detail": "Analytics dataset unavailable"}
            assert "missing_analytics" not in str(res.json())
    finally:
        app.dependency_overrides.clear()
