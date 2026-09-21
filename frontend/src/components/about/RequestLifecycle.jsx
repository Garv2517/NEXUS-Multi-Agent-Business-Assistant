import React from 'react';
import {
  MessageSquare,
  Sparkles,
  GitFork,
  Wrench,
  FolderGit2,
  Database,
  FileCheck,
  CheckCircle2,
  ShieldAlert,
  ArrowRight
} from 'lucide-react';

const STEPS = [
  {
    step: '01',
    title: 'Natural Language Request',
    actor: 'User / Interface',
    desc: 'Business query submitted via Chat Assistant or automated intent trigger.',
    icon: MessageSquare,
    accent: 'text-slate-200 bg-slate-800/60 border-slate-700/60'
  },
  {
    step: '02',
    title: 'Intent Selection',
    actor: 'Foundry Router / Deterministic',
    desc: 'Maps natural language query to an authorized NexusIntent without executing free-form actions.',
    icon: Sparkles,
    accent: 'text-purple-300 bg-purple-950/40 border-purple-500/40'
  },
  {
    step: '03',
    title: 'Specialist Delegation',
    actor: 'Nexus Manager Agent',
    desc: 'Manager formulates an execution plan and routes to Sales, Inventory, or People Management.',
    icon: GitFork,
    accent: 'text-indigo-300 bg-indigo-950/40 border-indigo-500/40'
  },
  {
    step: '04',
    title: 'Business Tools',
    actor: 'Specialist Components',
    desc: 'Deterministic specialist functions execute discrete, bounded business queries.',
    icon: Wrench,
    accent: 'text-sky-300 bg-sky-950/40 border-sky-500/40'
  },
  {
    step: '05',
    title: 'Repositories',
    actor: 'Data Access Layer',
    desc: 'Abstracted repository operations query persistent relational tables with strict parameterization.',
    icon: FolderGit2,
    accent: 'text-blue-300 bg-blue-950/40 border-blue-500/40'
  },
  {
    step: '06',
    title: 'SQLite Database',
    actor: 'Persistent Store',
    desc: 'Single source of truth containing verified sales, product stock, and workforce census records.',
    icon: Database,
    accent: 'text-emerald-300 bg-emerald-950/40 border-emerald-500/40'
  },
  {
    step: '07',
    title: 'Structured Results',
    actor: 'Business Service',
    desc: 'Structured tool and API results strictly typed with exact numbers, counts, and currency figures.',
    icon: FileCheck,
    accent: 'text-amber-300 bg-amber-950/40 border-amber-500/40'
  },
  {
    step: '08',
    title: 'Verified Response',
    actor: 'Nexus Manager Agent',
    desc: 'Manager synthesizes final user-facing response with complete, transparent Agent Trace telemetry.',
    icon: CheckCircle2,
    accent: 'text-teal-300 bg-teal-950/40 border-teal-500/40'
  }
];

export function RequestLifecycle() {
  return (
    <div className="space-y-6">
      {/* Prominent Architectural Distinction Callout */}
      <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-r from-[#2f27ce]/20 via-[#433bff]/15 to-[#0c0827] border border-[#433bff]/40 shadow-card-glow flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-[#2f27ce] flex items-center justify-center text-white shrink-0 border border-[#433bff]/50 shadow-subtle-glow mt-0.5">
            <Sparkles className="w-5 h-5 text-[#dedcff]" />
          </div>
          <div>
            <div className="text-sm sm:text-base font-bold text-[#fbfbfe] tracking-tight">
              GPT-5-mini selects the workflow. It does not generate the business metrics.
            </div>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
              In Foundry Manager Mode, the cloud model parses user intent and constructs a structured execution plan.
              Actual facts—revenues, stock levels, and headcount—are computed deterministically by verified backend repositories and SQLite.
            </p>
          </div>
        </div>

        <div className="shrink-0 flex items-center gap-2">
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-[#2f27ce]/40 border border-[#433bff]/50 text-[#dedcff]">
            Trusted Execution Mesh
          </span>
        </div>
      </div>

      {/* Horizontal / Grid Request Steps */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        {STEPS.map((item, idx) => {
          const Icon = item.icon;
          return (
            <div
              key={item.step}
              className="nexus-card p-4 flex flex-col justify-between hover:border-[#433bff]/50 transition-all duration-150 relative group"
            >
              <div>
                <div className="flex items-center justify-between mb-2.5">
                  <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-[#080520] border border-[#1f1a54] text-slate-400">
                    STEP {item.step}
                  </span>
                  <div
                    className={`w-7 h-7 rounded-lg flex items-center justify-center border ${item.accent}`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                  </div>
                </div>

                <h4 className="text-xs sm:text-sm font-semibold text-[#fbfbfe] tracking-tight">
                  {item.title}
                </h4>
                <div className="text-[10px] font-mono text-[#dedcff] mt-0.5">
                  {item.actor}
                </div>

                <p className="text-[11px] text-slate-300 mt-2 leading-relaxed">
                  {item.desc}
                </p>
              </div>

              {idx < STEPS.length - 1 && (
                <div className="hidden lg:block absolute -right-2 top-1/2 -translate-y-1/2 z-10 text-[#433bff]/60 pointer-events-none">
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
