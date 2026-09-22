import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Package,
  AlertTriangle,
  Boxes,
  DollarSign,
  Search,
  ShieldAlert,
  ArrowRight,
  AlertCircle,
  RefreshCw,
  Store
} from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { StatCard } from '../components/dashboard/StatCard';
import { UnifiedDataSourceBar } from '../components/common/UnifiedDataSourceBar';
import { getInventoryData } from '../services/api';
import { InventoryHealthChart } from '../components/charts/InventoryHealthChart';
import { formatNumber, formatPercent, formatUSDFromCents } from '../utils/formatters';

const FILTERS = ['All', 'Stockout Exposure', 'Fully In Stock'];

export function Inventory() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await getInventoryData());
    } catch (err) {
      setError(err.message || 'Failed to load inventory analytics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const filteredProducts = useMemo(() => {
    if (!data) return [];
    const q = searchTerm.trim().toLowerCase();
    return data.products.filter((p) => {
      const matchesSearch = !q ||
        p.name.toLowerCase().includes(q) ||
        String(p.id).includes(q) ||
        p.category.toLowerCase().includes(q);
      const matchesStatus = statusFilter === 'All' || p.exposureStatus === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [data, searchTerm, statusFilter]);

  if (loading) {
    return (
      <div className="p-6 sm:p-8 flex items-center justify-center min-h-[50vh]">
        <div className="flex items-center gap-2 text-slate-400 text-xs">
          <div className="w-4 h-4 rounded-full border-2 border-[#433bff] border-t-transparent animate-spin" />
          <span>Loading unified Kaggle inventory...</span>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 sm:p-8 max-w-5xl mx-auto">
        <div className="nexus-card p-6 border-rose-500/30 text-center">
          <AlertCircle className="w-7 h-7 text-rose-400 mx-auto mb-2" />
          <div className="text-sm font-semibold text-[#fbfbfe]">Inventory analytics unavailable</div>
          <div className="text-xs text-slate-400 mt-1">{error}</div>
          <button onClick={load} className="mt-4 px-3 py-2 rounded-lg bg-[#2f27ce] text-white text-xs inline-flex items-center gap-2">
            <RefreshCw className="w-3.5 h-3.5" /> Retry
          </button>
        </div>
      </div>
    );
  }

  const { metrics, products, stockoutExposure, metadata } = data;

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <PageHeader
        title="Inventory Management"
        description="Unified product stock, store placements, valuation, and stockout exposure from the Kaggle retail inventory snapshot."
        badge="External Analytics · USD"
        actions={
          <button
            type="button"
            onClick={() => navigate('/risk')}
            className="px-3 py-1.5 rounded-xl bg-[#2f27ce] hover:bg-[#433bff] text-white text-xs font-medium flex items-center gap-1.5 shadow-subtle-glow transition-all"
          >
            <ShieldAlert className="w-3.5 h-3.5 text-[#dedcff]" />
            <span>Open Risk Analysis</span>
          </button>
        }
      />

      <UnifiedDataSourceBar metadata={metadata} inventory />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Stock Units"
          value={formatNumber(metrics.totalStockUnits)}
          change={`${formatNumber(metrics.totalProducts)} products`}
          isNeutral={true}
          timeframe="across all stores"
          icon={Boxes}
        />
        <StatCard
          title="Inventory Cost Value"
          value={formatUSDFromCents(metrics.costValueCents, { compact: true })}
          change={formatUSDFromCents(metrics.retailValueCents, { compact: true })}
          isNeutral={true}
          timeframe="retail value"
          icon={DollarSign}
        />
        <StatCard
          title="Out-of-Stock Placements"
          value={formatNumber(metrics.outOfStockPlacements)}
          change={formatPercent(metrics.stockoutRatePct)}
          isWarning={true}
          timeframe="of store-SKU placements"
          icon={AlertTriangle}
        />
        <StatCard
          title="Store-SKU Placements"
          value={formatNumber(metrics.totalPlacements)}
          change={formatNumber(metrics.inStockPlacements)}
          isPositive={true}
          timeframe="currently in stock"
          icon={Store}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="nexus-card p-5 flex flex-col justify-between">
          <div>
            <div className="pb-3 mb-3 border-b border-[#1f1a54]/60">
              <h3 className="text-sm font-semibold text-[#fbfbfe]">Inventory Placement Status</h3>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Point-in-time store-product placement availability. No reorder thresholds are invented.
              </p>
            </div>
            <InventoryHealthChart data={metrics} />
          </div>
          <div className="mt-3 pt-2.5 border-t border-[#1f1a54]/50 text-[10px] text-slate-500 font-mono">
            Snapshot date is assumed as {metrics.snapshotDate} for analytical use.
          </div>
        </div>

        <div className="lg:col-span-2 nexus-card p-5 border-rose-500/30 bg-gradient-to-br from-rose-950/15 via-[#0c0827] to-[#0c0827]">
          <div className="flex items-start gap-3.5 mb-4 pb-4 border-b border-[#1f1a54]/60">
            <div className="w-10 h-10 rounded-xl bg-rose-500/15 border border-rose-500/30 flex items-center justify-center text-rose-300 shrink-0 mt-0.5">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm sm:text-base font-semibold text-[#fbfbfe]">Current Stockout Exposure</h4>
              <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
                {formatNumber(stockoutExposure.zero_stock_placements)} zero-stock placements affect {formatNumber(stockoutExposure.affected_products_count)} products across {formatNumber(stockoutExposure.affected_stores_count)} stores and all {formatNumber(stockoutExposure.affected_categories_count)} categories.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="p-3 rounded-lg bg-[#050315] border border-[#1f1a54]">
              <div className="text-[10px] uppercase tracking-wider text-slate-500">Historical Revenue Associated</div>
              <div className="text-base font-bold font-mono text-[#fbfbfe] mt-1">{formatUSDFromCents(stockoutExposure.historical_revenue_associated_cents)}</div>
            </div>
            <div className="p-3 rounded-lg bg-[#050315] border border-[#1f1a54]">
              <div className="text-[10px] uppercase tracking-wider text-slate-500">Historical Units Sold</div>
              <div className="text-base font-bold font-mono text-[#fbfbfe] mt-1">{formatNumber(stockoutExposure.historical_units_sold)}</div>
            </div>
            <div className="p-3 rounded-lg bg-[#050315] border border-[#1f1a54]">
              <div className="text-[10px] uppercase tracking-wider text-slate-500">Revenue Share</div>
              <div className="text-base font-bold font-mono text-[#fbfbfe] mt-1">{formatPercent(stockoutExposure.historical_revenue_share_pct)}</div>
            </div>
          </div>

          <p className="text-[10px] text-slate-500 mt-3 leading-relaxed">
            Historical revenue associated is descriptive context for store-product pairs that currently have zero stock. It is not a measure of lost sales.
          </p>

          <div className="mt-4 pt-4 border-t border-[#1f1a54]/60 flex items-center justify-between gap-3">
            <span className="text-xs text-slate-400">Detailed pressure, DOS and slow-moving analysis is available in Insights & Risk.</span>
            <button
              type="button"
              onClick={() => navigate('/risk')}
              className="px-3.5 py-2 rounded-lg bg-rose-500/15 hover:bg-rose-500/25 border border-rose-500/30 text-rose-200 text-xs font-medium flex items-center gap-2 shrink-0 transition-colors"
            >
              Review Risk
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      <div className="nexus-card p-5">
        <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-3 pb-4 mb-4 border-b border-[#1f1a54]/60">
          <div>
            <h3 className="text-sm font-semibold text-[#fbfbfe]">Product Inventory Registry</h3>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Aggregated product inventory across store placements; sorted by total stock units.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search product ID, name or category..."
                className="pl-8 pr-3 py-1.5 rounded-lg bg-[#080520] border border-[#1f1a54] text-xs text-[#fbfbfe] placeholder-slate-500 focus:outline-none focus:border-[#433bff] w-full sm:w-64"
              />
            </div>

            <div className="flex items-center gap-1 bg-[#080520] p-1 rounded-lg border border-[#1f1a54] text-xs overflow-x-auto">
              {FILTERS.map((f) => (
                <button
                  key={f}
                  type="button"
                  onClick={() => setStatusFilter(f)}
                  className={`px-2 py-0.5 rounded text-[11px] font-medium whitespace-nowrap transition-colors ${
                    statusFilter === f ? 'bg-[#2f27ce] text-white' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[#1f1a54]/80 text-slate-400 uppercase text-[10px] tracking-wider">
                <th className="pb-3 font-semibold">Product ID</th>
                <th className="pb-3 font-semibold">Product</th>
                <th className="pb-3 font-semibold">Category</th>
                <th className="pb-3 font-semibold text-right">Stock Units</th>
                <th className="pb-3 font-semibold text-right">Placements</th>
                <th className="pb-3 font-semibold text-right">Zero-Stock Stores</th>
                <th className="pb-3 font-semibold text-right">Cost Value</th>
                <th className="pb-3 font-semibold text-right">Retail Value</th>
                <th className="pb-3 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1f1a54]/40 text-slate-300">
              {filteredProducts.map((prod) => (
                <tr key={prod.id} className="hover:bg-[#130f3b]/30 transition-colors">
                  <td className="py-3 font-mono font-medium text-[#dedcff]">{prod.id}</td>
                  <td className="py-3 font-medium text-[#fbfbfe]">{prod.name}</td>
                  <td className="py-3 text-slate-400">{prod.category}</td>
                  <td className="py-3 text-right font-mono">{formatNumber(prod.stockUnits)}</td>
                  <td className="py-3 text-right font-mono">{formatNumber(prod.storePlacements)}</td>
                  <td className={`py-3 text-right font-mono ${prod.zeroStockStores > 0 ? 'text-rose-300 font-semibold' : 'text-emerald-400'}`}>
                    {formatNumber(prod.zeroStockStores)}
                  </td>
                  <td className="py-3 text-right font-mono">{formatUSDFromCents(prod.costValueCents)}</td>
                  <td className="py-3 text-right font-mono text-emerald-400">{formatUSDFromCents(prod.retailValueCents)}</td>
                  <td className="py-3">
                    <span className={`px-2 py-1 rounded-full text-[10px] font-semibold border ${
                      prod.zeroStockStores > 0
                        ? 'bg-rose-950/30 border-rose-500/30 text-rose-300'
                        : 'bg-emerald-950/30 border-emerald-500/30 text-emerald-300'
                    }`}>
                      {prod.exposureStatus}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-3 text-[10px] text-slate-500 font-mono">
          Showing {filteredProducts.length} of {products.length} products · No reorder levels are available in the Kaggle source dataset.
        </div>
      </div>
    </div>
  );
}
