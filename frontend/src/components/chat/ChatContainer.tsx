import React, { useState, useEffect, useCallback } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { useStreaming } from '@/hooks/useStreaming';
import type { Message, SessionInfo, ToolUsage } from '@/lib/types';

interface ChatContainerProps {
  sessionInfo: Partial<SessionInfo> | null;
  onSessionUpdate: (info: Partial<SessionInfo>) => void;
}

export const ChatContainer: React.FC<ChatContainerProps> = ({
  sessionInfo,
  onSessionUpdate,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentResponse, setCurrentResponse] = useState('');
  const [activeTools, setActiveTools] = useState<ToolUsage[]>([]);
  const { isStreaming, error, startStream } = useStreaming();
  const currentResponseRef = React.useRef('');

  const handleSend = useCallback(
    (query: string) => {
      // Add user message
      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: query,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // Start assistant message
      setCurrentResponse('');
      currentResponseRef.current = '';
      setActiveTools([]);

      const assistantMessageId = (Date.now() + 1).toString();
      const startTime = Date.now();

      startStream(
        query,
        sessionInfo?.sessionId,
        // onChunk
        (content) => {
          currentResponseRef.current += content;
          setCurrentResponse(currentResponseRef.current);
        },
        // onToolUse
        (tool, status) => {
          setActiveTools((prev) => {
            const existing = prev.find((t) => t.tool === tool);
            if (existing) {
              return prev.map((t) =>
                t.tool === tool ? { ...t, status } : t
              );
            }
            return [...prev, { tool, status }];
          });
        },
        // onComplete
        (sessionStats) => {
          const duration = Date.now() - startTime;
          const finalContent = currentResponseRef.current;
          const toolsUsed = [...new Set(activeTools.map((t) => t.tool))]; // Unique tool names

          // Remove streaming message and add final message
          setMessages((prev) => {
            const withoutStreaming = prev.filter((m) => m.id !== 'streaming');
            const assistantMessage: Message = {
              id: assistantMessageId,
              role: 'assistant',
              content: finalContent,
              timestamp: new Date(),
              metadata: {
                duration,
                toolsUsed,
              },
            };
            return [...withoutStreaming, assistantMessage];
          });

          setCurrentResponse('');
          currentResponseRef.current = '';
          setActiveTools([]);

          if (sessionStats) {
            onSessionUpdate(sessionStats);
          }
        },
        // onError
        (errorMsg) => {
          console.error('Stream error:', errorMsg);
          setMessages((prev) => {
            const withoutStreaming = prev.filter((m) => m.id !== 'streaming');
            const errorMessage: Message = {
              id: assistantMessageId,
              role: 'assistant',
              content: `❌ Error: ${errorMsg}`,
              timestamp: new Date(),
            };
            return [...withoutStreaming, errorMessage];
          });
          setCurrentResponse('');
          currentResponseRef.current = '';
          setActiveTools([]);
        }
      );
    },
    [sessionInfo?.sessionId, startStream, onSessionUpdate]
  );

  // Add streaming response to messages for display
  useEffect(() => {
    if (currentResponse) {
      const assistantMessage: Message = {
        id: 'streaming',
        role: 'assistant',
        content: currentResponse,
        timestamp: new Date(),
      };

      setMessages((prev) => {
        const withoutStreaming = prev.filter((m) => m.id !== 'streaming');
        return [...withoutStreaming, assistantMessage];
      });
    }
  }, [currentResponse]);

  return (
    <Card className="flex flex-col h-[calc(100vh-250px)]">
      <div className="p-4 border-b flex-shrink-0">
        <div className="flex gap-2 items-center">
          <span className="text-sm text-muted-foreground">Tools:</span>
          {activeTools.length === 0 ? (
            <Badge variant="secondary">Ready</Badge>
          ) : (
            activeTools.map((tool, idx) => (
              <Badge
                key={idx}
                variant={tool.status === 'completed' ? 'default' : 'secondary'}
              >
                {tool.tool} {tool.status === 'started' && '⏳'}
                {tool.status === 'completed' && '✓'}
              </Badge>
            ))
          )}
        </div>
      </div>

      <div className="flex-1 overflow-hidden p-4">
        <MessageList messages={messages} />
      </div>

      <div className="p-4 border-t flex-shrink-0">
        <ChatInput
          onSend={handleSend}
          disabled={isStreaming}
          isStreaming={isStreaming}
        />
        {error && (
          <p className="text-sm text-destructive mt-2">Error: {error}</p>
        )}
      </div>
    </Card>
  );
};
