import React, { useState } from 'react';
import {
  Brain,
  Sparkles,
  TrendingUp,
  Package,
  Users,
  Wrench,
  CheckCircle2,
  Clock,
  AlertCircle,
  Loader2,
  ChevronRight,
  ChevronDown
} from 'lucide-react';

const AGENT_CONFIGS = {
  manager: {
    name: 'Manager Agent',
    icon: Sparkles,
    color: 'text-[#dedcff]',
    bg: 'bg-[#2f27ce]/30',
    border: 'border-[#433bff]/40'
  },
  sales: {
    name: 'Sales Agent',
    icon: TrendingUp,
    color: 'text-emerald-300',
    bg: 'bg-emerald-950/40',
    border: 'border-emerald-500/30'
  },
  inventory: {
    name: 'Inventory Agent',
    icon: Package,
    color: 'text-amber-300',
    bg: 'bg-amber-950/40',
    border: 'border-amber-500/30'
  },
  hr: {
    name: 'People Management Agent',
    icon: Users,
    color: 'text-sky-300',
    bg: 'bg-sky-950/40',
    border: 'border-sky-500/30'
  },
  tool: {
    name: 'Tool Invocation',
    icon: Wrench,
    color: 'text-purple-300',
    bg: 'bg-purple-950/40',
    border: 'border-purple-500/30'
  },
  bridge: {
    name: 'Context Transfer',
    icon: Sparkles,
    color: 'text-indigo-300',
    bg: 'bg-indigo-950/40',
    border: 'border-indigo-500/40'
  }
};

export function AgentTraceItem({ event, isLast, index }) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Normalize agent key
  const agentKey = event.type === 'context_passed'
    ? 'bridge'
    : event.tool
    ? 'tool'
    : (event.agent || '').toLowerCase().includes('sales')
    ? 'sales'
    : (event.agent || '').toLowerCase().includes('inventory')
    ? 'inventory'
    : ((event.agent || '').toLowerCase().includes('hr') || (event.agent || '').toLowerCase().includes('people'))
    ? 'hr'
    : 'manager';

  const config = AGENT_CONFIGS[agentKey] || AGENT_CONFIGS.manager;
  const Icon = config.icon;

  const isRunning = event.status === 'running';
  const isSuccess = event.status === 'success';
  const isError = event.status === 'error';

  const hasDetails = event.params || event.result || event.meta;

  return (
    <div className="relative flex items-start gap-3 text-xs group">
      {/* Vertical timeline connecting line */}
      {!isLast && (
        <div
          className={`absolute left-4 top-8 bottom-0 w-[1.5px] -ml-[0.75px] transition-colors duration-300 ${
            isSuccess ? 'bg-[#433bff]/40' : 'bg-[#1f1a54]/60'
          }`}
        />
      )}

      {/* Node Avatar Icon */}
      <div
        className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 z-10 border transition-all duration-200 ${
          config.bg
        } ${config.border} ${
          isRunning ? 'ring-2 ring-[#433bff] shadow-card-glow' : ''
        }`}
      >
        {isRunning ? (
          <Loader2 className="w-4 h-4 animate-spin text-[#dedcff]" />
        ) : (
          <Icon className={`w-4 h-4 ${config.color}`} />
        )}
      </div>

      {/* Step Content Card */}
      <div className="flex-1 pb-5 min-w-0">
        <div className="p-3 rounded-xl bg-[#0c0827] border border-[#1f1a54] hover:border-[#433bff]/40 transition-all shadow-sm">
          {/* Header row */}
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 min-w-0">
              <span className="font-semibold text-[#fbfbfe] truncate">
                {event.tool || event.agent || config.name}
              </span>

              {event.type && (
                <span className="text-[10px] font-mono text-slate-400 bg-[#16113c] px-1.5 py-0.2 rounded border border-[#1f1a54] hidden sm:inline">
                  {event.type}
                </span>
              )}
            </div>

            {/* Status indicator */}
            <div className="flex items-center gap-1.5 shrink-0">
              {event.duration && (
                <span className="text-[10px] font-mono text-slate-400 flex items-center gap-0.5">
                  <Clock className="w-2.5 h-2.5" />
                  {event.duration}
                </span>
              )}

              {isRunning && (
                <span className="inline-flex items-center gap-1 text-[11px] text-[#dedcff] bg-[#2f27ce]/30 border border-[#433bff]/40 px-1.5 py-0.2 rounded-full">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#433bff] animate-ping" />
                  running
                </span>
              )}

              {isSuccess && (
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              )}

              {isError && (
                <AlertCircle className="w-4 h-4 text-rose-400" />
              )}
            </div>
          </div>

          {/* Description Message */}
          {event.message && (
            <p className="text-slate-300 text-[11px] mt-1.5 leading-normal">
              {event.message}
            </p>
          )}

          {/* Visual context transfer indicator */}
          {event.type === 'context_passed' && (
            <div className="mt-2.5 p-2 rounded-lg bg-[#0e0a2d] border border-[#433bff]/40 flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5 font-medium text-emerald-300">
                <TrendingUp className="w-3 h-3" />
                <span>Sales Agent</span>
              </div>
              <div className="flex items-center gap-1 text-[10px] text-[#dedcff] font-mono">
                <span>→</span>
                <span className="bg-[#2f27ce]/50 px-1.5 py-0.5 rounded border border-[#433bff]/40">
                  {event.metadata?.product_ids?.join(', ') || 'product context'}
                </span>
                <span>→</span>
              </div>
              <div className="flex items-center gap-1.5 font-medium text-amber-300">
                <Package className="w-3 h-3" />
                <span>Inventory Agent</span>
              </div>
            </div>
          )}

          {/* Expandable inspector for parameters / payload */}
          {hasDetails && (
            <div className="mt-2 pt-2 border-t border-[#1f1a54]/50">
              <button
                type="button"
                onClick={() => setIsExpanded(!isExpanded)}
                className="flex items-center gap-1 text-[10px] font-mono text-slate-400 hover:text-[#dedcff] transition-colors"
              >
                {isExpanded ? (
                  <ChevronDown className="w-3 h-3" />
                ) : (
                  <ChevronRight className="w-3 h-3" />
                )}
                <span>Inspect Step Payload</span>
              </button>

              {isExpanded && (
                <div className="mt-1.5 p-2 rounded bg-[#07041a] border border-[#1f1a54] text-[10px] text-slate-300 overflow-x-auto">
                  <pre className="font-mono">
                    {JSON.stringify(
                      { params: event.params, result: event.result, meta: event.meta },
                      null,
                      2
                    )}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
