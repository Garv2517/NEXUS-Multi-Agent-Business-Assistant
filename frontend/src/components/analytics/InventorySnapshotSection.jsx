import React from 'react';
import { PackageCheck, AlertTriangle, Boxes, Tag, ShieldAlert, DollarSign } from 'lucide-react';
import { formatUSDFromCents, formatNumber, formatPercent } from '../../utils/formatters';

export function InventorySnapshotSection({
  inventorySummary,
  inventoryProducts = []
}) {
  if (!inventorySummary) return null;

  return (
    <div className="rounded-xl bg-[#0a0624] border border-[#1f1a54] p-5 shadow-card-glow space-y-5">
      {/* Header & Explicit Guardrail 7 Notice */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <div className="text-sm font-semibold text-[#fbfbfe] flex items-center gap-2">
            <Boxes className="w-4 h-4 text-[#dedcff]" />
            External Inventory Position Snapshot
          </div>
          <div className="text-xs text-amber-300/90 font-medium mt-0.5">
            Inventory snapshot date is assumed as Dec 31, 2025 for analytical use.
          </div>
        </div>

        <div className="text-xs text-slate-400">
          Total Store-SKU Placements: <span className="text-[#dedcff] font-mono">{formatNumber(inventorySummary.total_placements)}</span>
        </div>
      </div>

      {/* 4 Key Inventory Snapshot Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="p-3 rounded-lg bg-[#07041c] border border-[#1f1a54] space-y-1">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <PackageCheck className="w-3.5 h-3.5 text-[#dedcff]" />
            Units on Hand
          </div>
          <div className="text-lg font-bold text-[#fbfbfe] font-mono">
            {formatNumber(inventorySummary.total_units_on_hand)}
          </div>
          <div className="text-[11px] text-slate-400">Across 120 retail stores</div>
        </div>

        <div className="p-3 rounded-lg bg-[#07041c] border border-[#1f1a54] space-y-1">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <DollarSign className="w-3.5 h-3.5 text-blue-400" />
            Inventory Cost Basis
          </div>
          <div className="text-lg font-bold text-blue-300 font-mono">
            {formatUSDFromCents(inventorySummary.total_cost_value_cents, { compact: true })}
          </div>
          <div className="text-[11px] text-slate-400">
            {formatUSDFromCents(inventorySummary.total_cost_value_cents)}
          </div>
        </div>

        <div className="p-3 rounded-lg bg-[#07041c] border border-[#1f1a54] space-y-1">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <Tag className="w-3.5 h-3.5 text-emerald-400" />
            Retail Selling Value
          </div>
          <div className="text-lg font-bold text-emerald-300 font-mono">
            {formatUSDFromCents(inventorySummary.total_retail_value_cents, { compact: true })}
          </div>
          <div className="text-[11px] text-slate-400">
            {formatPercent(inventorySummary.potential_gross_margin_pct)} potential margin
          </div>
        </div>

        <div className="p-3 rounded-lg bg-[#07041c] border border-[#1f1a54] space-y-1">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            Out-of-Stock Placements
          </div>
          <div className="text-lg font-bold text-amber-300 font-mono">
            {formatNumber(inventorySummary.out_of_stock_placements ?? inventorySummary.zero_stock_placements)}
          </div>
          <div className="text-[11px] text-slate-400">
            {formatPercent(inventorySummary.stockout_rate_pct)} stockout rate
          </div>
        </div>
      </div>

      {/* Product-Level Inventory Aggregation Table (Descriptive Only) */}
      <div className="pt-2">
        <div className="text-xs font-semibold text-slate-300 mb-2 flex items-center justify-between">
          <span>Top Product Inventory Placements</span>
          <span className="text-[11px] font-normal text-slate-400">Showing top 10 SKUs by stock units</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[#1f1a54] text-slate-400 text-[11px]">
                <th className="pb-2 font-medium pl-1">Product</th>
                <th className="pb-2 font-medium">Category</th>
                <th className="pb-2 font-medium text-right">Stock Units</th>
                <th className="pb-2 font-medium text-right">Store Placements</th>
                <th className="pb-2 font-medium text-right">Zero-Stock Stores</th>
                <th className="pb-2 font-medium text-right">Cost Value</th>
                <th className="pb-2 font-medium text-right pr-1">Retail Value</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1f1a54]/40">
              {inventoryProducts.map((p) => (
                <tr key={p.product_id} className="hover:bg-[#130f3b]/40 transition-colors group">
                  <td className="py-2 pl-1">
                    <div className="font-medium text-[#fbfbfe] group-hover:text-[#dedcff] transition-colors">
                      {p.product_name}
                    </div>
                    <div className="text-[10px] text-slate-500 font-mono">SKU #{p.product_id}</div>
                  </td>
                  <td className="py-2 text-slate-300">
                    <span className="px-1.5 py-0.5 rounded text-[10px] bg-[#07041c] border border-[#1f1a54]">
                      {p.category}
                    </span>
                  </td>
                  <td className="py-2 text-right font-mono font-semibold text-[#dedcff]">
                    {formatNumber(p.stock_units)}
                  </td>
                  <td className="py-2 text-right font-mono text-slate-300">
                    {p.store_placements} stores
                  </td>
                  <td className="py-2 text-right font-mono">
                    {p.zero_stock_store_count > 0 ? (
                      <span className="text-amber-400 font-medium">
                        {p.zero_stock_store_count} stores
                      </span>
                    ) : (
                      <span className="text-slate-500">0</span>
                    )}
                  </td>
                  <td className="py-2 text-right font-mono text-slate-300">
                    {formatUSDFromCents(p.inventory_cost_value_cents)}
                  </td>
                  <td className="py-2 text-right font-mono font-medium text-emerald-400 pr-1">
                    {formatUSDFromCents(p.inventory_retail_value_cents)}
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
