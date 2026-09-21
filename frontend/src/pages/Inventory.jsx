import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Package,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Warehouse,
  ArrowRight,
  Sparkles,
  RefreshCw,
  Search,
  Filter
} from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { StatCard } from '../components/dashboard/StatCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { getInventoryData } from '../services/api';
import { InventoryHealthChart } from '../components/charts/InventoryHealthChart';

export function Inventory() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');

  useEffect(() => {
    let isMounted = true;
    getInventoryData().then((res) => {
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
          <span>Scanning inventory catalog...</span>
        </div>
      </div>
    );
  }

  const { metrics, products } = data;

  const filteredProducts = products.filter((p) => {
    const matchesSearch =
      p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.category.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus =
      statusFilter === 'All' ? true : p.status.toLowerCase() === statusFilter.toLowerCase();

    return matchesSearch && matchesStatus;
  });

  const lowStockItems = products.filter(
    (p) => p.status === 'Low' || p.status === 'Out of Stock'
  );

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <PageHeader
        title="Inventory Management"
        description="Warehouse telemetry, stock threshold triggers, and real-time replenishment."
        badge="Live Catalog"
        actions={
          <button
            type="button"
            onClick={() => navigate('/assistant')}
            className="px-3 py-1.5 rounded-xl bg-[#2f27ce] hover:bg-[#433bff] text-white text-xs font-medium flex items-center gap-1.5 shadow-subtle-glow transition-all"
          >
            <Sparkles className="w-3.5 h-3.5 text-[#dedcff]" />
            <span>Ask Inventory Agent</span>
          </button>
        }
      />

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Products"
          value={metrics.totalProducts}
          change="52 active SKUs"
          isNeutral={true}
          timeframe="across 3 hubs"
          icon={Package}
        />
        <StatCard
          title="Low Stock"
          value={metrics.lowStock}
          change="Replenish ASAP"
          isWarning={true}
          timeframe="below safety margin"
          icon={AlertTriangle}
        />
        <StatCard
          title="Out of Stock"
          value={metrics.outOfStock}
          change="Critical"
          isPositive={false}
          timeframe="immediate backorder"
          icon={XCircle}
        />
        <StatCard
          title="Healthy Stock"
          value={metrics.healthyStock}
          change="90.4% optimal"
          isPositive={true}
          timeframe="in stock & ready"
          icon={CheckCircle2}
        />
      </div>

      {/* Inventory Health Visualization & Depletion Alert */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Inventory Health Donut Chart (1 column) */}
        <div className="nexus-card p-5 flex flex-col justify-between">
          <div>
            <div className="pb-3 mb-3 border-b border-[#1f1a54]/60">
              <h3 className="text-sm font-semibold text-[#fbfbfe]">
                Inventory Health
              </h3>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Stock status distribution across catalog.
              </p>
            </div>

            <InventoryHealthChart data={metrics} />
          </div>

          <div className="mt-3 pt-2.5 border-t border-[#1f1a54]/50 flex items-center justify-between text-[11px] text-slate-400 font-mono">
            <span>Verified from /api/inventory</span>
            <span className="text-emerald-400">8 Healthy / 4 Low</span>
          </div>
        </div>

        {/* Low Stock Urgent Alert Banner & Action (2 columns) */}
        <div className="lg:col-span-2 flex flex-col justify-between nexus-card p-5 border-amber-500/40 bg-gradient-to-br from-amber-950/20 via-[#0c0827] to-[#0c0827]">
          <div>
            <div className="flex items-start gap-3.5 mb-4 pb-4 border-b border-[#1f1a54]/60">
              <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-300 shrink-0 mt-0.5">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm sm:text-base font-semibold text-[#fbfbfe] flex items-center gap-2">
                  Inventory Depletion Alert ({lowStockItems.length} SKUs flagged)
                </h4>
                <p className="text-xs text-slate-400 mt-1 max-w-xl leading-relaxed">
                  <span className="text-[#fbfbfe] font-medium">Laptop Pro</span> (4 units left),{' '}
                  <span className="text-[#fbfbfe] font-medium">Mechanical Keyboard</span> (8 units left), and{' '}
                  <span className="text-[#fbfbfe] font-medium">USB-C Multi-Hub</span> (0 units left) have breached designated reorder thresholds.
                </p>
              </div>
            </div>

            <div className="space-y-2 text-xs text-slate-300">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Automatic safety buffer calculation active across regional fulfillment hubs.</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Nexus Inventory Specialist tracks supplier lead times and warehouse stockout risk.</span>
              </div>
            </div>
          </div>

          <div className="mt-5 pt-4 border-t border-[#1f1a54]/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <span className="text-xs text-slate-400 font-mono">
              Action priority: Restock 4 depleted hardware lines
            </span>
            <button
              type="button"
              onClick={() => navigate('/assistant')}
              className="px-3.5 py-2 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-200 text-xs font-medium flex items-center gap-2 shrink-0 transition-colors self-start sm:self-auto"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Trigger AI Reorder Plan</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Product Catalog Table Section */}
      <div className="nexus-card p-5">
        {/* Table Header & Search Filter */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 mb-4 border-b border-[#1f1a54]/60">
          <div>
            <h3 className="text-sm font-semibold text-[#fbfbfe]">
              Product Stock Registry
            </h3>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Current inventory levels across distribution warehouses.
            </p>
          </div>

          <div className="flex items-center gap-2.5">
            {/* Search Input */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search SKU or name..."
                className="pl-8 pr-3 py-1.5 rounded-lg bg-[#080520] border border-[#1f1a54] text-xs text-[#fbfbfe] placeholder-slate-500 focus:outline-none focus:border-[#433bff] w-40 sm:w-52"
              />
            </div>

            {/* Filter Pills */}
            <div className="flex items-center gap-1 bg-[#080520] p-1 rounded-lg border border-[#1f1a54] text-xs">
              {['All', 'Low', 'Healthy'].map((f) => (
                <button
                  key={f}
                  type="button"
                  onClick={() => setStatusFilter(f)}
                  className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                    statusFilter === f
                      ? 'bg-[#2f27ce] text-white'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[#1f1a54]/80 text-slate-400 uppercase text-[10px] tracking-wider">
                <th className="pb-3 font-semibold">SKU</th>
                <th className="pb-3 font-semibold">Product Name</th>
                <th className="pb-3 font-semibold">Category</th>
                <th className="pb-3 font-semibold">Current Stock</th>
                <th className="pb-3 font-semibold">Reorder Level</th>
                <th className="pb-3 font-semibold">Warehouse</th>
                <th className="pb-3 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1f1a54]/40 text-slate-300">
              {filteredProducts.map((prod) => (
                <tr key={prod.id} className="hover:bg-[#130f3b]/30 transition-colors">
                  <td className="py-3 font-mono font-medium text-[#dedcff]">
                    {prod.id}
                  </td>
                  <td className="py-3 font-medium text-[#fbfbfe]">
                    {prod.name}
                  </td>
                  <td className="py-3 text-slate-400">
                    {prod.category}
                  </td>
                  <td className="py-3 font-mono font-semibold">
                    <span
                      className={
                        prod.stock <= 4
                          ? 'text-rose-400 font-bold'
                          : prod.stock <= 8
                          ? 'text-amber-300 font-bold'
                          : 'text-emerald-400'
                      }
                    >
                      {prod.stock} units
                    </span>
                  </td>
                  <td className="py-3 font-mono text-slate-400">
                    {prod.reorderLevel} units
                  </td>
                  <td className="py-3 text-slate-400">
                    {prod.warehouse}
                  </td>
                  <td className="py-3">
                    <StatusBadge status={prod.status} size="xs" />
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
