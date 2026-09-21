import React from 'react';
import { Layers, Info } from 'lucide-react';
import { formatUSDFromCents, formatNumber } from '../../utils/formatters';

const PRODUCT_DOS_P90 = 241.34;
const PRODUCT_CAPITAL_FLOOR = 2087756; // cents
const PLACEMENT_DOS_P90 = 392.04;
const PLACEMENT_CAPITAL_FLOOR = 27554; // cents

/**
 * SlowMovingExposureSection
 *
 * Displays slow-moving inventory exposure at both product and placement level.
 * Uses "Slow-Moving Inventory Exposure" terminology — never "obsolete" or "holding cost".
 */
export function SlowMovingExposureSection({ data }) {
  if (!data) {
    return (
      <div className="rounded-xl border border-[#1f1a54]/60 bg-[#07041c]/60 p-6 text-center text-slate-400 text-sm">
        Slow-moving exposure data unavailable.
      </div>
    );
  }

  const {
    product_level_candidates_count = 0,
    product_level_capital_exposure_cents = 0,
    placement_level_candidates_count = 0,
    placement_level_capital_exposure_cents = 0,
    candidate_products = [],
    candidate_placements = [],
    snapshot_date,
    snapshot_date_is_assumed,
    currency_code = 'USD',
    terminology_note,
  } = data;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2 flex-wrap">
        <Layers className="w-5 h-5 text-orange-400" />
        <h2 className="text-base font-semibold text-[#fbfbfe]">Slow-Moving Inventory Exposure</h2>
        <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-orange-950/40 border border-orange-500/40 text-orange-300">
          Capital Exposure in Low-Turnover Inventory
        </span>
      </div>

      {/* Dual-condition rule explanation */}
      <div className="rounded-xl border border-[#1f1a54]/60 bg-[#07041c]/80 p-4 space-y-3">
        <div className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
          <Info className="w-3.5 h-3.5 text-[#a5a0ff]" />
          Dual-Condition Classification Rules (D2A Calibrated)
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-[11px]">
          <div className="rounded-lg bg-[#130f3b]/60 border border-orange-500/20 px-3 py-2.5 space-y-1">
            <div className="font-semibold text-orange-200">Product-Level</div>
            <div className="text-slate-300">DOS &gt; {PRODUCT_DOS_P90} days (P90)</div>
            <div className="text-slate-300">AND inventory cost ≥ ${(PRODUCT_CAPITAL_FLOOR / 100).toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
            <div className="text-slate-400 text-[10px]">P90 of product annual velocity; P75 of product inventory cost</div>
          </div>
          <div className="rounded-lg bg-[#130f3b]/60 border border-violet-500/20 px-3 py-2.5 space-y-1">
            <div className="font-semibold text-violet-200">Placement-Level</div>
            <div className="text-slate-300">DOS &gt; {PLACEMENT_DOS_P90} days (P90)</div>
            <div className="text-slate-300">AND inventory cost ≥ ${(PLACEMENT_CAPITAL_FLOOR / 100).toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
            <div className="text-slate-400 text-[10px]">P90 of positive-stock placement DOS; P75 of placement inventory cost</div>
          </div>
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="rounded-xl border border-orange-500/30 bg-orange-950/10 p-4">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">Product-Level Candidates</div>
          <div className="text-2xl font-bold text-[#fbfbfe]">{formatNumber(product_level_candidates_count)}</div>
          <div className="text-xs text-slate-400 mt-1">products meeting dual condition</div>
          <div className="mt-3 text-[10px] text-slate-400 uppercase tracking-wider">Capital Exposure</div>
          <div className="text-lg font-bold text-orange-200">
            {formatUSDFromCents(product_level_capital_exposure_cents)}
          </div>
        </div>
        <div className="rounded-xl border border-violet-500/30 bg-violet-950/10 p-4">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">Placement-Level Candidates</div>
          <div className="text-2xl font-bold text-[#fbfbfe]">{formatNumber(placement_level_candidates_count)}</div>
          <div className="text-xs text-slate-400 mt-1">placements meeting dual condition</div>
          <div className="mt-3 text-[10px] text-slate-400 uppercase tracking-wider">Capital Exposure</div>
          <div className="text-lg font-bold text-violet-200">
            {formatUSDFromCents(placement_level_capital_exposure_cents)}
          </div>
        </div>
      </div>

      {/* Product-level candidates table */}
      {candidate_products.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs font-semibold text-slate-300">Product-Level Slow-Moving Candidates</div>
          <div className="rounded-xl border border-[#1f1a54]/60 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-[#1f1a54]/60 bg-[#07041c]/80">
                    <th className="px-3 py-2.5 text-left text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Product</th>
                    <th className="px-3 py-2.5 text-left text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Category</th>
                    <th className="px-3 py-2.5 text-right text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Stock</th>
                    <th className="px-3 py-2.5 text-right text-[10px] text-slate-400 font-semibold uppercase tracking-wider">DOS</th>
                    <th className="px-3 py-2.5 text-right text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Ann. Velocity</th>
                    <th className="px-3 py-2.5 text-right text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Inv. Cost</th>
                    <th className="px-3 py-2.5 text-left text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {candidate_products.slice(0, 10).map((p, i) => (
                    <tr
                      key={p.product_id}
                      className={`border-b border-[#1f1a54]/30 ${i % 2 === 0 ? 'bg-[#050315]/40' : ''} hover:bg-[#130f3b]/30 transition-colors`}
                    >
                      <td className="px-3 py-2">
                        <div className="text-slate-200 font-medium truncate max-w-[140px]">{p.product_name}</div>
                        <div className="text-[10px] text-[#a5a0ff] font-mono">#{p.product_id}</div>
                      </td>
                      <td className="px-3 py-2 text-slate-400">{p.category}</td>
                      <td className="px-3 py-2 text-right font-mono text-slate-300">{formatNumber(p.stock_units)}</td>
                      <td className="px-3 py-2 text-right font-mono text-orange-300">
                        {p.days_of_supply != null ? `${Number(p.days_of_supply).toFixed(1)}d` : '—'}
                      </td>
                      <td className="px-3 py-2 text-right font-mono text-slate-300">{formatNumber(Math.round(p.annual_units_sold))}</td>
                      <td className="px-3 py-2 text-right font-mono text-emerald-300">
                        {formatUSDFromCents(p.inventory_cost_value_cents)}
                      </td>
                      <td className="px-3 py-2 text-[10px] text-slate-400 max-w-[180px]">{p.classification_reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Placement-level candidates table */}
      {candidate_placements.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs font-semibold text-slate-300">Placement-Level Slow-Moving Candidates</div>
          <div className="rounded-xl border border-[#1f1a54]/60 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-[#1f1a54]/60 bg-[#07041c]/80">
                    <th className="px-3 py-2.5 text-left text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Product</th>
                    <th className="px-3 py-2.5 text-left text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Store</th>
                    <th className="px-3 py-2.5 text-right text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Stock</th>
                    <th className="px-3 py-2.5 text-right text-[10px] text-slate-400 font-semibold uppercase tracking-wider">DOS</th>
                    <th className="px-3 py-2.5 text-right text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Inv. Cost</th>
                    <th className="px-3 py-2.5 text-left text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Tier</th>
                  </tr>
                </thead>
                <tbody>
                  {candidate_placements.slice(0, 10).map((p, i) => (
                    <tr
                      key={`${p.product_id}-${p.store_id}`}
                      className={`border-b border-[#1f1a54]/30 ${i % 2 === 0 ? 'bg-[#050315]/40' : ''} hover:bg-[#130f3b]/30 transition-colors`}
                    >
                      <td className="px-3 py-2">
                        <div className="text-slate-200 font-medium truncate max-w-[130px]">{p.product_name}</div>
                        <div className="text-[10px] text-[#a5a0ff] font-mono">#{p.product_id}</div>
                      </td>
                      <td className="px-3 py-2 text-slate-400">#{p.store_id}</td>
                      <td className="px-3 py-2 text-right font-mono text-slate-300">{formatNumber(p.stock_units)}</td>
                      <td className="px-3 py-2 text-right font-mono text-violet-300">
                        {p.days_of_supply != null ? `${Number(p.days_of_supply).toFixed(1)}d` : '—'}
                      </td>
                      <td className="px-3 py-2 text-right font-mono text-emerald-300">
                        {formatUSDFromCents(p.inventory_cost_value_cents)}
                      </td>
                      <td className="px-3 py-2 text-[10px] text-violet-300">{p.coverage_tier}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Terminology note from API */}
      {terminology_note && (
        <div className="rounded-lg border border-[#1f1a54]/60 bg-[#07041c]/40 px-4 py-2.5 text-[11px] text-slate-400 flex items-start gap-1.5">
          <Info className="w-3.5 h-3.5 text-[#dedcff] shrink-0 mt-0.5" />
          <span>{terminology_note}</span>
        </div>
      )}

      {snapshot_date_is_assumed && (
        <div className="text-[10px] text-slate-500">
          Snapshot: {snapshot_date} (assumed) · {currency_code}
        </div>
      )}
    </div>
  );
}
