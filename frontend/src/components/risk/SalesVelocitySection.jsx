import React from 'react';
import { TrendingDown, TrendingUp, Minus, Info } from 'lucide-react';
import { formatNumber } from '../../utils/formatters';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts';

const CLASSIFICATION_STYLES = {
  'Severe Contraction': {
    bg: 'bg-rose-950/40',
    border: 'border-rose-500/40',
    text: 'text-rose-300',
    barColor: '#f87171',
  },
  'Moderate Contraction': {
    bg: 'bg-orange-950/30',
    border: 'border-orange-500/30',
    text: 'text-orange-300',
    barColor: '#fb923c',
  },
  'Stable': {
    bg: 'bg-slate-900/40',
    border: 'border-slate-500/30',
    text: 'text-slate-300',
    barColor: '#94a3b8',
  },
  'Growth': {
    bg: 'bg-emerald-950/30',
    border: 'border-emerald-500/30',
    text: 'text-emerald-300',
    barColor: '#34d399',
  },
};

function ClassificationBadge({ classification }) {
  const style = CLASSIFICATION_STYLES[classification] || {
    bg: 'bg-slate-900/40', border: 'border-slate-500/30', text: 'text-slate-300'
  };
  const Icon = classification?.includes('Contraction')
    ? TrendingDown
    : classification === 'Growth'
      ? TrendingUp
      : Minus;
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold border ${style.bg} ${style.border} ${style.text}`}>
      <Icon className="w-3 h-3" />
      {classification}
    </span>
  );
}

function ProductVelocityTable({ title, items }) {
  if (!items || items.length === 0) return null;
  return (
    <div className="space-y-2">
      <div className="text-xs font-semibold text-slate-300">{title}</div>
      <div className="rounded-xl border border-[#1f1a54]/60 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-[#1f1a54]/60 bg-[#07041c]/80">
                <th className="px-3 py-2.5 text-left text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Product</th>
                <th className="px-3 py-2.5 text-left text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Category</th>
                <th className="px-3 py-2.5 text-right text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Prior</th>
                <th className="px-3 py-2.5 text-right text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Recent</th>
                <th className="px-3 py-2.5 text-right text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Change</th>
                <th className="px-3 py-2.5 text-left text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Class.</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item, i) => {
                const pct = item.change_pct;
                const pctText = pct != null ? `${pct >= 0 ? '+' : ''}${Number(pct).toFixed(2)}%` : '—';
                const pctColor = pct == null ? 'text-slate-400' : pct >= 0 ? 'text-emerald-300' : 'text-rose-300';
                return (
                  <tr key={item.product_id} className={`border-b border-[#1f1a54]/30 ${i % 2 === 0 ? 'bg-[#050315]/40' : ''} hover:bg-[#130f3b]/30 transition-colors`}>
                    <td className="px-3 py-2">
                      <div className="text-slate-200 font-medium truncate max-w-[140px]">{item.product_name}</div>
                      <div className="text-[10px] text-[#a5a0ff] font-mono">#{item.product_id}</div>
                    </td>
                    <td className="px-3 py-2 text-slate-400">{item.category}</td>
                    <td className="px-3 py-2 text-right font-mono text-slate-300">{formatNumber(item.prior_28d_units)}</td>
                    <td className="px-3 py-2 text-right font-mono text-slate-300">{formatNumber(item.recent_28d_units)}</td>
                    <td className={`px-3 py-2 text-right font-mono font-semibold ${pctColor}`}>{pctText}</td>
                    <td className="px-3 py-2">
                      <ClassificationBadge classification={item.classification} />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

/**
 * SalesVelocitySection
 *
 * Shows 28-day consecutive window comparison: prior vs recent.
 * PRIOR: 2025-11-06 to 2025-12-03 · RECENT: 2025-12-04 to 2025-12-31
 * Uses actual API shape: company_momentum, categories_momentum,
 * top_contracting_products, top_growing_products.
 */
export function SalesVelocitySection({ data }) {
  if (!data) {
    return (
      <div className="rounded-xl border border-[#1f1a54]/60 bg-[#07041c]/60 p-6 text-center text-slate-400 text-sm">
        Sales velocity data unavailable.
      </div>
    );
  }

  const {
    company_momentum,
    categories_momentum = [],
    top_contracting_products = [],
    top_growing_products = [],
    recent_window,
    prior_window,
    window_days = 28,
    methodology_note,
  } = data;

  // Build category chart data
  const catChartData = categories_momentum.map((c) => ({
    name: c.category.length > 12 ? c.category.slice(0, 12) + '…' : c.category,
    fullName: c.category,
    change: c.change_pct != null ? Number(c.change_pct.toFixed(2)) : 0,
    classification: c.classification,
  }));

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center gap-2 flex-wrap">
        <TrendingDown className="w-5 h-5 text-sky-400" />
        <h2 className="text-base font-semibold text-[#fbfbfe]">Sales Velocity Changes</h2>
      </div>

      {/* Window reference */}
      <div className="rounded-xl border border-[#1f1a54]/60 bg-[#07041c]/80 p-4 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
        <div className="rounded-lg bg-[#130f3b]/60 border border-[#1f1a54]/60 px-3 py-2.5">
          <div className="text-slate-400 text-[10px] uppercase tracking-wider mb-1">Prior Window</div>
          <div className="font-semibold text-[#fbfbfe]">{prior_window}</div>
          <div className="text-slate-400 text-[10px] mt-0.5">{window_days} days</div>
        </div>
        <div className="rounded-lg bg-[#130f3b]/60 border border-[#1f1a54]/60 px-3 py-2.5">
          <div className="text-slate-400 text-[10px] uppercase tracking-wider mb-1">Recent Window</div>
          <div className="font-semibold text-[#fbfbfe]">{recent_window}</div>
          <div className="text-slate-400 text-[10px] mt-0.5">{window_days} days</div>
        </div>
        <div className="sm:col-span-2 text-[10px] text-slate-500">
          D2A boundaries — Severe Contraction: ≤−22.03% · Moderate Contraction: −22.03% to −9.35% ·
          Stable: −9.35% to +11.60% · Growth: ≥+11.60% · Min prior units: 100
        </div>
      </div>

      {/* Company summary */}
      {company_momentum && (
        <div className="rounded-xl border border-[#1f1a54]/60 bg-[#07041c]/80 p-4 flex flex-col sm:flex-row sm:items-center gap-4">
          <div className="flex-1">
            <div className="text-xs text-slate-400 mb-1">Company-Level Unit Velocity Movement</div>
            <div className={`text-2xl font-bold ${(company_momentum.change_pct || 0) >= 0 ? 'text-emerald-300' : 'text-rose-300'}`}>
              {company_momentum.change_pct != null
                ? `${company_momentum.change_pct > 0 ? '+' : ''}${Number(company_momentum.change_pct).toFixed(4)}%`
                : '—'}
            </div>
            <div className="mt-1">
              <ClassificationBadge classification={company_momentum.classification} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="rounded-lg bg-[#130f3b]/60 border border-[#1f1a54]/60 px-3 py-2">
              <div className="text-slate-400 text-[10px]">Prior 28d Units</div>
              <div className="font-semibold text-[#fbfbfe]">{formatNumber(company_momentum.prior_28d_units)}</div>
            </div>
            <div className="rounded-lg bg-[#130f3b]/60 border border-[#1f1a54]/60 px-3 py-2">
              <div className="text-slate-400 text-[10px]">Recent 28d Units</div>
              <div className="font-semibold text-[#fbfbfe]">{formatNumber(company_momentum.recent_28d_units)}</div>
            </div>
          </div>
        </div>
      )}

      {/* Category chart */}
      {catChartData.length > 0 && (
        <div className="rounded-xl border border-[#1f1a54]/60 bg-[#07041c]/80 p-4">
          <div className="text-xs font-semibold text-slate-300 mb-3">Category Unit Velocity Change %</div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={catChartData} layout="vertical" margin={{ left: 10, right: 24, top: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f1a54" horizontal={false} />
              <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 9 }} tickFormatter={(v) => `${v}%`} />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fill: '#94a3b8', fontSize: 9 }}
                width={100}
              />
              <Tooltip
                contentStyle={{ background: '#07041c', border: '1px solid #1f1a54', borderRadius: 8 }}
                labelStyle={{ color: '#fbfbfe' }}
                itemStyle={{ color: '#dedcff' }}
                formatter={(v, name, props) => [`${Number(v).toFixed(2)}%`, props.payload.fullName]}
              />
              <Bar dataKey="change" name="Change %" radius={[0, 4, 4, 0]}>
                {catChartData.map((entry) => (
                  <Cell
                    key={entry.fullName}
                    fill={(CLASSIFICATION_STYLES[entry.classification] || { barColor: '#64748b' }).barColor}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Contracting products */}
      <ProductVelocityTable title="Top Contracting Products" items={top_contracting_products} />

      {/* Growing products */}
      <ProductVelocityTable title="Top Growing Products" items={top_growing_products} />

      {/* Methodology note from API */}
      {methodology_note && (
        <div className="rounded-lg border border-[#1f1a54]/60 bg-[#07041c]/40 px-4 py-2.5 text-[11px] text-slate-400 flex items-start gap-1.5">
          <Info className="w-3.5 h-3.5 text-[#dedcff] shrink-0 mt-0.5" />
          <span>{methodology_note}</span>
        </div>
      )}
    </div>
  );
}
