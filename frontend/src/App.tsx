import { useState, useEffect } from 'react';
import { Layout } from '@/components/layout/Layout';
import { SessionInfo } from '@/components/session/SessionInfo';
import { ChatContainer } from '@/components/chat/ChatContainer';
import type { SessionInfo as SessionInfoType } from '@/lib/types';

function App() {
  const [sessionInfo, setSessionInfo] = useState<Partial<SessionInfoType> | null>(null);
  const [duration, setDuration] = useState(0);

  // Timer for session duration
  useEffect(() => {
    const interval = setInterval(() => {
      setDuration((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const handleSessionUpdate = (info: Partial<SessionInfoType>) => {
    setSessionInfo((prev) => ({
      ...prev,
      ...info,
    }));
  };

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        <SessionInfo sessionInfo={sessionInfo} duration={duration} />
        <ChatContainer
          sessionInfo={sessionInfo}
          onSessionUpdate={handleSessionUpdate}
        />
      </div>
    </Layout>
  );
}

export default App;
