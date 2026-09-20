import React from 'react';
import { Sparkles, User, Wrench, CheckCircle2 } from 'lucide-react';
import { ToolCallItem } from '../common/ToolCallItem';

export function MessageBubble({ message }) {
  const isUser = message.sender === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end my-3">
        <div className="flex items-start gap-2.5 max-w-[85%] sm:max-w-[75%] flex-row-reverse">
          <div className="w-7 h-7 rounded-lg bg-[#2f27ce] flex items-center justify-center text-white shrink-0 mt-0.5 shadow-subtle-glow">
            <User className="w-3.5 h-3.5" />
          </div>
          <div className="text-right">
            <div className="p-3.5 rounded-2xl rounded-tr-sm bg-[#2f27ce]/25 border border-[#433bff]/40 text-[#fbfbfe] text-xs sm:text-sm leading-relaxed text-left shadow-subtle-glow">
              {message.content}
            </div>
            {message.timestamp && (
              <span className="text-[10px] text-slate-500 font-mono mt-1 mr-1 inline-block">
                {message.timestamp}
              </span>
            )}
          </div>
        </div>
      </div>
    );
  }

  // AI Assistant message
  return (
    <div className="flex justify-start my-4">
      <div className="flex items-start gap-3 max-w-[90%] sm:max-w-[85%]">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[#2f27ce] to-[#433bff] flex items-center justify-center text-white shrink-0 mt-0.5 shadow-card-glow border border-[#dedcff]/30">
          <Sparkles className="w-4 h-4 text-[#dedcff]" />
        </div>

        <div className="flex-1 space-y-2">
          {/* Agent orchestration badge header */}
          {message.agents_used && message.agents_used.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-slate-400">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                Orchestrated via:
              </span>
              {message.agents_used.map((agent, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-[#1e194f]/60 border border-[#433bff]/30 text-[#dedcff] capitalize inline-flex items-center gap-1"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                  {agent} Agent
                </span>
              ))}
            </div>
          )}

          {/* Core Response Card */}
          <div className="p-4 rounded-2xl rounded-tl-sm bg-[#0c0827] border border-[#1f1a54] text-xs sm:text-sm text-[#fbfbfe] leading-relaxed shadow-sm">
            <div className="whitespace-pre-wrap">{message.content}</div>

            {/* If tool calls are present, display expandable summaries */}
            {message.tool_calls && message.tool_calls.length > 0 && (
              <div className="mt-3.5 pt-3 border-t border-[#1f1a54]/70">
                <div className="text-[10px] uppercase font-semibold text-slate-400 mb-1 flex items-center gap-1 tracking-wider">
                  <Wrench className="w-3 h-3 text-[#dedcff]" />
                  Verified Tools Executed ({message.tool_calls.length})
                </div>
                <div className="space-y-1 mt-1.5">
                  {message.tool_calls.map((toolCall, idx) => (
                    <ToolCallItem key={idx} toolCall={toolCall} />
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="flex items-center gap-3 text-[10px] text-slate-500 font-mono ml-1">
            {message.timestamp && <span>{message.timestamp}</span>}
            {message.session_id && <span>Session: {message.session_id}</span>}
            <span className="text-emerald-400 flex items-center gap-1">
              <CheckCircle2 className="w-2.5 h-2.5" />
              Verified Multi-Agent Synthesis
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
