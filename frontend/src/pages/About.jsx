import React from 'react';
import {
  Sparkles,
  TrendingUp,
  Package,
  Users,
  Layers,
  Scale,
  ShieldCheck,
  Cpu,
  Lock,
  Eye,
  RotateCcw,
  CheckCircle2,
  Database,
  Bot
} from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { NexusNetworkGraph } from '../components/about/NexusNetworkGraph';
import { RequestLifecycle } from '../components/about/RequestLifecycle';
import { CapabilityCard } from '../components/about/CapabilityCard';
import { SystemModesComparison } from '../components/about/SystemModesComparison';
import { ProjectRoadmap } from '../components/about/ProjectRoadmap';

export function About() {
  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-12">
      {/* 1. Page Header & Hero Section */}
      <div className="space-y-4">
        <PageHeader
          title="About NEXUS"
          description="Multi-Agent Business Intelligence Assistant"
          badge="Architecture & Insights"
        />

        <div className="nexus-card p-6 sm:p-8 bg-gradient-to-r from-[#0c082b] via-[#090624] to-[#050315] border-[#433bff]/40 shadow-card-glow relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-[#2f27ce]/10 rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10 max-w-3xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-[#2f27ce]/30 border border-[#433bff]/50 text-[#dedcff]">
              <Sparkles className="w-3.5 h-3.5 text-[#dedcff]" />
              Enterprise Multi-Agent Architecture
            </div>

            <h1 className="text-2xl sm:text-3xl font-extrabold text-[#fbfbfe] tracking-tight leading-tight">
              NEXUS coordinates specialized business agents across Sales, Inventory and People Management to transform structured business data into reliable, traceable insights.
            </h1>

            <p className="text-sm sm:text-base text-slate-300 font-medium leading-relaxed">
              AI selects the workflow. Trusted business tools determine the facts.
            </p>

            <div className="pt-2 flex flex-wrap items-center gap-3 text-xs text-slate-400">
              <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#07041a] border border-[#1f1a54]">
                <Cpu className="w-3.5 h-3.5 text-[#dedcff]" />
                Dual-Mode Routing (Local / Foundry)
              </span>
              <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#07041a] border border-[#1f1a54]">
                <Database className="w-3.5 h-3.5 text-emerald-400" />
                Persistent SQLite Backend
              </span>
              <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#07041a] border border-[#1f1a54]">
                <ShieldCheck className="w-3.5 h-3.5 text-purple-400" />
                Deterministic Specialist Tools
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Multi-Agent Network Graph */}
      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-bold text-[#fbfbfe] tracking-tight flex items-center gap-2">
            <Layers className="w-5 h-5 text-[#dedcff]" />
            Multi-Agent Network Architecture
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Hierarchical dispatch model connecting user inquiries to deterministic domain tools and transactional data.
          </p>
        </div>

        <NexusNetworkGraph />
      </section>

      {/* 3. Request Lifecycle */}
      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-bold text-[#fbfbfe] tracking-tight flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-[#dedcff]" />
            Request Lifecycle & Execution Pipeline
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            How natural language queries flow from intent validation to discrete repository queries and transparent response synthesis.
          </p>
        </div>

        <RequestLifecycle />
      </section>

      {/* 4. Trusted Data Principle & Responsible AI */}
      <section className="space-y-6">
        <div>
          <h2 className="text-lg font-bold text-[#fbfbfe] tracking-tight flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            Trusted Data Principle & Responsible AI
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Architectural guarantees ensuring business metrics are calculated directly from verified databases, never hallucinated.
          </p>
        </div>

        {/* Trusted Data Banner */}
        <div className="nexus-card p-6 border-emerald-500/30 bg-gradient-to-r from-emerald-950/20 via-[#07041c] to-[#050315]">
          <h3 className="text-base sm:text-lg font-bold text-[#fbfbfe] mb-2 flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            AI decides what needs to be done. Business tools determine the facts.
          </h3>
          <p className="text-xs text-slate-300 leading-relaxed max-w-3xl mb-4">
            Nexus enforces strict boundary separation between workflow selection (handled by AI routing) and numerical computation (handled by deterministic Python tools and relational SQL queries).
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <div className="p-3 rounded-lg bg-[#050315] border border-emerald-500/20 flex items-start gap-2 text-xs text-slate-300">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>Revenue figures originate directly from structured sales records.</span>
            </div>
            <div className="p-3 rounded-lg bg-[#050315] border border-emerald-500/20 flex items-start gap-2 text-xs text-slate-300">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>Stock quantities reflect verified inventory levels and reorder thresholds.</span>
            </div>
            <div className="p-3 rounded-lg bg-[#050315] border border-emerald-500/20 flex items-start gap-2 text-xs text-slate-300">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>People information is queried directly from structured employee data.</span>
            </div>
            <div className="p-3 rounded-lg bg-[#050315] border border-emerald-500/20 flex items-start gap-2 text-xs text-slate-300">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>The LLM never fabricates, rounds, or hallucinates operational numbers.</span>
            </div>
          </div>
        </div>

        {/* Responsible AI Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
          <div className="nexus-card p-4 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 text-purple-300 text-xs font-semibold mb-1">
                <Cpu className="w-4 h-4" />
                Structured Routing
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Only validated Nexus intents enter business workflows. Free-form arbitrary code or unexpected intent structures are strictly rejected at the router level.
              </p>
            </div>
          </div>

          <div className="nexus-card p-4 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 text-indigo-300 text-xs font-semibold mb-1">
                <Lock className="w-4 h-4" />
                Controlled Tool Access
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Specialist agents execute only through bounded domain tools. Agents cannot perform arbitrary database operations or access unauthorized data schemas.
              </p>
            </div>
          </div>

          <div className="nexus-card p-4 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 text-sky-300 text-xs font-semibold mb-1">
                <Eye className="w-4 h-4" />
                Full Traceability
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Every router decision, specialist dispatch, tool invocation, and duration is captured and exposed transparently through the live Agent Trace interface.
              </p>
            </div>
          </div>

          <div className="nexus-card p-4 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 text-amber-300 text-xs font-semibold mb-1">
                <RotateCcw className="w-4 h-4" />
                Fallback Reliability
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                When operating in Foundry Manager Mode, the system automatically falls back to deterministic local pattern routing if cloud endpoints experience outages or latency spikes.
              </p>
            </div>
          </div>

          <div className="nexus-card p-4 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 text-teal-300 text-xs font-semibold mb-1">
                <ShieldCheck className="w-4 h-4" />
                Data Protection
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Azure credentials, tokens, and sensitive business records remain securely on the backend server. The client browser never receives cloud tokens or raw SQL credentials.
              </p>
            </div>
          </div>

          <div className="nexus-card p-4 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 text-emerald-300 text-xs font-semibold mb-1">
                <Database className="w-4 h-4" />
                Schema Enforcement
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                All business records utilize relational integrity with foreign keys, constraints, and structured API serialization models across all endpoints.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 5. System Modes Comparison */}
      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-bold text-[#fbfbfe] tracking-tight flex items-center gap-2">
            <Cpu className="w-5 h-5 text-[#dedcff]" />
            System Modes Comparison
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Nexus supports dual orchestration modes sharing the exact same business tools and relational data foundation.
          </p>
        </div>

        <SystemModesComparison />
      </section>

      {/* 6. Core Capabilities */}
      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-bold text-[#fbfbfe] tracking-tight flex items-center gap-2">
            <Bot className="w-5 h-5 text-[#dedcff]" />
            Core Capabilities & Domains
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Specialist domains and supported analytical functions across the Nexus intelligence mesh.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <CapabilityCard
            icon={TrendingUp}
            title="Sales Intelligence"
            subtitle="SalesAgent &bull; sales_tools"
            description="Analyzes gross revenue, periodic sales velocity, average order values, and product performance rankings."
            capabilities={[
              'Total Revenue Calculation',
              'Monthly Sales Velocity & History',
              'Top-Selling Products Identification',
              'Revenue Growth Rate Tracking'
            ]}
            badge="Sales Domain"
            accentColor="emerald"
          />

          <CapabilityCard
            icon={Package}
            title="Inventory Intelligence"
            subtitle="InventoryAgent &bull; inventory_tools"
            description="Monitors real-time warehouse stock levels, triggers replenishment alerts, and flags critical stockouts."
            capabilities={[
              'Product Stock Level Queries',
              'Low-Stock Detection (< Reorder Level)',
              'Out-of-Stock Emergency Flagging',
              'Inventory Health Breakdown'
            ]}
            badge="Inventory Domain"
            accentColor="amber"
          />

          <CapabilityCard
            icon={Users}
            title="People Management"
            subtitle="HRAgent &bull; hr_tools"
            description="Manages workforce census information, departmental allocation, active leave schedules, and organizational policies."
            capabilities={[
              'Workforce Headcount Summary',
              'Employee Details & Attendance',
              'Company Policy & Guideline Retrieval',
              'Departmental Census Aggregation'
            ]}
            badge="People Domain"
            accentColor="sky"
          />

          <CapabilityCard
            icon={Scale}
            title="Cross-Domain Intelligence"
            subtitle="ManagerAgent &bull; Multi-Specialist"
            description="Executes compound multi-specialist queries that require correlating insights across disparate business domains."
            capabilities={[
              'Executive Business Summary',
              'Top Products vs Stock Correlation',
              'Multi-Domain Parallel Dispatch',
              'Cross-Specialist Synthesis'
            ]}
            badge="Cross-Domain"
            accentColor="purple"
          />

          <CapabilityCard
            icon={Layers}
            title="Multi-Agent Orchestration"
            subtitle="ManagerAgent &bull; Telemetry"
            description="Orchestrates specialist execution plans, passes contextual state between specialists, and streams live telemetry."
            capabilities={[
              'Intelligent Intent Classification',
              'Dynamic Execution Plan Generation',
              'Context Passing Between Specialists',
              'Live Agent Trace Audit Trail'
            ]}
            badge="Orchestration"
            accentColor="indigo"
          />
        </div>
      </section>

      {/* 7. Technology Stack */}
      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-bold text-[#fbfbfe] tracking-tight flex items-center gap-2">
            <Cpu className="w-5 h-5 text-[#dedcff]" />
            Technology Stack & Foundations
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Engineered using modern web standards, lightweight local databases, and enterprise cloud AI integration.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
          <div className="nexus-card p-4 space-y-2.5">
            <div className="text-xs font-bold text-[#fbfbfe] uppercase tracking-wider flex items-center gap-1.5 text-indigo-300">
              <span className="w-2 h-2 rounded-full bg-indigo-400" />
              Frontend
            </div>
            <div className="flex flex-wrap gap-1.5 text-[11px] font-mono">
              <span className="px-2 py-0.5 rounded bg-[#07041a] border border-[#1f1a54] text-slate-300">React 19</span>
              <span className="px-2 py-0.5 rounded bg-[#07041a] border border-[#1f1a54] text-slate-300">Vite 8</span>
              <span className="px-2 py-0.5 rounded bg-[#07041a] border border-[#1f1a54] text-slate-300">Tailwind CSS</span>
              <span className="px-2 py-0.5 rounded bg-[#07041a] border border-[#1f1a54] text-slate-300">Lucide Icons</span>
              <span className="px-2 py-0.5 rounded bg-[#07041a] border border-[#1f1a54] text-slate-300">Framer Motion</span>
              <span className="px-2 py-0.5 rounded bg-[#07041a] border border-[#1f1a54] text-slate-300">Recharts</span>
            </div>
          </div>

          <div className="nexus-card p-4 space-y-2.5">
            <div className="text-xs font-bold text-[#fbfbfe] uppercase tracking-wider flex items-center gap-1.5 text-emerald-300">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              Backend
            </div>
            <div className="flex flex-wrap gap-1.5 text-[11px] font-mono">
              <span className="px-2 py-0.5 rounded bg-[#07041a] border border-[#1f1a54] text-slate-300">Python 3.13</span>
              <span className="px-2 py-0.5 rounded bg-[#07041a] border border-[#1f1a54] text-slate-300">FastAPI</span>
              <span className="px-2 py-0.5 rounded bg-[#07041a] border border-[#1f1a54] text-slate-300">SQLite 3</span>
              <span className="px-2 py-0.5 rounded bg-[#07041a] border border-[#1f1a54] text-slate-300">Pydantic v2</span>
              <span className="px-2 py-0.5 rounded bg-[#07041a] border border-[#1f1a54] text-slate-300">Uvicorn</span>
            </div>
          </div>

          <div className="nexus-card p-4 space-y-2.5">
            <div className="text-xs font-bold text-[#fbfbfe] uppercase tracking-wider flex items-center gap-1.5 text-purple-300">
              <span className="w-2 h-2 rounded-full bg-purple-400" />
              AI & Cloud
            </div>
            <div className="flex flex-wrap gap-1.5 text-[11px] font-mono">
              <span className="px-2 py-0.5 rounded bg-[#07041a] border border-[#1f1a54] text-slate-300">Microsoft Foundry</span>
              <span className="px-2 py-0.5 rounded bg-[#07041a] border border-[#1f1a54] text-slate-300">Agent Framework</span>
              <span className="px-2 py-0.5 rounded bg-[#07041a] border border-[#1f1a54] text-slate-300">gpt-5-mini</span>
              <span className="px-2 py-0.5 rounded bg-[#07041a] border border-[#1f1a54] text-slate-300">Azure CLI Auth</span>
            </div>
          </div>

          <div className="nexus-card p-4 space-y-2.5">
            <div className="text-xs font-bold text-[#fbfbfe] uppercase tracking-wider flex items-center gap-1.5 text-sky-300">
              <span className="w-2 h-2 rounded-full bg-sky-400" />
              Architecture
            </div>
            <div className="flex flex-wrap gap-1.5 text-[11px] font-mono">
              <span className="px-2 py-0.5 rounded bg-[#07041a] border border-[#1f1a54] text-slate-300">Manager Agent</span>
              <span className="px-2 py-0.5 rounded bg-[#07041a] border border-[#1f1a54] text-slate-300">Specialist Agents</span>
              <span className="px-2 py-0.5 rounded bg-[#07041a] border border-[#1f1a54] text-slate-300">Deterministic Tools</span>
              <span className="px-2 py-0.5 rounded bg-[#07041a] border border-[#1f1a54] text-slate-300">Structured Routing</span>
            </div>
          </div>
        </div>
      </section>

      {/* 8. Project Roadmap */}
      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-bold text-[#fbfbfe] tracking-tight flex items-center gap-2">
            <Layers className="w-5 h-5 text-[#dedcff]" />
            Project Roadmap & Development Milestones
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Tracking completed baselines (B1–B4B) and planned analytical evolutions (B5+).
          </p>
        </div>

        <ProjectRoadmap />
      </section>
    </div>
  );
}
