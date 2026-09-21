import React, { useState, useEffect, useCallback } from 'react';
import {
  ShieldAlert,
  AlertCircle,
  Loader2,
  RefreshCw,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

import {
  getRiskOverview,
  getRiskStockouts,
  getRiskInventoryPressure,
  getRiskSlowMoving,
  getRiskConcentration,
  getRiskSalesVelocity,
} from '../services/api';

import { RiskTransparencyBanner } from '../components/risk/RiskTransparencyBanner';
import { RiskOverviewSection } from '../components/risk/RiskOverviewSection';
import { StockoutExposureSection } from '../components/risk/StockoutExposureSection';
import { InventoryPressureSection } from '../components/risk/InventoryPressureSection';
import { SlowMovingExposureSection } from '../components/risk/SlowMovingExposureSection';
import { SalesVelocitySection } from '../components/risk/SalesVelocitySection';
import { PortfolioConcentrationSection } from '../components/risk/PortfolioConcentrationSection';

// ─── Collapsible section wrapper ─────────────────────────────────────────────
function RiskSection({ id, title, defaultOpen = true, children }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <section id={id} className="rounded-xl border border-[#1f1a54]/60 bg-[#07041c]/40 overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-[#130f3b]/30 transition-colors"
      >
        <span className="text-sm font-semibold text-[#fbfbfe]">{title}</span>
        {open
          ? <ChevronUp className="w-4 h-4 text-slate-400" />
          : <ChevronDown className="w-4 h-4 text-slate-400" />}
      </button>
      {open && (
        <div className="px-5 pb-5 space-y-4 border-t border-[#1f1a54]/40 pt-4">
          {children}
        </div>
      )}
    </section>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────
export function InsightsAndRisk() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isUnavailable503, setIsUnavailable503] = useState(false);

  // Domain data
  const [overview, setOverview] = useState(null);
  const [stockouts, setStockouts] = useState(null);
  const [inventoryPressure, setInventoryPressure] = useState(null);
  const [slowMoving, setSlowMoving] = useState(null);
  const [concentration, setConcentration] = useState(null);
  const [salesVelocity, setSalesVelocity] = useState(null);

  /**
   * Coordinated single page-load fetch — no duplicate requests per render.
   */
  const loadRiskData = useCallback(async () => {
    setLoading(true);
    setError(null);
    setIsUnavailable503(false);

    try {
      const [
        overviewRes,
        stockoutsRes,
        pressureRes,
        slowRes,
        concRes,
        velocityRes,
      ] = await Promise.all([
        getRiskOverview(),
        getRiskStockouts(),
        getRiskInventoryPressure({ limit: 50 }),
        getRiskSlowMoving({ limit: 20 }),
        getRiskConcentration(),
        getRiskSalesVelocity({ limit: 50 }),
      ]);

      setOverview(overviewRes);
      setStockouts(stockoutsRes);
      setInventoryPressure(pressureRes);
      setSlowMoving(slowRes);
      setConcentration(concRes);
      setSalesVelocity(velocityRes);
    } catch (err) {
      console.error('Error loading risk data:', err);
      const msg = err.message || '';
      if (msg.includes('503') || msg.toLowerCase().includes('unavailable')) {
        setIsUnavailable503(true);
      } else {
        setError(msg || 'An unexpected error occurred while loading risk analytics.');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadRiskData();
  }, [loadRiskData]);

  // ── Loading ────────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="p-6 md:p-8 max-w-7xl mx-auto flex flex-col items-center justify-center min-h-[60vh] text-slate-400">
        <Loader2 className="w-8 h-8 animate-spin text-rose-400 mb-3" />
        <div className="text-sm font-medium text-slate-200">Loading Risk Analytics…</div>
        <div className="text-xs text-slate-500 mt-1">Running deterministic computations on nexus_analytics.db</div>
      </div>
    );
  }

  // ── 503 Unavailable ────────────────────────────────────────────────────────
  if (isUnavailable503) {
    return (
      <div className="p-6 md:p-8 max-w-7xl mx-auto">
        <div className="rounded-xl bg-amber-950/30 border border-amber-500/40 p-8 text-center space-y-4">
          <div className="w-12 h-12 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center mx-auto">
            <AlertCircle className="w-6 h-6" />
          </div>
          <div className="text-base font-semibold text-amber-200">Analytics Database Unavailable</div>
          <p className="text-sm text-amber-300/70 max-w-lg mx-auto">
            The risk analytics database (nexus_analytics.db) is not available.
            Run <code className="bg-amber-900/40 px-1.5 py-0.5 rounded text-amber-200">python import_kaggle_dataset.py</code> to generate it.
          </p>
          <button
            type="button"
            onClick={loadRiskData}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-amber-500/20 border border-amber-500/40 text-amber-200 hover:bg-amber-500/30 transition-colors text-sm font-medium"
          >
            <RefreshCw className="w-4 h-4" />
            Retry
          </button>
        </div>
      </div>
    );
  }

  // ── Generic Error ──────────────────────────────────────────────────────────
  if (error) {
    return (
      <div className="p-6 md:p-8 max-w-7xl mx-auto">
        <div className="rounded-xl bg-rose-950/30 border border-rose-500/40 p-6 text-center space-y-3">
          <AlertCircle className="w-6 h-6 text-rose-400 mx-auto" />
          <div className="text-sm font-semibold text-rose-200">{error}</div>
          <button
            type="button"
            onClick={loadRiskData}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-rose-500/20 border border-rose-500/40 text-rose-200 hover:bg-rose-500/30 transition-colors text-sm font-medium"
          >
            <RefreshCw className="w-4 h-4" />
            Retry
          </button>
        </div>
      </div>
    );
  }

  // ── Main Render ────────────────────────────────────────────────────────────
  return (
    <div className="p-6 md:p-8 space-y-6 max-w-7xl mx-auto">

      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-rose-950/60 border border-rose-500/40 flex items-center justify-center">
            <ShieldAlert className="w-5 h-5 text-rose-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-[#fbfbfe]">Insights &amp; Risk</h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Deterministic risk analytics · D2A-calibrated thresholds · No AI scoring
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={loadRiskData}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#07041c]/80 border border-[#1f1a54]/60 text-slate-300 hover:text-white hover:bg-[#130f3b]/60 transition-colors text-xs font-medium"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      {/* Dataset & methodology transparency */}
      <RiskTransparencyBanner />

      {/* 1. Independent Domain Overview */}
      <RiskSection id="risk-overview" title="Independent Risk Domain Overview" defaultOpen>
        <RiskOverviewSection overview={overview} />
      </RiskSection>

      {/* 2. Stockout Exposure */}
      <RiskSection id="stockout-exposure" title="Stockout Exposure" defaultOpen>
        <StockoutExposureSection data={stockouts} />
      </RiskSection>

      {/* 3. Inventory Pressure */}
      <RiskSection id="inventory-pressure" title="Inventory Pressure" defaultOpen>
        <InventoryPressureSection data={inventoryPressure} />
      </RiskSection>

      {/* 4. Slow-Moving Inventory Exposure */}
      <RiskSection id="slow-moving" title="Slow-Moving Inventory Exposure" defaultOpen>
        <SlowMovingExposureSection data={slowMoving} />
      </RiskSection>

      {/* 5. Sales Velocity */}
      <RiskSection id="sales-velocity" title="Sales Velocity Changes" defaultOpen>
        <SalesVelocitySection data={salesVelocity} />
      </RiskSection>

      {/* 6. Portfolio Revenue Concentration */}
      <RiskSection id="concentration" title="Portfolio Revenue Concentration" defaultOpen>
        <PortfolioConcentrationSection data={concentration} />
      </RiskSection>

      {/* Footer note */}
      <div className="text-[11px] text-slate-500 text-center pb-4">
        Risk analytics sourced exclusively from nexus_analytics.db (Kaggle USA Toy Sales 2025, CC0).
        No Azure, Foundry, or AI model calls are involved in these computations.
      </div>
    </div>
  );
}
