import React from 'react';
import { Boxes, CalendarClock } from 'lucide-react';
import { formatNumber } from '../../utils/formatters';

export function DemandCoverageSection({ data }) {
  const items = data?.categories || [];
  return (
    <div className="nexus-card p-5">
      <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-3 mb-4">
        <div>
          <h3 className="text-sm font-semibold text-[#fbfbfe] flex items-center gap-2"><Boxes className="w-4 h-4 text-[#dedcff]"/>Demand Coverage Planning</h3>
          <p className="text-[11px] text-slate-400 mt-1">Current category stock compared with validated next-4-week demand. Planning aid only; no replenishment orders are generated.</p>
        </div>
        <div className="text-[10px] text-amber-300 bg-amber-950/30 border border-amber-500/30 rounded-md px-2.5 py-1.5 flex items-center gap-1.5"><CalendarClock className="w-3 h-3"/>Inventory snapshot date assumed: Dec 31, 2025</div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs min-w-[760px]">
          <thead><tr className="text-[10px] uppercase tracking-wider text-slate-500 border-b border-[#1f1a54]"><th className="text-left py-2">Category</th><th className="text-right py-2">Current Stock</th><th className="text-right py-2">4W Forecast</th><th className="text-right py-2">Coverage Ratio</th><th className="text-right py-2">Forecast Coverage</th><th className="text-right py-2">Reliability</th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.category} className="border-b border-[#1f1a54]/55 last:border-0 hover:bg-[#0c0827]/70">
                <td className="py-3 text-[#fbfbfe] font-medium">{item.category}</td>
                <td className="py-3 text-right text-slate-300 tabular-nums">{formatNumber(item.current_stock_units)}</td>
                <td className="py-3 text-right text-slate-300 tabular-nums">{formatNumber(item.forecast_4w_units)}</td>
                <td className="py-3 text-right text-[#dedcff] tabular-nums">{item.coverage_ratio.toFixed(2)}×</td>
                <td className="py-3 text-right text-white font-semibold tabular-nums">{item.forecast_coverage_weeks.toFixed(1)} weeks</td>
                <td className="py-3 text-right text-slate-400">{item.forecast_validation_reliability} · {(item.forecast_validation_wape * 100).toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-3 text-[10px] text-slate-500">Coverage ratio is dimensionless: 1.0× means current stock equals one full 4-week forecast quantity. Forecast coverage weeks converts that same relationship into estimated weeks of stock at forecast average weekly demand.</div>
    </div>
  );
}
