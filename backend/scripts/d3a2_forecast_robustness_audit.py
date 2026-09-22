"""
NEXUS D3A.2 — Forecast Robustness Audit
========================================
Analysis-only, stdlib-only audit. Uses exhaustive eligible rolling origins
(minimum 20 training weeks, H=4) over the 51 verified complete weekly buckets.
No API/frontend/agent/Azure work is performed here.
"""
from __future__ import annotations

import math
from datetime import date, timedelta
from pathlib import Path
import importlib.util

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
D3A1_PATH = SCRIPT_DIR / "d3a1_forecast_audit.py"

spec = importlib.util.spec_from_file_location("d3a1", D3A1_PATH)
d3a1 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(d3a1)

H = 4
MIN_TRAIN = 20
PRACTICAL_TIE = 0.002


def exhaustive_eval(series, h=H, min_train=MIN_TRAIN):
    n = len(series)
    max_t = n - h
    if max_t < min_train:
        raise ValueError("Insufficient observations for exhaustive H-step evaluation")
    origins = list(range(min_train, max_t + 1))
    results = {m: {i: ([], []) for i in range(h)} for m in d3a1.MODELS}
    for t in origins:
        train = series[:t]
        actual = series[t:t+h]
        for model in d3a1.MODELS:
            preds = d3a1.run_model(model, train, h)
            for i in range(h):
                results[model][i][0].append(actual[i])
                results[model][i][1].append(preds[i])
    return results, origins


def select_best_strict(metrics):
    """Exact WAPE winner; tie annotation handled separately in reporting."""
    return min(d3a1.MODELS, key=lambda m: (metrics[m]["agg_wape"], metrics[m]["agg_rmse"]))


def reliability_label(wape):
    if wape <= 0.10:
        return "Strong"
    if wape <= 0.20:
        return "Moderate"
    return "Limited"


def pct(v):
    return f"{v:.4f}"


