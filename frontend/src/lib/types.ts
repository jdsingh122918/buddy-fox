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

// Transcription types

export interface TranscriptionChunk {
  text: string;
  confidence: number;
  is_final: boolean;
  timestamp: number;
  audio_start?: number;
  audio_end?: number;
}

export interface TranscriptionEvent {
  type: 'session_started' | 'browser_ready' | 'audio_started' | 'transcription_connecting' | 'transcription_ready' | 'audio_ready' | 'transcription' | 'error' | 'complete';
  message?: string;
  session_id?: string;
  webcast_url?: string;
  language?: string;
  transcription?: TranscriptionChunk;
  error?: string;
  summary?: {
    session_id: string;
    total_duration_seconds: number;
    chunks_transcribed: number;
  };
}

export interface WebcastTranscriptionRequest {
  webcast_url: string;
  session_id?: string;
  language?: string;
}

export interface TranscriptionSessionInfo {
  session_id: string;
  webcast_url: string;
  started_at: Date;
  status: string;
  total_duration_seconds: number;
  chunks_transcribed: number;
  language: string;
}
