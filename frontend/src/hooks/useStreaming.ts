import { useState, useCallback, useRef } from 'react';
import type { StreamEvent, Message, SessionInfo } from '@/lib/types';

export const useStreaming = () => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const startStream = useCallback(
    (
      query: string,
      sessionId: string | undefined,
      onChunk: (content: string) => void,
      onToolUse: (tool: string, status: 'started' | 'completed') => void,
      onComplete: (sessionStats?: Partial<SessionInfo>) => void,
      onError: (error: string) => void
    ) => {
      // Close any existing connection
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      setIsStreaming(true);
      setError(null);

      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

      // Create query params
      const params = new URLSearchParams({
        query,
        stream: 'true',
      });

      if (sessionId) {
        params.append('session_id', sessionId);
      }

      // Make POST request to initiate stream
      fetch(`${API_BASE_URL}/api/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          session_id: sessionId,
          stream: true,
        }),
      })
        .then(async (response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const reader = response.body?.getReader();
          if (!reader) {
            throw new Error('No response body');
          }

          const decoder = new TextDecoder();
          let buffer = '';

          while (true) {
            const { done, value } = await reader.read();

            if (done) {
              setIsStreaming(false);
              break;
            }

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6)) as StreamEvent;

                  if (data.type === 'text' && data.content) {
                    onChunk(data.content);
                  } else if (data.type === 'tool' && data.tool && data.status) {
                    onToolUse(data.tool, data.status);
                  } else if (data.type === 'complete') {
                    onComplete(data.sessionStats);
                    setIsStreaming(false);
                  } else if (data.type === 'error') {
                    const errorMsg = data.error || 'Unknown error';
                    setError(errorMsg);
                    onError(errorMsg);
                    setIsStreaming(false);
                  }
                } catch (e) {
                  console.error('Failed to parse SSE data:', e);
                }
              }
            }
          }
        })
        .catch((err) => {
          console.error('Stream error:', err);
          const errorMsg = err.message || 'Failed to connect to server';
          setError(errorMsg);
          onError(errorMsg);
          setIsStreaming(false);
        });
    },
    []
  );

  const stopStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  return {
    isStreaming,
    error,
    startStream,
    stopStream,
  };
};
