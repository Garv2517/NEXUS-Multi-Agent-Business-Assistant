import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine } from 'recharts';
import { formatNumber, formatUSDFromCents } from '../../utils/formatters';

function shortWeek(iso) {
  const d = new Date(`${iso}T00:00:00`);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function ForecastTooltip({ active, payload, label, valueUnit }) {
  if (!active || !payload?.length) return null;
  const row = payload[0]?.payload;
  const value = row?.value ?? 0;
  return (
    <div className="rounded-lg border border-[#2d2760] bg-[#080520] px-3 py-2 shadow-xl text-[11px]">
      <div className="text-slate-400 mb-1">Week of {label}</div>
      <div className="text-white font-semibold">{valueUnit === 'cents' ? formatUSDFromCents(value) : `${formatNumber(value)} units`}</div>
      <div className={`mt-1 ${row?.kind === 'forecast' ? 'text-[#a5a0ff]' : 'text-emerald-400'}`}>{row?.kind === 'forecast' ? `Forecast · H${row?.horizon}` : 'Historical actual'}</div>
      {row?.historical_mae_reference != null && (
        <div className="text-slate-500 mt-1">Historical MAE reference: ±{valueUnit === 'cents' ? formatUSDFromCents(row.historical_mae_reference) : `${Math.round(row.historical_mae_reference)} units`}</div>
      )}
    </div>
  );
}

export function CompanyForecastChart({ title, series }) {
  if (!series?.points?.length) return null;
  const data = series.points.map((p) => ({ ...p, label: shortWeek(p.week_start) }));
  const firstForecast = data.find((p) => p.kind === 'forecast')?.label;
  return (
    <div className="nexus-card p-5">
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2 mb-4">
        <div>
          <h3 className="text-sm font-semibold text-[#fbfbfe]">{title}</h3>
          <p className="text-[11px] text-slate-400 mt-1">Model: <span className="text-[#dedcff] font-medium">{series.model_used}</span> · Validation WAPE {(series.validation_wape * 100).toFixed(2)}% · {series.validation_reliability}</p>
        </div>
        <span className="text-[10px] rounded-md px-2 py-1 border border-[#433bff]/30 bg-[#433bff]/10 text-[#dedcff]">Actual → Forecast</span>
      </div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f1a54" vertical={false} />
            <XAxis dataKey="label" tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={{ stroke: '#1f1a54' }} tickLine={false} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={(v) => series.value_unit === 'cents' ? formatUSDFromCents(v, { compact: true, decimals: 1 }) : formatNumber(v)} width={62} />
            <Tooltip content={<ForecastTooltip valueUnit={series.value_unit} />} />
            {firstForecast && <ReferenceLine x={firstForecast} stroke="#a5a0ff" strokeDasharray="4 4" label={{ value: 'Forecast', fill: '#a5a0ff', fontSize: 10, position: 'insideTopLeft' }} />}
            <Line type="monotone" dataKey="value" stroke="#433bff" strokeWidth={2.2} dot={(props) => {
              const { cx, cy, payload } = props;
              return <circle cx={cx} cy={cy} r={payload.kind === 'forecast' ? 4 : 2.5} fill={payload.kind === 'forecast' ? '#dedcff' : '#433bff'} stroke="#050315" strokeWidth={1.5} />;
            }} activeDot={{ r: 5 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-3 text-[10px] text-slate-500">Historical MAE references are empirical validation errors, not confidence or prediction intervals.</div>
    </div>
  );
}
