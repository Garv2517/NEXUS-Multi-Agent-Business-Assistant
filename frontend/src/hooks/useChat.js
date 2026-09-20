import { useState, useCallback } from 'react';
import { sendMessage as apiSendMessage } from '../services/api';

/**
 * useChat Hook
 * Manages conversational message stream, query execution, and links to useAgentTrace.
 */
export function useChat(agentTraceManager) {
  const [messages, setMessages] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = useCallback(
    async (text) => {
      if (!text || !text.trim() || isProcessing) return;

      const trimmed = text.trim();
      const userMessageId = `msg_user_${Date.now()}`;
      const nowTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      // 1. Immediately append user message
      const userMsg = {
        id: userMessageId,
        sender: 'user',
        content: trimmed,
        timestamp: nowTime
      };

      setMessages((prev) => [...prev, userMsg]);
      setIsProcessing(true);
      setError(null);

      // 2. Clear trace for the new run
      if (agentTraceManager?.resetTrace) {
        agentTraceManager.resetTrace();
        agentTraceManager.setIsOrchestrating(true);
      }

      try {
        // 3. Invoke API with streaming event listener
        const response = await apiSendMessage(trimmed, (event) => {
          if (agentTraceManager?.appendOrUpdateEvent) {
            agentTraceManager.appendOrUpdateEvent(event);
          }
        });

        // 4. Append final AI message
        const aiMsg = {
          id: `msg_ai_${Date.now()}`,
          sender: 'assistant',
          content: response.answer,
          timestamp: response.timestamp || nowTime,
          agents_used: response.agents_used || [],
          tool_calls: response.tool_calls || [],
          session_id: response.session_id,
          plan: response.plan || null
        };

        setMessages((prev) => [...prev, aiMsg]);
      } catch (err) {
        console.error("Chat execution error:", err);
        setError("Failed to execute agent workflow. Please try again.");
      } finally {
        setIsProcessing(false);
        if (agentTraceManager?.setIsOrchestrating) {
          agentTraceManager.setIsOrchestrating(false);
        }
      }
    },
    [isProcessing, agentTraceManager]
  );

  const clearChat = useCallback(() => {
    setMessages([]);
    if (agentTraceManager?.resetTrace) {
      agentTraceManager.resetTrace();
    }
  }, [agentTraceManager]);

  return {
    messages,
    isProcessing,
    error,
    sendMessage,
    clearChat
  };
}
