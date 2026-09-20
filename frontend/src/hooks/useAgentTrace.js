import { useState, useCallback } from 'react';

/**
 * useAgentTrace Hook
 * Manages live multi-agent orchestration state and step events.
 * Designed around future SSE streaming events:
 * manager_started, route_selected, agent_started, tool_started, tool_completed, agent_completed, response_completed
 */
export function useAgentTrace() {
  const [events, setEvents] = useState([]);
  const [isOrchestrating, setIsOrchestrating] = useState(false);
  const [activeAgent, setActiveAgent] = useState(null);

  const resetTrace = useCallback(() => {
    setEvents([]);
    setIsOrchestrating(false);
    setActiveAgent(null);
  }, []);

  const appendOrUpdateEvent = useCallback((event) => {
    setEvents((prev) => {
      // If event has an ID and already exists in list, update it (e.g. tool running -> tool success)
      const existingIdx = prev.findIndex((e) => e.id === event.id);
      if (existingIdx !== -1) {
        const next = [...prev];
        next[existingIdx] = { ...next[existingIdx], ...event };
        return next;
      }
      return [...prev, event];
    });

    if (event.agent) {
      setActiveAgent(event.agent);
    }

    if (event.status === 'running') {
      setIsOrchestrating(true);
    } else if (event.type === 'response_completed' || event.status === 'error') {
      setIsOrchestrating(false);
    }
  }, []);

  const setInitialTrace = useCallback((initialEvents) => {
    setEvents(initialEvents || []);
    setIsOrchestrating(false);
    setActiveAgent(null);
  }, []);

  return {
    events,
    isOrchestrating,
    activeAgent,
    resetTrace,
    appendOrUpdateEvent,
    setInitialTrace,
    setIsOrchestrating
  };
}
