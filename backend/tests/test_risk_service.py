"""
Unit tests for RiskService (NEXUS Phase D2: Deterministic Risk Management).

Verifies mathematical formulas, threshold boundary transitions, exact authoritative counts,
and explainability outputs against verified Kaggle data in nexus_analytics.db.
"""
import pytest
from app.core.risk_config import RiskConfig, risk_config
from app.repositories.analytics_repository import AnalyticsRepository
from app.services.risk_service import RiskService


@pytest.fixture
def risk_service():
    repo = AnalyticsRepository()
    return RiskService(repository=repo, config=risk_config)


# --- 1. Risk Config & Boundary Logic ---

def test_risk_config_thresholds():
    cfg = risk_config
    assert cfg.ASSUMED_SNAPSHOT_DATE == "2025-12-31"
    assert cfg.SNAPSHOT_DATE_IS_ASSUMED is True

    # Empirical placement percentiles
    assert cfg.PLACEMENT_DOS_P10_DAYS == 130.87
    assert cfg.PLACEMENT_DOS_P25_DAYS == 171.76
    assert cfg.PLACEMENT_DOS_P75_DAYS == 298.64
    assert cfg.PLACEMENT_DOS_P90_DAYS == 392.04
    assert cfg.PLACEMENT_MATERIAL_CAPITAL_CENTS == 27554

    # Product percentiles
    assert cfg.PRODUCT_DOS_P90_DAYS == 241.34
    assert cfg.PRODUCT_MATERIAL_CAPITAL_CENTS == 2087756

    # Sales velocity percentiles
    assert cfg.VELOCITY_MIN_PRIOR_UNITS == 100
    assert cfg.VELOCITY_SEVERE_CONTRACTION_PCT == -22.03
    assert cfg.VELOCITY_MODERATE_CONTRACTION_PCT == -9.35
    assert cfg.VELOCITY_GROWTH_PCT == 11.60


def test_dos_threshold_boundary_transitions():
    cfg = risk_config

    # Stockout
    assert cfg.classify_placement_coverage(stock_on_hand=0, dos=0.0) == "Stockout"
    assert cfg.classify_placement_coverage(stock_on_hand=0, dos=None) == "Stockout"

    # High Pressure (0 < DOS <= 130.87)
    assert cfg.classify_placement_coverage(stock_on_hand=10, dos=0.1) == "High Pressure"
    assert cfg.classify_placement_coverage(stock_on_hand=10, dos=130.87) == "High Pressure"

    # Moderate Pressure (130.87 < DOS <= 171.76)
    assert cfg.classify_placement_coverage(stock_on_hand=10, dos=130.88) == "Moderate Pressure"
    assert cfg.classify_placement_coverage(stock_on_hand=10, dos=171.76) == "Moderate Pressure"

    # Typical (171.76 < DOS <= 298.64)
    assert cfg.classify_placement_coverage(stock_on_hand=10, dos=171.77) == "Typical"
    assert cfg.classify_placement_coverage(stock_on_hand=10, dos=298.64) == "Typical"

    # Elevated Coverage (298.64 < DOS <= 392.04)
    assert cfg.classify_placement_coverage(stock_on_hand=10, dos=298.65) == "Elevated Coverage"
    assert cfg.classify_placement_coverage(stock_on_hand=10, dos=392.04) == "Elevated Coverage"

    # Slow-Moving Candidate (DOS > 392.04)
    assert cfg.classify_placement_coverage(stock_on_hand=10, dos=392.05) == "Slow-Moving Candidate"
    assert cfg.classify_placement_coverage(stock_on_hand=10, dos=1000.0) == "Slow-Moving Candidate"

    # Edge case: positive stock with zero velocity -> None
    assert cfg.classify_placement_coverage(stock_on_hand=10, dos=None) == "Undefined"


