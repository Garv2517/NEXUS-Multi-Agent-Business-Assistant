import React, { useState, useEffect, useCallback } from 'react';
import {
  DollarSign,
  TrendingUp,
  Percent,
  ShoppingCart,
  Receipt,
  Store,
  Boxes,
  Package,
  AlertCircle,
  Loader2,
  RefreshCw
} from 'lucide-react';

import {
  getAnalyticsMetadata,
  getAnalyticsSummary,
  getAnalyticsMonthlySales,
  getAnalyticsCategories,
  getAnalyticsProducts,
  getAnalyticsStores,
  getAnalyticsLocations,
  getAnalyticsInventory,
  getAnalyticsInventoryProducts
} from '../services/api';

import { formatUSDFromCents, formatNumber, formatPercent } from '../utils/formatters';
import { DatasetTransparencyBanner } from '../components/analytics/DatasetTransparencyBanner';
import { MonthlyPerformanceChart } from '../components/analytics/MonthlyPerformanceChart';
import { CategoryPerformanceChart } from '../components/analytics/CategoryPerformanceChart';
import { TopProductsTable } from '../components/analytics/TopProductsTable';
import { StoreLocationSection } from '../components/analytics/StoreLocationSection';
import { InventorySnapshotSection } from '../components/analytics/InventorySnapshotSection';

