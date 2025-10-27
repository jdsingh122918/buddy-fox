import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { SessionInfo as SessionInfoType } from '@/lib/types';

interface SessionInfoProps {
  sessionInfo: Partial<SessionInfoType> | null;
  duration: number;
}

export const SessionInfo: React.FC<SessionInfoProps> = ({ sessionInfo, duration }) => {
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <Card className="mb-4">
      <div className="p-4 flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Session:</span>
            <Badge variant="outline">
              {sessionInfo?.sessionId?.slice(0, 8) || 'New Session'}
            </Badge>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">⏱️</span>
            <span className="text-sm font-mono">{formatDuration(duration)}</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">🔍</span>
            <span className="text-sm font-mono">
              {sessionInfo?.webSearchesUsed || 0} / {sessionInfo?.maxSearches || 10}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge
            variant={sessionInfo?.sessionId ? "default" : "secondary"}
          >
            {sessionInfo?.sessionId ? "Connected" : "Ready"}
          </Badge>
        </div>
      </div>
    </Card>
  );
};