def test_slow_moving_dual_condition():
    cfg = risk_config

    # Placement level (DOS > 392.04 AND cost >= 27554 cents)
    # Case 1: High DOS but low capital -> False
    assert cfg.is_placement_slow_moving(stock_on_hand=10, dos=400.0, cost_value_cents=20000) is False
    # Case 2: High capital but low DOS -> False
    assert cfg.is_placement_slow_moving(stock_on_hand=10, dos=350.0, cost_value_cents=30000) is False
    # Case 3: Both conditions met -> True
    assert cfg.is_placement_slow_moving(stock_on_hand=10, dos=392.05, cost_value_cents=27554) is True

    # Product level (DOS > 241.34 AND cost >= 2087756 cents)
    assert cfg.is_product_slow_moving(dos=240.0, cost_value_cents=2500000) is False
    assert cfg.is_product_slow_moving(dos=250.0, cost_value_cents=2000000) is False
    assert cfg.is_product_slow_moving(dos=241.35, cost_value_cents=2087756) is True


def test_sales_velocity_boundary_transitions():
    cfg = risk_config

    # Low volume floor (< 100 units)
    assert cfg.classify_velocity_change(prior_units=99, change_pct=-50.0) == "Low Volume Baseline"

    # Severe Contraction (<= -22.03%)
    assert cfg.classify_velocity_change(prior_units=150, change_pct=-33.33) == "Severe Contraction"
    assert cfg.classify_velocity_change(prior_units=150, change_pct=-22.03) == "Severe Contraction"

    # Moderate Contraction (-22.03% < change <= -9.35%)
    assert cfg.classify_velocity_change(prior_units=150, change_pct=-22.02) == "Moderate Contraction"
    assert cfg.classify_velocity_change(prior_units=150, change_pct=-9.35) == "Moderate Contraction"

    # Stable (-9.35% < change < 11.60%)
    assert cfg.classify_velocity_change(prior_units=150, change_pct=-9.34) == "Stable"
    assert cfg.classify_velocity_change(prior_units=150, change_pct=0.0) == "Stable"
    assert cfg.classify_velocity_change(prior_units=150, change_pct=11.59) == "Stable"

    # Growth (>= 11.60%)
    assert cfg.classify_velocity_change(prior_units=150, change_pct=11.60) == "Growth"
    assert cfg.classify_velocity_change(prior_units=150, change_pct=50.0) == "Growth"

    # Null change
    assert cfg.classify_velocity_change(prior_units=150, change_pct=None) == "Undefined"


# --- 2. Authoritative Dataset Facts Tests ---

def test_exact_stockout_exposure(risk_service):
    res = risk_service.get_stockout_exposure()
    s = res.summary

    # Exact facts verified in D2A
    assert s.total_placements == 14143
    assert s.zero_stock_placements == 321
    assert s.affected_products_count == 148
    assert s.affected_stores_count == 27
    assert s.affected_categories_count == 16
    assert s.historical_units_sold == 14936
    assert s.historical_revenue_associated_cents == 22884556
    assert s.historical_gross_profit_associated_cents == 9855306
    assert round(s.historical_revenue_share_pct, 2) == 2.32
    assert s.currency_code == "USD"

    # Confirm correct terminology in wording note
    assert "Historical revenue associated with current zero-stock placements" in s.wording_note
    assert "lost revenue" not in s.wording_note.lower()
    assert "revenue at risk" not in s.wording_note.lower()

    # Verify top affected products and stores structure
    assert len(res.top_affected_products) <= 10
    assert len(res.top_affected_stores) <= 10
    assert len(res.sample_placements) > 0

    # Ensure integer IDs and cents
    p0 = res.sample_placements[0]
    assert isinstance(p0.product_id, int)
    assert isinstance(p0.store_id, int)
    assert isinstance(p0.historical_revenue_associated_cents, int)
    assert p0.stock_on_hand == 0


def test_inventory_pressure_evaluation(risk_service):
    res = risk_service.get_inventory_pressure(limit=50)
    assert res.currency_code == "USD"
    assert res.snapshot_date == "2025-12-31"
    assert res.snapshot_date_is_assumed is True
    assert res.total_placements_evaluated == 50

    # Verify tier classifications and explainability
    for item in res.high_pressure_items:
        assert isinstance(item.product_id, int)
        assert isinstance(item.store_id, int)
        assert item.currency_code == "USD"
        assert item.coverage_tier in [
            "Stockout", "High Pressure", "Moderate Pressure",
            "Typical", "Elevated Coverage", "Slow-Moving Candidate"
        ]
        assert len(item.threshold_applied) > 0
        assert len(item.explanation) > 0


