import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Layout } from '@/components/layout/Layout';
import { SessionInfo } from '@/components/session/SessionInfo';
import { ChatContainer } from '@/components/chat/ChatContainer';
import { WebcastTranscriber } from '@/pages/WebcastTranscriber';
import type { SessionInfo as SessionInfoType } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { MessageSquare, Radio } from 'lucide-react';

function ChatPage() {
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
    <div className="max-w-6xl mx-auto">
      <SessionInfo sessionInfo={sessionInfo} duration={duration} />
      <ChatContainer
        sessionInfo={sessionInfo}
        onSessionUpdate={handleSessionUpdate}
      />
    </div>
  );
}

function Navigation() {
  return (
    <div className="bg-white border-b">
      <div className="max-w-6xl mx-auto px-6 py-3">
        <nav className="flex gap-2">
          <Link to="/">
            <Button variant="ghost" className="gap-2">
              <MessageSquare className="w-4 h-4" />
              Chat
            </Button>
          </Link>
          <Link to="/transcribe">
            <Button variant="ghost" className="gap-2">
              <Radio className="w-4 h-4" />
              Webcast Transcriber
            </Button>
          </Link>
        </nav>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Navigation />
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/transcribe" element={<WebcastTranscriber />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
