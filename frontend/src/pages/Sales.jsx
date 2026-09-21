import React, { useState, useEffect } from 'react';
import {
  DollarSign,
  Package,
  TrendingUp,
  CreditCard,
  BarChart3,
  Calendar,
  Filter,
  CheckCircle2,
  Clock
} from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { StatCard } from '../components/dashboard/StatCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { getSalesData } from '../services/api';
import { SalesTrendChart } from '../components/charts/SalesTrendChart';
import { TopProductsChart } from '../components/charts/TopProductsChart';

export function Sales() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    getSalesData().then((res) => {
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
          <span>Loading sales intelligence...</span>
        </div>
      </div>
    );
  }

  const { metrics, monthlyRevenueChart, topProducts, recentSales } = data;

  // Maximum value for CSS bar normalization
  const maxRevenue = Math.max(...monthlyRevenueChart.map((d) => d.revenue));

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <PageHeader
        title="Sales Intelligence"
        description="Real-time revenue performance, conversion velocity, and catalog leaders."
        badge="Active Month"
        actions={
          <div className="flex items-center gap-2">
            <span className="px-3 py-1.5 rounded-lg bg-[#0c0827] border border-[#1f1a54] text-xs text-slate-300 flex items-center gap-1.5 font-medium">
              <Calendar className="w-3.5 h-3.5 text-[#dedcff]" />
              Sept 2026
            </span>
          </div>
        }
      />

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Monthly Revenue"
          value={metrics.monthlyRevenue}
          change="+12.4%"
          isPositive={true}
          timeframe="vs prior period"
          icon={DollarSign}
        />
        <StatCard
          title="Units Sold"
          value={metrics.unitsSold}
          change="+8.2%"
          isPositive={true}
          timeframe="248 fulfilled"
          icon={Package}
        />
        <StatCard
          title="Average Order Value"
          value={metrics.averageOrderValue}
          change="+3.6%"
          isPositive={true}
          timeframe="per completed checkout"
          icon={CreditCard}
        />
        <StatCard
          title="Revenue Growth"
          value={metrics.growth}
          change="Strong Momentum"
          isPositive={true}
          timeframe="month-over-month"
          icon={TrendingUp}
        />
      </div>

      {/* Revenue Overview Chart & Top Products */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue Overview Chart (2 columns) */}
        <div className="lg:col-span-2 nexus-card p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-4 mb-4 border-b border-[#1f1a54]/60">
              <div>
                <h3 className="text-sm font-semibold text-[#fbfbfe] flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-[#dedcff]" />
                  Monthly Sales Trend (Last 6 Months)
                </h3>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  Consistent month-over-month trajectory peaking at ₹1,24,500.
                </p>
              </div>
              <span className="text-xs font-mono text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-500/30">
                +51.8% H1 Growth
              </span>
            </div>

            <SalesTrendChart data={monthlyRevenueChart} />
          </div>

          <div className="mt-4 pt-3 border-t border-[#1f1a54]/50 flex items-center justify-between text-[11px] text-slate-400 font-mono">
            <span>Verified from /api/sales</span>
            <span className="text-emerald-400">Peak: ₹1,24,500</span>
          </div>
        </div>

        {/* Top Products Chart (1 column) */}
        <div className="nexus-card p-5 flex flex-col justify-between">
          <div>
            <div className="pb-3 mb-3 border-b border-[#1f1a54]/60">
              <h3 className="text-sm font-semibold text-[#fbfbfe]">
                Top Products
              </h3>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Ranked by revenue contribution.
              </p>
            </div>

            <TopProductsChart data={topProducts} />
          </div>

          <div className="mt-4 pt-3 border-t border-[#1f1a54]/50 flex items-center justify-between text-[11px] text-slate-400 font-mono">
            <span>Top SKU: Laptop Pro</span>
            <span className="text-indigo-300">54% Revenue Share</span>
          </div>
        </div>
      </div>

      {/* Recent Sales Table */}
      <div className="nexus-card p-5">
        <div className="flex items-center justify-between pb-4 mb-4 border-b border-[#1f1a54]/60">
          <div>
            <h3 className="text-sm font-semibold text-[#fbfbfe]">
              Recent Orders & Transactions
            </h3>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Real-time checkout records recorded across channels.
            </p>
          </div>
          <span className="text-xs font-medium text-slate-400">
            5 latest records
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[#1f1a54]/80 text-slate-400 uppercase text-[10px] tracking-wider">
                <th className="pb-3 font-semibold">Order ID</th>
                <th className="pb-3 font-semibold">Customer</th>
                <th className="pb-3 font-semibold">Items</th>
                <th className="pb-3 font-semibold">Amount</th>
                <th className="pb-3 font-semibold">Date</th>
                <th className="pb-3 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1f1a54]/40 text-slate-300">
              {recentSales.map((sale) => (
                <tr key={sale.id} className="hover:bg-[#130f3b]/30 transition-colors">
                  <td className="py-3 font-mono font-medium text-[#dedcff]">
                    {sale.id}
                  </td>
                  <td className="py-3 font-medium text-[#fbfbfe]">
                    {sale.customer}
                  </td>
                  <td className="py-3 text-slate-300">
                    {sale.product}
                  </td>
                  <td className="py-3 font-mono font-semibold text-emerald-400">
                    {sale.amount}
                  </td>
                  <td className="py-3 text-slate-400">
                    {sale.date}
                  </td>
                  <td className="py-3">
                    <StatusBadge status={sale.status} size="xs" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
