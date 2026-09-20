import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Loader2, CornerDownLeft } from 'lucide-react';

export function ChatInput({ onSend, isProcessing, placeholder }) {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  // Auto-adjust height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
    }
  }, [input]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!input.trim() || isProcessing) return;
    onSend(input.trim());
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="relative border-t border-[#1f1a54]/70 bg-[#07041c]/90 p-3 sm:p-4 backdrop-blur">
      <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative">
        <div className="relative flex items-end rounded-xl bg-[#0c0827] border border-[#1f1a54] focus-within:border-[#433bff] focus-within:ring-1 focus-within:ring-[#433bff]/50 transition-all shadow-inner">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            disabled={isProcessing}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder || "Ask Nexus about your business..."}
            className="flex-1 max-h-36 min-h-[44px] py-3 px-3.5 bg-transparent text-xs sm:text-sm text-[#fbfbfe] placeholder-slate-500 resize-none focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed leading-relaxed"
          />

          <div className="flex items-center gap-2 p-2 shrink-0">
            <span className="hidden sm:inline-flex items-center gap-1 text-[10px] text-slate-500 font-mono pr-1">
              <span>Return</span>
              <CornerDownLeft className="w-2.5 h-2.5" />
            </span>

            <button
              type="submit"
              disabled={!input.trim() || isProcessing}
              className="w-9 h-9 rounded-lg bg-[#2f27ce] hover:bg-[#433bff] disabled:bg-[#1a1447] disabled:text-slate-500 text-white flex items-center justify-center transition-all duration-150 shadow-subtle-glow disabled:shadow-none cursor-pointer disabled:cursor-not-allowed"
              aria-label="Send query"
            >
              {isProcessing ? (
                <Loader2 className="w-4 h-4 animate-spin text-[#dedcff]" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between text-[11px] text-slate-500 px-1 mt-1.5">
          <span className="flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-[#433bff]" />
            Multi-agent routing: Manager &rarr; Sales, Inventory, HR
          </span>
          <span className="hidden md:inline font-mono">Shift+Enter for new line</span>
        </div>
      </form>
    </div>
  );
}
