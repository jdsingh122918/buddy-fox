import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { Message as MessageType } from '@/lib/types';
import 'highlight.js/styles/github-dark.css';

interface MessageProps {
  message: MessageType;
}

export const Message: React.FC<MessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const isStreaming = message.id === 'streaming';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <Card className={`max-w-[80%] ${isUser ? 'bg-primary text-primary-foreground' : 'bg-card'}`}>
        <div className="p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">{isUser ? '👤' : '🦊'}</span>
            <span className="text-sm font-semibold">
              {isUser ? 'You' : 'Buddy Fox'}
            </span>
            {isStreaming && (
              <Badge variant="outline" className="text-xs animate-pulse">
                Thinking...
              </Badge>
            )}
            {message.metadata?.toolsUsed && message.metadata.toolsUsed.length > 0 && (
              <div className="flex gap-1 ml-auto">
                {message.metadata.toolsUsed.map((tool, idx) => (
                  <Badge key={idx} variant="secondary" className="text-xs">
                    {tool}
                  </Badge>
                ))}
              </div>
            )}
          </div>

          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeHighlight]}
                components={{
                  a: ({ node, ...props }) => (
                    <a {...props} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline" />
                  ),
                  code: ({ node, inline, ...props }: any) => (
                    inline ?
                      <code className="bg-muted px-1 py-0.5 rounded text-sm" {...props} /> :
                      <code className="block bg-muted p-2 rounded text-sm overflow-x-auto" {...props} />
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
              {isStreaming && message.content === '' && (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <div className="animate-pulse">●</div>
                  <div className="animate-pulse delay-75">●</div>
                  <div className="animate-pulse delay-150">●</div>
                </div>
              )}
            </div>
          )}

          {message.metadata?.duration && (
            <div className="mt-2 text-xs text-muted-foreground">
              Response time: {message.metadata.duration}ms
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};
