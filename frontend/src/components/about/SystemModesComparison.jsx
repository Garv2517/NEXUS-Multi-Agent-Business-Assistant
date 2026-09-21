import React from 'react';
import { Cpu, Cloud, CheckCircle2, ShieldCheck, Zap, Database } from 'lucide-react';

export function SystemModesComparison() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
        {/* Local Agent Mode Card */}
        <div className="nexus-card p-5 sm:p-6 flex flex-col justify-between border-[#1f1a54] hover:border-[#433bff]/40 transition-colors">
          <div>
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-[#1f1a54]/60">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-[#16113c] border border-[#1f1a54] flex items-center justify-center text-slate-300">
                  <Cpu className="w-4 h-4 text-[#dedcff]" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-[#fbfbfe]">
                    Local Agent Mode
                  </h3>
                  <div className="text-[10px] font-mono text-slate-400">
                    B3 Orchestration Baseline
                  </div>
                </div>
              </div>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-800/80 text-slate-300 border border-slate-700">
                Deterministic
              </span>
            </div>

            <div className="space-y-3">
              <div className="p-3 rounded-lg bg-[#050315] border border-[#1f1a54]/60 font-mono text-xs text-slate-300 space-y-1">
                <div className="text-slate-400 text-[10px] uppercase font-semibold">
                  Execution Flow
                </div>
                <div className="text-[#dedcff] text-[11px] leading-relaxed">
                  User &rarr; Deterministic Router &rarr; Manager &rarr; Specialists &rarr; Tools &rarr; Repositories &rarr; SQLite
                </div>
              </div>

              <div className="space-y-2 pt-1 text-xs text-slate-300">
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold text-[#fbfbfe]">Cloud inference:</span> No Foundry model inference required.
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold text-[#fbfbfe]">Routing speed:</span> Instantaneous regex & keyword pattern matching (&lt;5ms).
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold text-[#fbfbfe]">Availability:</span> Operates reliably on any standard workstation without Azure connectivity.
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-5 pt-3 border-t border-[#1f1a54]/60 flex items-center justify-between text-[11px] text-slate-400">
            <span>Data Source: Local SQLite</span>
            <span className="text-emerald-400 font-mono">Zero Latency Overhead</span>
          </div>
        </div>

        {/* Foundry Manager Mode Card */}
        <div className="nexus-card p-5 sm:p-6 flex flex-col justify-between border-[#433bff]/40 shadow-card-glow relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-[#433bff]/10 rounded-full blur-2xl pointer-events-none" />

          <div>
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-[#1f1a54]/60">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-[#2f27ce] border border-[#433bff]/50 flex items-center justify-center text-white shadow-subtle-glow">
                  <Cloud className="w-4 h-4 text-[#dedcff]" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-[#fbfbfe]">
                    Foundry Manager Mode
                  </h3>
                  <div className="text-[10px] font-mono text-[#dedcff]">
                    B4B Microsoft Agent Framework
                  </div>
                </div>
              </div>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-[#2f27ce]/30 text-[#dedcff] border border-[#433bff]/40">
                GPT-5-mini Guided
              </span>
            </div>

            <div className="space-y-3">
              <div className="p-3 rounded-lg bg-[#050315] border border-[#433bff]/30 font-mono text-xs text-slate-300 space-y-1">
                <div className="text-purple-300 text-[10px] uppercase font-semibold">
                  Execution Flow
                </div>
                <div className="text-[#dedcff] text-[11px] leading-relaxed">
                  User &rarr; GPT-5-mini &rarr; Validated Nexus Intent &rarr; Manager &rarr; Specialists &rarr; Tools &rarr; Repositories &rarr; SQLite
                </div>
              </div>

              <div className="space-y-2 pt-1 text-xs text-slate-300">
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold text-[#fbfbfe]">AI role:</span> Natural-language routing and multi-step inquiry planning.
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold text-[#fbfbfe]">Guardrails:</span> Output strictly validated into NexusIntent enum before tool dispatch.
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold text-[#fbfbfe]">Resilience:</span> Automatic graceful fallback to deterministic local router if cloud is unreachable.
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-5 pt-3 border-t border-[#1f1a54]/60 flex items-center justify-between text-[11px] text-slate-400">
            <span>Model: gpt-5-mini (Foundry)</span>
            <span className="text-purple-300 font-mono">Server-Side Auth</span>
          </div>
        </div>
      </div>

      {/* Unified Data Foundation Footer */}
      <div className="p-3.5 rounded-xl bg-[#090623] border border-[#1f1a54] flex items-center justify-center gap-2 text-center text-xs text-slate-300">
        <Database className="w-4 h-4 text-[#dedcff] shrink-0" />
        <span>
          <strong className="text-[#fbfbfe]">Unified Foundation:</strong> Both modes share the identical deterministic business tools, repository abstractions, and SQLite business records.
        </span>
      </div>
    </div>
  );
}
