import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Users,
  Calendar,
  Building2,
  FileText,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  Clock,
  Search
} from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { StatCard } from '../components/dashboard/StatCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { getHRData } from '../services/api';

export function HR() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    let isMounted = true;
    getHRData().then((res) => {
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
          <span>Loading workforce telemetry...</span>
        </div>
      </div>
    );
  }

  const { metrics, policies, employees } = data;

  const filteredEmployees = employees.filter(
    (e) =>
      e.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.department.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.role.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <PageHeader
        title="Human Resources"
        description="Team census, active leave schedules, and organizational policies."
        badge="Active Team"
        actions={
          <button
            type="button"
            onClick={() => navigate('/assistant')}
            className="px-3 py-1.5 rounded-xl bg-[#2f27ce] hover:bg-[#433bff] text-white text-xs font-medium flex items-center gap-1.5 shadow-subtle-glow transition-all"
          >
            <Sparkles className="w-3.5 h-3.5 text-[#dedcff]" />
            <span>Ask HR Agent</span>
          </button>
        }
      />

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Employees"
          value={metrics.employees}
          change="Full headcount"
          isNeutral={true}
          timeframe="across all offices"
          icon={Users}
        />
        <StatCard
          title="On Leave"
          value={metrics.onLeave}
          change="3 scheduled today"
          isWarning={true}
          timeframe="approved time off"
          icon={Calendar}
        />
        <StatCard
          title="Departments"
          value={metrics.departments}
          change="5 active divisions"
          isNeutral={true}
          timeframe="cross-functional"
          icon={Building2}
        />
        <StatCard
          title="Open Requests"
          value={metrics.openRequests}
          change="Needs review"
          isPositive={true}
          timeframe="leave & expense forms"
          icon={FileText}
        />
      </div>

      {/* HR Policies Cards */}
      <div>
        <div className="flex items-center justify-between pb-3 mb-3">
          <h3 className="text-sm font-semibold text-[#fbfbfe] flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-[#dedcff]" />
            Corporate HR Policies & Guidelines
          </h3>
          <span className="text-xs text-slate-400">
            Nexus automated policy guidance
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {policies.map((policy) => (
            <div
              key={policy.code}
              className="nexus-card p-4 flex flex-col justify-between hover:border-[#433bff]/50 transition-colors"
            >
              <div>
                <div className="flex items-center justify-between text-xs font-mono text-[#dedcff] mb-2">
                  <span className="px-2 py-0.5 rounded bg-[#2f27ce]/20 border border-[#1f1a54]">
                    {policy.category}
                  </span>
                  <span className="text-slate-500">{policy.code}</span>
                </div>
                <h4 className="text-sm font-semibold text-[#fbfbfe]">
                  {policy.title}
                </h4>
                <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                  {policy.description}
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-[#1f1a54]/60 flex items-center justify-between text-[11px] text-slate-500">
                <span className="flex items-center gap-1 text-emerald-400">
                  <CheckCircle2 className="w-3 h-3" />
                  Active Policy
                </span>
                <button
                  type="button"
                  onClick={() => navigate('/assistant')}
                  className="text-[#dedcff] hover:underline"
                >
                  Query with AI &rarr;
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Employee Directory Table */}
      <div className="nexus-card p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 mb-4 border-b border-[#1f1a54]/60">
          <div>
            <h3 className="text-sm font-semibold text-[#fbfbfe]">
              Employee Directory (Sample Data)
            </h3>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Current active team roster and attendance statuses.
            </p>
          </div>

          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search team member..."
              className="pl-8 pr-3 py-1.5 rounded-lg bg-[#080520] border border-[#1f1a54] text-xs text-[#fbfbfe] placeholder-slate-500 focus:outline-none focus:border-[#433bff] w-48 sm:w-60"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[#1f1a54]/80 text-slate-400 uppercase text-[10px] tracking-wider">
                <th className="pb-3 font-semibold">ID</th>
                <th className="pb-3 font-semibold">Name</th>
                <th className="pb-3 font-semibold">Department</th>
                <th className="pb-3 font-semibold">Role</th>
                <th className="pb-3 font-semibold">Tenure</th>
                <th className="pb-3 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1f1a54]/40 text-slate-300">
              {filteredEmployees.map((emp) => (
                <tr key={emp.id} className="hover:bg-[#130f3b]/30 transition-colors">
                  <td className="py-3 font-mono font-medium text-[#dedcff]">
                    {emp.id}
                  </td>
                  <td className="py-3 font-medium text-[#fbfbfe]">
                    {emp.name}
                  </td>
                  <td className="py-3 text-slate-300">
                    {emp.department}
                  </td>
                  <td className="py-3 text-slate-400">
                    {emp.role}
                  </td>
                  <td className="py-3 font-mono text-slate-400">
                    {emp.tenure}
                  </td>
                  <td className="py-3">
                    <StatusBadge status={emp.status} size="xs" />
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
