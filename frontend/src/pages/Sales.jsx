import React, { useEffect, useState } from 'react';
import {
  DollarSign,
  Package,
  TrendingUp,
  CreditCard,
  BarChart3,
  Percent,
  AlertCircle,
  RefreshCw
} from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { StatCard } from '../components/dashboard/StatCard';
import { UnifiedDataSourceBar } from '../components/common/UnifiedDataSourceBar';
import { getSalesData } from '../services/api';
import { SalesTrendChart } from '../components/charts/SalesTrendChart';
import { TopProductsChart } from '../components/charts/TopProductsChart';
import { formatNumber, formatPercent, formatUSDFromCents } from '../utils/formatters';

export function Sales() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await getSalesData());
    } catch (err) {
      setError(err.message || 'Failed to load sales analytics.');
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
          <span>Loading unified Kaggle sales intelligence...</span>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 sm:p-8 max-w-5xl mx-auto">
        <div className="nexus-card p-6 border-rose-500/30 text-center">
          <AlertCircle className="w-7 h-7 text-rose-400 mx-auto mb-2" />
          <div className="text-sm font-semibold text-[#fbfbfe]">Sales analytics unavailable</div>
          <div className="text-xs text-slate-400 mt-1">{error}</div>
          <button onClick={load} className="mt-4 px-3 py-2 rounded-lg bg-[#2f27ce] text-white text-xs inline-flex items-center gap-2">
            <RefreshCw className="w-3.5 h-3.5" /> Retry
          </button>
        </div>
      </div>
    );
  }

  const { metrics, monthlyRevenueChart, topProducts, categories, metadata } = data;
  const peakMonth = monthlyRevenueChart.reduce(
    (best, item) => (!best || item.revenue > best.revenue ? item : best),
    null
  );
  const topProduct = topProducts[0];

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <PageHeader
        title="Sales Intelligence"
        description="Unified 2025 retail sales, product performance, profitability, and category contribution from the Kaggle analytics dataset."
        badge="External Analytics · USD"
      />

      <UnifiedDataSourceBar metadata={metadata} />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Gross Revenue"
          value={formatUSDFromCents(metrics.grossRevenueCents, { compact: true })}
          change={`${metrics.monthlyChangePct >= 0 ? '+' : ''}${metrics.monthlyChangePct.toFixed(2)}%`}
          isPositive={metrics.monthlyChangePct >= 0}
          timeframe="Dec vs Nov 2025"
          icon={DollarSign}
        />
        <StatCard
          title="Units Sold"
          value={formatNumber(metrics.unitsSold)}
          change={formatNumber(metrics.transactions)}
          isNeutral={true}
          timeframe="sales line items"
          icon={Package}
        />
        <StatCard
          title="Gross Profit"
          value={formatUSDFromCents(metrics.grossProfitCents, { compact: true })}
          change={formatPercent(metrics.grossMarginPct)}
          isPositive={true}
          timeframe="gross margin"
          icon={TrendingUp}
        />
        <StatCard
          title="Average Order Value"
          value={formatUSDFromCents(metrics.averageOrderValueCents)}
          change="USD"
          isNeutral={true}
          timeframe="per transaction line"
          icon={CreditCard}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 nexus-card p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-4 mb-4 border-b border-[#1f1a54]/60 gap-3">
              <div>
                <h3 className="text-sm font-semibold text-[#fbfbfe] flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-[#dedcff]" />
                  Monthly Revenue · Jan–Dec 2025
                </h3>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  All twelve months are aggregated directly from 245,800 source sales rows.
                </p>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/40 border border-emerald-500/30 text-emerald-300">
                /api/analytics/monthly-sales
              </span>
            </div>
            <SalesTrendChart data={monthlyRevenueChart} />
          </div>

          <div className="mt-4 pt-3 border-t border-[#1f1a54]/50 flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-400 font-mono">
            <span>Currency: USD</span>
            {peakMonth && <span className="text-emerald-400">Peak month: {peakMonth.month} · {new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(peakMonth.revenue)}</span>}
          </div>
        </div>

        <div className="nexus-card p-5 flex flex-col justify-between">
          <div>
            <div className="pb-3 mb-3 border-b border-[#1f1a54]/60">
              <h3 className="text-sm font-semibold text-[#fbfbfe]">Top Products</h3>
              <p className="text-[11px] text-slate-400 mt-0.5">Ranked by verified 2025 gross revenue.</p>
            </div>
            <TopProductsChart data={topProducts} />
          </div>

          {topProduct && (
            <div className="mt-4 pt-3 border-t border-[#1f1a54]/50 text-[11px] text-slate-400 font-mono">
              <div className="text-[#dedcff] truncate">Top SKU: {topProduct.name}</div>
              <div className="text-emerald-400 mt-0.5">{topProduct.sharePct.toFixed(2)}% company revenue share</div>
            </div>
          )}
        </div>
      </div>

      <div className="nexus-card p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 mb-4 border-b border-[#1f1a54]/60">
          <div>
            <h3 className="text-sm font-semibold text-[#fbfbfe] flex items-center gap-2">
              <Percent className="w-4 h-4 text-[#dedcff]" />
              Category Performance
            </h3>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Revenue, units, profit and margin across all 16 merchandise categories.
            </p>
          </div>
          <span className="text-[10px] text-slate-400 font-mono">{categories.length} categories</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[#1f1a54]/80 text-slate-400 uppercase text-[10px] tracking-wider">
                <th className="pb-3 font-semibold">Category</th>
                <th className="pb-3 font-semibold text-right">Products</th>
                <th className="pb-3 font-semibold text-right">Units</th>
                <th className="pb-3 font-semibold text-right">Revenue</th>
                <th className="pb-3 font-semibold text-right">Gross Profit</th>
                <th className="pb-3 font-semibold text-right">Margin</th>
                <th className="pb-3 font-semibold text-right">Revenue Share</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1f1a54]/40 text-slate-300">
              {categories.map((cat) => (
                <tr key={cat.category} className="hover:bg-[#130f3b]/30 transition-colors">
                  <td className="py-3 font-medium text-[#fbfbfe]">{cat.category}</td>
                  <td className="py-3 text-right font-mono">{formatNumber(cat.product_count)}</td>
                  <td className="py-3 text-right font-mono">{formatNumber(cat.units_sold)}</td>
                  <td className="py-3 text-right font-mono text-emerald-400">{formatUSDFromCents(cat.revenue_cents)}</td>
                  <td className="py-3 text-right font-mono">{formatUSDFromCents(cat.profit_cents)}</td>
                  <td className="py-3 text-right font-mono">{formatPercent(cat.gross_margin_pct)}</td>
                  <td className="py-3 text-right font-mono text-[#dedcff]">{formatPercent(cat.revenue_share_pct)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
