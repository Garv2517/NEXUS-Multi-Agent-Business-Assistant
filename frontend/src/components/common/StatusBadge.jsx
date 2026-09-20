import React from 'react';
import { CheckCircle2, Clock, AlertCircle, AlertTriangle, Loader2 } from 'lucide-react';

export function StatusBadge({ status, label, size = 'sm', pulse = false }) {
  const normStatus = (status || '').toLowerCase();

  let styles = {
    bg: 'bg-slate-800/60',
    border: 'border-slate-700/60',
    text: 'text-slate-300',
    dot: 'bg-slate-400',
    icon: null
  };

  if (normStatus === 'success' || normStatus === 'healthy' || normStatus === 'completed' || normStatus === 'active') {
    styles = {
      bg: 'bg-emerald-950/40',
      border: 'border-emerald-500/30',
      text: 'text-emerald-300',
      dot: 'bg-emerald-400',
      icon: <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" />
    };
  } else if (normStatus === 'running' || normStatus === 'processing' || normStatus === 'in_progress') {
    styles = {
      bg: 'bg-[#2f27ce]/25',
      border: 'border-[#433bff]/40',
      text: 'text-[#dedcff]',
      dot: 'bg-[#433bff]',
      icon: <Loader2 className="w-3 h-3 text-[#dedcff] animate-spin shrink-0" />
    };
  } else if (normStatus === 'low' || normStatus === 'warning' || normStatus === 'on leave') {
    styles = {
      bg: 'bg-amber-950/40',
      border: 'border-amber-500/30',
      text: 'text-amber-300',
      dot: 'bg-amber-400',
      icon: <AlertTriangle className="w-3 h-3 text-amber-400 shrink-0" />
    };
  } else if (normStatus === 'error' || normStatus === 'out of stock' || normStatus === 'failed') {
    styles = {
      bg: 'bg-rose-950/40',
      border: 'border-rose-500/30',
      text: 'text-rose-300',
      dot: 'bg-rose-400',
      icon: <AlertCircle className="w-3 h-3 text-rose-400 shrink-0" />
    };
  } else if (normStatus === 'idle') {
    styles = {
      bg: 'bg-slate-900/60',
      border: 'border-slate-700/40',
      text: 'text-slate-400',
      dot: 'bg-slate-500',
      icon: <Clock className="w-3 h-3 text-slate-400 shrink-0" />
    };
  }

  const displayText = label || status;
  const padding = size === 'xs' ? 'px-1.5 py-0.5 text-[11px]' : 'px-2 py-0.5 text-xs';

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium rounded-full border ${styles.bg} ${styles.border} ${styles.text} ${padding} transition-all duration-150`}
    >
      {styles.icon ? (
        styles.icon
      ) : (
        <span className={`w-1.5 h-1.5 rounded-full ${styles.dot} ${pulse ? 'animate-ping' : ''}`} />
      )}
      <span>{displayText}</span>
    </span>
  );
}
