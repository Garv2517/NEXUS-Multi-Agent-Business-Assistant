import React from 'react';
import { TrendingUp, TrendingDown, ArrowUpRight } from 'lucide-react';

export function StatCard({ title, value, change, isPositive, isWarning, isNeutral, timeframe, icon: Icon }) {
  return (
    <div className="nexus-card p-5 relative overflow-hidden group">
      {/* Subtle violet top accent line on hover */}
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-transparent group-hover:bg-gradient-to-r group-hover:from-transparent group-hover:via-[#433bff] group-hover:to-transparent transition-all duration-300" />

      <div className="flex items-start justify-between">
        <div>
          <span className="text-xs font-medium text-slate-400 tracking-wider uppercase">
            {title}
          </span>
          <div className="text-2xl font-bold text-[#fbfbfe] mt-1 tracking-tight">
            {value}
          </div>
        </div>

        {Icon && (
          <div className="w-10 h-10 rounded-lg bg-[#2f27ce]/20 border border-[#1f1a54] flex items-center justify-center text-[#dedcff] group-hover:border-[#433bff]/50 transition-colors shrink-0">
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      <div className="mt-4 flex items-center gap-2 text-xs">
        {change && (
          <span
            className={`inline-flex items-center gap-1 font-semibold px-2 py-0.5 rounded-full border ${
              isWarning
                ? 'bg-amber-950/40 border-amber-500/30 text-amber-300'
                : isPositive
                ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300'
                : isNeutral
                ? 'bg-[#2f27ce]/20 border-[#1f1a54] text-[#dedcff]'
                : 'bg-rose-950/40 border-rose-500/30 text-rose-300'
            }`}
          >
            {isPositive && <TrendingUp className="w-3 h-3 shrink-0" />}
            {!isPositive && !isWarning && !isNeutral && <TrendingDown className="w-3 h-3 shrink-0" />}
            {change}
          </span>
        )}

        {timeframe && (
          <span className="text-slate-500 text-[11px] truncate">
            {timeframe}
          </span>
        )}
      </div>
    </div>
  );
}
