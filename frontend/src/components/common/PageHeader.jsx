import React from 'react';

export function PageHeader({ title, description, badge, actions }) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-[#1f1a54]/50">
      <div>
        <div className="flex items-center gap-2.5">
          <h1 className="text-xl sm:text-2xl font-semibold tracking-tight text-[#fbfbfe]">
            {title}
          </h1>
          {badge && (
            <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-[#2f27ce]/30 border border-[#433bff]/40 text-[#dedcff]">
              {badge}
            </span>
          )}
        </div>
        {description && (
          <p className="text-sm text-slate-400 mt-1">
            {description}
          </p>
        )}
      </div>

      {actions && (
        <div className="flex items-center gap-3 shrink-0">
          {actions}
        </div>
      )}
    </div>
  );
}
