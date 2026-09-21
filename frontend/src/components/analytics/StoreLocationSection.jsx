import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell
} from 'recharts';
import { Store, MapPin, Filter } from 'lucide-react';
import { formatUSDFromCents, formatNumber, formatPercent } from '../../utils/formatters';

export function StoreLocationSection({
  locations = [],
  stores = [],
  selectedLocation = '',
  onLocationChange
}) {
  const locationOptions = [
    { id: '', label: 'All Locations' },
    ...locations.map((loc) => ({
      id: loc.store_location,
      label: loc.store_location
    }))
  ];

  // Location breakdown chart data
  const locationChartData = locations.map((loc) => ({
    name: loc.store_location,
    revenueDollars: loc.revenue_cents / 100,
    revenueCents: loc.revenue_cents,
    profitCents: loc.profit_cents,
    storeCount: loc.store_count,
    unitsSold: loc.units_sold,
    marginPct: loc.gross_margin_pct,
    sharePct: loc.revenue_share_pct
  }));

  const CustomLocationTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload;
      return (
        <div className="p-3 rounded-xl bg-[#07041c]/95 border border-[#1f1a54] shadow-2xl text-xs backdrop-blur-md space-y-1.5 min-w-[210px]">
          <div className="font-semibold text-[#fbfbfe] border-b border-[#1f1a54] pb-1 flex justify-between items-center">
            <span>{d.name} Zoning</span>
            <span className="text-[10px] text-[#dedcff] bg-[#2f27ce]/30 px-1.5 py-0.5 rounded border border-[#433bff]/40">
              {formatPercent(d.sharePct)} Share
            </span>
          </div>

          <div className="space-y-1 pt-0.5">
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Gross Revenue:</span>
              <span className="text-[#dedcff] font-semibold font-mono">
                {formatUSDFromCents(d.revenueCents)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Gross Profit:</span>
              <span className="text-emerald-300 font-semibold font-mono">
                {formatUSDFromCents(d.profitCents)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Stores Count:</span>
              <span className="font-mono text-slate-300">{d.storeCount} stores</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Units Sold:</span>
              <span className="font-mono text-slate-300">{formatNumber(d.unitsSold)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Gross Margin:</span>
              <span className="font-mono text-slate-300">{formatPercent(d.marginPct)}</span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      {/* 1. Location Zoning Performance (5 Cols) */}
      <div className="lg:col-span-5 rounded-xl bg-[#0a0624] border border-[#1f1a54] p-5 shadow-card-glow flex flex-col justify-between">
        <div>
          <div className="text-sm font-semibold text-[#fbfbfe] flex items-center gap-2 mb-1">
            <MapPin className="w-4 h-4 text-[#dedcff]" />
            Location Zoning Breakdown
          </div>
          <div className="text-xs text-slate-400 mb-4">
            Commercial retail performance by store site environment
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={locationChartData}
                margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#1f1a54"
                  opacity={0.5}
                  vertical={false}
                />
                <XAxis
                  dataKey="name"
                  stroke="#64748b"
                  fontSize={10}
                  tickLine={false}
                  axisLine={{ stroke: '#1f1a54' }}
                />
                <YAxis
                  stroke="#64748b"
                  fontSize={10}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v) => `$${(v / 1_000_000).toFixed(0)}M`}
                />
                <Tooltip content={<CustomLocationTooltip />} />
                <Bar
                  dataKey="revenueDollars"
                  radius={[4, 4, 0, 0]}
                  fill="#433bff"
                >
                  {locationChartData.map((entry, index) => (
                    <Cell
                      key={`loc-cell-${index}`}
                      fill={entry.name === 'Downtown' ? '#433bff' : '#2f27ce'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Small location summary pill row */}
        <div className="grid grid-cols-3 gap-2 pt-3 border-t border-[#1f1a54]/60 text-center">
          {locations.slice(0, 3).map((l) => (
            <div key={l.store_location} className="p-1.5 rounded-lg bg-[#07041c] border border-[#1f1a54]">
              <div className="text-[10px] text-slate-400 truncate">{l.store_location}</div>
              <div className="text-xs font-semibold text-[#dedcff] font-mono">
                {formatUSDFromCents(l.revenue_cents, { compact: true })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 2. Top Stores Performance (7 Cols) */}
      <div className="lg:col-span-7 rounded-xl bg-[#0a0624] border border-[#1f1a54] p-5 shadow-card-glow flex flex-col justify-between">
        <div>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
            <div>
              <div className="text-sm font-semibold text-[#fbfbfe] flex items-center gap-2">
                <Store className="w-4 h-4 text-[#dedcff]" />
                Top Performing Stores
              </div>
              <div className="text-xs text-slate-400">
                Ranked retail units across nationwide footprint
              </div>
            </div>

            {/* Filter Dropdown */}
            <div className="relative">
              <select
                value={selectedLocation}
                onChange={(e) => onLocationChange && onLocationChange(e.target.value)}
                className="appearance-none bg-[#07041c] border border-[#1f1a54] text-slate-200 text-xs rounded-lg px-3 py-1.5 pr-7 focus:outline-none focus:border-[#433bff] text-[11px]"
              >
                {locationOptions.map((opt) => (
                  <option key={opt.id} value={opt.id}>
                    {opt.label}
                  </option>
                ))}
              </select>
              <Filter className="w-3 h-3 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          </div>

          {/* Store List */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#1f1a54] text-slate-400 text-[11px]">
                  <th className="pb-2 font-medium pl-1">Store</th>
                  <th className="pb-2 font-medium">City</th>
                  <th className="pb-2 font-medium">Location Type</th>
                  <th className="pb-2 font-medium text-right">Units</th>
                  <th className="pb-2 font-medium text-right">Revenue</th>
                  <th className="pb-2 font-medium text-right pr-1">Gross Profit</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1f1a54]/40">
                {stores.slice(0, 7).map((s) => (
                  <tr key={s.store_id} className="hover:bg-[#130f3b]/40 transition-colors group">
                    <td className="py-2.5 pl-1">
                      <div className="font-medium text-[#fbfbfe] group-hover:text-[#dedcff] transition-colors truncate max-w-[170px]">
                        {s.store_name}
                      </div>
                      <div className="text-[10px] text-slate-500 font-mono">Store #{s.store_id}</div>
                    </td>
                    <td className="py-2.5 text-slate-300 truncate max-w-[110px]">
                      {s.store_city}
                    </td>
                    <td className="py-2.5 text-slate-300">
                      <span className="px-1.5 py-0.5 rounded text-[10px] bg-[#07041c] border border-[#1f1a54]">
                        {s.store_location}
                      </span>
                    </td>
                    <td className="py-2.5 text-right font-mono text-slate-300">
                      {formatNumber(s.units_sold)}
                    </td>
                    <td className="py-2.5 text-right font-mono font-semibold text-[#dedcff]">
                      {formatUSDFromCents(s.revenue_cents)}
                    </td>
                    <td className="py-2.5 text-right font-mono font-medium text-emerald-400 pr-1">
                      {formatUSDFromCents(s.profit_cents)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
