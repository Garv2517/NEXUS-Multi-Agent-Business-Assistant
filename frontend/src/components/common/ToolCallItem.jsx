import React, { useState } from 'react';
import { Wrench, ChevronDown, ChevronRight, Clock, CheckCircle2 } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

export function ToolCallItem({ toolCall }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!toolCall) return null;

  const toolName = toolCall.tool || 'anonymous_tool';
  const duration = toolCall.duration || (toolCall.duration_ms ? `${toolCall.duration_ms}ms` : null);

  return (
    <div className="rounded-lg border border-[#1f1a54] bg-[#0c0827]/70 overflow-hidden text-xs my-1.5 transition-all">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-2.5 hover:bg-[#150f3d]/60 text-left transition-colors"
      >
        <div className="flex items-center gap-2 min-w-0">
          <div className="w-5 h-5 rounded bg-[#2f27ce]/30 flex items-center justify-center text-[#dedcff] shrink-0">
            <Wrench className="w-3 h-3" />
          </div>
          <span className="font-mono text-[#dedcff] font-medium truncate">
            {toolName}
          </span>
          {duration && (
            <span className="text-slate-400 text-[11px] flex items-center gap-1 shrink-0 ml-1">
              <Clock className="w-2.5 h-2.5" />
              {duration}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <StatusBadge status={toolCall.status || 'success'} size="xs" />
          {isOpen ? (
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          ) : (
            <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
          )}
        </div>
      </button>

      {isOpen && (
        <div className="p-2.5 border-t border-[#1f1a54]/60 bg-[#07041a] space-y-2">
          {toolCall.agent && (
            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <span>Invoked by agent:</span>
              <span className="text-[#dedcff] font-medium capitalize">{toolCall.agent} Agent</span>
            </div>
          )}

          {toolCall.params && (
            <div>
              <div className="text-[10px] uppercase font-semibold text-slate-400 mb-1 tracking-wider">
                Parameters
              </div>
              <pre className="p-2 rounded bg-[#090620] border border-[#1f1a54] text-[11px] text-emerald-300 overflow-x-auto">
                {JSON.stringify(toolCall.params, null, 2)}
              </pre>
            </div>
          )}

          {toolCall.result && (
            <div>
              <div className="text-[10px] uppercase font-semibold text-slate-400 mb-1 tracking-wider">
                Execution Output
              </div>
              <pre className="p-2 rounded bg-[#090620] border border-[#1f1a54] text-[11px] text-[#dedcff] overflow-x-auto">
                {JSON.stringify(toolCall.result, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
