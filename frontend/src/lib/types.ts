// TypeScript types for Buddy Fox frontend

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: {
    duration?: number;
    toolsUsed?: string[];
  };
}

export interface SessionInfo {
  sessionId: string;
  startedAt: Date;
  webSearchesUsed: number;
  webFetchesUsed: number;
  maxSearches: number;
  duration: number;
  messageCount: number;
}

export interface StreamEvent {
  type: 'text' | 'tool' | 'complete' | 'error';
  content?: string;
  tool?: string;
  status?: 'started' | 'completed';
  error?: string;
  sessionStats?: Partial<SessionInfo>;
}

export interface QueryRequest {
  query: string;
  session_id?: string;
  stream?: boolean;
}

export interface ToolUsage {
  tool: string;
  status: 'started' | 'completed' | 'error';
}
