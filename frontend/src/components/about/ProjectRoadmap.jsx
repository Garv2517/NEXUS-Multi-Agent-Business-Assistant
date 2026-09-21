import React from 'react';
import { CheckCircle2, Clock, Sparkles, Layers, ArrowRight } from 'lucide-react';

const ROADMAP_PHASES = [
  {
    code: 'B1',
    title: 'FastAPI Foundation',
    status: 'completed',
    period: 'Frozen Baseline',
    desc: 'Core web service architecture, CORS handling, Pydantic schemas, and frontend API contracts.'
  },
  {
    code: 'B2',
    title: 'SQLite + Business Tools',
    status: 'completed',
    period: 'Frozen Baseline',
    desc: 'Relational business database, deterministic specialist tool definitions, and transactional repositories.'
  },
  {
    code: 'B3',
    title: 'Local Multi-Agent Orchestration',
    status: 'completed',
    period: 'Frozen Baseline',
    desc: 'Deterministic Manager routing, specialist domain delegation, context passing, and compound response synthesis.'
  },
  {
    code: 'B4A',
    title: 'Foundry Connectivity Preflight',
    status: 'completed',
    period: 'Frozen Baseline',
    desc: 'Azure CLI credential authentication, Foundry project client integration, and initial model smoke verification.'
  },
  {
    code: 'B4B',
    title: 'Foundry Manager Routing',
    status: 'completed',
    period: 'Current Release',
    desc: 'Microsoft Agent Framework agent routing natural language inquiries into validated NexusIntent execution plans.'
  },
  {
    code: 'B5',
    title: 'Foundry Specialist Agents',
    status: 'planned',
    period: 'Upcoming Phase',
    desc: 'Upgrading domain specialists (Sales, Inventory, People Management) to autonomous conversational agents.'
  },
  {
    code: 'B6',
    title: 'Insights & Risk Intelligence',
    status: 'planned',
    period: 'Upcoming Phase',
    desc: 'Predictive sales forecasting, stockout probability models, and Kaggle retail dataset integration.'
  },
  {
    code: 'B7',
    title: 'Agent-to-Agent (A2A) Protocols',
    status: 'planned',
    period: 'Future Roadmap',
    desc: 'Direct peer negotiation between specialist agents and standardized multi-agent communication networks.'
  }
];

export function ProjectRoadmap() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3.5">
        {ROADMAP_PHASES.map((item) => {
          const isDone = item.status === 'completed';
          return (
            <div
              key={item.code}
              className={`p-4 rounded-xl border flex flex-col justify-between transition-all duration-150 ${
                isDone
                  ? 'bg-[#090624] border-[#2f27ce]/50 hover:border-[#433bff]'
                  : 'bg-[#060417]/60 border-[#1f1a54]/50 opacity-80 hover:opacity-100 hover:border-[#1f1a54]'
              }`}
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span
                    className={`font-mono text-[11px] font-bold px-2 py-0.5 rounded border ${
                      isDone
                        ? 'bg-[#2f27ce]/30 border-[#433bff]/50 text-[#dedcff]'
                        : 'bg-slate-900 border-slate-700 text-slate-400'
                    }`}
                  >
                    {item.code}
                  </span>

                  <span
                    className={`text-[10px] font-semibold flex items-center gap-1 ${
                      isDone ? 'text-emerald-400' : 'text-slate-400'
                    }`}
                  >
                    {isDone ? (
                      <>
                        <CheckCircle2 className="w-3 h-3" />
                        Completed
                      </>
                    ) : (
                      <>
                        <Clock className="w-3 h-3" />
                        Planned
                      </>
                    )}
                  </span>
                </div>

                <h4 className="text-xs font-semibold text-[#fbfbfe] tracking-tight">
                  {item.title}
                </h4>

                <div className="text-[10px] font-mono text-slate-400 mt-0.5">
                  {item.period}
                </div>

                <p className="text-[11px] text-slate-300 mt-2 leading-relaxed">
                  {item.desc}
                </p>
              </div>

              <div className="mt-3 pt-2.5 border-t border-[#1f1a54]/50 flex items-center justify-between text-[10px] text-slate-400">
                <span>Phase Status</span>
                <span
                  className={
                    isDone
                      ? 'text-[#dedcff] font-medium'
                      : 'text-slate-500 italic'
                  }
                >
                  {isDone ? 'Verified & Frozen' : 'Under Design'}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
