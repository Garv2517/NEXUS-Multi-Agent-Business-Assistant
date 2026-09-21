import React from 'react';
import { CheckCircle2 } from 'lucide-react';

export function CapabilityCard({
  icon: Icon,
  title,
  subtitle,
  description,
  capabilities = [],
  badge = null,
  accentColor = 'indigo'
}) {
  const colorStyles = {
    indigo: {
      border: 'border-[#433bff]/30 hover:border-[#433bff]/60',
      iconBg: 'bg-[#2f27ce]/20 text-[#dedcff] border-[#433bff]/30',
      badge: 'bg-[#2f27ce]/20 text-[#dedcff] border-[#433bff]/30'
    },
    emerald: {
      border: 'border-emerald-500/30 hover:border-emerald-500/60',
      iconBg: 'bg-emerald-950/40 text-emerald-300 border-emerald-500/30',
      badge: 'bg-emerald-950/40 text-emerald-300 border-emerald-500/30'
    },
    amber: {
      border: 'border-amber-500/30 hover:border-amber-500/60',
      iconBg: 'bg-amber-950/40 text-amber-300 border-amber-500/30',
      badge: 'bg-amber-950/40 text-amber-300 border-amber-500/30'
    },
    sky: {
      border: 'border-sky-500/30 hover:border-sky-500/60',
      iconBg: 'bg-sky-950/40 text-sky-300 border-sky-500/30',
      badge: 'bg-sky-950/40 text-sky-300 border-sky-500/30'
    },
    purple: {
      border: 'border-purple-500/30 hover:border-purple-500/60',
      iconBg: 'bg-purple-950/40 text-purple-300 border-purple-500/30',
      badge: 'bg-purple-950/40 text-purple-300 border-purple-500/30'
    }
  };

  const style = colorStyles[accentColor] || colorStyles.indigo;

  return (
    <div
      className={`nexus-card p-5 flex flex-col justify-between transition-all duration-200 ${style.border}`}
    >
      <div>
        <div className="flex items-start justify-between gap-3 mb-3">
          <div
            className={`w-9 h-9 rounded-lg flex items-center justify-center border shrink-0 ${style.iconBg}`}
          >
            {Icon && <Icon className="w-4 h-4" />}
          </div>
          {badge && (
            <span
              className={`text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded border ${style.badge}`}
            >
              {badge}
            </span>
          )}
        </div>

        <h3 className="text-sm font-semibold text-[#fbfbfe] tracking-tight">
          {title}
        </h3>
        {subtitle && (
          <div className="text-[11px] text-slate-400 font-medium mt-0.5">
            {subtitle}
          </div>
        )}

        <p className="text-xs text-slate-300 mt-2 leading-relaxed">
          {description}
        </p>

        {capabilities.length > 0 && (
          <div className="mt-4 pt-3 border-t border-[#1f1a54]/60 space-y-1.5">
            <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Verified Capabilities
            </div>
            {capabilities.map((cap, idx) => (
              <div
                key={idx}
                className="flex items-center gap-2 text-xs text-slate-300"
              >
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>{cap}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
