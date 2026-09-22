import React from 'react';
import { formatNumber } from '../../utils/formatters';

function reliabilityClass(label) {
  if (label === 'Strong') return 'text-emerald-300 border-emerald-500/30 bg-emerald-950/40';
  if (label === 'Moderate') return 'text-amber-300 border-amber-500/30 bg-amber-950/40';
  return 'text-rose-300 border-rose-500/30 bg-rose-950/40';
}

export function CategoryForecastTable({ data = [] }) {
  return (
    <div className="nexus-card p-5 overflow-hidden">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-[#fbfbfe]">Category Demand Forecasts</h3>
        <p className="text-[11px] text-slate-400 mt-1">Each category uses its independently validated 4-horizon model. WAPE is shown beside the project-defined reliability label.</p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs min-w-[850px]">
          <thead>
            <tr className="text-[10px] uppercase tracking-wider text-slate-500 border-b border-[#1f1a54]">
              <th className="text-left py-2 pr-4">Category</th>
              <th className="text-left py-2 px-3">Model</th>
              <th className="text-left py-2 px-3">Validation</th>
              <th className="text-right py-2 px-3">Wk +1</th>
              <th className="text-right py-2 px-3">Wk +2</th>
              <th className="text-right py-2 px-3">Wk +3</th>
              <th className="text-right py-2 px-3">Wk +4</th>
              <th className="text-right py-2 pl-3">4W Demand</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item) => (
              <tr key={item.category} className="border-b border-[#1f1a54]/55 last:border-0 hover:bg-[#0c0827]/70">
                <td className="py-3 pr-4 text-[#fbfbfe] font-medium">{item.category}</td>
                <td className="py-3 px-3 text-[#dedcff] font-mono text-[11px]">{item.model_used}</td>
                <td className="py-3 px-3">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded border text-[10px] ${reliabilityClass(item.validation_reliability)}`}>{item.validation_reliability}</span>
                    <span className="text-[10px] text-slate-500">{(item.validation_wape * 100).toFixed(2)}%</span>
                  </div>
                </td>
                {item.forecast_points.map((p) => <td key={p.horizon} className="py-3 px-3 text-right text-slate-300 tabular-nums">{formatNumber(p.value)}</td>)}
                <td className="py-3 pl-3 text-right text-white font-semibold tabular-nums">{formatNumber(item.forecast_4w_units)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
