import React from 'react';
import { CalendarRange, Database, FlaskConical, ShieldCheck } from 'lucide-react';

export function ForecastTransparencyBanner({ config }) {
  return (
    <div className="nexus-card p-4 sm:p-5 bg-gradient-to-br from-[#0b0827] to-[#120c3d] border-[#2f2770]">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className="text-[10px] font-semibold tracking-wider uppercase px-2 py-1 rounded-md bg-[#433bff]/20 border border-[#433bff]/40 text-[#dedcff]">Forecasting & Demand Planning</span>
            <span className="text-[10px] font-semibold px-2 py-1 rounded-md bg-emerald-950/50 border border-emerald-500/30 text-emerald-300">4-week horizon</span>
            <span className="text-[10px] font-semibold px-2 py-1 rounded-md bg-amber-950/40 border border-amber-500/30 text-amber-300">Synthetic Kaggle data</span>
          </div>
          <h2 className="text-base font-semibold text-[#fbfbfe]">Validated weekly demand forecasts</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-3xl leading-relaxed">
            Models were selected with exhaustive chronological H1–H4 rolling-origin validation. No random split, no annual seasonality claim, and no AI model generates the forecast values.
          </p>
        </div>
        <div className="grid grid-cols-2 gap-2 min-w-[290px] text-[11px]">
          <div className="rounded-lg bg-[#080520] border border-[#1f1a54] px-3 py-2 flex items-center gap-2"><Database className="w-3.5 h-3.5 text-[#dedcff]"/><span className="text-slate-300">51 complete weeks</span></div>
          <div className="rounded-lg bg-[#080520] border border-[#1f1a54] px-3 py-2 flex items-center gap-2"><CalendarRange className="w-3.5 h-3.5 text-[#dedcff]"/><span className="text-slate-300">Through Dec 28, 2025</span></div>
          <div className="rounded-lg bg-[#080520] border border-[#1f1a54] px-3 py-2 flex items-center gap-2"><FlaskConical className="w-3.5 h-3.5 text-[#dedcff]"/><span className="text-slate-300">Stdlib deterministic models</span></div>
          <div className="rounded-lg bg-[#080520] border border-[#1f1a54] px-3 py-2 flex items-center gap-2"><ShieldCheck className="w-3.5 h-3.5 text-emerald-400"/><span className="text-slate-300">No data leakage</span></div>
        </div>
      </div>
      <div className="mt-3 pt-3 border-t border-[#1f1a54]/70 text-[10px] text-slate-500">
        {config?.partial_week_policy || 'Partial source observations from Dec 29–31 are excluded from model training and full-week forecast comparison.'}
      </div>
    </div>
  );
}
