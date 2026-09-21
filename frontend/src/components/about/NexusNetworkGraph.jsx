import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  MessageCircle,
  Brain,
  TrendingUp,
  Package,
  Users,
  Wrench,
  Database,
  ArrowDown,
  Info,
  Sparkles,
  CheckCircle2,
  Cpu
} from 'lucide-react';

const NODE_DETAILS = {
  user: {
    title: 'Enterprise User',
    role: 'Client Interface',
    type: 'Entry Point',
    description: 'Submits natural language business questions via the Chat Assistant or dashboard queries.',
    capabilities: [
      'Interactive Natural Language Chat',
      'Preset Suggested Queries',
      'Real-time Multi-Agent Trace Inspection',
      'Direct Business Dashboard Access'
    ],
    accent: 'border-slate-500/40 text-slate-200 bg-slate-900/60'
  },
  manager: {
    title: 'Nexus Manager Agent',
    role: 'Central Orchestrator',
    type: 'Foundry / Deterministic',
    description: 'Decomposes user inquiries, maps validated NexusIntents, constructs execution plans, and synthesizes multi-agent responses.',
    capabilities: [
      'Intent Selection (GPT-5-mini / Deterministic)',
      'Workflow Coordination & Plan Generation',
      'Context Passing Between Domain Specialists',
      'Graceful Fallback Routing'
    ],
    accent: 'border-[#433bff] text-[#dedcff] bg-[#2f27ce]/20'
  },
  sales: {
    title: 'Sales Agent',
    role: 'Specialist Component',
    type: 'Domain Specialist',
    description: 'Dedicated business specialist managing revenue calculations, periodic sales velocity, and product ranking.',
    capabilities: [
      'Gross Revenue Calculation',
      'Monthly Sales Trajectory & History',
      'Top-Selling Products Identification',
      'Average Order Value & Volume Metrics'
    ],
    accent: 'border-emerald-500/40 text-emerald-300 bg-emerald-950/40'
  },
  inventory: {
    title: 'Inventory Agent',
    role: 'Specialist Component',
    type: 'Domain Specialist',
    description: 'Dedicated warehouse specialist monitoring stock thresholds, replenishment alerts, and inventory health.',
    capabilities: [
      'Product Stock Level Lookup',
      'Low-Stock Detection (< Reorder Level)',
      'Out-of-Stock Emergency Flagging',
      'Warehouse Distribution & Inventory Summary'
    ],
    accent: 'border-amber-500/40 text-amber-300 bg-amber-950/40'
  },
  people: {
    title: 'People Management Agent',
    role: 'Specialist Component',
    type: 'Domain Specialist',
    description: 'Workforce intelligence specialist managing employee census records, leave schedules, and company policies.',
    capabilities: [
      'Workforce Census & Headcount Summary',
      'Employee Attendance & Active Leave Details',
      'Company Policy & Guideline Retrieval',
      'Organizational Department Structure'
    ],
    accent: 'border-sky-500/40 text-sky-300 bg-sky-950/40'
  },
  tools: {
    title: 'Deterministic Tools Layer',
    role: 'Execution Engine',
    type: 'Deterministic Python',
    description: 'Strict, parameter-validated business functions that interface directly with transactional repositories.',
    capabilities: [
      'sales_tools (get_total_sales, get_top_products, get_sales_trend)',
      'inventory_tools (get_inventory_summary, get_low_stock_products)',
      'hr_tools (get_employee_summary, get_hr_policy, list_all_policies)',
      'activity_tools (log_activity, get_recent_activity)'
    ],
    accent: 'border-purple-500/40 text-purple-300 bg-purple-950/40'
  },
  db: {
    title: 'SQLite Business Database',
    role: 'Source of Truth',
    type: 'Relational Database',
    description: 'Embedded, persistent transactional database storing verified orders, products, inventory, and employee records.',
    capabilities: [
      'Structured Relational Schema',
      'Zero-Latency Local Querying',
      'Atomic Transaction Integrity',
      'Single Source of Factual Truth'
    ],
    accent: 'border-blue-500/40 text-blue-300 bg-blue-950/40'
  }
};

