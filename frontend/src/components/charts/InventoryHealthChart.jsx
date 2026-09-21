import React from 'react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip
} from 'recharts';
import { AlertCircle, Loader2 } from 'lucide-react';

export function InventoryHealthChart({ data = null, loading = false, error = null }) {
  if (loading) {
    return (
      <div className="h-64 flex flex-col items-center justify-center text-slate-400 gap-2">
        <Loader2 className="w-5 h-5 animate-spin text-[#433bff]" />
        <span className="text-xs">Loading inventory telemetry...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-64 flex flex-col items-center justify-center text-slate-400 gap-2 p-4 text-center">
        <AlertCircle className="w-5 h-5 text-rose-400" />
        <span className="text-xs text-rose-300">Demo analytics unavailable.</span>
        <span className="text-[11px] text-slate-500">Could not retrieve stock distribution.</span>
      </div>
    );
  }

  // Normalize data (supports { healthy, lowStock, outOfStock, totalProducts } or snake_case)
  const healthyCount = Number(data?.healthyStock ?? data?.healthy ?? 0);
  const lowStockCount = Number(data?.lowStock ?? data?.low_stock ?? 0);
  const outOfStockCount = Number(data?.outOfStock ?? data?.out_of_stock ?? 0);
  const totalCount = Number(data?.totalProducts ?? data?.total ?? (healthyCount + lowStockCount + outOfStockCount));

  if (totalCount === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-500 text-xs">
        No inventory data available.
      </div>
    );
  }

  const chartData = [
    { name: 'Healthy', value: healthyCount, color: '#10b981' },
    { name: 'Low Stock', value: lowStockCount, color: '#f59e0b' },
    { name: 'Out of Stock', value: outOfStockCount, color: '#f43f5e' }
  ].filter((d) => d.value > 0);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const p = payload[0];
      const pct = Math.round((p.value / totalCount) * 100);
      return (
        <div className="p-2.5 rounded-lg bg-[#07041c]/95 border border-[#1f1a54] shadow-xl text-xs backdrop-blur-sm">
          <div className="flex items-center gap-1.5 font-medium text-[#fbfbfe]">
            <span
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: p.payload.color }}
            />
            {p.name}
          </div>
          <div className="text-[#dedcff] font-mono mt-1 text-[11px]">
            {p.value} items ({pct}%)
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full flex flex-col items-center">
      <div className="h-56 sm:h-60 w-full relative">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Tooltip content={<CustomTooltip />} />
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius="62%"
              outerRadius="86%"
              paddingAngle={4}
              dataKey="value"
              stroke="#050315"
              strokeWidth={2}
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>

        {/* Center count overlay */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-2xl font-bold font-mono text-[#fbfbfe] tracking-tight">
            {totalCount}
          </span>
          <span className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">
            Total SKUs
          </span>
        </div>
      </div>

      {/* Accessible Legend with actual counts and percentages */}
      <div className="grid grid-cols-3 gap-2 w-full pt-2 border-t border-[#1f1a54]/50 text-center">
        <div className="p-1.5 rounded bg-[#07041c]/60 border border-[#1f1a54]/60">
          <div className="flex items-center justify-center gap-1 text-[11px] font-medium text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            Healthy
          </div>
          <div className="text-xs font-mono text-[#fbfbfe] mt-0.5">
            {healthyCount} <span className="text-[10px] text-slate-400">({Math.round((healthyCount / totalCount) * 100)}%)</span>
          </div>
        </div>

        <div className="p-1.5 rounded bg-[#07041c]/60 border border-[#1f1a54]/60">
          <div className="flex items-center justify-center gap-1 text-[11px] font-medium text-amber-400">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
            Low Stock
          </div>
          <div className="text-xs font-mono text-[#fbfbfe] mt-0.5">
            {lowStockCount} <span className="text-[10px] text-slate-400">({Math.round((lowStockCount / totalCount) * 100)}%)</span>
          </div>
        </div>

        <div className="p-1.5 rounded bg-[#07041c]/60 border border-[#1f1a54]/60">
          <div className="flex items-center justify-center gap-1 text-[11px] font-medium text-rose-400">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
            Out of Stock
          </div>
          <div className="text-xs font-mono text-[#fbfbfe] mt-0.5">
            {outOfStockCount} <span className="text-[10px] text-slate-400">({Math.round((outOfStockCount / totalCount) * 100)}%)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
