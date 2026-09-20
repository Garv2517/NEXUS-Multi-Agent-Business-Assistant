import React, { useRef, useEffect } from 'react';
import { Sparkles, Loader2, Bot, Layers } from 'lucide-react';
import { MessageBubble } from './MessageBubble';
import { SuggestedPrompts } from './SuggestedPrompts';

export function ChatWindow({ messages, isProcessing, onSelectPrompt }) {
  const scrollEndRef = useRef(null);

  useEffect(() => {
    scrollEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isProcessing]);

  const isEmpty = messages.length === 0;

  return (
    <div className="flex-1 overflow-y-auto p-4 sm:p-6 flex flex-col">
      {isEmpty ? (
        <div className="my-auto flex flex-col items-center text-center max-w-xl mx-auto py-8">
          {/* Nexus Brand Hero Mark */}
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-[#2f27ce] to-[#433bff] flex items-center justify-center text-white shadow-card-glow border border-[#dedcff]/30 mb-5">
            <Sparkles className="w-7 h-7 text-[#dedcff]" />
          </div>

          <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-[#fbfbfe]">
            What can I help you understand?
          </h2>

          <p className="text-xs sm:text-sm text-slate-400 mt-2 max-w-md">
            Ask about sales performance, inventory levels, workforce logistics, or request an overall business briefing.
          </p>

          <div className="w-full mt-8">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-3 text-center">
              Suggested queries to trigger multi-agent orchestration
            </div>
            <SuggestedPrompts
              onSelectPrompt={onSelectPrompt}
              disabled={isProcessing}
            />
          </div>
        </div>
      ) : (
        <div className="space-y-4 max-w-4xl w-full mx-auto pb-4">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}

          {/* Subtle live processing indicator */}
          {isProcessing && (
            <div className="flex items-center gap-3 text-xs text-[#dedcff] p-3 rounded-xl bg-[#0c0827] border border-[#2f27ce]/40 animate-pulse-subtle max-w-md shadow-card-glow">
              <Loader2 className="w-4 h-4 animate-spin text-[#433bff] shrink-0" />
              <div className="flex-1">
                <span className="font-semibold text-[#fbfbfe]">
                  Multi-Agent Orchestration Active
                </span>
                <div className="text-[11px] text-slate-400">
                  Manager coordinating Sales & Inventory tools...
                </div>
              </div>
            </div>
          )}

          <div ref={scrollEndRef} />
        </div>
      )}
    </div>
  );
}
