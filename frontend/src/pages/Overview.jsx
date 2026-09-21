import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  DollarSign,
  ShoppingCart,
  AlertTriangle,
  Users,
  Sparkles,
  ArrowRight,
  TrendingUp,
  Package,
  Brain,
  Layers,
  Clock,
  CheckCircle2
} from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { StatCard } from '../components/dashboard/StatCard';
import { getDashboardData } from '../services/api';

const ICON_MAP = {
  TrendingUp,
  Package,
  Brain
};

export function Overview() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    getDashboardData().then((res) => {
      if (isMounted) {
        setData(res);
        setLoading(false);
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  if (loading || !data) {
    return (
      <div className="p-6 sm:p-8 flex items-center justify-center min-h-[50vh]">
        <div className="flex items-center gap-2 text-slate-400 text-xs">
          <div className="w-4 h-4 rounded-full border-2 border-[#433bff] border-t-transparent animate-spin" />
          <span>Loading executive metrics...</span>
        </div>
      </div>
    );
  }

  const { metrics, businessSummary, recentActivity } = data;

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Top Heading */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-semibold text-[#dedcff] tracking-wider uppercase">
            Good morning
          </span>
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold tracking-tight text-[#fbfbfe] mt-0.5">
            Here's what is happening across your business.
          </h1>
        </div>

        <button
          type="button"
          onClick={() => navigate('/assistant')}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#2f27ce] hover:bg-[#433bff] text-white text-xs sm:text-sm font-medium transition-all shadow-subtle-glow group self-start sm:self-auto cursor-pointer"
        >
          <Sparkles className="w-4 h-4 text-[#dedcff]" />
          <span>Ask Nexus</span>
          <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Revenue"
          value={metrics.revenue.value}
          change={metrics.revenue.change}
          isPositive={metrics.revenue.isPositive}
          timeframe={metrics.revenue.timeframe}
          icon={DollarSign}
        />
        <StatCard
          title="Orders"
          value={metrics.orders.value}
          change={metrics.orders.change}
          isPositive={metrics.orders.isPositive}
          timeframe={metrics.orders.timeframe}
          icon={ShoppingCart}
        />
        <StatCard
          title="Low Stock"
          value={metrics.lowStock.value}
          change={metrics.lowStock.change}
          isWarning={metrics.lowStock.isWarning}
          timeframe={metrics.lowStock.timeframe}
          icon={AlertTriangle}
        />
        <StatCard
          title="Employees"
          value={metrics.employees.value}
          change={metrics.employees.change}
          isNeutral={metrics.employees.isNeutral}
          timeframe={metrics.employees.timeframe}
          icon={Users}
        />
      </div>

      {/* Business Summary AI Banner */}
      <div className="nexus-card p-6 relative overflow-hidden bg-gradient-to-br from-[#0c0827] via-[#0e0a33] to-[#120c3d] border-[#1f1a54]">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-5">
          <div className="space-y-2 max-w-3xl">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#433bff] animate-pulse" />
              <span className="text-xs font-semibold uppercase tracking-wider text-[#dedcff]">
                Executive Business Summary
              </span>
              <span className="text-[10px] text-slate-400 font-mono">
                {businessSummary.generatedAt}
              </span>
            </div>

            <p className="text-sm sm:text-base text-[#fbfbfe] font-medium leading-relaxed">
              "{businessSummary.headline}"
            </p>

            <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px] text-slate-400">
              <span>Synthesized by:</span>
              {businessSummary.agentsInvolved.map((agent, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 rounded-md bg-[#1f1a54]/60 text-[#dedcff] font-medium border border-[#433bff]/20"
                >
                  {agent} Agent
                </span>
              ))}
              <span className="text-emerald-400 font-mono ml-1">
                Confidence: {businessSummary.confidence}
              </span>
            </div>
          </div>

          <button
            type="button"
            onClick={() => navigate('/assistant')}
            className="px-4 py-2.5 rounded-xl bg-[#2f27ce]/40 hover:bg-[#2f27ce] border border-[#433bff]/40 text-white text-xs sm:text-sm font-medium transition-all flex items-center justify-center gap-2 shrink-0 group shadow-card-glow"
          >
            <Sparkles className="w-4 h-4 text-[#dedcff]" />
            <span>Ask Nexus</span>
            <ArrowRight className="w-3.5 h-3.5 text-[#dedcff] group-hover:translate-x-0.5 transition-transform" />
          </button>
        </div>
      </div>

      {/* Two-Column Section: Recent AI Activity & Quick Prompts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent AI Activity (2 columns) */}
        <div className="lg:col-span-2 nexus-card p-5">
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-[#1f1a54]/60">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-[#dedcff]" />
              <h3 className="text-sm font-semibold text-[#fbfbfe]">
                Recent AI Activity
              </h3>
            </div>
            <button
              type="button"
              onClick={() => navigate('/activity')}
              className="text-xs text-[#dedcff] hover:text-white flex items-center gap-1 font-medium transition-colors"
            >
              View Full Audit Log
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-3">
            {recentActivity.map((item) => {
              const Icon = ICON_MAP[item.icon] || Brain;
              return (
                <div
                  key={item.id}
                  className="p-3 rounded-xl bg-[#080520] border border-[#1f1a54]/70 flex items-center justify-between gap-3 hover:border-[#433bff]/40 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-[#2f27ce]/20 border border-[#1f1a54] flex items-center justify-center text-[#dedcff] shrink-0">
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-[#fbfbfe]">
                        {item.agent}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-0.5">
                        {item.action}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 text-right">
                    <span className="text-[11px] text-slate-400 font-mono flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {item.timeAgo}
                    </span>
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Quick Multi-Agent Assist Launcher (1 column) */}
        <div className="nexus-card p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 pb-3 border-b border-[#1f1a54]/60 mb-4">
              <Brain className="w-4 h-4 text-[#dedcff]" />
              <h3 className="text-sm font-semibold text-[#fbfbfe]">
                Multi-Agent Dispatch
              </h3>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              The Nexus Manager Agent automatically routes complex inquiries across Sales, Inventory, and People Management systems.
            </p>

            <div className="space-y-2">
              <button
                type="button"
                onClick={() => navigate('/assistant')}
                className="w-full text-left p-2.5 rounded-lg bg-[#080520] hover:bg-[#120d3a] border border-[#1f1a54] text-xs text-slate-300 hover:text-white transition-colors flex items-center justify-between"
              >
                <span>Compare top products vs stock</span>
                <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
              </button>
              <button
                type="button"
                onClick={() => navigate('/assistant')}
                className="w-full text-left p-2.5 rounded-lg bg-[#080520] hover:bg-[#120d3a] border border-[#1f1a54] text-xs text-slate-300 hover:text-white transition-colors flex items-center justify-between"
              >
                <span>Review Q3 sales velocity</span>
                <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
              </button>
              <button
                type="button"
                onClick={() => navigate('/assistant')}
                className="w-full text-left p-2.5 rounded-lg bg-[#080520] hover:bg-[#120d3a] border border-[#1f1a54] text-xs text-slate-300 hover:text-white transition-colors flex items-center justify-between"
              >
                <span>Check low inventory alerts</span>
                <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
              </button>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[#1f1a54]/60 text-[10px] text-slate-400 flex items-center justify-between">
            <span>Powered by Azure AI Models</span>
            <span className="text-emerald-400">Mesh Active</span>
          </div>
        </div>
      </div>
    </div>
  );
}
