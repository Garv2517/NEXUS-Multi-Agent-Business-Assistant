import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell
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

export function TopProductsChart({ data = [], loading = false, error = null }) {
  if (loading) {
    return (
      <div className="h-64 flex flex-col items-center justify-center text-slate-400 gap-2">
        <Loader2 className="w-5 h-5 animate-spin text-[#433bff]" />
        <span className="text-xs">Loading top-selling products...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-64 flex flex-col items-center justify-center text-slate-400 gap-2 p-4 text-center">
        <AlertCircle className="w-5 h-5 text-rose-400" />
        <span className="text-xs text-rose-300">Analytics unavailable.</span>
        <span className="text-[11px] text-slate-500">Could not retrieve product metrics.</span>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return <div className="h-64 flex items-center justify-center text-slate-500 text-xs">No product data available.</div>;
  }

  const chartData = data.slice(0, 5).map((item) => ({
    name: item.name || String(item.id || 'Product'),
    revenue: typeof item.revenueRaw === 'number' ? item.revenueRaw : Number(item.revenue || 0),
    unitsSold: item.unitsSold !== undefined ? item.unitsSold : item.units || 0,
    category: item.category || ''
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const p = payload[0].payload;
      return (
        <div className="p-2.5 rounded-lg bg-[#07041c]/95 border border-[#1f1a54] shadow-xl text-xs backdrop-blur-sm">
          <div className="text-[#fbfbfe] font-semibold">{p.name}</div>
          {p.category && <div className="text-[10px] text-slate-500 mt-0.5">{p.category}</div>}
          <div className="mt-1 space-y-0.5 font-mono text-[11px]">
            <div className="text-[#dedcff] flex items-center justify-between gap-3">
              <span className="text-slate-400">Revenue:</span>
              <span className="font-bold">{formatUSD(p.revenue)}</span>
            </div>
            <div className="text-slate-300 flex items-center justify-between gap-3">
              <span className="text-slate-400">Units Sold:</span>
              <span>{Number(p.unitsSold).toLocaleString('en-US')}</span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  const BAR_COLORS = ['#433bff', '#3b32cc', '#3129b8', '#28219c', '#201a7d'];

  return (
    <div className="w-full">
      <div className="h-64 sm:h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
            <XAxis
              type="number"
              stroke="#64748b"
              fontSize={10}
              tickLine={false}
              axisLine={{ stroke: '#1f1a54' }}
              tickFormatter={(v) => formatUSD(v, true)}
            />
            <YAxis
              type="category"
              dataKey="name"
              stroke="#94a3b8"
              fontSize={11}
              tickLine={false}
              axisLine={false}
              width={120}
              tick={{ fill: '#dedcff' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="revenue" radius={[0, 4, 4, 0]}>
              {chartData.map((_, index) => (
                <Cell key={`cell-${index}`} fill={BAR_COLORS[index % BAR_COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