def test_slow_moving_inventory(risk_service):
    res = risk_service.get_slow_moving_inventory()
    assert res.currency_code == "USD"
    assert res.snapshot_date == "2025-12-31"
    assert res.snapshot_date_is_assumed is True

    # Check candidates
    assert res.product_level_candidates_count >= 0
    assert isinstance(res.product_level_capital_exposure_cents, int)
    assert res.placement_level_candidates_count >= 0
    assert isinstance(res.placement_level_capital_exposure_cents, int)

    # Confirm terminology
    assert "obsolete" not in res.terminology_note.lower()
    assert "carrying cost" not in res.terminology_note.lower()

    for p in res.candidate_products:
        assert isinstance(p.product_id, int)
        assert p.days_of_supply > risk_config.PRODUCT_DOS_P90_DAYS
        assert p.inventory_cost_value_cents >= risk_config.PRODUCT_MATERIAL_CAPITAL_CENTS


def test_portfolio_concentration_metrics(risk_service):
    res = risk_service.get_concentration()
    assert res.currency_code == "USD"

    # Products (N=180)
    p = res.products
    assert p.entity_count == 180
    assert round(p.hhi, 2) == 66.35
    assert round(p.equal_share_hhi, 2) == 55.56
    assert round(p.hhi_to_equal_ratio, 2) == 1.19
    assert p.top_1_share_pct == pytest.approx(2.35, rel=1e-2)

    # Categories (N=16)
    c = res.categories
    assert c.entity_count == 16
    assert round(c.hhi, 2) == 701.76
    assert round(c.equal_share_hhi, 2) == 625.00
    assert round(c.hhi_to_equal_ratio, 2) == 1.12
    assert c.top_1_share_pct == pytest.approx(10.75, rel=1e-2)

    # Stores (N=120)
    s = res.stores
    assert s.entity_count == 120
    assert round(s.hhi, 2) == 85.26
    assert round(s.equal_share_hhi, 2) == 83.33
    assert round(s.hhi_to_equal_ratio, 2) == 1.02
    assert s.top_1_share_pct == pytest.approx(1.05, rel=1e-2)

    # Verify no antitrust / market concentration labels
    assert "market concentration" not in res.methodology_note.lower()
    assert "doj" not in res.methodology_note.lower()


def test_sales_velocity_comparison(risk_service):
    res = risk_service.get_sales_velocity()
    assert res.window_days == 28
    assert res.recent_window == "2025-12-04 to 2025-12-31"
    assert res.prior_window == "2025-11-06 to 2025-12-03"

    # Company total momentum
    comp = res.company_momentum
    assert comp.recent_28d_units == 43701
    assert comp.prior_28d_units == 43245
    assert comp.unit_change == 456
    assert round(comp.change_pct, 2) == 1.05
    assert comp.classification == "Stable"

    # 16 Categories
    assert len(res.categories_momentum) == 16
    for cat in res.categories_momentum:
        assert cat.currency_code == "USD"
        assert cat.classification in ["Severe Contraction", "Moderate Contraction", "Stable", "Growth"]

    # Top contracting & growing products
    assert len(res.top_contracting_products) > 0
    top_c = res.top_contracting_products[0]
    assert isinstance(top_c.product_id, int)
    assert top_c.change_pct is not None
    assert top_c.change_pct <= 0
    assert top_c.classification in ["Severe Contraction", "Moderate Contraction", "Stable"]


def test_risk_overview_assembly(risk_service):
    overview = risk_service.get_risk_overview()
    assert overview.currency_code == "USD"
    assert overview.assumed_snapshot_date == "2025-12-31"
    assert overview.snapshot_date_is_assumed is True
    assert len(overview.domains) == 5

    domain_names = [d.domain for d in overview.domains]
    assert domain_names == [
        "Stockout Exposure",
        "Inventory Pressure",
        "Slow-Moving Exposure",
        "Sales Velocity",
        "Portfolio Concentration"
    ]

    # Confirm governance note certifies no 0-100 score
    assert "No single 0-100 score" in overview.governance_note
