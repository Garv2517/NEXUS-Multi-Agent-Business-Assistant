import React, { useState, useEffect } from 'react';
import {
  Activity as ActivityIcon,
  Filter,
  Clock,
  Wrench,
  Sparkles,
  Search,
  Code2,
  X
} from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { StatusBadge } from '../components/common/StatusBadge';
import { getActivityLogs } from '../services/api';

const AGENT_FILTERS = ['All', 'Manager', 'Sales', 'Inventory', 'HR'];

export function Activity() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFilter, setSelectedFilter] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [inspectItem, setInspectItem] = useState(null);

  useEffect(() => {
    let isMounted = true;
    getActivityLogs().then((res) => {
      if (isMounted) {
        setLogs(res);
        setLoading(false);
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) {
    return (
      <div className="p-6 sm:p-8 flex items-center justify-center min-h-[50vh]">
        <div className="flex items-center gap-2 text-slate-400 text-xs">
          <div className="w-4 h-4 rounded-full border-2 border-[#433bff] border-t-transparent animate-spin" />
          <span>Retrieving multi-agent execution history...</span>
        </div>
      </div>
    );
  }

  const filteredLogs = logs.filter((item) => {
    const matchesFilter =
      selectedFilter === 'All'
        ? true
        : item.agent.toLowerCase().includes(selectedFilter.toLowerCase());

    const matchesSearch =
      item.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.agent.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.tool.toLowerCase().includes(searchTerm.toLowerCase());

    return matchesFilter && matchesSearch;
  });

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <PageHeader
        title="AI Activity & Audit Logs"
        description="Comprehensive audit trail of multi-agent routing, tool executions, and latency metrics."
        badge="Audit Enabled"
      />

      {/* Filter and Search Bar */}
      <div className="nexus-card p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        {/* Agent Category Filters */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
          <span className="text-xs text-slate-400 mr-1 flex items-center gap-1">
            <Filter className="w-3.5 h-3.5" />
            Agent:
          </span>
          {AGENT_FILTERS.map((filter) => (
            <button
              key={filter}
              type="button"
              onClick={() => setSelectedFilter(filter)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors shrink-0 ${
                selectedFilter === filter
                  ? 'bg-[#2f27ce] text-white shadow-subtle-glow'
                  : 'bg-[#080520] text-slate-400 hover:text-white border border-[#1f1a54]'
              }`}
            >
              {filter}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search action or tool..."
            className="pl-8 pr-3 py-1.5 rounded-lg bg-[#080520] border border-[#1f1a54] text-xs text-[#fbfbfe] placeholder-slate-500 focus:outline-none focus:border-[#433bff] w-full sm:w-56"
          />
        </div>
      </div>

      {/* Activity Log Table */}
      <div className="nexus-card p-5">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[#1f1a54]/80 text-slate-400 uppercase text-[10px] tracking-wider">
                <th className="pb-3 font-semibold">Timestamp</th>
                <th className="pb-3 font-semibold">Agent</th>
                <th className="pb-3 font-semibold">Action</th>
                <th className="pb-3 font-semibold">Tool Invoked</th>
                <th className="pb-3 font-semibold">Status</th>
                <th className="pb-3 font-semibold">Duration</th>
                <th className="pb-3 font-semibold text-right">Payload</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1f1a54]/40 text-slate-300">
              {filteredLogs.map((log) => (
                <tr key={log.id} className="hover:bg-[#130f3b]/30 transition-colors">
                  <td className="py-3 font-mono text-slate-400 whitespace-nowrap">
                    {log.timestamp}
                  </td>
                  <td className="py-3 font-medium text-[#fbfbfe] whitespace-nowrap">
                    <span className="inline-flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#433bff]" />
                      {log.agent}
                    </span>
                  </td>
                  <td className="py-3 text-slate-200">
                    {log.action}
                  </td>
                  <td className="py-3 font-mono text-[#dedcff]">
                    {log.tool === '-' ? (
                      <span className="text-slate-600">-</span>
                    ) : (
                      <span className="px-1.5 py-0.5 rounded bg-[#16113c] border border-[#1f1a54] text-[11px]">
                        {log.tool}()
                      </span>
                    )}
                  </td>
                  <td className="py-3">
                    <StatusBadge status={log.status} size="xs" />
                  </td>
                  <td className="py-3 font-mono text-slate-400 whitespace-nowrap">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3 text-slate-500" />
                      {log.duration}
                    </span>
                  </td>
                  <td className="py-3 text-right">
                    <button
                      type="button"
                      onClick={() => setInspectItem(log)}
                      className="px-2 py-1 rounded bg-[#080520] hover:bg-[#1f1a54] text-slate-400 hover:text-white font-mono text-[11px] border border-[#1f1a54] transition-colors"
                    >
                      Inspect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Payload Modal */}
      {inspectItem && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0c0827] border border-[#1f1a54] rounded-xl max-w-lg w-full p-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-[#1f1a54]">
              <div className="flex items-center gap-2">
                <Code2 className="w-4 h-4 text-[#dedcff]" />
                <h4 className="text-sm font-semibold text-[#fbfbfe]">
                  Execution Audit Details ({inspectItem.id})
                </h4>
              </div>
              <button
                type="button"
                onClick={() => setInspectItem(null)}
                className="text-slate-400 hover:text-white p-1 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="mt-3 space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-[#1f1a54]/50">
                <span className="text-slate-400">Agent:</span>
                <span className="text-[#dedcff] font-medium">{inspectItem.agent}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#1f1a54]/50">
                <span className="text-slate-400">Tool:</span>
                <span className="text-[#dedcff] font-mono">{inspectItem.tool}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#1f1a54]/50">
                <span className="text-slate-400">Duration:</span>
                <span className="text-emerald-400 font-mono">{inspectItem.duration}</span>
              </div>

              <div className="pt-2">
                <span className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider mb-1 block">
                  Metadata Payload:
                </span>
                <pre className="p-3 bg-[#050315] border border-[#1f1a54] rounded-lg text-[#dedcff] font-mono text-[11px] overflow-x-auto">
                  {JSON.stringify(inspectItem.meta || {}, null, 2)}
                </pre>
              </div>
            </div>

            <div className="mt-4 flex justify-end">
              <button
                type="button"
                onClick={() => setInspectItem(null)}
                className="px-3 py-1.5 text-xs rounded-lg bg-[#2f27ce] text-white hover:bg-[#433bff] transition-colors"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
