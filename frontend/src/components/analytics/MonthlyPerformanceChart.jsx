import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';
import { TrendingUp } from 'lucide-react';
import { formatUSDFromCents } from '../../utils/formatters';

export function MonthlyPerformanceChart({ data = [] }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-72 flex items-center justify-center text-slate-500 text-xs">
        No monthly performance records available.
      </div>
    );
  }

  // Normalize monthly points
  const chartData = data.map((item) => {
    // Format "2025-01" to "Jan"
    const monthIndex = parseInt(item.year_month.split('-')[1], 10) - 1;
    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const monthLabel = monthNames[monthIndex] || item.year_month;

    return {
      monthLabel,
      yearMonth: item.year_month,
      revenueDollars: item.revenue_cents / 100,
      profitDollars: item.profit_cents / 100,
      cogsDollars: item.cogs_cents / 100,
      revenueCents: item.revenue_cents,
      profitCents: item.profit_cents,
      cogsCents: item.cogs_cents,
      marginPct: item.gross_margin_pct,
      unitsSold: item.units_sold,
      transactionCount: item.transaction_count
    };
  });

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload;
      return (
        <div className="p-3 rounded-xl bg-[#07041c]/95 border border-[#1f1a54] shadow-2xl text-xs backdrop-blur-md space-y-1.5 min-w-[200px]">
          <div className="text-slate-400 font-semibold border-b border-[#1f1a54] pb-1 flex justify-between items-center">
            <span>{d.yearMonth} ({d.monthLabel} 2025)</span>
            <span className="text-[10px] text-emerald-400 font-normal">{d.marginPct}% Margin</span>
          </div>

          <div className="space-y-1 pt-0.5">
            <div className="flex justify-between items-center">
              <span className="text-slate-400 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-[#433bff]" />
                Gross Revenue:
              </span>
              <span className="text-[#dedcff] font-semibold font-mono">
                {formatUSDFromCents(d.revenueCents)}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-slate-400 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                Gross Profit:
              </span>
              <span className="text-emerald-300 font-semibold font-mono">
                {formatUSDFromCents(d.profitCents)}
              </span>
            </div>

            <div className="flex justify-between items-center text-[11px] text-slate-500 pt-1 border-t border-[#1f1a54]/50">
              <span>Units Sold:</span>
              <span className="font-mono text-slate-300">{d.unitsSold.toLocaleString('en-US')}</span>
            </div>

            <div className="flex justify-between items-center text-[11px] text-slate-500">
              <span>Transactions:</span>
              <span className="font-mono text-slate-300">{d.transactionCount.toLocaleString('en-US')}</span>
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
            <TrendingUp className="w-4 h-4 text-[#dedcff]" />
            Monthly Revenue & Gross Profit Trend
          </div>
          <div className="text-xs text-slate-400">
            Chronological 12-month commercial trajectory (Jan 2025 – Dec 2025)
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-[#433bff]" />
            <span className="text-slate-300">Revenue (USD)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-emerald-400" />
            <span className="text-slate-300">Gross Profit (USD)</span>
          </div>
        </div>
      </div>

      <div className="h-64 sm:h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={chartData}
            margin={{ top: 10, right: 15, left: -5, bottom: 0 }}
          >
            <defs>
              <linearGradient id="revGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#433bff" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#2f27ce" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="profitGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#059669" stopOpacity={0.0} />
              </linearGradient>
            </defs>

            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#1f1a54"
              opacity={0.5}
              vertical={false}
            />

            <XAxis
              dataKey="monthLabel"
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#1f1a54' }}
            />

            <YAxis
              stroke="#64748b"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => `$${(v / 1_000_000).toFixed(1)}M`}
            />

            <Tooltip content={<CustomTooltip />} />

            <Area
              type="monotone"
              dataKey="revenueDollars"
              stroke="#433bff"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#revGradient)"
              name="Revenue"
            />

            <Area
              type="monotone"
              dataKey="profitDollars"
              stroke="#10b981"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#profitGradient)"
              name="Gross Profit"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
