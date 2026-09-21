import React, { useState } from 'react';
import {
  Sparkles,
  Layers,
  Code2,
  RefreshCw,
  Clock,
  CheckCircle2,
  AlertCircle,
  X,
  Sliders
} from 'lucide-react';
import { AgentTraceItem } from './AgentTraceItem';

export function AgentTrace({ events, isOrchestrating, activeAgent, onReset, onCloseMobile, lastResponse }) {
  const [showJsonModal, setShowJsonModal] = useState(false);
  const [developerMode, setDeveloperMode] = useState(false);

  const completedSteps = events.filter((e) => e.status === 'success').length;
  const runningSteps = events.filter((e) => e.status === 'running').length;

  return (
    <div className="h-full flex flex-col bg-[#07041c]/95 border-l border-[#1f1a54]/70">
      {/* Trace Header */}
      <div className="p-4 border-b border-[#1f1a54]/60 flex items-center justify-between shrink-0 bg-[#090623]">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-[#2f27ce]/20 border border-[#433bff]/30 flex items-center justify-center text-[#dedcff]">
            <Sparkles className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <h3 className="text-xs sm:text-sm font-semibold text-[#fbfbfe] tracking-tight leading-none">
                Agent Trace
              </h3>
              {developerMode && (
                <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-purple-950/60 border border-purple-500/40 text-purple-300">
                  DEV VIEW
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-400 mt-1 leading-none">
              Live orchestration
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {isOrchestrating ? (
            <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium bg-[#2f27ce]/30 border border-[#433bff]/40 text-[#dedcff]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#433bff] animate-ping" />
              Routing...
            </span>
          ) : events.length > 0 ? (
            <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-950/40 border border-emerald-500/30 text-emerald-300">
              <CheckCircle2 className="w-3 h-3" />
              Synced
            </span>
          ) : (
            <span className="text-[11px] text-slate-500 font-mono">Idle</span>
          )}

          {/* Close button if rendered in mobile drawer */}
          {onCloseMobile && (
            <button
              type="button"
              onClick={onCloseMobile}
              className="lg:hidden p-1 rounded-md text-slate-400 hover:text-white hover:bg-[#1f1a54]"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Trace Timeline Body */}
      <div className="flex-1 overflow-y-auto p-4">
        {events.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-4">
            <div className="w-10 h-10 rounded-xl bg-[#0c0827] border border-[#1f1a54] flex items-center justify-center text-slate-500 mb-3">
              <Layers className="w-5 h-5" />
            </div>
            <div className="text-xs font-semibold text-[#dedcff]">
              Waiting for Agent Query
            </div>
            <p className="text-[11px] text-slate-400 mt-1 max-w-[200px]">
              Send a query to observe the Manager Agent route tasks to Sales, Inventory, and People Management in real-time.
            </p>
          </div>
        ) : (
          <div className="relative pt-1">
            {events.map((event, idx) => (
              <AgentTraceItem
                key={event.id || idx}
                event={event}
                index={idx}
                isLast={idx === events.length - 1}
              />
            ))}
          </div>
        )}
      </div>

      {/* Trace Footer Controls */}
      <div className="p-3 border-t border-[#1f1a54]/60 bg-[#090623] flex items-center justify-between text-[11px] text-slate-400 shrink-0">
        {/* Developer View Toggle */}
        <label className="flex items-center gap-1.5 cursor-pointer select-none text-[11px] text-slate-400 hover:text-slate-200">
          <input
            type="checkbox"
            checked={developerMode}
            onChange={(e) => setDeveloperMode(e.target.checked)}
            className="w-3.5 h-3.5 rounded bg-[#0c0827] border-[#1f1a54] text-[#433bff] focus:ring-0 focus:ring-offset-0 cursor-pointer accent-[#433bff]"
          />
          <span className="font-medium">Developer View</span>
        </label>

        <div className="flex items-center gap-2">
          {events.length > 0 && (
            <>
              {/* Raw JSON Button — visible ONLY in Developer View */}
              {developerMode && (
                <button
                  type="button"
                  onClick={() => setShowJsonModal(true)}
                  className="px-2 py-1 rounded bg-[#0c0827] hover:bg-[#1f1a54] border border-purple-500/40 text-purple-300 hover:text-white text-[11px] font-mono flex items-center gap-1 transition-colors"
                >
                  <Code2 className="w-3 h-3" />
                  JSON
                </button>
              )}

              {onReset && (
                <button
                  type="button"
                  onClick={onReset}
                  className="p-1 rounded hover:bg-[#1f1a54] text-slate-400 hover:text-white transition-colors"
                  title="Clear Trace"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                </button>
              )}
            </>
          )}
        </div>
      </div>

      {/* Raw Event Stream Inspector Modal */}
      {showJsonModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0c0827] border border-[#1f1a54] rounded-xl max-w-xl w-full p-4 max-h-[80vh] flex flex-col shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-[#1f1a54]">
              <div className="flex items-center gap-2">
                <Code2 className="w-4 h-4 text-purple-300" />
                <h4 className="text-sm font-semibold text-[#fbfbfe]">
                  Developer View: Raw Orchestration Events
                </h4>
              </div>
              <button
                type="button"
                onClick={() => setShowJsonModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto mt-3 p-3 bg-[#050315] rounded-lg border border-[#1f1a54] text-xs font-mono">
              <div className="mb-3 pb-2 border-b border-[#1f1a54]/60">
                <div className="text-slate-400 text-[11px]">Session ID: <span className="text-[#dedcff]">{lastResponse?.session_id || 'None'}</span></div>
                <div className="text-slate-400 text-[11px] mt-1">Agents Used: <span className="text-emerald-300">{lastResponse?.agents_used?.join(', ') || 'None'}</span></div>
              </div>

              {lastResponse?.plan && (
                <div className="mb-3 pb-2 border-b border-[#1f1a54]/60">
                  <div className="text-purple-300 font-semibold mb-1 text-[11px]">Execution Plan:</div>
                  <pre className="text-[10px] text-slate-300 whitespace-pre-wrap bg-[#07041a] p-2 rounded border border-[#1f1a54]/40">
                    {JSON.stringify(lastResponse.plan, null, 2)}
                  </pre>
                </div>
              )}

              {lastResponse?.tool_calls && lastResponse.tool_calls.length > 0 && (
                <div className="mb-3 pb-2 border-b border-[#1f1a54]/60">
                  <div className="text-amber-300 font-semibold mb-1 text-[11px]">Tool Executions ({lastResponse.tool_calls.length}):</div>
                  <pre className="text-[10px] text-slate-300 whitespace-pre-wrap bg-[#07041a] p-2 rounded border border-[#1f1a54]/40">
                    {JSON.stringify(lastResponse.tool_calls, null, 2)}
                  </pre>
                </div>
              )}

              <div>
                <div className="text-sky-300 font-semibold mb-1 text-[11px]">Raw Trace Events ({events.length}):</div>
                <pre className="text-[10px] text-[#dedcff] whitespace-pre-wrap bg-[#07041a] p-2 rounded border border-[#1f1a54]/40">
                  {JSON.stringify(events, null, 2)}
                </pre>
              </div>
            </div>

            <div className="mt-3 flex justify-end">
              <button
                type="button"
                onClick={() => setShowJsonModal(false)}
                className="px-3 py-1.5 text-xs rounded-lg bg-[#2f27ce] text-white hover:bg-[#433bff] transition-colors"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
