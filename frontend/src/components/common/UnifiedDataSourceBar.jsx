import React from 'react';
import { Database, BadgeDollarSign, CalendarDays, FlaskConical } from 'lucide-react';

export function UnifiedDataSourceBar({ metadata, inventory = false }) {
  if (!metadata) return null;

  return (
    <div className="rounded-xl border border-[#433bff]/30 bg-[#0b0728]/80 px-4 py-3 flex flex-col lg:flex-row lg:items-center justify-between gap-3 shadow-card-glow">
      <div className="flex items-start sm:items-center gap-3 min-w-0">
        <div className="w-9 h-9 rounded-lg bg-[#2f27ce]/20 border border-[#433bff]/30 flex items-center justify-center shrink-0">
          <Database className="w-4 h-4 text-[#dedcff]" />
        </div>
        <div className="min-w-0">
          <div className="text-xs font-semibold text-[#fbfbfe] flex flex-wrap items-center gap-2">
            <span>Unified Retail Data</span>
            <span className="px-2 py-0.5 rounded-full text-[9px] font-semibold bg-emerald-950/50 border border-emerald-500/30 text-emerald-300">
              KAGGLE ANALYTICS
            </span>
          </div>
          <p className="text-[11px] text-slate-400 mt-0.5 truncate">
            {metadata.dataset_name} · {metadata.dataset_nature}
          </p>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2 text-[10px] font-mono text-slate-300">
        <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-md bg-[#050315] border border-[#1f1a54]">
          <BadgeDollarSign className="w-3 h-3 text-emerald-400" />
          {metadata.currency_code}
        </span>
        <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-md bg-[#050315] border border-[#1f1a54]">
          <CalendarDays className="w-3 h-3 text-sky-300" />
          {metadata.sales_start_date} → {metadata.sales_end_date}
        </span>
        <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-md bg-[#050315] border border-[#1f1a54]">
          <FlaskConical className="w-3 h-3 text-purple-300" />
          Synthetic
        </span>
        {inventory && metadata.inventory_snapshot_date && (
          <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-md bg-amber-950/20 border border-amber-500/30 text-amber-200">
            Inventory snapshot {metadata.inventory_snapshot_date_is_assumed ? 'assumed ' : ''}{metadata.inventory_snapshot_date}
          </span>
        )}
      </div>
    </div>
  );
}