def main():
    rows = d3a1.load_raw()
    first_sale = date.fromisoformat(rows[0][0])
    last_sale = date.fromisoformat(rows[-1][0])
    company, categories = d3a1.build_buckets(rows)
    complete, partial = d3a1.classify_buckets(company, first_sale, last_sale)

    assert len(company) == 53
    assert len(complete) == 51
    assert len(partial) == 2
    assert complete[0].isoformat() == "2025-01-06"
    assert complete[-1].isoformat() == "2025-12-22"
    assert partial[0].isoformat() == "2024-12-30"
    assert partial[-1].isoformat() == "2025-12-29"
    assert all(len(company[m]["dates"]) == 7 for m in complete)

    units = d3a1.make_series(company, complete, "units")
    revenue = d3a1.make_series(company, complete, "rev_cents")

    ures, origins = exhaustive_eval(units)
    rres, origins_r = exhaustive_eval(revenue)
    assert origins == origins_r
    um = d3a1.horizon_metrics(ures, H)
    rm = d3a1.horizon_metrics(rres, H)
    best_units = select_best_strict(um)
    best_revenue = select_best_strict(rm)

    print("="*76)
    print("NEXUS D3A.2 — EXHAUSTIVE 4-HORIZON FORECAST ROBUSTNESS AUDIT")
    print("="*76)
    print("A. WEEKLY SERIES")
    print(f"  total buckets      : {len(company)}")
    print(f"  partial buckets    : {[m.isoformat() for m in partial]}")
    print(f"  complete buckets   : {len(complete)}")
    print(f"  clean range        : {complete[0]} -> {complete[-1]} (through {complete[-1]+timedelta(days=6)})")
    print()
    print("B. EXHAUSTIVE ROLLING ORIGINS")
    print(f"  min training weeks : {MIN_TRAIN}")
    print(f"  horizon            : {H}")
    print(f"  exact origin count : {len(origins)}")
    print(f"  origin indices     : {origins[0]} .. {origins[-1]}")
    print(f"  first eval week    : {complete[origins[0]]}")
    print(f"  last H4 week       : {complete[origins[-1]+H-1]}")

    def print_company(title, metrics):
        print("\n"+title)
        print(f"  {'Model':<7} {'H1':>8} {'H2':>8} {'H3':>8} {'H4':>8} {'AggWAPE':>9} {'AggRMSE':>12}")
        for m in d3a1.MODELS:
            x=metrics[m]
            print(f"  {m:<7} {x['h'][0]['WAPE']:>8.4f} {x['h'][1]['WAPE']:>8.4f} {x['h'][2]['WAPE']:>8.4f} {x['h'][3]['WAPE']:>8.4f} {x['agg_wape']:>9.4f} {x['agg_rmse']:>12.2f}")

    print_company("C. COMPANY UNITS", um)
    print(f"  exact winner       : {best_units}")
    print(f"  practical-tie set  : {[m for m in d3a1.MODELS if um[m]['agg_wape']-um[best_units]['agg_wape'] <= PRACTICAL_TIE]}")
    print("  horizon MAE        : "+", ".join(f"H{i+1}={um[best_units]['h'][i]['MAE']:.2f}" for i in range(H)))

    print_company("D. COMPANY REVENUE", rm)
    print(f"  exact winner       : {best_revenue}")
    print(f"  practical-tie set  : {[m for m in d3a1.MODELS if rm[m]['agg_wape']-rm[best_revenue]['agg_wape'] <= PRACTICAL_TIE]}")
    print("  horizon MAE cents  : "+", ".join(f"H{i+1}={rm[best_revenue]['h'][i]['MAE']:.0f}" for i in range(H)))

    print("\nE. CATEGORY UNITS")
    print(f"  {'Category':<20} {'Best':<6} {'H1':>7} {'H2':>7} {'H3':>7} {'H4':>7} {'Agg':>7} {'Reliability':<10}")
    category_results = []
    tally = {m:0 for m in d3a1.MODELS}
    for cat in sorted(categories):
        s = d3a1.make_series(categories[cat], complete, "units")
        cres, corig = exhaustive_eval(s)
        cm = d3a1.horizon_metrics(cres, H)
        best = select_best_strict(cm)
        tally[best]+=1
        x=cm[best]
        rel=reliability_label(x['agg_wape'])
        category_results.append((cat,best,x,rel))
        print(f"  {cat:<20} {best:<6} {x['h'][0]['WAPE']:>7.4f} {x['h'][1]['WAPE']:>7.4f} {x['h'][2]['WAPE']:>7.4f} {x['h'][3]['WAPE']:>7.4f} {x['agg_wape']:>7.4f} {rel:<10}")
    print("  tally              : "+", ".join(f"{m}={tally[m]}" for m in d3a1.MODELS))

    print("\nF. LOCKED FORECASTS FROM ALL 51 COMPLETE WEEKS")
    future = [complete[-1] + timedelta(weeks=i) for i in range(1,H+1)]
    # complete[-1] is 2025-12-22; +1 week = Dec 29
    unit_preds = d3a1.run_model(best_units, units, H)
    rev_preds = d3a1.run_model(best_revenue, revenue, H)
    print(f"  Company Units model   : {best_units}")
    print("  Company Units          : "+", ".join(f"{future[i]}={unit_preds[i]:.1f}" for i in range(H)))
    print(f"  Company Revenue model : {best_revenue}")
    print("  Company Revenue cents  : "+", ".join(f"{future[i]}={rev_preds[i]:.0f}" for i in range(H)))

    print("\n  Category forecasts:")
    for cat,best,x,rel in category_results:
        s=d3a1.make_series(categories[cat], complete, "units")
        preds=d3a1.run_model(best,s,H)
        print(f"  {cat:<20} {best:<6} {rel:<9} " + " ".join(f"{p:.1f}" for p in preds))

    print("\nG. LOCKED CONTRACT")
    print("  Reliability: <=0.10 Strong; <=0.20 Moderate; >0.20 Limited")
    print("  Historical MAE Reference: horizon-specific MAE; NOT a confidence interval")
    print("  coverage_ratio = current_stock / forecast_4w_units")
    print("  forecast_coverage_weeks = current_stock / (forecast_4w_units / 4)")
    print("  Model cutoff: complete weeks through 2025-12-28; partial Dec29-31 excluded from training")
    print("  No Azure / no new dependencies / no production code changes")


if __name__ == "__main__":
    main()
