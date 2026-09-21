import React from 'react';
import { Menu, Sparkles, Activity, ShieldCheck, Zap } from 'lucide-react';
import { useLocation } from 'react-router-dom';

const ROUTE_TITLES = {
  '/': 'Overview',
  '/assistant': 'Assistant',
  '/sales': 'Sales Intelligence',
  '/inventory': 'Inventory Management',
  '/hr': 'People Management',
  '/activity': 'AI Activity & Audit Logs',
  '/about': 'About Nexus'
};

export function Header({ onToggleMobileMenu, healthStatus }) {
  const location = useLocation();
  const currentTitle = ROUTE_TITLES[location.pathname] || 'Dashboard';

  const isOnline = healthStatus?.status === 'ONLINE';
  const isFoundryConnected = healthStatus?.foundry && healthStatus?.foundry !== 'not_configured';

  return (
    <header className="h-14 bg-[#07041c]/90 backdrop-blur border-b border-[#1f1a54]/60 px-4 sm:px-6 flex items-center justify-between shrink-0 z-30">
      {/* Left: Mobile menu toggle + Page title */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onToggleMobileMenu}
          className="md:hidden p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-[#1a1447] focus:outline-none transition-colors"
          aria-label="Toggle navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2">
          <h2 className="text-base sm:text-lg font-semibold text-[#fbfbfe] tracking-tight">
            {currentTitle}
          </h2>
          {location.pathname === '/assistant' && (
            <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-[#2f27ce]/30 border border-[#433bff]/40 text-[#dedcff]">
              <Sparkles className="w-3 h-3 text-[#dedcff]" />
              Multi-Agent Mode
            </span>
          )}
        </div>
      </div>

      {/* Right: Connection status & User Profile */}
      <div className="flex items-center gap-3 sm:gap-4">
        {/* Backend / Foundry Status Badge */}
        <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-[#0c0827] border border-[#1f1a54] text-xs">
          <span className="relative flex h-2 w-2">
            {isOnline ? (
              <>
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </>
            ) : (
              <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
            )}
          </span>

          {isFoundryConnected ? (
            <>
              <span className="text-slate-300 font-medium">Azure AI</span>
              <span className="text-slate-500 hidden sm:inline">•</span>
              <span className="text-emerald-400 font-semibold hidden sm:inline">Ready</span>
            </>
          ) : (
            <>
              <span className="text-slate-300 font-medium">Nexus API</span>
              <span className="text-slate-500 hidden sm:inline">•</span>
              <span className="text-emerald-400 font-semibold hidden sm:inline">
                {isOnline ? 'Online' : 'Connecting...'}
              </span>
              <span className="px-1.5 py-0.2 rounded text-[10px] font-medium bg-[#2f27ce]/30 border border-[#433bff]/30 text-[#dedcff] hidden md:inline ml-0.5">
                {healthStatus?.mode === 'local_orchestration' ? 'Local Agent Mode' : 'Demo Mode'}
              </span>
            </>
          )}

          {isOnline && (
            <span className="text-[10px] text-slate-500 font-mono hidden md:inline ml-1">
              42ms
            </span>
          )}
        </div>

        {/* User / University Profile Avatar */}
        <div className="flex items-center gap-2.5 pl-2 sm:border-l sm:border-[#1f1a54]">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#2f27ce] to-[#433bff] flex items-center justify-center text-white font-medium text-xs shadow-subtle-glow border border-[#dedcff]/20">
            NX
          </div>
          <div className="hidden lg:block text-left">
            <div className="text-xs font-medium text-[#fbfbfe] leading-none">
              Nexus Workspace
            </div>
            <div className="text-[10px] text-slate-400 leading-none mt-1">
              AI Project Edition
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
