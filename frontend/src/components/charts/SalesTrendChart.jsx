import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';
import { AlertCircle, Loader2 } from 'lucide-react';

const formatUSD = (value, compact = false) => {
  const n = Number(value) || 0;
  if (compact) {
    if (Math.abs(n) >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
    if (Math.abs(n) >= 1_000) return `$${(n / 1_000).toFixed(0)}K`;
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0
  }).format(n);
};

export function SalesTrendChart({
  data = [],
  loading = false,
  error = null,
  compact = false
}) {
  const containerHeight = compact ? 'h-44 sm:h-48' : 'h-64 sm:h-72';

  if (loading) {
    return (
      <div className={`${containerHeight} flex flex-col items-center justify-center text-slate-400 gap-2`}>
        <Loader2 className="w-5 h-5 animate-spin text-[#433bff]" />
        <span className="text-xs">Loading monthly sales telemetry...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`${containerHeight} flex flex-col items-center justify-center text-slate-400 gap-2 p-4 text-center`}>
        <AlertCircle className="w-5 h-5 text-rose-400" />
        <span className="text-xs text-rose-300">Analytics unavailable.</span>
        <span className="text-[11px] text-slate-500">Could not retrieve sales records.</span>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-500 text-xs">
        No sales trend records available.
      </div>
    );
  }

  const chartData = data.map((item) => ({
    period: item.month || item.period || 'N/A',
    revenue: typeof item.revenue === 'number' ? item.revenue : Number(item.revenue) || 0,
    units: Number(item.units || 0),
    transactions: Number(item.transactions || 0)
  }));

  const maxRevenue = Math.max(...chartData.map((d) => d.revenue), 1);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const p = payload[0].payload;
      return (
        <div className="p-2.5 rounded-lg bg-[#07041c]/95 border border-[#1f1a54] shadow-xl text-xs backdrop-blur-sm">
          <div className="text-slate-400 text-[11px] font-medium">{label}</div>
          <div className="text-[#dedcff] font-semibold font-mono mt-0.5 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#433bff]" />
            {formatUSD(p.revenue)}
          </div>
          {p.units > 0 && (
            <div className="text-[10px] text-slate-400 mt-1">{p.units.toLocaleString('en-US')} units sold</div>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full">
      <div className={`${containerHeight} w-full`}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={chartData}
            margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
          >
            <defs>
              <linearGradient id="salesTrendGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#433bff" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#2f27ce" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f1a54" opacity={0.4} vertical={false} />
            <XAxis
              dataKey="period"
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
              tickFormatter={(v) => formatUSD(v, true)}
              domain={[0, Math.ceil(maxRevenue * 1.15)]}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="revenue"
              stroke="#433bff"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#salesTrendGradient)"
            />
            <Line
              type="monotone"
              dataKey="revenue"
              stroke="#dedcff"
              strokeWidth={1}
              dot={{ r: 3, fill: '#050315', stroke: '#dedcff', strokeWidth: 2 }}
              activeDot={{ r: 5, fill: '#433bff', stroke: '#dedcff', strokeWidth: 2 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
