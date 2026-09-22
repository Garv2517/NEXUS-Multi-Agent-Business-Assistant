import React from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';
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
        <span className="text-xs text-rose-300">Analytics unavailable.</span>
        <span className="text-[11px] text-slate-500">Could not retrieve stock distribution.</span>
      </div>
    );
  }

  const inStock = Number(data?.inStockPlacements ?? 0);
  const outOfStock = Number(data?.outOfStockPlacements ?? 0);
  const total = Number(data?.totalPlacements ?? (inStock + outOfStock));

  if (total === 0) {
    return <div className="h-64 flex items-center justify-center text-slate-500 text-xs">No inventory data available.</div>;
  }

  const chartData = [
    { name: 'In Stock', value: inStock, color: '#10b981' },
    { name: 'Out of Stock', value: outOfStock, color: '#f43f5e' }
  ].filter((d) => d.value > 0);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const p = payload[0];
      const pct = ((p.value / total) * 100).toFixed(2);
      return (
        <div className="p-2.5 rounded-lg bg-[#07041c]/95 border border-[#1f1a54] shadow-xl text-xs backdrop-blur-sm">
          <div className="flex items-center gap-1.5 font-medium text-[#fbfbfe]">
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: p.payload.color }} />
            {p.name}
          </div>
          <div className="text-[#dedcff] font-mono mt-1 text-[11px]">
            {Number(p.value).toLocaleString('en-US')} placements ({pct}%)
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
              {chartData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
            </Pie>
          </PieChart>
        </ResponsiveContainer>

        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-2xl font-bold font-mono text-[#fbfbfe] tracking-tight">
            {total.toLocaleString('en-US')}
          </span>
          <span className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">
            Store-SKU Placements
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 w-full pt-2 border-t border-[#1f1a54]/50 text-center">
        <div className="p-1.5 rounded bg-[#07041c]/60 border border-emerald-500/20">
          <div className="text-[11px] font-medium text-emerald-400">In Stock</div>
          <div className="text-xs font-mono text-[#fbfbfe] mt-0.5">
            {inStock.toLocaleString('en-US')} <span className="text-[10px] text-slate-400">({((inStock / total) * 100).toFixed(2)}%)</span>
          </div>
        </div>
        <div className="p-1.5 rounded bg-[#07041c]/60 border border-rose-500/20">
          <div className="text-[11px] font-medium text-rose-400">Out of Stock</div>
          <div className="text-xs font-mono text-[#fbfbfe] mt-0.5">
            {outOfStock.toLocaleString('en-US')} <span className="text-[10px] text-slate-400">({((outOfStock / total) * 100).toFixed(2)}%)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
