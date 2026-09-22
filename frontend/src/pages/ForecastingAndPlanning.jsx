import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { AlertCircle, RefreshCw, Loader2, TrendingUp, DollarSign, CalendarRange, Gauge } from 'lucide-react';
import { getForecastConfig, getCompanyForecast, getCategoryForecasts, getForecastCoverage } from '../services/api';
import { formatNumber, formatUSDFromCents } from '../utils/formatters';
import { ForecastTransparencyBanner } from '../components/forecast/ForecastTransparencyBanner';
import { CompanyForecastChart } from '../components/forecast/CompanyForecastChart';
import { CategoryForecastTable } from '../components/forecast/CategoryForecastTable';
import { DemandCoverageSection } from '../components/forecast/DemandCoverageSection';

export function ForecastingAndPlanning() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [config, setConfig] = useState(null);
  const [company, setCompany] = useState(null);
  const [categories, setCategories] = useState([]);
  const [coverage, setCoverage] = useState(null);

  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const [cfg, comp, cats, cov] = await Promise.all([
        getForecastConfig(), getCompanyForecast(), getCategoryForecasts(), getForecastCoverage()
      ]);
      setConfig(cfg); setCompany(comp); setCategories(cats.categories || []); setCoverage(cov);
    } catch (err) {
      setError(err?.message || 'Unable to load forecasting analytics.');
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const unitForecasts = useMemo(() => company?.units?.points?.filter((p) => p.kind === 'forecast') || [], [company]);
  const revenueForecasts = useMemo(() => company?.revenue?.points?.filter((p) => p.kind === 'forecast') || [], [company]);
  const fourWeekUnits = unitForecasts.reduce((s, p) => s + p.value, 0);
  const fourWeekRevenue = revenueForecasts.reduce((s, p) => s + p.value, 0);

  if (loading) return <div className="p-8 min-h-[60vh] flex flex-col items-center justify-center text-slate-400"><Loader2 className="w-8 h-8 animate-spin text-[#433bff] mb-3"/><div className="text-sm text-slate-200">Calibrating forecast view...</div><div className="text-xs mt-1">Loading complete-week demand series</div></div>;

  if (error) return <div className="p-6 md:p-8 max-w-7xl mx-auto"><div className="nexus-card p-6 text-center border-rose-500/30 bg-rose-950/20"><AlertCircle className="w-8 h-8 text-rose-400 mx-auto mb-3"/><div className="text-sm font-semibold text-rose-200">Forecasting data unavailable</div><div className="text-xs text-slate-400 mt-2">{error}</div><button onClick={load} className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#2f27ce] text-white text-xs"><RefreshCw className="w-3.5 h-3.5"/>Retry</button></div></div>;

  const kpis = [
    { label: 'Next 4W Units', value: formatNumber(fourWeekUnits), sub: `${company?.units?.model_used || '-'} · ${(company?.units?.validation_wape * 100 || 0).toFixed(2)}% WAPE`, icon: TrendingUp },
    { label: 'Next 4W Revenue', value: formatUSDFromCents(fourWeekRevenue, { compact: true }), sub: `${company?.revenue?.model_used || '-'} · ${(company?.revenue?.validation_wape * 100 || 0).toFixed(2)}% WAPE`, icon: DollarSign },
    { label: 'Forecast Horizon', value: '4 weeks', sub: `Starts ${company?.first_forecast_week || '-'}`, icon: CalendarRange },
    { label: 'Category Reliability', value: `${categories.filter((c) => c.validation_reliability === 'Strong').length}/16 Strong`, sub: `${categories.filter((c) => c.validation_reliability === 'Limited').length} Limited`, icon: Gauge },
  ];

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <div><span className="text-xs font-semibold uppercase tracking-wider text-[#a5a0ff]">Intelligence</span><h1 className="text-2xl lg:text-3xl font-bold text-[#fbfbfe] mt-1">Forecasting & Demand Planning</h1><p className="text-sm text-slate-400 mt-1">Validated 4-week demand forecasts and stock coverage planning from the unified retail analytics dataset.</p></div>
      <ForecastTransparencyBanner config={config} />
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">{kpis.map(({label,value,sub,icon:Icon}) => <div key={label} className="nexus-card p-4"><div className="flex items-center justify-between"><span className="text-[11px] text-slate-400">{label}</span><Icon className="w-4 h-4 text-[#dedcff]"/></div><div className="text-xl font-bold text-white mt-2">{value}</div><div className="text-[10px] text-slate-500 mt-1">{sub}</div></div>)}</div>
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6"><CompanyForecastChart title="Company Unit Demand" series={company?.units}/><CompanyForecastChart title="Company Revenue Forecast" series={company?.revenue}/></div>
      <CategoryForecastTable data={categories} />
      <DemandCoverageSection data={coverage} />
      <div className="text-center text-[10px] text-slate-500 pb-4">Forecasts are model outputs from a synthetic 2025 retail dataset, not known future facts. No annual seasonality is claimed from one year of history.</div>
    </div>
  );
}