export function BusinessPerformance() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isUnavailable503, setIsUnavailable503] = useState(false);

  // Core Analytical Datasets
  const [metadata, setMetadata] = useState(null);
  const [summary, setSummary] = useState(null);
  const [monthlySales, setMonthlySales] = useState([]);
  const [categories, setCategories] = useState([]);
  const [locations, setLocations] = useState([]);
  const [inventory, setInventory] = useState(null);
  const [inventoryProducts, setInventoryProducts] = useState([]);

  // Filterable product state
  const [products, setProducts] = useState([]);
  const [productOrderBy, setProductOrderBy] = useState('revenue');
  const [productCategory, setProductCategory] = useState('');

  // Filterable store state
  const [stores, setStores] = useState([]);
  const [storeLocation, setStoreLocation] = useState('');

  /**
   * Coordinated fetch on mount:
   * Dispatches parallel independent analytics requests once per page load.
   */
  const loadInitialData = useCallback(async () => {
    setLoading(true);
    setError(null);
    setIsUnavailable503(false);

    try {
      const [
        metaRes,
        summaryRes,
        monthlyRes,
        catRes,
        prodRes,
        storeRes,
        locRes,
        invRes,
        invProdRes
      ] = await Promise.all([
        getAnalyticsMetadata(),
        getAnalyticsSummary(),
        getAnalyticsMonthlySales(),
        getAnalyticsCategories(),
        getAnalyticsProducts({ limit: 10, order_by: 'revenue' }),
        getAnalyticsStores({ limit: 10, order_by: 'revenue' }),
        getAnalyticsLocations(),
        getAnalyticsInventory(),
        getAnalyticsInventoryProducts({ limit: 10, order_by: 'stock_units' })
      ]);

      setMetadata(metaRes);
      setSummary(summaryRes);
      setMonthlySales(monthlyRes.monthly_trend || []);
      setCategories(catRes.categories || []);
      setProducts(prodRes.products || []);
      setStores(storeRes.stores || []);
      setLocations(locRes.locations || []);
      setInventory(invRes);
      setInventoryProducts(invProdRes.products || []);
    } catch (err) {
      console.error("Error loading analytics data:", err);
      const errMsg = err.message || '';
      if (errMsg.includes('503') || errMsg.toLowerCase().includes('unavailable')) {
        setIsUnavailable503(true);
      } else {
        setError(errMsg || "An unexpected error occurred while loading business performance metrics.");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  // Handle product filter updates
  const handleProductSortChange = async (newOrder) => {
    setProductOrderBy(newOrder);
    try {
      const res = await getAnalyticsProducts({
        limit: 10,
        order_by: newOrder,
        category: productCategory || undefined
      });
      setProducts(res.products || []);
    } catch (err) {
      console.error("Failed to re-sort products:", err);
    }
  };

  const handleProductCategoryChange = async (newCategory) => {
    setProductCategory(newCategory);
    try {
      const res = await getAnalyticsProducts({
        limit: 10,
        order_by: productOrderBy,
        category: newCategory || undefined
      });
      setProducts(res.products || []);
    } catch (err) {
      console.error("Failed to filter products by category:", err);
    }
  };

  // Handle store location filter updates
  const handleStoreLocationChange = async (newLocation) => {
    setStoreLocation(newLocation);
    try {
      const res = await getAnalyticsStores({
        limit: 10,
        order_by: 'revenue',
        location: newLocation || undefined
      });
      setStores(res.stores || []);
    } catch (err) {
      console.error("Failed to filter stores by location:", err);
    }
  };

  // Loading Skeleton State
  if (loading) {
    return (
      <div className="p-6 md:p-8 space-y-6 max-w-7xl mx-auto flex flex-col items-center justify-center min-h-[60vh] text-slate-400">
        <Loader2 className="w-8 h-8 animate-spin text-[#433bff] mb-2" />
        <div className="text-sm font-medium text-slate-200">Loading Business Performance Analytics...</div>
        <div className="text-xs text-slate-500">Querying external 2025 retail dataset telemetry</div>
      </div>
    );
  }

  // 503 Analytics Database Unavailable State
  if (isUnavailable503) {
    return (
      <div className="p-6 md:p-8 space-y-6 max-w-7xl mx-auto">
        <div className="rounded-xl bg-amber-950/30 border border-amber-500/40 p-6 text-center space-y-3 shadow-card-glow">
          <div className="w-12 h-12 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center mx-auto">
            <AlertCircle className="w-6 h-6" />
          </div>
          <div className="text-base font-semibold text-amber-200">
            Analytics dataset unavailable
          </div>
          <p className="text-xs text-slate-300 max-w-md mx-auto">
            Analytics dataset unavailable. Rebuild it using the dataset importer.
          </p>
          <div className="pt-2">
            <button
              type="button"
              onClick={loadInitialData}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#2f27ce] hover:bg-[#433bff] text-white text-xs font-medium transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Retry Connection
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Generic Error State
  if (error) {
    return (
      <div className="p-6 md:p-8 space-y-6 max-w-7xl mx-auto">
        <div className="rounded-xl bg-rose-950/30 border border-rose-500/40 p-6 text-center space-y-3 shadow-card-glow">
          <div className="w-12 h-12 rounded-full bg-rose-500/20 text-rose-400 flex items-center justify-center mx-auto">
            <AlertCircle className="w-6 h-6" />
          </div>
          <div className="text-base font-semibold text-rose-200">
            Failed to load business performance data
          </div>
          <p className="text-xs text-slate-300 max-w-md mx-auto">{error}</p>
          <div className="pt-2">
            <button
              type="button"
              onClick={loadInitialData}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#2f27ce] hover:bg-[#433bff] text-white text-xs font-medium transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  // KPI Metrics List
  const kpiItems = summary ? [
    {
      label: 'Gross Revenue',
      value: formatUSDFromCents(summary.total_revenue_cents, { compact: true }),
      fullValue: formatUSDFromCents(summary.total_revenue_cents),
      subtext: 'Jan–Dec 2025',
      icon: DollarSign,
      color: 'text-[#dedcff]',
      bgColor: 'bg-[#433bff]/20'
    },
    {
      label: 'Gross Profit',
      value: formatUSDFromCents(summary.gross_profit_cents, { compact: true }),
      fullValue: formatUSDFromCents(summary.gross_profit_cents),
      subtext: 'After COGS basis',
      icon: TrendingUp,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/20'
    },
    {
      label: 'Gross Margin',
      value: formatPercent(summary.gross_margin_pct),
      subtext: 'Revenue efficiency',
      icon: Percent,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/20'
    },
    {
      label: 'Units Sold',
      value: formatNumber(summary.total_units_sold),
      subtext: 'Across all SKUs',
      icon: ShoppingCart,
      color: 'text-purple-300',
      bgColor: 'bg-purple-500/20'
    },
    {
      label: 'Transactions',
      value: formatNumber(summary.transaction_count),
      subtext: `AOV: ${formatUSDFromCents(summary.average_order_value_cents)}`,
      icon: Receipt,
      color: 'text-indigo-300',
      bgColor: 'bg-indigo-500/20'
    },
    {
      label: 'Store Footprint',
      value: `${summary.store_count}`,
      subtext: 'Active nationwide',
      icon: Store,
      color: 'text-blue-300',
      bgColor: 'bg-blue-500/20'
    },
    {
      label: 'Product Catalog',
      value: `${summary.product_count}`,
      subtext: `${summary.category_count} categories`,
      icon: Package,
      color: 'text-amber-300',
      bgColor: 'bg-amber-500/20'
    },
    {
      label: 'Inventory Units',
      value: formatNumber(summary.inventory_units),
      subtext: 'Dec 31, 2025 snapshot',
      icon: Boxes,
      color: 'text-teal-300',
      bgColor: 'bg-teal-500/20'
    }
  ] : [];

  return (
    <div className="p-4 sm:p-6 md:p-8 space-y-6 max-w-7xl mx-auto">
      {/* 1. Dataset Transparency Banner */}
      <DatasetTransparencyBanner metadata={metadata} />

      {/* 2. Executive KPI Row (8 items in responsive grid) */}
      <div>
        <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2.5 flex items-center gap-2">
          <span>Executive Performance Overview</span>
          <span className="text-[10px] px-2 py-0.5 rounded bg-[#1f1a54] text-slate-300">
            USD Currency
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2.5">
          {kpiItems.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div
                key={idx}
                className="p-3 rounded-xl bg-[#0a0624] border border-[#1f1a54] shadow-card-glow hover:border-[#433bff]/40 transition-colors group flex flex-col justify-between"
                title={item.fullValue || item.value}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] font-medium text-slate-400 truncate uppercase">
                    {item.label}
                  </span>
                  <div className={`w-6 h-6 rounded-md ${item.bgColor} flex items-center justify-center shrink-0`}>
                    <Icon className={`w-3 h-3 ${item.color}`} />
                  </div>
                </div>

                <div>
                  <div className={`text-base font-bold font-mono tracking-tight ${item.color}`}>
                    {item.value}
                  </div>
                  <div className="text-[10px] text-slate-400 truncate mt-0.5">
                    {item.subtext}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 3. Monthly Revenue & Profit Trajectory Chart */}
      <MonthlyPerformanceChart data={monthlySales} />

      {/* 4. Category Performance & Top Products Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-5">
          <CategoryPerformanceChart categories={categories} />
        </div>
        <div className="lg:col-span-7">
          <TopProductsTable
            products={products}
            categories={categories}
            orderBy={productOrderBy}
            onOrderByChange={handleProductSortChange}
            selectedCategory={productCategory}
            onCategoryChange={handleProductCategoryChange}
          />
        </div>
      </div>

      {/* 5. Store & Location Commercial Breakdown */}
      <StoreLocationSection
        locations={locations}
        stores={stores}
        selectedLocation={storeLocation}
        onLocationChange={handleStoreLocationChange}
      />

      {/* 6. External Inventory Snapshot & Product Inventory Table */}
      <InventorySnapshotSection
        inventorySummary={inventory}
        inventoryProducts={inventoryProducts}
      />
    </div>
  );
}
