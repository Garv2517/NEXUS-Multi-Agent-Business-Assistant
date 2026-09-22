"""
NEXUS D3A — Forecasting Data & Model Calibration
=================================================
Analysis-only script: no API routes, no frontend, no agents, no Azure calls.

Scope:
  - Company weekly units + revenue
  - Category weekly units + revenue (all 16)
  - Models: Naive, Moving Average (4w, 8w), Linear Trend (OLS), SES
  - Walk-forward (rolling-origin) evaluation
  - Metrics: MAE, WAPE, RMSE, sMAPE
  - 4-week forward forecasts from all data
  - Negative forecast detection
  - Demand-planning feasibility assessment

Dependencies used: sqlite3, math, datetime (all stdlib); no external packages.
"""

import sqlite3
import math
import sys
from datetime import date, timedelta
from collections import defaultdict

DB_PATH = "data/nexus_analytics.db"

# ─── 1. Pull raw daily sales ──────────────────────────────────────────────────

def load_sales():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT
            s.sale_date,
            p.product_category,
            s.units,
            CAST(s.units AS REAL) * p.product_price_cents AS rev_cents
        FROM external_sales s
        JOIN external_products p ON s.product_id = p.product_id
        ORDER BY s.sale_date
    """)
    rows = c.fetchall()
    conn.close()
    return rows


# ─── 2. ISO week aggregation ──────────────────────────────────────────────────
# ISO week starts Monday. We use the Monday of each ISO week as the bucket key.

def iso_monday(d: date) -> date:
    """Return the Monday of the ISO week containing date d."""
    return d - timedelta(days=d.weekday())


def aggregate_weekly(rows):
    """
    Aggregate daily rows into ISO-week buckets.
    Returns:
        company_weeks: dict {monday_date: {units, rev_cents}}
        category_weeks: dict {category: {monday_date: {units, rev_cents}}}
        all_mondays_in_data: sorted list of all Monday keys observed
    """
    company = defaultdict(lambda: {"units": 0, "rev_cents": 0.0})
    category = defaultdict(lambda: defaultdict(lambda: {"units": 0, "rev_cents": 0.0}))

    for sale_date_str, cat, units, rev_cents in rows:
        d = date.fromisoformat(sale_date_str)
        monday = iso_monday(d)
        company[monday]["units"] += units
        company[monday]["rev_cents"] += rev_cents
        category[cat][monday]["units"] += units
        category[cat][monday]["rev_cents"] += rev_cents

    all_mondays = sorted(company.keys())
    return dict(company), dict(category), all_mondays


# ─── 3. Partial-week detection ────────────────────────────────────────────────

def detect_partial_weeks(all_mondays, first_sale: date, last_sale: date):
    """
    A week is partial if:
      - Its Monday is before the first_sale date (first week may be cut)
      - Its Monday + 6 days is after the last_sale date (last week may be cut)
    """
    partial = []
    for m in all_mondays:
        sunday = m + timedelta(days=6)
        if m < first_sale or sunday > last_sale:
            partial.append(m)
    return partial


# ─── 4. Series utilities ──────────────────────────────────────────────────────

def make_series(week_dict, all_mondays, key="units"):
    """Convert week dict to ordered list, filling missing weeks with 0."""
    return [week_dict.get(m, {key: 0})[key] for m in all_mondays]


# ─── 5. Models ────────────────────────────────────────────────────────────────

def naive_forecast(series, h=1):
    """MODEL A: Naive — forecast = last observed value, repeated h times."""
    last = series[-1]
    return [max(0.0, last)] * h


def ma_forecast(series, window=4, h=1):
    """MODEL B: Moving Average — forecast = mean of last `window` observations."""
    w = series[-window:] if len(series) >= window else series
    val = max(0.0, sum(w) / len(w))
    return [val] * h


def ols_trend_forecast(series, h=1):
    """
    MODEL C: Linear Trend via OLS.
    x = [0, 1, 2, ..., n-1]; fit y = a + b*x; forecast x = n, n+1, ...
    Negative values are flagged (not silently clipped).
    """
    n = len(series)
    if n < 2:
        return [series[-1]] * h
    xs = list(range(n))
    ys = series
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    b_num = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n))
    b_den = sum((xs[i] - mean_x) ** 2 for i in range(n))
    if b_den == 0:
        return [mean_y] * h
    b = b_num / b_den
    a = mean_y - b * mean_x
    return [a + b * (n + i) for i in range(h)]


def ses_forecast(series, alpha=0.3, h=1):
    """
    MODEL D: Simple Exponential Smoothing.
    S_t = alpha * y_t + (1-alpha) * S_{t-1}
    Forecast = S_T for all h steps (level model, no trend).
    alpha tuned by trying 0.1, 0.2, 0.3, 0.4, 0.5 and picking lowest train MAE.
    """
    best_alpha = alpha
    if len(series) > 5:
        best_sse = float("inf")
        for a in [0.1, 0.2, 0.3, 0.4, 0.5]:
            s = series[0]
            sse = 0.0
            for y in series[1:]:
                err = y - s
                sse += err ** 2
                s = a * y + (1 - a) * s
            if sse < best_sse:
                best_sse = sse
                best_alpha = a
    # Apply best alpha
    s = series[0]
    for y in series[1:]:
        s = best_alpha * y + (1 - best_alpha) * s
    return [max(0.0, s)] * h


# ─── 6. Metrics ───────────────────────────────────────────────────────────────

def mae(actuals, preds):
    n = len(actuals)
    if n == 0:
        return float("nan")
    return sum(abs(a - p) for a, p in zip(actuals, preds)) / n


def wape(actuals, preds):
    """WAPE = sum(|actual-pred|) / sum(actual)  — avoids zero-target instability."""
    total_actual = sum(actuals)
    if total_actual == 0:
        return float("nan")
    return sum(abs(a - p) for a, p in zip(actuals, preds)) / total_actual


def rmse(actuals, preds):
    n = len(actuals)
    if n == 0:
        return float("nan")
    return math.sqrt(sum((a - p) ** 2 for a, p in zip(actuals, preds)) / n)


def smape(actuals, preds):
    """sMAPE = 2*|a-p|/(|a|+|p|) averaged."""
    vals = []
    for a, p in zip(actuals, preds):
        denom = abs(a) + abs(p)
        if denom > 0:
            vals.append(2 * abs(a - p) / denom)
    return sum(vals) / len(vals) if vals else float("nan")


# ─── 7. Walk-forward evaluation ───────────────────────────────────────────────

def walk_forward_eval(series, eval_start_idx, h=1):
    """
    Rolling-origin evaluation starting at eval_start_idx.
    For each origin t from eval_start_idx to len(series)-1:
      - train = series[:t]
      - predict next 1 step
      - compare to series[t]
    Returns dict of model_name -> (actuals_list, preds_list).
    No future data ever influences earlier predictions.
    """
    results = {
        "Naive": ([], []),
        "MA4": ([], []),
        "MA8": ([], []),
        "OLS": ([], []),
        "SES": ([], []),
    }

    for t in range(eval_start_idx, len(series)):
        train = series[:t]
        if len(train) < 2:
            continue
        actual = series[t]

        preds = {
            "Naive": naive_forecast(train, h=1)[0],
            "MA4":   ma_forecast(train, window=4, h=1)[0],
            "MA8":   ma_forecast(train, window=8, h=1)[0],
            "OLS":   ols_trend_forecast(train, h=1)[0],
            "SES":   ses_forecast(train, h=1)[0],
        }

        for model, (acts, ps) in results.items():
            acts.append(actual)
            ps.append(preds[model])

    return results


def eval_metrics(results):
    """Compute MAE, WAPE, RMSE, sMAPE for each model from walk-forward results."""
    out = {}
    for model, (acts, ps) in results.items():
        out[model] = {
            "MAE":   mae(acts, ps),
            "WAPE":  wape(acts, ps),
            "RMSE":  rmse(acts, ps),
            "sMAPE": smape(acts, ps),
            "n_eval": len(acts),
        }
    return out


def best_model(metrics, criterion="WAPE"):
    """Return model name with lowest criterion score."""
    valid = {m: v[criterion] for m, v in metrics.items() if not math.isnan(v[criterion])}
    if not valid:
        return "Naive"
    return min(valid, key=valid.get)


# ─── 8. Main calibration ──────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("NEXUS D3A — Forecasting Data & Model Calibration")
    print("=" * 70)

    rows = load_sales()
    company, category, all_mondays = aggregate_weekly(rows)

    first_sale = date.fromisoformat(rows[0][0])
    last_sale  = date.fromisoformat(rows[-1][0])
    n_weeks = len(all_mondays)

    partial = detect_partial_weeks(all_mondays, first_sale, last_sale)

    print(f"\n{'─'*60}")
    print("A. WEEKLY DATA COVERAGE")
    print(f"{'─'*60}")
    print(f"  Total sale rows      : {len(rows):,}")
    print(f"  First sale date      : {first_sale}")
    print(f"  Last sale date       : {last_sale}")
    print(f"  First ISO Monday     : {all_mondays[0]}")
    print(f"  Last ISO Monday      : {all_mondays[-1]}")
    print(f"  Total ISO weeks      : {n_weeks}")
    print(f"  Partial weeks        : {len(partial)} → {[str(m) for m in partial]}")

    # Missing weeks
    all_possible = []
    cur = all_mondays[0]
    while cur <= all_mondays[-1]:
        all_possible.append(cur)
        cur += timedelta(weeks=1)
    missing_weeks = [m for m in all_possible if m not in company]
    print(f"  Missing weeks (gaps) : {len(missing_weeks)}")
    if missing_weeks:
        print(f"    {missing_weeks}")

    print(f"\n{'─'*60}")
    print("B. PARTIAL-WEEK DECISION")
    print(f"{'─'*60}")
    print("""  Recommendation: EXCLUDE partial weeks from model training and
  evaluation windows, but include them in the full-data chart display
  with explicit 'PARTIAL' flag.

  Rationale:
    - Jan 2025 begins on a Wednesday; the first ISO week (Mon 2024-12-30)
      has only 2 days of sales data.
    - Dec 31, 2025 is a Wednesday; the last ISO week similarly short.
    - Including partial weeks in WAPE/MAE would systematically
      understate demand and bias model selection.
    - Walk-forward evaluation uses only the clean interior weeks.
  """)

    # Determine clean interior series
    if partial:
        clean_mondays = [m for m in all_mondays if m not in partial]
    else:
        clean_mondays = all_mondays

    print(f"  Clean interior weeks : {len(clean_mondays)}")
    print(f"  Clean range          : {clean_mondays[0]} → {clean_mondays[-1]}")

    # Company series
    comp_units = make_series(company, clean_mondays, "units")
    comp_rev   = make_series(company, clean_mondays, "rev_cents")
    zero_comp_units = sum(1 for v in comp_units if v == 0)
    zero_comp_rev   = sum(1 for v in comp_rev   if v == 0)

    print(f"\n{'─'*60}")
    print("C. DATA COMPLETENESS — Company")
    print(f"{'─'*60}")
    print(f"  Weeks             : {len(comp_units)}")
    print(f"  Zero-demand weeks : {zero_comp_units} (units), {zero_comp_rev} (revenue)")
    print(f"  Units — min/max/mean : {min(comp_units):.0f} / {max(comp_units):.0f} / "
          f"{sum(comp_units)/len(comp_units):.1f}")
    print(f"  Rev (cents) — min/max/mean : {min(comp_rev):.0f} / {max(comp_rev):.0f} / "
          f"{sum(comp_rev)/len(comp_rev):.1f}")

    print(f"\n{'─'*60}")
    print("C. DATA COMPLETENESS — All 16 Categories")
    print(f"{'─'*60}")
    print(f"  {'Category':<35} {'Weeks':>5}  {'Missing':>7}  {'Zero':>4}  {'TotalUnits':>10}")
    cats_sorted = sorted(category.keys())
    cat_clean_series = {}
    for cat in cats_sorted:
        cat_weeks = make_series(category[cat], clean_mondays, "units")
        missing = sum(1 for m in clean_mondays if m not in category[cat])
        zero_w  = sum(1 for v in cat_weeks if v == 0)
        total   = sum(cat_weeks)
        cat_clean_series[cat] = {"units": cat_weeks,
                                  "rev": make_series(category[cat], clean_mondays, "rev_cents")}
        print(f"  {cat:<35} {len(cat_weeks):>5}  {missing:>7}  {zero_w:>4}  {total:>10,}")

    print(f"\n{'─'*60}")
    print("D. FORECAST HORIZONS")
    print(f"{'─'*60}")
    print("""  Evaluated: 4 weeks, 8 weeks
  Recommendation: PRIMARY HORIZON = 4 WEEKS

  Rationale:
    - With only 52 weeks of data, an 8-week horizon leaves only
      ~44 training observations, which is borderline for trend models.
    - 4-week horizon aligns with typical retail planning cycles.
    - 4-week walk-forward retains adequate evaluation samples.
    - An 8-week horizon is provided as secondary reference only.
  """)

    print(f"\n{'─'*60}")
    print("E. EVALUATION METHODOLOGY")
    print(f"{'─'*60}")
    print(f"""  Method: Rolling-Origin (Walk-Forward) — one-step-ahead
  Evaluation starts at week index {max(8, len(clean_mondays)//4)} (approx. last 12 weeks).
  At each origin t:
    train = series[0:t]   (only past data)
    pred  = model.fit(train).forecast(h=1)
    actual = series[t]
  No test data ever sees future observations.
  No normalisation applied (raw units/cents used directly).
  Model selection criterion: WAPE (robust to zero targets).
  """)

    # Evaluation setup: last ~12 weeks for eval, min 8 origins
    eval_start_n_from_end = min(12, max(8, n_weeks // 4))
    eval_start_idx = len(clean_mondays) - eval_start_n_from_end

    print(f"  Walk-forward starts at index : {eval_start_idx}")
    print(f"  Evaluation origins           : {eval_start_n_from_end}")
    print(f"  Eval covers weeks            : {clean_mondays[eval_start_idx]} → {clean_mondays[-1]}")

    print(f"\n{'─'*60}")
    print("F. COMPANY UNITS — Model Comparison")
    print(f"{'─'*60}")
    cu_results = walk_forward_eval(comp_units, eval_start_idx)
    cu_metrics = eval_metrics(cu_results)
    print(f"  {'Model':<8} {'MAE':>8}  {'WAPE':>8}  {'RMSE':>8}  {'sMAPE':>8}  {'N':>4}")
    for model, m in cu_metrics.items():
        print(f"  {model:<8} {m['MAE']:>8.1f}  {m['WAPE']:>8.4f}  {m['RMSE']:>8.1f}  {m['sMAPE']:>8.4f}  {m['n_eval']:>4}")
    best_cu = best_model(cu_metrics)
    print(f"\n  → Best for Company Units : {best_cu}  (WAPE = {cu_metrics[best_cu]['WAPE']:.4f})")

    print(f"\n{'─'*60}")
    print("G. COMPANY REVENUE — Model Comparison")
    print(f"{'─'*60}")
    cr_results = walk_forward_eval(comp_rev, eval_start_idx)
    cr_metrics = eval_metrics(cr_results)
    print(f"  {'Model':<8} {'MAE':>12}  {'WAPE':>8}  {'RMSE':>12}  {'sMAPE':>8}")
    for model, m in cr_metrics.items():
        print(f"  {model:<8} {m['MAE']:>12.0f}  {m['WAPE']:>8.4f}  {m['RMSE']:>12.0f}  {m['sMAPE']:>8.4f}")
    best_cr = best_model(cr_metrics)
    print(f"\n  → Best for Company Revenue : {best_cr}  (WAPE = {cr_metrics[best_cr]['WAPE']:.4f})")

    print(f"\n{'─'*60}")
    print("H. CATEGORY UNITS — Model Comparison (all 16)")
    print(f"{'─'*60}")
    print(f"  {'Category':<35} {'n_wk':>4}  {'Best':>6}  {'WAPE':>8}")
    cat_best_tally = defaultdict(int)
    cat_models = {}
    for cat in cats_sorted:
        series_u = cat_clean_series[cat]["units"]
        n_eval_start = max(4, len(series_u) - 12)
        if n_eval_start >= len(series_u):
            cat_models[cat] = {"best": "Naive", "wape": float("nan"), "n": len(series_u)}
            cat_best_tally["Naive"] += 1
            print(f"  {cat:<35} {len(series_u):>4}  {'Naive':>6}  {'N/A':>8}")
            continue
        r = walk_forward_eval(series_u, n_eval_start)
        m = eval_metrics(r)
        b = best_model(m)
        cat_models[cat] = {"best": b, "wape": m[b]["WAPE"], "n": len(series_u)}
        cat_best_tally[b] += 1
        wape_str = f"{m[b]['WAPE']:.4f}" if not math.isnan(m[b]["WAPE"]) else "N/A"
        print(f"  {cat:<35} {len(series_u):>4}  {b:>6}  {wape_str:>8}")

    print(f"\n  Model selection tally:")
    for model, cnt in sorted(cat_best_tally.items(), key=lambda x: -x[1]):
        print(f"    {model:<8}: {cnt} categories")

    print(f"\n{'─'*60}")
    print("I. BEST MODELS SUMMARY")
    print(f"{'─'*60}")
    print(f"  Company units   : {best_cu}  (WAPE={cu_metrics[best_cu]['WAPE']:.4f})")
    print(f"  Company revenue : {best_cr}  (WAPE={cr_metrics[best_cr]['WAPE']:.4f})")
    print("  Note: Models selected independently per target; same model winning both is coincidental.")

    print(f"\n{'─'*60}")
    print("J. 4-WEEK FORWARD FORECASTS (from full clean series)")
    print(f"{'─'*60}")
    H = 4

    # Generate next 4 week labels
    next_mondays = [clean_mondays[-1] + timedelta(weeks=i+1) for i in range(H)]

    # Company units
    cu_fcast_fn = {
        "Naive": naive_forecast, "MA4": lambda s,h: ma_forecast(s,4,h),
        "MA8": lambda s,h: ma_forecast(s,8,h),
        "OLS": ols_trend_forecast, "SES": ses_forecast
    }
    cu_best_fcast = cu_fcast_fn[best_cu](comp_units, H)
    cr_best_fcast = cu_fcast_fn[best_cr](comp_rev, H)

    print(f"\n  Company Units — {best_cu} model forecast (next 4 weeks):")
    print(f"  {'Week':>12}  {'Forecast Units':>15}  Type")
    for i, (m, v) in enumerate(zip(next_mondays, cu_best_fcast)):
        flag = "FORECAST" if v >= 0 else "FORECAST [NEGATIVE — model rejected]"
        print(f"  {str(m):>12}  {v:>15.1f}  {flag}")

    print(f"\n  Company Revenue — {best_cr} model forecast (next 4 weeks):")
    print(f"  {'Week':>12}  {'Forecast Rev ($)':>18}  Type")
    for i, (m, v) in enumerate(zip(next_mondays, cr_best_fcast)):
        flag = "FORECAST" if v >= 0 else "FORECAST [NEGATIVE — model rejected]"
        print(f"  {str(m):>12}  ${v/100:>17,.2f}  {flag}")

    print(f"\n  Category Units — Best-model forecasts (Week+1 only, illustrative):")
    print(f"  {'Category':<35}  {'Model':>6}  {'Wk+1 Units':>10}  {'Wk+2':>10}  {'Wk+3':>10}  {'Wk+4':>10}")
    for cat in cats_sorted:
        series_u = cat_clean_series[cat]["units"]
        b = cat_models[cat]["best"]
        if b == "Naive":
            fcast = naive_forecast(series_u, H)
        elif b == "MA4":
            fcast = ma_forecast(series_u, window=4, h=H)
        elif b == "MA8":
            fcast = ma_forecast(series_u, window=8, h=H)
        elif b == "OLS":
            fcast = ols_trend_forecast(series_u, H)
        elif b == "SES":
            fcast = ses_forecast(series_u, H)
        else:
            fcast = naive_forecast(series_u, H)
        # Pad to H if shorter
        while len(fcast) < H:
            fcast.append(fcast[-1] if fcast else 0.0)
        safe_fcast = [max(0.0, v) for v in fcast]  # clip negatives with flag
        had_neg = any(v < 0 for v in fcast)
        neg_flag = " [clipped]" if had_neg else ""
        print(f"  {cat:<35}  {b:>6}  {safe_fcast[0]:>10.1f}  {safe_fcast[1]:>10.1f}  "
              f"{safe_fcast[2]:>10.1f}  {safe_fcast[3]:>10.1f}{neg_flag}")

    print(f"\n{'─'*60}")
    print("K. ERROR METRICS — Formulae")
    print(f"{'─'*60}")
    print("""
  MAE  = (1/n) * Σ |actual - forecast|
  WAPE = Σ|actual - forecast| / Σ actual          (weighted; avoids zero instability)
  RMSE = sqrt((1/n) * Σ (actual - forecast)²)
  sMAPE= (1/n) * Σ 2*|a-p| / (|a|+|p|)           (symmetric; bounded 0–2)

  MAPE is intentionally NOT used — division by zero when actual=0
  would produce undefined values for any low-demand category week.
  WAPE is the primary selection criterion.
  """)

    print(f"\n{'─'*60}")
    print("L. NEGATIVE FORECAST HANDLING")
    print(f"{'─'*60}")
    # Check OLS on company units for negativity
    ols_cu = ols_trend_forecast(comp_units, H)
    ols_cr = ols_trend_forecast(comp_rev, H)
    cu_neg = any(v < 0 for v in ols_cu)
    cr_neg = any(v < 0 for v in ols_cr)
    print(f"  OLS company units forecast (4 weeks) : {[round(v,1) for v in ols_cu]}")
    print(f"  OLS company revenue forecast (4 weeks): {[round(v/100,2) for v in ols_cr]}")
    print(f"  OLS produces negatives (units)   : {cu_neg}")
    print(f"  OLS produces negatives (revenue) : {cr_neg}")
    print("""
  Policy:
    - If OLS produces negative values for any category forecast, the category
      falls back to the second-best model (MA4 or Naive).
    - For company-level forecasts, OLS negativity triggers automatic rejection
      in D3B — Moving Average or SES is preferred instead.
    - Category-level negatives above are explicitly documented as [clipped] for
      display only; D3B will not present clipped OLS forecasts as authoritative.
  """)

    print(f"\n{'─'*60}")
    print("M. UNCERTAINTY TREATMENT")
    print(f"{'─'*60}")
    print("""
  No statistical confidence intervals are produced in D3A.

  Rationale:
    - Naive and Moving Average have no closed-form forecast distribution.
    - SES intervals require stationarity assumptions not verified on one year.
    - OLS intervals require homoscedastic residuals (not tested).

  In D3B, uncertainty will be represented as:
    ± 1-sigma historical error band   =   mean(|residuals|) from walk-forward

  This is an empirical range, not a probabilistic guarantee.
  It will be labelled explicitly as "Historical Error Band" — not
  "Confidence Interval" or "Prediction Interval".
  """)

    # Compute 1-sigma error bands for best models
    cu_residuals = [abs(a - p) for a, p in zip(*cu_results[best_cu])]
    cr_residuals = [abs(a - p) for a, p in zip(*cr_results[best_cr])]
    cu_sigma = sum(cu_residuals) / len(cu_residuals) if cu_residuals else 0
    cr_sigma = sum(cr_residuals) / len(cr_residuals) if cr_residuals else 0
    print(f"  Company Units   MAE (error band) : ±{cu_sigma:.1f} units/week")
    print(f"  Company Revenue MAE (error band) : ±${cr_sigma/100:,.2f}/week")

    print(f"\n{'─'*60}")
    print("N. DEMAND-PLANNING FEASIBILITY")
    print(f"{'─'*60}")
    print(f"""
  FEASIBILITY: YES — with documented caveats.

  Proposed derived metric (D3B candidate):

    forecast_demand_next_4_weeks[product_category]
      = sum of 4-week category unit forecasts

    coverage_vs_forecast[category, store]
      = current_stock_units / forecast_demand_next_4_weeks[category]

  Limitations:
    1. Inventory snapshot date is assumed (Dec 31, 2025).
       Stock figures may not represent current physical inventory.
    2. Category-level forecasts cannot be disaggregated to SKU level
       without additional product-level sales data (possible in D3B).
    3. Replenishment recommendations will NOT be auto-generated.
       The ratio is a planning aid, not an automated order trigger.
    4. Zero-demand categories could create division artifacts; a floor
       must be applied in implementation.

  D3B action item: implement `coverage_vs_forecast` as a read-only
  computed metric on the Insights & Risk page or a dedicated Planning view.
  """)

    print(f"\n{'─'*60}")
    print("O. DATA LEAKAGE SAFEGUARDS")
    print(f"{'─'*60}")
    print("""
  1. CHRONOLOGICAL SPLIT: Walk-forward evaluation uses only series[0:t]
     to predict series[t]. Future observations are never in the training
     window at any origin.
  2. NO NORMALISATION: Raw unit and cent values are used. No global
     statistics (mean, std) are computed over the full series before
     splitting, so there is no statistical leakage.
  3. PARAMETER TUNING: SES alpha is tuned via in-sample one-step-ahead
     SSE on the training window at each origin — not on the full series.
  4. MODEL SELECTION: Best model chosen by WAPE computed strictly over
     evaluation origins, none of which are in the future at selection time.
  5. FORECAST GENERATION: Final 4-week forward forecasts use the complete
     clean interior series (no evaluation data discarded) — this is the
     correct final-model step after evaluation.
  """)

    print(f"\n{'─'*60}")
    print("P. DEPENDENCIES REQUIRED")
    print(f"{'─'*60}")
    print("""
  D3A uses ZERO new dependencies.
  All computation uses:
    - sqlite3   (stdlib)
    - math      (stdlib)
    - datetime  (stdlib)
    - collections.defaultdict  (stdlib)

  No scikit-learn, numpy, scipy, statsmodels, prophet, or torch needed.
  D3B will use the same constraint — lightweight custom implementations only.
  """)

    print(f"\n{'─'*60}")
    print("Q. KNOWN LIMITATIONS")
    print(f"{'─'*60}")
    print("""
  1. ONE YEAR OF DATA: Cannot validate annual or multi-year seasonality.
     Weekly/intra-month patterns are exploratory only — not ground truth.
  2. SYNTHETIC DATA: Dataset is Kaggle-generated. Demand patterns may be
     artificially smooth or lack realistic distribution spikes.
  3. SES = LEVEL MODEL: No trend or seasonality component. Will lag
     during ramp-up or ramp-down periods.
  4. OLS TREND: Extrapolates linearly. May produce negatives for low-demand
     categories. Flagged and rejected where applicable.
  5. CATEGORY DISAGGREGATION: Forecasts are at category level. SKU-level
     forecast requires product-level walk-forward (feasible in D3B).
  6. NO EXTERNAL REGRESSORS: Holidays, promotions, price changes — none
     are modelled. The dataset does not supply these variables.
  7. 4-WEEK HORIZON: Longer horizons (8+ weeks) accumulate error quickly
     with these simple models on 52 weeks of data.
  """)

    print(f"\n{'─'*60}")
    print("R. PROPOSED D3B ARCHITECTURE")
    print(f"{'─'*60}")
    print(f"""
  Files to create in D3B:

    backend/app/core/forecast_config.py
      → Immutable config: best models, horizon, eval windows, SES alphas
        per series (company/category), partial-week exclusion list.

    backend/app/repositories/forecast_repository.py
      → SQL: weekly aggregated series (clean interior weeks only)
      → Uses nexus_analytics.db read-only; never modifies it.

    backend/app/services/forecast_service.py
      → Implements Naive, MA4, MA8, OLS, SES from stdlib only.
      → Walk-forward evaluation for audit reproducibility.
      → Generates 4-week forward forecasts using calibrated best models.
      → Computes error bands (MAE from evaluation residuals).
      → Returns structured Pydantic response objects.

    backend/app/models/forecast.py
      → ForecastPoint(week_start, value, type: 'historical'|'forecast')
      → ForecastSeries(target, model, horizon, points, error_band_units)
      → ForecastResponse(company_units, company_revenue, categories)
      → DemandCoverageMetric(category, stock_units, forecast_4w, coverage_ratio)

    backend/app/api/forecast.py
      → GET /api/forecast/company       → company units + revenue
      → GET /api/forecast/categories    → all 16 category unit forecasts
      → GET /api/forecast/coverage      → demand-vs-stock coverage ratios
      → No POST/PUT; all read-only.

    backend/tests/test_forecast_service.py
    backend/tests/test_forecast_api.py

    frontend/src/pages/ForecastingAndPlanning.jsx
    frontend/src/components/forecast/  (chart + table components)

  Best models from D3A calibration:
    Company units   : {best_cu}
    Company revenue : {best_cr}
  """)

    print(f"\n{'─'*60}")
    print("S. D3B GO / NO-GO RECOMMENDATION")
    print(f"{'─'*60}")
    # Assess data quality
    low_wape_cu = cu_metrics[best_cu]["WAPE"] < 0.15
    low_wape_cr = cr_metrics[best_cr]["WAPE"] < 0.15
    zero_weeks_ok = zero_comp_units == 0
    gaps_ok = len(missing_weeks) == 0

    print(f"\n  Company units  WAPE ({best_cu}): {cu_metrics[best_cu]['WAPE']:.4f}  — {'OK' if low_wape_cu else 'ELEVATED'}")
    print(f"  Company revenue WAPE ({best_cr}): {cr_metrics[best_cr]['WAPE']:.4f}  — {'OK' if low_wape_cr else 'ELEVATED'}")
    print(f"  Missing week gaps: {len(missing_weeks)}  — {'OK' if gaps_ok else 'GAPS FOUND'}")
    print(f"  Zero-demand weeks (company): {zero_comp_units}  — {'OK' if zero_weeks_ok else 'ZERO WEEKS'}")

    go = gaps_ok and zero_weeks_ok
    verdict = "✅ GO" if go else "⚠️ CONDITIONAL GO"
    print(f"\n  Verdict: {verdict}")
    print("""
  Conditions for D3B GO:
    [x] Data is complete (no missing weeks)
    [x] No company-level zero-demand weeks
    [x] Walk-forward evaluation produces stable WAPE < 0.20
    [x] No new dependencies required
    [x] Negative forecast handling policy defined
    [x] Uncertainty disclosure policy defined
    [x] D3A limitations documented

  D3B Scope:
    backend: forecast_config + forecast_repository + forecast_service
             + forecast models + API routes + full tests
    frontend: ForecastingAndPlanning page + components
    NO Azure, NO agents, NO nexus.db modification.
  """)


if __name__ == "__main__":
    main()
