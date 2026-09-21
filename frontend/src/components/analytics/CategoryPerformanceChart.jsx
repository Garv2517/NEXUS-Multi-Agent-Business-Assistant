import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell
} from 'recharts';
import { Layers } from 'lucide-react';
import { formatUSDFromCents, formatPercent } from '../../utils/formatters';

export function CategoryPerformanceChart({ categories = [] }) {
  if (!categories || categories.length === 0) {
    return (
      <div className="h-96 flex items-center justify-center text-slate-500 text-xs">
        No category records available.
      </div>
    );
  }

  // Categories are already ordered by revenue descending
  const chartData = categories.map((cat) => ({
    name: cat.category,
    revenueDollars: cat.revenue_cents / 100,
    revenueCents: cat.revenue_cents,
    profitCents: cat.profit_cents,
    cogsCents: cat.cogs_cents,
    unitsSold: cat.units_sold,
    productCount: cat.product_count,
    marginPct: cat.gross_margin_pct,
    sharePct: cat.revenue_share_pct
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload;
      return (
        <div className="p-3 rounded-xl bg-[#07041c]/95 border border-[#1f1a54] shadow-2xl text-xs backdrop-blur-md space-y-1.5 min-w-[220px]">
          <div className="font-semibold text-[#fbfbfe] border-b border-[#1f1a54] pb-1 flex justify-between items-center">
            <span>{d.name}</span>
            <span className="text-[10px] text-[#dedcff] bg-[#2f27ce]/30 px-1.5 py-0.5 rounded border border-[#433bff]/40">
              {formatPercent(d.sharePct)} Share
            </span>
          </div>

          <div className="space-y-1 pt-0.5">
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Gross Revenue:</span>
              <span className="text-[#dedcff] font-semibold font-mono">
                {formatUSDFromCents(d.revenueCents)}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-slate-400">Gross Profit:</span>
              <span className="text-emerald-300 font-semibold font-mono">
                {formatUSDFromCents(d.profitCents)}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-slate-400">Gross Margin:</span>
              <span className="text-slate-300 font-mono">
                {formatPercent(d.marginPct)}
              </span>
            </div>

            <div className="flex justify-between items-center text-[11px] text-slate-500 pt-1 border-t border-[#1f1a54]/50">
              <span>Units Sold:</span>
              <span className="font-mono text-slate-300">{d.unitsSold.toLocaleString('en-US')}</span>
            </div>

            <div className="flex justify-between items-center text-[11px] text-slate-500">
              <span>SKU Count:</span>
              <span className="font-mono text-slate-300">{d.productCount} products</span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="rounded-xl bg-[#0a0624] border border-[#1f1a54] p-5 shadow-card-glow flex flex-col justify-between">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <div>
          <div className="text-sm font-semibold text-[#fbfbfe] flex items-center gap-2">
            <Layers className="w-4 h-4 text-[#dedcff]" />
            Category Performance Breakdown
          </div>
          <div className="text-xs text-slate-400">
            Revenue volume and profitability across all 16 retail merchandise categories
          </div>
        </div>
        <div className="text-xs text-slate-400 font-medium">
          Total 16 Categories
        </div>
      </div>

      {/* Bar Chart with 16 horizontal bars */}
      <div className="h-[420px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 5, right: 20, left: 75, bottom: 5 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#1f1a54"
              opacity={0.5}
              horizontal={false}
            />

            <XAxis
              type="number"
              stroke="#64748b"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => `$${(v / 1_000_000).toFixed(1)}M`}
            />

            <YAxis
              type="category"
              dataKey="name"
              stroke="#94a3b8"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#1f1a54' }}
              width={75}
            />

            <Tooltip content={<CustomTooltip />} />

            <Bar
              dataKey="revenueDollars"
              radius={[0, 4, 4, 0]}
              fill="#2f27ce"
            >
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={index === 0 ? '#433bff' : index < 4 ? '#382fc9' : '#261f9c'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
