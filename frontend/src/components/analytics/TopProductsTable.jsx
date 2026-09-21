import React from 'react';
import { Package, ArrowUpDown, Filter } from 'lucide-react';
import { formatUSDFromCents, formatNumber, formatPercent } from '../../utils/formatters';

export function TopProductsTable({
  products = [],
  categories = [],
  orderBy = 'revenue',
  onOrderByChange,
  selectedCategory = '',
  onCategoryChange
}) {
  const sortOptions = [
    { id: 'revenue', label: 'Revenue' },
    { id: 'units', label: 'Units Sold' },
    { id: 'profit', label: 'Gross Profit' },
    { id: 'margin', label: 'Gross Margin' }
  ];

  return (
    <div className="rounded-xl bg-[#0a0624] border border-[#1f1a54] p-5 shadow-card-glow flex flex-col justify-between">
      {/* Header controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-4">
        <div>
          <div className="text-sm font-semibold text-[#fbfbfe] flex items-center gap-2">
            <Package className="w-4 h-4 text-[#dedcff]" />
            Top Products Performance
          </div>
          <div className="text-xs text-slate-400">
            Ranked SKU commercial performance across the retail catalog
          </div>
        </div>

        {/* Controls: Ranking Metric Selector + Category Filter */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Metric Sort Pills */}
          <div className="flex items-center rounded-lg bg-[#07041c] p-0.5 border border-[#1f1a54] text-xs">
            {sortOptions.map((opt) => (
              <button
                key={opt.id}
                type="button"
                onClick={() => onOrderByChange && onOrderByChange(opt.id)}
                className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition-all ${
                  orderBy === opt.id
                    ? 'bg-[#2f27ce] text-[#fbfbfe] shadow-subtle-glow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>

          {/* Category Dropdown Filter */}
          <div className="relative">
            <select
              value={selectedCategory}
              onChange={(e) => onCategoryChange && onCategoryChange(e.target.value)}
              className="appearance-none bg-[#07041c] border border-[#1f1a54] text-slate-200 text-xs rounded-lg px-3 py-1.5 pr-7 focus:outline-none focus:border-[#433bff] text-[11px]"
            >
              <option value="">All Categories</option>
              {categories.map((c) => (
                <option key={c.category || c} value={c.category || c}>
                  {c.category || c}
                </option>
              ))}
            </select>
            <Filter className="w-3 h-3 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>
        </div>
      </div>

      {/* Table view */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-[#1f1a54] text-slate-400 text-[11px]">
              <th className="pb-2.5 font-medium pl-1">#</th>
              <th className="pb-2.5 font-medium">Product / SKU</th>
              <th className="pb-2.5 font-medium">Category</th>
              <th className="pb-2.5 font-medium text-right">Unit Price</th>
              <th className="pb-2.5 font-medium text-right">Units Sold</th>
              <th className="pb-2.5 font-medium text-right">Gross Revenue</th>
              <th className="pb-2.5 font-medium text-right">Gross Profit</th>
              <th className="pb-2.5 font-medium text-right pr-1">Margin</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1f1a54]/40">
            {products.length === 0 ? (
              <tr>
                <td colSpan="8" className="py-6 text-center text-slate-500 text-xs">
                  No products match the selected criteria.
                </td>
              </tr>
            ) : (
              products.map((prod, idx) => (
                <tr key={prod.product_id} className="hover:bg-[#130f3b]/40 transition-colors group">
                  <td className="py-2.5 pl-1 font-mono text-[11px] text-slate-500">
                    {idx + 1}
                  </td>
                  <td className="py-2.5">
                    <div className="font-medium text-[#fbfbfe] group-hover:text-[#dedcff] transition-colors">
                      {prod.product_name}
                    </div>
                    <div className="text-[10px] text-slate-500 font-mono">
                      ID: {prod.product_id}
                    </div>
                  </td>
                  <td className="py-2.5 text-slate-300">
                    <span className="px-2 py-0.5 rounded text-[10px] bg-[#07041c] border border-[#1f1a54]">
                      {prod.product_category}
                    </span>
                  </td>
                  <td className="py-2.5 text-right font-mono text-slate-300">
                    {formatUSDFromCents(prod.product_price_cents)}
                  </td>
                  <td className="py-2.5 text-right font-mono text-slate-300">
                    {formatNumber(prod.units_sold)}
                  </td>
                  <td className="py-2.5 text-right font-mono font-semibold text-[#dedcff]">
                    {formatUSDFromCents(prod.revenue_cents)}
                  </td>
                  <td className="py-2.5 text-right font-mono font-medium text-emerald-400">
                    {formatUSDFromCents(prod.profit_cents)}
                  </td>
                  <td className="py-2.5 text-right font-mono text-slate-300 pr-1">
                    {formatPercent(prod.gross_margin_pct)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
