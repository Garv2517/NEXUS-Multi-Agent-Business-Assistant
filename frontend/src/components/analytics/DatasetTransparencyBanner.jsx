import React from 'react';
import { Database, Info, Calendar, DollarSign, Sparkles } from 'lucide-react';

export function DatasetTransparencyBanner({ metadata }) {
  return (
    <div className="rounded-xl bg-gradient-to-r from-[#0d0a30] via-[#120e3a] to-[#0d0a30] border border-[#2f27ce]/40 p-4 sm:p-5 shadow-card-glow relative overflow-hidden">
      {/* Glow highlight */}
      <div className="absolute -top-12 -right-12 w-44 h-44 bg-[#433bff]/10 rounded-full blur-2xl pointer-events-none" />

      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Left info */}
        <div className="space-y-1.5">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[#2f27ce]/30 border border-[#433bff]/50 text-[#dedcff]">
              <Database className="w-3.5 h-3.5 text-[#a5a0ff]" />
              External Analytics
            </span>
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-purple-950/40 border border-purple-500/30 text-purple-300">
              <Sparkles className="w-3 h-3 text-purple-400" />
              Synthetic Kaggle Dataset
            </span>
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-950/40 border border-emerald-500/30 text-emerald-300">
              <DollarSign className="w-3 h-3 text-emerald-400" />
              Currency: USD
            </span>
          </div>

          <div className="text-sm font-semibold text-[#fbfbfe] flex items-center gap-2">
            <span>USA Toy Sales Dataset</span>
            <span className="text-xs font-normal text-slate-400">
              (Source: Kaggle • CC0 Public Domain)
            </span>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed max-w-3xl">
            This module provides descriptive retail performance analytics from the external 2025 Kaggle dataset.
            Figures represent synthetic US retail sales and point-in-time inventory, distinct from the operational seed business.
          </p>
        </div>

        {/* Right metadata badge grid */}
        <div className="flex flex-wrap sm:flex-nowrap items-center gap-3 shrink-0 text-xs">
          <div className="px-3 py-2 rounded-lg bg-[#07041c]/80 border border-[#1f1a54] text-slate-300 flex items-center gap-2.5">
            <Calendar className="w-4 h-4 text-[#dedcff]" />
            <div>
              <div className="text-[10px] text-slate-400 uppercase tracking-wider">Sales Period</div>
              <div className="font-medium text-[#fbfbfe]">Jan 2025 – Dec 2025</div>
            </div>
          </div>

          <div className="px-3 py-2 rounded-lg bg-[#07041c]/80 border border-[#1f1a54] text-slate-300 flex items-center gap-2.5">
            <Info className="w-4 h-4 text-amber-300" />
            <div>
              <div className="text-[10px] text-slate-400 uppercase tracking-wider">Inventory Assumption</div>
              <div className="font-medium text-amber-200">Assumed as Dec 31, 2025</div>
            </div>
          </div>
        </div>
      </div>

      {/* Mandatory explicit inventory notice per Guardrail 7 */}
      <div className="mt-3 pt-2.5 border-t border-[#1f1a54]/60 text-[11px] text-slate-400 flex items-center gap-1.5">
        <Info className="w-3.5 h-3.5 text-[#dedcff] shrink-0" />
        <span>
          <strong>Analytical Notice:</strong> Inventory snapshot date is assumed as Dec 31, 2025 for analytical use.
        </span>
      </div>
    </div>
  );
}
