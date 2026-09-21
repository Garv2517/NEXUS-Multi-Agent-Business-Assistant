import React from 'react';
import { Package, Info } from 'lucide-react';
import { formatUSDFromCents, formatNumber } from '../../utils/formatters';

const TIER_STYLES = {
  'Stockout': {
    bg: 'bg-rose-950/60',
    border: 'border-rose-500/60',
    text: 'text-rose-300',
    dot: 'bg-rose-400',
  },
  'High Pressure': {
    bg: 'bg-orange-950/60',
    border: 'border-orange-500/50',
    text: 'text-orange-300',
    dot: 'bg-orange-400',
  },
  'Moderate Pressure': {
    bg: 'bg-amber-950/40',
    border: 'border-amber-500/40',
    text: 'text-amber-200',
    dot: 'bg-amber-400',
  },
  'Typical': {
    bg: 'bg-emerald-950/20',
    border: 'border-emerald-500/20',
    text: 'text-emerald-300',
    dot: 'bg-emerald-400',
  },
  'Elevated Coverage': {
    bg: 'bg-sky-950/20',
    border: 'border-sky-500/20',
    text: 'text-sky-300',
    dot: 'bg-sky-400',
  },
  'Slow-Moving Candidate': {
    bg: 'bg-violet-950/30',
    border: 'border-violet-500/30',
    text: 'text-violet-300',
    dot: 'bg-violet-400',
  },
};

function TierBadge({ tier }) {
  const style = TIER_STYLES[tier] || {
    bg: 'bg-slate-900/40',
    border: 'border-slate-500/30',
    text: 'text-slate-300',
    dot: 'bg-slate-400',
  };
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold border ${style.bg} ${style.border} ${style.text}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${style.dot}`} />
      {tier}
    </span>
  );
}

const P10 = 130.87, P25 = 171.76, P75 = 298.64, P90 = 392.04;

/**
 * InventoryPressureSection
 *
 * Displays DOS-tiered inventory pressure using D2A empirical percentile boundaries.
 * Includes methodology explanation for all 6 tiers.
 */
export function InventoryPressureSection({ data }) {
  if (!data) {
    return (
      <div className="rounded-xl border border-[#1f1a54]/60 bg-[#07041c]/60 p-6 text-center text-slate-400 text-sm">
        Inventory pressure data unavailable.
      </div>
    );
  }

  const {
    high_pressure_items = [],
    total_placements_evaluated = 0,
    snapshot_date,
    snapshot_date_is_assumed,
    currency_code = 'USD',
  } = data;

  // Count by tier
  const tierCounts = {};
  high_pressure_items.forEach((item) => {
    tierCounts[item.coverage_tier] = (tierCounts[item.coverage_tier] || 0) + 1;
  });

  const tierOrder = ['Stockout', 'High Pressure', 'Moderate Pressure', 'Typical', 'Elevated Coverage', 'Slow-Moving Candidate'];

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2 flex-wrap">
        <Package className="w-5 h-5 text-amber-400" />
        <h2 className="text-base font-semibold text-[#fbfbfe]">Inventory Pressure</h2>
        <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-[#07041c]/80 border border-[#1f1a54] text-slate-300">
          {formatNumber(total_placements_evaluated)} evaluated
        </span>
      </div>

      {/* Methodology reference */}
      <div className="rounded-xl border border-[#1f1a54]/60 bg-[#07041c]/80 p-4 space-y-3">
        <div className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
          <Info className="w-3.5 h-3.5 text-[#a5a0ff]" />
          Empirical D2A Percentile Boundaries — Days of Supply (Positive-Stock Placements)
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-[11px]">
          {[
            { label: 'P10 (High Pressure ↔ Moderate)', value: `${P10} days` },
            { label: 'P25 (Moderate ↔ Typical)', value: `${P25} days` },
            { label: 'P75 (Typical ↔ Elevated Coverage)', value: `${P75} days` },
            { label: 'P90 (Elevated ↔ Slow-Moving)', value: `${P90} days` },
          ].map((b) => (
            <div key={b.label} className="rounded-lg bg-[#130f3b]/60 border border-[#1f1a54]/60 px-3 py-2">
              <div className="text-slate-400 leading-tight mb-1">{b.label}</div>
              <div className="font-semibold text-[#fbfbfe]">{b.value}</div>
            </div>
          ))}
        </div>
        <div className="text-[10px] text-slate-500">
          DOS formula: stock_on_hand / (total_2025_units_sold / 365). Stockout = stock_on_hand == 0.
          Boundaries are mutually exclusive and empirically calibrated to this dataset.
        </div>
      </div>

      {/* Tier summary pills */}
      <div className="flex flex-wrap gap-2">
        {tierOrder.filter((t) => tierCounts[t]).map((tier) => (
          <div key={tier} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#07041c]/80 border border-[#1f1a54]/60 text-[11px]">
            <TierBadge tier={tier} />
            <span className="text-slate-300 font-semibold">{tierCounts[tier]}</span>
          </div>
        ))}
      </div>

      {/* Items table */}
      {high_pressure_items.length > 0 && (
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
                  <th className="px-3 py-2.5 text-left text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Explanation</th>
                </tr>
              </thead>
              <tbody>
                {high_pressure_items.slice(0, 20).map((item, i) => (
                  <tr
                    key={`${item.product_id}-${item.store_id}`}
                    className={`border-b border-[#1f1a54]/30 ${i % 2 === 0 ? 'bg-[#050315]/40' : ''} hover:bg-[#130f3b]/30 transition-colors`}
                  >
                    <td className="px-3 py-2">
                      <div className="text-slate-200 font-medium truncate max-w-[130px]">{item.product_name}</div>
                      <div className="text-[10px] text-[#a5a0ff] font-mono">#{item.product_id}</div>
                    </td>
                    <td className="px-3 py-2 text-slate-400">#{item.store_id}</td>
                    <td className="px-3 py-2 text-right font-mono text-slate-300">{formatNumber(item.stock_on_hand)}</td>
                    <td className="px-3 py-2 text-right font-mono text-slate-200">
                      {item.days_of_supply !== null && item.days_of_supply !== undefined
                        ? `${Number(item.days_of_supply).toFixed(1)}d`
                        : '—'}
                    </td>
                    <td className="px-3 py-2 text-right font-mono text-emerald-300">
                      {formatUSDFromCents(item.inventory_cost_cents)}
                    </td>
                    <td className="px-3 py-2">
                      <TierBadge tier={item.coverage_tier} />
                    </td>
                    <td className="px-3 py-2 text-[10px] text-slate-400 max-w-[220px]">
                      {item.explanation}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
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
