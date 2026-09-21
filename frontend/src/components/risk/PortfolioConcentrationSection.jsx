import React from 'react';
import { BarChart2, Info } from 'lucide-react';
import { formatPercent } from '../../utils/formatters';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

/**
 * PortfolioConcentrationSection
 *
 * Displays quantitative HHI / share concentration metrics — no DOJ/FTC tiers.
 * Rule: 1.0 HHI-to-equal ratio = equal-distribution baseline.
 * Uses ConcentrationResponse shape: products / categories / stores as ConcentrationMetric.
 */
export function PortfolioConcentrationSection({ data }) {
  if (!data) {
    return (
      <div className="rounded-xl border border-[#1f1a54]/60 bg-[#07041c]/60 p-6 text-center text-slate-400 text-sm">
        Concentration data unavailable.
      </div>
    );
  }

  const { products, categories, stores, currency_code = 'USD', methodology_note } = data;

  const domains = [
    { key: 'products', label: 'Products', data: products },
    { key: 'categories', label: 'Categories', data: categories },
    { key: 'stores', label: 'Stores', data: stores },
  ].filter((d) => d.data != null);

  // Bar chart data for top-1 / top-5 share comparison
  const shareChartData = domains.map(({ label, data: d }) => ({
    name: label,
    'Top-1 Share': d?.top_1_share_pct ?? 0,
    'Top-5 Share': d?.top_5_share_pct ?? 0,
    'Top-10 Share': d?.top_10_share_pct ?? null,
  }));

  // HHI ratio chart
  const hhiChartData = domains.map(({ label, data: d }) => ({
    name: label,
    'HHI': d?.hhi ?? 0,
    'Equal-Share HHI': d?.equal_share_hhi ?? 0,
  }));

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center gap-2 flex-wrap">
        <BarChart2 className="w-5 h-5 text-violet-400" />
        <h2 className="text-base font-semibold text-[#fbfbfe]">Portfolio Revenue Concentration</h2>
        <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-violet-950/40 border border-violet-500/40 text-violet-300">
          HHI-based · Quantitative metrics only
        </span>
      </div>

      {/* HHI methodology note */}
      <div className="rounded-xl border border-[#1f1a54]/60 bg-[#07041c]/80 p-4 space-y-2">
        <div className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
          <Info className="w-3.5 h-3.5 text-[#a5a0ff]" />
          Herfindahl-Hirschman Index (HHI) Methodology
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          HHI = Σ(revenue_share_pct²) across all entities. Equal-Share HHI = 10000 / N
          (baseline for perfectly uniform distribution). HHI-to-Equal ratio = HHI / equal-share-HHI.
          A ratio of{' '}
          <strong className="text-slate-200">1.0 represents the equal-distribution baseline</strong>.
          Values above 1.0 indicate increasing concentration; below 1.0 indicates below-baseline concentration.
          No Low / Moderate / High labels are applied — raw quantitative values are presented.
        </p>
      </div>

      {/* Per-domain metric cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {domains.map(({ key, label, data: d }) => (
          <div key={key} className="rounded-xl border border-violet-500/20 bg-violet-950/10 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-[#fbfbfe]">{label}</span>
              <span className="text-[10px] text-slate-400">N = {d.entity_count.toLocaleString()}</span>
            </div>

            <div className="grid grid-cols-2 gap-2.5 text-[11px]">
              <div>
                <div className="text-slate-400 text-[10px]">Top-1 Share</div>
                <div className="font-bold text-[#fbfbfe]">{formatPercent(d.top_1_share_pct)}</div>
                <div className="text-[10px] text-slate-500 truncate" title={d.top_1_entity_name}>
                  {d.top_1_entity_name}
                </div>
              </div>
              <div>
                <div className="text-slate-400 text-[10px]">Top-5 Share</div>
                <div className="font-bold text-[#fbfbfe]">{formatPercent(d.top_5_share_pct)}</div>
              </div>
              <div>
                <div className="text-slate-400 text-[10px]">HHI</div>
                <div className="font-bold text-violet-200">{d.hhi != null ? Number(d.hhi).toFixed(2) : '—'}</div>
              </div>
              <div>
                <div className="text-slate-400 text-[10px]">Equal-Share HHI</div>
                <div className="font-bold text-[#fbfbfe]">{d.equal_share_hhi != null ? Number(d.equal_share_hhi).toFixed(2) : '—'}</div>
              </div>
              <div className="col-span-2">
                <div className="text-slate-400 text-[10px]">HHI-to-Equal Ratio</div>
                <div className="font-bold text-sky-200 text-lg">
                  {d.hhi_to_equal_ratio != null ? Number(d.hhi_to_equal_ratio).toFixed(3) : '—'}
                </div>
                <div className="text-[10px] text-slate-500">
                  {d.hhi_to_equal_ratio != null
                    ? Number(d.hhi_to_equal_ratio) > 1.01
                      ? 'Above equal-distribution baseline'
                      : Number(d.hhi_to_equal_ratio) < 0.99
                        ? 'Below equal-distribution baseline'
                        : 'At equal-distribution baseline'
                    : ''}
                </div>
              </div>
              {d.normalized_hhi != null && (
                <div className="col-span-2">
                  <div className="text-slate-400 text-[10px]">Normalized HHI</div>
                  <div className="font-semibold text-[#fbfbfe]">{Number(d.normalized_hhi).toFixed(4)}</div>
                  <div className="text-[10px] text-slate-500">(range 0–1)</div>
                </div>
              )}
            </div>

            {/* Explanation from API */}
            {d.explanation && (
              <div className="pt-2 border-t border-[#1f1a54]/40 text-[10px] text-slate-500 leading-relaxed">
                {d.explanation}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Top-1 / Top-5 share bar chart */}
      <div className="rounded-xl border border-[#1f1a54]/60 bg-[#07041c]/80 p-4">
        <div className="text-xs font-semibold text-slate-300 mb-3">Revenue Share: Top-1 vs Top-5</div>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={shareChartData} margin={{ left: 0, right: 8, top: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f1a54" vertical={false} />
            <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 10 }} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} tickFormatter={(v) => `${v}%`} />
            <Tooltip
              contentStyle={{ background: '#07041c', border: '1px solid #1f1a54', borderRadius: 8 }}
              labelStyle={{ color: '#fbfbfe' }}
              itemStyle={{ color: '#dedcff' }}
              formatter={(v) => `${Number(v).toFixed(2)}%`}
            />
            <Bar dataKey="Top-1 Share" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Top-5 Share" fill="#a5f3fc" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* HHI vs Equal-Share chart */}
      <div className="rounded-xl border border-[#1f1a54]/60 bg-[#07041c]/80 p-4">
        <div className="text-xs font-semibold text-slate-300 mb-3">HHI vs Equal-Share HHI</div>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={hhiChartData} margin={{ left: 0, right: 8, top: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f1a54" vertical={false} />
            <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 10 }} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} />
            <Tooltip
              contentStyle={{ background: '#07041c', border: '1px solid #1f1a54', borderRadius: 8 }}
              labelStyle={{ color: '#fbfbfe' }}
              itemStyle={{ color: '#dedcff' }}
              formatter={(v) => Number(v).toFixed(2)}
            />
            <Bar dataKey="HHI" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Equal-Share HHI" fill="#475569" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Methodology note */}
      {methodology_note && (
        <div className="rounded-lg border border-[#1f1a54]/60 bg-[#07041c]/40 px-4 py-2.5 text-[11px] text-slate-400 flex items-start gap-1.5">
          <Info className="w-3.5 h-3.5 text-[#dedcff] shrink-0 mt-0.5" />
          <span>{methodology_note}</span>
        </div>
      )}
    </div>
  );
}