export function NexusNetworkGraph() {
  const [selectedNode, setSelectedNode] = useState('manager');

  const activeDetail = NODE_DETAILS[selectedNode] || NODE_DETAILS.manager;

  const nodeVariants = {
    hidden: { opacity: 0, y: 15 },
    visible: (custom) => ({
      opacity: 1,
      y: 0,
      transition: { delay: custom * 0.1, duration: 0.4, ease: 'easeOut' }
    })
  };

  return (
    <div className="space-y-6">
      {/* Network Canvas Card */}
      <div className="nexus-card p-4 sm:p-6 lg:p-8 relative overflow-hidden bg-gradient-to-b from-[#090623] to-[#050315] border-[#1f1a54]">
        {/* Subtle decorative grid background */}
        <div
          className="absolute inset-0 opacity-[0.03] pointer-events-none"
          style={{
            backgroundImage: `radial-gradient(#dedcff 1px, transparent 1px)`,
            backgroundSize: '24px 24px'
          }}
        />

        <div className="max-w-4xl mx-auto flex flex-col items-center relative z-10 space-y-6">
          {/* LEVEL 1: USER NODE */}
          <motion.div
            custom={0}
            variants={nodeVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            onClick={() => setSelectedNode('user')}
            onMouseEnter={() => setSelectedNode('user')}
            className={`cursor-pointer px-4 py-3 rounded-xl border flex items-center gap-3 transition-all duration-200 shadow-md ${
              selectedNode === 'user'
                ? 'bg-[#15103b] border-[#433bff] shadow-card-glow scale-105'
                : 'bg-[#0a0727] border-[#1f1a54] hover:border-[#433bff]/50'
            }`}
          >
            <div className="w-8 h-8 rounded-lg bg-slate-800/80 border border-slate-700 flex items-center justify-center text-slate-200">
              <MessageCircle className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs font-semibold text-[#fbfbfe]">Enterprise User</div>
              <div className="text-[10px] text-slate-400 font-mono">Inquiry Ingestion</div>
            </div>
          </motion.div>

          {/* CONNECTOR 1: User -> Manager */}
          <div className="w-px h-6 bg-gradient-to-b from-slate-500/60 to-[#433bff] relative">
            <div className="w-1.5 h-1.5 rounded-full bg-[#433bff] absolute top-1/2 -left-[2.5px] animate-pulse" />
          </div>

          {/* LEVEL 2: NEXUS MANAGER NODE */}
          <motion.div
            custom={1}
            variants={nodeVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            onClick={() => setSelectedNode('manager')}
            onMouseEnter={() => setSelectedNode('manager')}
            className={`cursor-pointer px-5 py-3.5 rounded-2xl border flex items-center gap-3.5 transition-all duration-200 shadow-lg ${
              selectedNode === 'manager'
                ? 'bg-[#191147] border-[#433bff] shadow-card-glow scale-105 ring-2 ring-[#433bff]/30'
                : 'bg-[#0f0b35] border-[#2f27ce]/60 hover:border-[#433bff]'
            }`}
          >
            <div className="w-10 h-10 rounded-xl bg-[#2f27ce] border border-[#433bff] flex items-center justify-center text-white shadow-subtle-glow">
              <Brain className="w-5 h-5 text-[#dedcff]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-[#fbfbfe] tracking-tight">Nexus Manager Agent</span>
                <span className="text-[9px] px-1.5 py-0.2 rounded font-mono font-semibold bg-[#433bff]/30 border border-[#433bff]/40 text-[#dedcff]">
                  HUB
                </span>
              </div>
              <div className="text-[11px] text-slate-300 font-mono mt-0.5">
                Multi-Agent Routing & Synthesis
              </div>
            </div>
          </motion.div>

          {/* CONNECTOR 2: Manager branching to 3 Specialists */}
          <div className="w-full max-w-2xl relative flex flex-col items-center">
            {/* Vertical stem */}
            <div className="w-px h-5 bg-[#433bff]/70" />
            {/* Horizontal crossbar */}
            <div className="w-4/5 h-px bg-gradient-to-r from-emerald-500/60 via-[#433bff] to-sky-500/60" />
            {/* Three drop lines */}
            <div className="w-4/5 flex justify-between">
              <div className="w-px h-5 bg-emerald-500/70" />
              <div className="w-px h-5 bg-amber-500/70" />
              <div className="w-px h-5 bg-sky-500/70" />
            </div>
          </div>

          {/* LEVEL 3: THREE SPECIALISTS ROW */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 w-full max-w-3xl">
            {/* Sales Agent Node */}
            <motion.div
              custom={2}
              variants={nodeVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              onClick={() => setSelectedNode('sales')}
              onMouseEnter={() => setSelectedNode('sales')}
              className={`cursor-pointer p-4 rounded-xl border flex flex-col items-start gap-2.5 transition-all duration-200 ${
                selectedNode === 'sales'
                  ? 'bg-emerald-950/40 border-emerald-400 shadow-card-glow scale-105'
                  : 'bg-[#0a0727] border-[#1f1a54] hover:border-emerald-500/50'
              }`}
            >
              <div className="w-full flex items-center justify-between">
                <div className="w-8 h-8 rounded-lg bg-emerald-950/60 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
                  <TrendingUp className="w-4 h-4" />
                </div>
                <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-500/30">
                  Sales
                </span>
              </div>
              <div>
                <div className="text-xs font-semibold text-[#fbfbfe]">Sales Agent</div>
                <div className="text-[10px] text-slate-400 mt-0.5">Revenue & Orders</div>
              </div>
            </motion.div>

            {/* Inventory Agent Node */}
            <motion.div
              custom={3}
              variants={nodeVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              onClick={() => setSelectedNode('inventory')}
              onMouseEnter={() => setSelectedNode('inventory')}
              className={`cursor-pointer p-4 rounded-xl border flex flex-col items-start gap-2.5 transition-all duration-200 ${
                selectedNode === 'inventory'
                  ? 'bg-amber-950/40 border-amber-400 shadow-card-glow scale-105'
                  : 'bg-[#0a0727] border-[#1f1a54] hover:border-amber-500/50'
              }`}
            >
              <div className="w-full flex items-center justify-between">
                <div className="w-8 h-8 rounded-lg bg-amber-950/60 border border-amber-500/40 flex items-center justify-center text-amber-400">
                  <Package className="w-4 h-4" />
                </div>
                <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-amber-950/60 text-amber-300 border border-amber-500/30">
                  Inventory
                </span>
              </div>
              <div>
                <div className="text-xs font-semibold text-[#fbfbfe]">Inventory Agent</div>
                <div className="text-[10px] text-slate-400 mt-0.5">Stock & Warehouse</div>
              </div>
            </motion.div>

            {/* People Management Agent Node */}
            <motion.div
              custom={4}
              variants={nodeVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              onClick={() => setSelectedNode('people')}
              onMouseEnter={() => setSelectedNode('people')}
              className={`cursor-pointer p-4 rounded-xl border flex flex-col items-start gap-2.5 transition-all duration-200 ${
                selectedNode === 'people'
                  ? 'bg-sky-950/40 border-sky-400 shadow-card-glow scale-105'
                  : 'bg-[#0a0727] border-[#1f1a54] hover:border-sky-500/50'
              }`}
            >
              <div className="w-full flex items-center justify-between">
                <div className="w-8 h-8 rounded-lg bg-sky-950/60 border border-sky-500/40 flex items-center justify-center text-sky-400">
                  <Users className="w-4 h-4" />
                </div>
                <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-sky-950/60 text-sky-300 border border-sky-500/30">
                  People
                </span>
              </div>
              <div>
                <div className="text-xs font-semibold text-[#fbfbfe]">People Management</div>
                <div className="text-[10px] text-slate-400 mt-0.5">Census & Policies</div>
              </div>
            </motion.div>
          </div>

          {/* CONNECTOR 3: Specialists converging to Tools */}
          <div className="w-full max-w-2xl relative flex flex-col items-center">
            {/* Three converging lines */}
            <div className="w-4/5 flex justify-between">
              <div className="w-px h-5 bg-emerald-500/70" />
              <div className="w-px h-5 bg-amber-500/70" />
              <div className="w-px h-5 bg-sky-500/70" />
            </div>
            {/* Horizontal collector bar */}
            <div className="w-4/5 h-px bg-gradient-to-r from-emerald-500/60 via-[#433bff] to-sky-500/60" />
            {/* Center drop line to Tools */}
            <div className="w-px h-5 bg-[#433bff]/80" />
          </div>

          {/* LEVEL 4: DETERMINISTIC TOOLS LAYER */}
          <motion.div
            custom={5}
            variants={nodeVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            onClick={() => setSelectedNode('tools')}
            onMouseEnter={() => setSelectedNode('tools')}
            className={`cursor-pointer px-4 sm:px-6 py-3 rounded-xl border flex items-center gap-3 transition-all duration-200 w-full max-w-md justify-center ${
              selectedNode === 'tools'
                ? 'bg-purple-950/40 border-purple-400 shadow-card-glow scale-105'
                : 'bg-[#0a0727] border-[#1f1a54] hover:border-purple-500/50'
            }`}
          >
            <div className="w-8 h-8 rounded-lg bg-purple-950/60 border border-purple-500/40 flex items-center justify-center text-purple-300 shrink-0">
              <Wrench className="w-4 h-4" />
            </div>
            <div className="text-left">
              <div className="text-xs font-semibold text-[#fbfbfe]">Deterministic Business Tools</div>
              <div className="text-[10px] text-purple-300 font-mono">sales_tools | inventory_tools | hr_tools</div>
            </div>
          </motion.div>

          {/* CONNECTOR 4: Tools -> SQLite */}
          <div className="w-px h-5 bg-gradient-to-b from-purple-500/80 to-blue-500/80" />

          {/* LEVEL 5: SQLITE DATABASE */}
          <motion.div
            custom={6}
            variants={nodeVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            onClick={() => setSelectedNode('db')}
            onMouseEnter={() => setSelectedNode('db')}
            className={`cursor-pointer px-4 sm:px-6 py-3 rounded-xl border flex items-center gap-3 transition-all duration-200 w-full max-w-sm justify-center ${
              selectedNode === 'db'
                ? 'bg-blue-950/40 border-blue-400 shadow-card-glow scale-105'
                : 'bg-[#080520] border-[#1f1a54] hover:border-blue-500/50'
            }`}
          >
            <div className="w-8 h-8 rounded-lg bg-blue-950/60 border border-blue-500/40 flex items-center justify-center text-blue-300 shrink-0">
              <Database className="w-4 h-4" />
            </div>
            <div className="text-left">
              <div className="text-xs font-semibold text-[#fbfbfe]">SQLite Business Database</div>
              <div className="text-[10px] text-blue-300 font-mono">Persistent Relational Store</div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Interactive Node Capability Inspector */}
      <div className="nexus-card p-5 border-[#1f1a54] bg-[#080520]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 mb-3 border-b border-[#1f1a54]/60 gap-2">
          <div className="flex items-center gap-2">
            <Info className="w-4 h-4 text-[#dedcff]" />
            <h4 className="text-sm font-semibold text-[#fbfbfe]">
              Architecture Node Inspector: <span className="text-[#dedcff]">{activeDetail.title}</span>
            </h4>
          </div>
          <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-[#16113c] border border-[#1f1a54] text-slate-300 self-start sm:self-auto">
            {activeDetail.type} &bull; {activeDetail.role}
          </span>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed mb-4">
          {activeDetail.description}
        </p>

        <div>
          <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 mb-2">
            Verified Node Responsibilities & Capabilities
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {activeDetail.capabilities.map((cap, idx) => (
              <div
                key={idx}
                className="flex items-center gap-2 text-xs text-slate-300 p-2 rounded-lg bg-[#0c0827] border border-[#1f1a54]/60"
              >
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span className="font-mono text-[11px]">{cap}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
