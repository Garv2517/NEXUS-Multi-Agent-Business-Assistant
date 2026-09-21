import React from 'react';
import { Database, Info, Calendar, DollarSign, ShieldAlert, FlaskConical } from 'lucide-react';

/**
 * D2B Risk Transparency Banner
 * Prominently displays dataset provenance, inventory assumption, and methodology notice.
 */
export function RiskTransparencyBanner() {
  return (
    <div className="rounded-xl bg-gradient-to-r from-[#0d0a30] via-[#120e3a] to-[#0d0a30] border border-[#2f27ce]/40 p-4 sm:p-5 shadow-card-glow relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute -top-12 -right-12 w-44 h-44 bg-[#433bff]/10 rounded-full blur-2xl pointer-events-none" />

      <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
        {/* Left: Description */}
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-rose-950/50 border border-rose-500/40 text-rose-300">
              <ShieldAlert className="w-3.5 h-3.5" />
              Risk Analytics
            </span>
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-purple-950/40 border border-purple-500/30 text-purple-300">
              <FlaskConical className="w-3 h-3" />
              Synthetic Kaggle Dataset
            </span>
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-950/40 border border-emerald-500/30 text-emerald-300">
              <DollarSign className="w-3 h-3" />
              Currency: USD
            </span>
          </div>

          <div className="text-sm font-semibold text-[#fbfbfe]">
            USA Toy Sales Dataset — Risk Domain
            <span className="text-xs font-normal text-slate-400 ml-2">(Source: Kaggle · CC0 Public Domain)</span>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed max-w-3xl">
            Risk metrics are computed deterministically from verified D2A calibration data.
            No AI-generated risk scores, no forecasting. All thresholds are empirically derived
            from this dataset's own distributions and must not be generalized to other businesses
            or interpreted as regulatory standards.
          </p>
        </div>

        {/* Right: Metadata badges */}
        <div className="flex flex-wrap sm:flex-nowrap items-center gap-3 shrink-0 text-xs">
          <div className="px-3 py-2 rounded-lg bg-[#07041c]/80 border border-[#1f1a54] text-slate-300 flex items-center gap-2.5">
            <Calendar className="w-4 h-4 text-[#dedcff]" />
            <div>
              <div className="text-[10px] text-slate-400 uppercase tracking-wider">Sales Period</div>
              <div className="font-medium text-[#fbfbfe]">Jan 2025 – Dec 2025</div>
            </div>
          </div>

          <div className="px-3 py-2 rounded-lg bg-[#07041c]/80 border border-amber-500/40 text-slate-300 flex items-center gap-2.5">
            <Info className="w-4 h-4 text-amber-300" />
            <div>
              <div className="text-[10px] text-slate-400 uppercase tracking-wider">Inventory Snapshot</div>
              <div className="font-medium text-amber-200">Assumed Dec 31, 2025</div>
            </div>
          </div>

          <div className="px-3 py-2 rounded-lg bg-[#07041c]/80 border border-[#1f1a54] text-slate-300 flex items-center gap-2.5">
            <Database className="w-4 h-4 text-[#a5a0ff]" />
            <div>
              <div className="text-[10px] text-slate-400 uppercase tracking-wider">Placements</div>
              <div className="font-medium text-[#fbfbfe]">14,143 total</div>
            </div>
          </div>
        </div>
      </div>

      {/* Mandatory inventory assumption notice */}
      <div className="mt-3 pt-2.5 border-t border-[#1f1a54]/60 text-[11px] text-amber-300/80 flex items-center gap-1.5">
        <Info className="w-3.5 h-3.5 shrink-0" />
        <span>
          <strong>Inventory Notice:</strong>{' '}
          Inventory snapshot date is assumed as Dec 31, 2025 for analytical use.
          The source dataset does not supply an explicit snapshot date.
        </span>
      </div>
    </div>
  );
}
