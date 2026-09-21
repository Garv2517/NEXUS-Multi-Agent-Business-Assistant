import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Bot,
  TrendingUp,
  Package,
  Users,
  Activity,
  X,
  Sparkles,
  Layers
} from 'lucide-react';

const NAV_ITEMS = [
  { path: '/', label: 'Overview', icon: LayoutDashboard },
  { path: '/assistant', label: 'Assistant', icon: Bot, badge: 'Live' },
  { path: '/sales', label: 'Sales', icon: TrendingUp },
  { path: '/inventory', label: 'Inventory', icon: Package, alertCount: 4 },
  { path: '/hr', label: 'People Management', icon: Users },
  { path: '/activity', label: 'Activity', icon: Activity },
];

export function Sidebar({ isMobileOpen, onCloseMobile }) {
  return (
    <>
      {/* Mobile Backdrop */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden"
          onClick={onCloseMobile}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed md:static inset-y-0 left-0 z-50 w-[230px] bg-[#07041c] border-r border-[#1f1a54]/60 flex flex-col transition-transform duration-200 ease-in-out ${
          isMobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        {/* Logo Branding */}
        <div className="h-14 px-5 flex items-center justify-between border-b border-[#1f1a54]/60 shrink-0">
          <NavLink to="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-[#2f27ce] flex items-center justify-center text-white shadow-subtle-glow border border-[#433bff]/40 group-hover:scale-105 transition-transform">
              <Sparkles className="w-4 h-4 text-[#dedcff]" />
            </div>
            <div>
              <div className="font-bold tracking-tight text-base text-[#fbfbfe] flex items-center gap-1.5">
                NEXUS
                <span className="text-[9px] px-1.5 py-0.2 rounded font-semibold bg-[#2f27ce]/40 border border-[#433bff]/40 text-[#dedcff]">
                  AI
                </span>
              </div>
              <div className="text-[10px] text-slate-400 font-normal">
                Multi-Agent Assistant
              </div>
            </div>
          </NavLink>

          {/* Close button for mobile */}
          <button
            type="button"
            onClick={onCloseMobile}
            className="md:hidden p-1 rounded-md text-slate-400 hover:text-white hover:bg-[#1f1a54]"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Navigation Items */}
        <div className="px-3 py-4 flex-1 overflow-y-auto space-y-1">
          <div className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
            Workspace
          </div>

          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onCloseMobile}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all duration-150 group ${
                    isActive
                      ? 'bg-[#2f27ce]/25 border border-[#433bff]/40 text-[#fbfbfe] shadow-card-glow'
                      : 'text-slate-300 hover:text-white hover:bg-[#130f3b]/50 border border-transparent'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <div className="flex items-center gap-3">
                      <Icon
                        className={`w-4 h-4 transition-colors ${
                          isActive
                            ? 'text-[#dedcff]'
                            : 'text-slate-400 group-hover:text-slate-200'
                        }`}
                      />
                      <span>{item.label}</span>
                    </div>

                    {item.badge && (
                      <span className="px-1.5 py-0.2 rounded text-[10px] font-semibold bg-[#433bff]/30 border border-[#433bff]/40 text-[#dedcff]">
                        {item.badge}
                      </span>
                    )}

                    {item.alertCount && (
                      <span className="px-1.5 py-0.2 rounded-full text-[10px] font-semibold bg-amber-950/60 border border-amber-500/40 text-amber-300">
                        {item.alertCount}
                      </span>
                    )}
                  </>
                )}
              </NavLink>
            );
          })}
        </div>

        {/* Footer info: Multi-Agent Model Mesh */}
        <div className="p-3.5 border-t border-[#1f1a54]/60 bg-[#050315]/70 shrink-0">
          <div className="p-2.5 rounded-lg bg-[#0c0827] border border-[#1f1a54]/80 text-[11px]">
            <div className="flex items-center gap-1.5 text-slate-300 font-medium mb-1">
              <Layers className="w-3.5 h-3.5 text-[#dedcff]" />
              <span>Orchestrator v1.2</span>
            </div>
            <div className="text-[10px] text-slate-400 flex items-center justify-between">
              <span>Mesh Status</span>
              <span className="text-emerald-400 font-medium">4 Agents Synced</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
