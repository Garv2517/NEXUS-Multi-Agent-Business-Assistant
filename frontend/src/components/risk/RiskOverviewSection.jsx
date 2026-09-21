import React from 'react';
import {
  AlertTriangle,
  Package,
  Store,
  Layers,
  TrendingDown,
  BarChart2,
  CheckCircle2,
  Info,
} from 'lucide-react';

const DOMAIN_ICONS = {
  stockout: AlertTriangle,
  inventory_pressure: Package,
  slow_moving: Layers,
  sales_velocity: TrendingDown,
  concentration: BarChart2,
};

const DOMAIN_COLORS = {
  stockout: {
    border: 'border-rose-500/40',
    bg: 'bg-rose-950/20',
    icon: 'text-rose-400',
    text: 'text-rose-200',
  },
  inventory_pressure: {
    border: 'border-amber-500/40',
    bg: 'bg-amber-950/20',
    icon: 'text-amber-400',
    text: 'text-amber-200',
  },
  slow_moving: {
    border: 'border-orange-500/40',
    bg: 'bg-orange-950/20',
    icon: 'text-orange-400',
    text: 'text-orange-200',
  },
  sales_velocity: {
    border: 'border-sky-500/40',
    bg: 'bg-sky-950/20',
    icon: 'text-sky-400',
    text: 'text-sky-200',
  },
  concentration: {
    border: 'border-violet-500/40',
    bg: 'bg-violet-950/20',
    icon: 'text-violet-400',
    text: 'text-violet-200',
  },
};

const DEFAULT_COLOR = {
  border: 'border-[#1f1a54]/60',
  bg: 'bg-[#07041c]/40',
  icon: 'text-slate-400',
  text: 'text-slate-300',
};

function DomainCard({ domainEntry }) {
  const { domain, status, headline_metric, detail, explainability } = domainEntry;
  const cfg = DOMAIN_COLORS[domain] || DEFAULT_COLOR;
  const Icon = DOMAIN_ICONS[domain] || CheckCircle2;

  return (
    <div className={`rounded-xl border ${cfg.border} ${cfg.bg} p-4 space-y-2`}>
      <div className="flex items-start gap-2">
        <div className="w-8 h-8 rounded-lg bg-[#07041c]/80 flex items-center justify-center shrink-0 mt-0.5">
          <Icon className={`w-4 h-4 ${cfg.icon}`} />
        </div>
        <div className="flex-1 min-w-0">
          <div className={`text-[11px] font-semibold ${cfg.text} uppercase tracking-wider`}>
            {domain.replace(/_/g, ' ')}
          </div>
          <div className="text-xs text-slate-400">{status}</div>
        </div>
      </div>

      <div className="text-lg font-bold text-[#fbfbfe] leading-tight">
        {headline_metric}
      </div>

      <p className="text-[11px] text-slate-300 leading-relaxed">
        {detail}
      </p>

      <div className="pt-1 border-t border-[#1f1a54]/40 text-[10px] text-slate-500 flex items-start gap-1">
        <Info className="w-3 h-3 shrink-0 mt-0.5 text-[#dedcff]/60" />
        <span>{explainability}</span>
      </div>
    </div>
  );
}

/**
 * RiskOverviewSection
 * Renders independent domain assessment cards.
 * Uses the `domains` list from /api/risk/overview — no unified composite score.
 */
export function RiskOverviewSection({ overview }) {
  if (!overview || !overview.domains) {
    return (
      <div className="rounded-xl border border-[#1f1a54]/60 bg-[#07041c]/60 p-6 text-center text-slate-400 text-sm">
        Risk overview unavailable.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <CheckCircle2 className="w-5 h-5 text-[#dedcff]" />
        <div>
          <h2 className="text-base font-semibold text-[#fbfbfe]">Independent Risk Domain Overview</h2>
          <p className="text-xs text-slate-400">
            Five domains assessed independently. No unified 0–100 score.
          </p>
        </div>
      </div>

      {/* Domain cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        {overview.domains.map((d) => (
          <DomainCard key={d.domain} domainEntry={d} />
        ))}
      </div>

      {/* Governance note */}
      {overview.governance_note && (
        <div className="rounded-lg border border-[#1f1a54]/60 bg-[#07041c]/40 px-4 py-2.5 text-[11px] text-slate-400 flex items-start gap-1.5">
          <Info className="w-3.5 h-3.5 text-[#dedcff] shrink-0 mt-0.5" />
          <span>{overview.governance_note}</span>
        </div>
      )}

      {/* Snapshot */}
      <div className="text-[10px] text-slate-500">
        Snapshot: {overview.assumed_snapshot_date} (assumed)
        {overview.snapshot_date_is_assumed ? ' — analytical assumption, not dataset-supplied' : ''}
        · Currency: {overview.currency_code}
      </div>
    </div>
  );
}
