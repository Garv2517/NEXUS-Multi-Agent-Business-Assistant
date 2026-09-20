import React, { useState } from 'react';
import { Layers, Sparkles, RefreshCw } from 'lucide-react';
import { ChatWindow } from '../components/assistant/ChatWindow';
import { ChatInput } from '../components/assistant/ChatInput';
import { AgentTrace } from '../components/assistant/AgentTrace';
import { useAgentTrace } from '../hooks/useAgentTrace';
import { useChat } from '../hooks/useChat';

export function Assistant() {
  const [isMobileTraceOpen, setIsMobileTraceOpen] = useState(false);

  // Initialize custom hooks
  const agentTraceManager = useAgentTrace();
  const { messages, isProcessing, sendMessage, clearChat } = useChat(agentTraceManager);

  const handleSelectPrompt = (promptText) => {
    sendMessage(promptText);
    // Auto-open trace panel on mobile when user sends a prompt
    if (window.innerWidth < 1024) {
      setIsMobileTraceOpen(true);
    }
  };

  return (
    <div className="h-full flex flex-col lg:flex-row overflow-hidden relative">
      {/* Center Conversational Interface (~70% width on Desktop) */}
      <div className="flex-1 flex flex-col min-w-0 h-full bg-[#050315]">
        {/* Top Chat Bar */}
        <div className="h-12 px-4 sm:px-6 border-b border-[#1f1a54]/50 flex items-center justify-between shrink-0 bg-[#07041c]/60 backdrop-blur">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-semibold text-[#fbfbfe]">
              Nexus Multi-Agent Workspace
            </span>
            <span className="text-[11px] text-slate-400 hidden sm:inline font-mono">
              • Direct routing active
            </span>
          </div>

          <div className="flex items-center gap-2">
            {/* Mobile / Tablet Toggle for Agent Trace */}
            <button
              type="button"
              onClick={() => setIsMobileTraceOpen(!isMobileTraceOpen)}
              className="lg:hidden px-2.5 py-1 rounded-lg bg-[#2f27ce]/25 border border-[#433bff]/40 text-[#dedcff] text-xs font-medium flex items-center gap-1.5 hover:bg-[#2f27ce]/40 transition-colors"
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Trace ({agentTraceManager.events.length})</span>
            </button>

            {messages.length > 0 && (
              <button
                type="button"
                onClick={clearChat}
                disabled={isProcessing}
                className="text-xs text-slate-400 hover:text-white px-2 py-1 rounded hover:bg-[#1f1a54] transition-colors flex items-center gap-1 disabled:opacity-50"
                title="Reset conversation"
              >
                <RefreshCw className="w-3 h-3" />
                <span className="hidden sm:inline">Clear</span>
              </button>
            )}
          </div>
        </div>

        {/* Message Stream */}
        <ChatWindow
          messages={messages}
          isProcessing={isProcessing}
          onSelectPrompt={handleSelectPrompt}
        />

        {/* Chat Input Bar */}
        <ChatInput
          onSend={sendMessage}
          isProcessing={isProcessing}
          placeholder="Ask Nexus about sales, inventory, HR, or your business..."
        />
      </div>

      {/* Right Agent Trace Panel (~30% width on Desktop, slide-over drawer on Mobile/Tablet) */}
      {/* Desktop Panel */}
      <div className="hidden lg:block w-[340px] xl:w-[380px] h-full shrink-0">
        <AgentTrace
          events={agentTraceManager.events}
          isOrchestrating={agentTraceManager.isOrchestrating}
          activeAgent={agentTraceManager.activeAgent}
          onReset={agentTraceManager.resetTrace}
          lastResponse={messages.filter((m) => m.sender === 'assistant').slice(-1)[0]}
        />
      </div>

      {/* Mobile Drawer */}
      {isMobileTraceOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/70 backdrop-blur-sm"
            onClick={() => setIsMobileTraceOpen(false)}
          />

          {/* Drawer Content */}
          <div className="relative ml-auto w-full max-w-sm h-full shadow-2xl z-10">
            <AgentTrace
              events={agentTraceManager.events}
              isOrchestrating={agentTraceManager.isOrchestrating}
              activeAgent={agentTraceManager.activeAgent}
              onReset={agentTraceManager.resetTrace}
              onCloseMobile={() => setIsMobileTraceOpen(false)}
              lastResponse={messages.filter((m) => m.sender === 'assistant').slice(-1)[0]}
            />
          </div>
        </div>
      )}
    </div>
  );
}
