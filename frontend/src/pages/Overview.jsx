import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  DollarSign,
  Receipt,
  AlertTriangle,
  Users,
  ArrowRight,
  TrendingUp,
  Package,
  Brain,
  Layers,
  Clock,
  CheckCircle2,
  BarChart3,
  ShieldAlert,
  CalendarRange,
  AlertCircle,
  RefreshCw
} from 'lucide-react';
import { StatCard } from '../components/dashboard/StatCard';
import { UnifiedDataSourceBar } from '../components/common/UnifiedDataSourceBar';
import { getDashboardData } from '../services/api';
import { SalesTrendChart } from '../components/charts/SalesTrendChart';
import { formatNumber, formatUSDFromCents } from '../utils/formatters';

const ICON_MAP = { TrendingUp, Package, Brain };

export function Overview() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await getDashboardData());
    } catch (err) {
      setError(err.message || 'Failed to load overview data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  if (loading) {
    return (
      <div className="p-6 sm:p-8 flex items-center justify-center min-h-[50vh]">
        <div className="flex items-center gap-2 text-slate-400 text-xs">
          <div className="w-4 h-4 rounded-full border-2 border-[#433bff] border-t-transparent animate-spin" />
          <span>Loading unified business overview...</span>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 sm:p-8 max-w-5xl mx-auto">
        <div className="nexus-card p-6 border-rose-500/30 text-center">
          <AlertCircle className="w-7 h-7 text-rose-400 mx-auto mb-2" />
          <div className="text-sm font-semibold text-[#fbfbfe]">Overview unavailable</div>
          <div className="text-xs text-slate-400 mt-1">{error}</div>
          <button onClick={load} className="mt-4 px-3 py-2 rounded-lg bg-[#2f27ce] text-white text-xs inline-flex items-center gap-2">
            <RefreshCw className="w-3.5 h-3.5" /> Retry
          </button>
        </div>
      </div>
    );
  }

  const { metrics, businessSummary, recentActivity, monthlyRevenueChart, metadata } = data;

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-semibold text-[#dedcff] tracking-wider uppercase">Unified Business Overview</span>
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold tracking-tight text-[#fbfbfe] mt-0.5">
            One retail dataset across sales, inventory, performance, risk and forecasting.
          </h1>
        </div>

        <button
          type="button"
          onClick={() => navigate('/performance')}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#2f27ce] hover:bg-[#433bff] text-white text-xs sm:text-sm font-medium transition-all shadow-subtle-glow group self-start sm:self-auto"
        >
          <BarChart3 className="w-4 h-4 text-[#dedcff]" />
          <span>Business Performance</span>
          <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
        </button>
      </div>

      <UnifiedDataSourceBar metadata={metadata} />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Gross Revenue"
          value={formatUSDFromCents(metrics.revenue.valueCents, { compact: true })}
          change={`${metrics.revenue.changePct >= 0 ? '+' : ''}${metrics.revenue.changePct.toFixed(2)}%`}
          isPositive={metrics.revenue.changePct >= 0}
          timeframe="Dec vs Nov 2025"
          icon={DollarSign}
        />
        <StatCard
          title="Transactions"
          value={formatNumber(metrics.transactions.value)}
          change="2025"
          isNeutral={true}
          timeframe={metrics.transactions.timeframe}
          icon={Receipt}
        />
        <StatCard
          title="Zero-Stock Placements"
          value={formatNumber(metrics.stockouts.value)}
          change="Review exposure"
          isWarning={true}
          timeframe={metrics.stockouts.timeframe}
          icon={AlertTriangle}
        />
        <StatCard
          title="Employees"
          value={formatNumber(metrics.employees.value)}
          change="Internal HR"
          isNeutral={true}
          timeframe={metrics.employees.timeframe}
          icon={Users}
        />
      </div>

      <div className="nexus-card p-6 relative overflow-hidden bg-gradient-to-br from-[#0c0827] via-[#0e0a33] to-[#120c3d] border-[#1f1a54]">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-5">
          <div className="space-y-2 max-w-3xl">
            <div className="flex flex-wrap items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              <span className="text-xs font-semibold uppercase tracking-wider text-[#dedcff]">Verified Business Summary</span>
              <span className="text-[10px] text-slate-400 font-mono">{businessSummary.generatedAt}</span>
            </div>

            <p className="text-sm sm:text-base text-[#fbfbfe] font-medium leading-relaxed">{businessSummary.headline}</p>

            <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px] text-slate-400">
              <span>Data domains:</span>
              {businessSummary.dataSources.map((source) => (
                <span key={source} className="px-2 py-0.5 rounded-md bg-[#1f1a54]/60 text-[#dedcff] font-medium border border-[#433bff]/20">
                  {source}
                </span>
              ))}
              <span className="text-emerald-400 font-mono ml-1">{businessSummary.status}</span>
            </div>
          </div>

          <button
            type="button"
            onClick={() => navigate('/performance')}
            className="px-4 py-2.5 rounded-xl bg-[#2f27ce]/40 hover:bg-[#2f27ce] border border-[#433bff]/40 text-white text-xs sm:text-sm font-medium transition-all flex items-center justify-center gap-2 shrink-0 group shadow-card-glow"
          >
            <span>Explore Analytics</span>
            <ArrowRight className="w-3.5 h-3.5 text-[#dedcff] group-hover:translate-x-0.5 transition-transform" />
          </button>
        </div>
      </div>

      <div className="nexus-card p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 mb-3 border-b border-[#1f1a54]/60 gap-2">
          <div>
            <h3 className="text-sm font-semibold text-[#fbfbfe] flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-[#dedcff]" />
              2025 Revenue Trajectory
            </h3>
            <p className="text-[11px] text-slate-400 mt-0.5">Twelve-month USD revenue from the same dataset used by Sales, Risk and Forecasting.</p>
          </div>
          <span className="self-start sm:self-auto text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/60 border border-emerald-500/30 text-emerald-400">
            /api/analytics/monthly-sales
          </span>
        </div>
        <SalesTrendChart data={monthlyRevenueChart} compact />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 nexus-card p-5">
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-[#1f1a54]/60">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-[#dedcff]" />
              <h3 className="text-sm font-semibold text-[#fbfbfe]">Recent AI Activity</h3>
            </div>
            <button
              type="button"
              onClick={() => navigate('/activity')}
              className="text-xs text-[#dedcff] hover:text-white flex items-center gap-1 font-medium transition-colors"
            >
              View Full Audit Log <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-3">
            {recentActivity.length === 0 && (
              <div className="text-xs text-slate-500 py-6 text-center">No agent activity has been recorded yet.</div>
            )}
            {recentActivity.map((item) => {
              const Icon = ICON_MAP[item.icon] || Brain;
              return (
                <div key={item.id} className="p-3 rounded-xl bg-[#080520] border border-[#1f1a54]/70 flex items-center justify-between gap-3 hover:border-[#433bff]/40 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-[#2f27ce]/20 border border-[#1f1a54] flex items-center justify-center text-[#dedcff] shrink-0">
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-[#fbfbfe]">{item.agent}</div>
                      <div className="text-[11px] text-slate-400 mt-0.5">{item.action}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 text-right">
                    <span className="text-[11px] text-slate-400 font-mono flex items-center gap-1">
                      <Clock className="w-3 h-3" /> {item.timeAgo}
                    </span>
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="nexus-card p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 pb-3 border-b border-[#1f1a54]/60 mb-4">
              <Brain className="w-4 h-4 text-[#dedcff]" />
              <h3 className="text-sm font-semibold text-[#fbfbfe]">Intelligence Shortcuts</h3>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              These views all operate on the same USA Toy Sales analytics dataset.
            </p>

            <div className="space-y-2">
              <button onClick={() => navigate('/performance')} className="w-full text-left p-2.5 rounded-lg bg-[#080520] hover:bg-[#120d3a] border border-[#1f1a54] text-xs text-slate-300 hover:text-white transition-colors flex items-center justify-between">
                <span className="flex items-center gap-2"><BarChart3 className="w-3.5 h-3.5" /> Business Performance</span><ArrowRight className="w-3.5 h-3.5 text-slate-500" />
              </button>
              <button onClick={() => navigate('/risk')} className="w-full text-left p-2.5 rounded-lg bg-[#080520] hover:bg-[#120d3a] border border-[#1f1a54] text-xs text-slate-300 hover:text-white transition-colors flex items-center justify-between">
                <span className="flex items-center gap-2"><ShieldAlert className="w-3.5 h-3.5" /> Insights & Risk</span><ArrowRight className="w-3.5 h-3.5 text-slate-500" />
              </button>
              <button onClick={() => navigate('/forecast')} className="w-full text-left p-2.5 rounded-lg bg-[#080520] hover:bg-[#120d3a] border border-[#1f1a54] text-xs text-slate-300 hover:text-white transition-colors flex items-center justify-between">
                <span className="flex items-center gap-2"><CalendarRange className="w-3.5 h-3.5" /> Forecasting & Planning</span><ArrowRight className="w-3.5 h-3.5 text-slate-500" />
              </button>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[#1f1a54]/60 text-[10px] text-slate-400 flex items-center justify-between">
            <span>Unified retail analytics</span>
            <span className="text-emerald-400">USD · 2025</span>
          </div>
        </div>
      </div>
    </div>
  );
}
