import React from 'react';
import { ArrowUpRight, TrendingUp, AlertTriangle, Scale, BarChart2 } from 'lucide-react';

const SUGGESTIONS = [
  {
    text: "Compare our top-selling products with inventory.",
    label: "Compare Sales vs Inventory",
    icon: Scale,
    highlight: true
  },
  {
    text: "How are sales performing this month?",
    label: "Monthly Sales Report",
    icon: TrendingUp
  },
  {
    text: "Which products are low in stock?",
    label: "Low Stock Inventory Scan",
    icon: AlertTriangle
  },
  {
    text: "Give me a business overview.",
    label: "Executive Summary",
    icon: BarChart2
  }
];

export function SuggestedPrompts({ onSelectPrompt, disabled }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 max-w-2xl w-full mx-auto">
      {SUGGESTIONS.map((item, index) => {
        const Icon = item.icon;
        return (
          <button
            key={index}
            type="button"
            disabled={disabled}
            onClick={() => onSelectPrompt(item.text)}
            className={`p-3 rounded-xl text-left border transition-all duration-200 flex items-start justify-between group ${
              item.highlight
                ? 'bg-[#0e0a33] border-[#433bff]/40 hover:border-[#433bff] hover:shadow-card-glow'
                : 'bg-[#0c0827]/70 border-[#1f1a54]/70 hover:border-[#433bff]/40 hover:bg-[#120d3d]'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-[#2f27ce]/20 border border-[#1f1a54] flex items-center justify-center text-[#dedcff] shrink-0 group-hover:border-[#433bff]/50 transition-colors">
                <Icon className="w-4 h-4" />
              </div>
              <div>
                <div className="text-xs font-semibold text-[#fbfbfe] group-hover:text-[#dedcff] transition-colors">
                  {item.label}
                </div>
                <div className="text-[11px] text-slate-400 line-clamp-1 mt-0.5">
                  "{item.text}"
                </div>
              </div>
            </div>

            <ArrowUpRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-[#dedcff] group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all shrink-0 mt-0.5" />
          </button>
        );
      })}
    </div>
  );
}
