# Buddy Fox UI - Implementation Plan

## Overview

Create a modern web interface for the Buddy Fox AI web browsing agent with real-time streaming responses, session management, and comprehensive observability.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                               │
├─────────────────────────────────────────────────────────────┤
│  React + TypeScript + shadcn/ui + TailwindCSS              │
│  - Chat Interface                                           │
│  - Real-time Streaming Display                              │
│  - Session Management                                        │
│  - Statistics Dashboard                                      │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTP/SSE
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
├─────────────────────────────────────────────────────────────┤
│  - REST API Endpoints                                       │
│  - Server-Sent Events (SSE) for streaming                   │
│  - WebSocket support (optional)                             │
│  - CORS handling                                            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              Buddy Fox Agent (Python)                        │
├─────────────────────────────────────────────────────────────┤
│  - WebBrowsingAgent                                         │
│  - Session Management                                        │
│  - Cache                                                     │
│  - Structured Logging                                        │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

### Frontend
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite (fast, modern)
- **UI Components**: shadcn/ui (accessible, customizable)
- **Styling**: TailwindCSS
- **Icons**: Lucide React (used by shadcn)
- **State Management**: React Context + Hooks
- **HTTP Client**: Fetch API with EventSource for SSE
- **Routing**: React Router (optional, for multi-page)

### Backend
- **Framework**: FastAPI (async Python web framework)
- **Streaming**: Server-Sent Events (SSE)
- **CORS**: FastAPI CORS middleware
- **Validation**: Pydantic models
- **Documentation**: Auto-generated OpenAPI docs

### Development Tools
- **Frontend Dev Server**: Vite dev server
- **Backend Dev Server**: Uvicorn with hot reload
- **Package Manager**: npm/pnpm for frontend, uv for backend
- **Linting**: ESLint + Prettier (frontend)

## Features

### Core Features (MVP)
1. **Chat Interface**
   - Text input for queries
   - Send button + Enter key support
   - Message history display
   - Streaming responses in real-time
   - Loading states and indicators

2. **Response Display**
   - Markdown rendering
   - Code syntax highlighting
   - URL links (clickable)
   - Typing animation for streaming

3. **Session Management**
   - Current session info
   - Session statistics (searches used, duration)
   - Clear session button
   - Session persistence (optional)

4. **Agent Status**
   - Connected/disconnected indicator
   - Tool usage display (WebSearch, WebFetch)
   - Response time metrics

### Enhanced Features (Phase 2)
1. **Statistics Dashboard**
   - Query history
   - Cache hit rate
   - Performance metrics
   - Cost tracking

2. **Settings Panel**
   - Model selection
   - Max searches configuration
   - Enable/disable tools
   - Theme toggle (light/dark)

3. **Source Citations**
   - Show URLs being fetched
   - Display search results
   - Link to sources

## UI Design

### Layout

```
┌──────────────────────────────────────────────────────────┐
│  Header: Buddy Fox 🦊                     [Settings] [📊] │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │ Session: session_123    ⏱️ 2m 34s    🔍 3/10   │    │
│  └─────────────────────────────────────────────────┘    │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Chat Messages Area                              │    │
│  │                                                   │    │
│  │  [User]: What are AI agents?                     │    │
│  │                                                   │    │
│  │  [🦊 Agent]: [Streaming response...]             │    │
│  │  Using WebSearch... ✓                            │    │
│  │  Fetching 3 sources... ⏳                        │    │
│  │                                                   │    │
│  │  AI agents are autonomous software...           │    │
│  │  [More content]                                  │    │
│  │                                                   │    │
│  └─────────────────────────────────────────────────┘    │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 💬 Ask me anything...              [Send →]      │    │
│  └─────────────────────────────────────────────────┘    │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### Color Scheme
- **Primary**: Blue (for agent responses, actions)
- **Secondary**: Orange/Fox color (for branding)
- **Success**: Green (for completed actions)
- **Warning**: Yellow (for warnings)
- **Error**: Red (for errors)
- **Background**: Light/Dark mode support

## Component Structure

### Frontend Components (shadcn/ui based)

```
src/
├── components/
│   ├── ui/                    # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   ├── badge.tsx
│   │   ├── scroll-area.tsx
│   │   ├── separator.tsx
│   │   ├── dialog.tsx
│   │   └── ...
│   │
│   ├── chat/
│   │   ├── ChatContainer.tsx   # Main chat wrapper
│   │   ├── MessageList.tsx     # Displays all messages
│   │   ├── Message.tsx         # Individual message component
│   │   ├── ChatInput.tsx       # Input field + send button
│   │   └── StreamingIndicator.tsx
│   │
│   ├── session/
│   │   ├── SessionInfo.tsx     # Session statistics display
│   │   ├── SessionControls.tsx # Clear, save, etc.
│   │   └── ToolUsageIndicator.tsx
│   │
│   ├── dashboard/
│   │   ├── StatsDashboard.tsx  # Overall stats
│   │   ├── MetricsCard.tsx     # Individual metric display
│   │   └── QueryHistory.tsx    # Past queries
│   │
│   ├── layout/
│   │   ├── Header.tsx          # App header
│   │   ├── Sidebar.tsx         # Optional sidebar
│   │   └── Layout.tsx          # Main layout wrapper
│   │
│   └── settings/
│       ├── SettingsDialog.tsx  # Settings modal
│       └── ConfigForm.tsx      # Configuration form
│
├── hooks/
│   ├── useAgent.ts             # Agent API communication
│   ├── useStreaming.ts         # SSE streaming hook
│   ├── useSession.ts           # Session management
│   └── useWebSocket.ts         # Optional WebSocket
│
├── lib/
│   ├── api.ts                  # API client
│   ├── types.ts                # TypeScript types
│   └── utils.ts                # Utility functions
│
├── contexts/
│   ├── AgentContext.tsx        # Global agent state
│   └── ThemeContext.tsx        # Theme management
│
├── App.tsx                      # Root component
├── main.tsx                     # Entry point
└── index.css                    # Global styles + Tailwind
```

## API Design

### Backend API Endpoints

#### 1. Query Endpoint (POST /api/query)
**Request:**
```json
{
  "query": "What are AI agents?",
  "session_id": "optional-session-id",
  "stream": true
}
```

**Response (SSE Stream):**
```
event: chunk
data: {"type": "text", "content": "AI agents are..."}

event: tool_use
data: {"type": "tool", "tool": "WebSearch", "status": "started"}

event: tool_complete
data: {"type": "tool", "tool": "WebSearch", "status": "completed"}

event: chunk
data: {"type": "text", "content": "more content..."}

event: complete
data: {"type": "complete", "session_stats": {...}}
```

#### 2. Session Endpoints
- **GET /api/session/{session_id}** - Get session info
- **DELETE /api/session/{session_id}** - Clear session
- **GET /api/sessions** - List all sessions

#### 3. Stats Endpoints
- **GET /api/stats** - Get overall statistics
- **GET /api/stats/cache** - Get cache statistics
- **GET /api/stats/metrics** - Get performance metrics

#### 4. Config Endpoints
- **GET /api/config** - Get current configuration
- **PUT /api/config** - Update configuration

#### 5. Health Check
- **GET /api/health** - Health check endpoint

### Data Models

```typescript
// Frontend Types
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: {
    duration?: number;
    toolsUsed?: string[];
  };
}

interface SessionInfo {
  sessionId: string;
  startedAt: Date;
  webSearchesUsed: number;
  webFetchesUsed: number;
  maxSearches: number;
  duration: number;
  messageCount: number;
}

interface StreamEvent {
  type: 'text' | 'tool' | 'complete' | 'error';
  content?: string;
  tool?: string;
  status?: string;
  error?: string;
  sessionStats?: SessionInfo;
}
```

## Project Structure

```
buddy-fox/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── query.py       # Query endpoints
│   │   │   ├── session.py     # Session endpoints
│   │   │   └── stats.py       # Stats endpoints
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py     # Pydantic models
│   │   └── services/
│   │       ├── __init__.py
│   │       └── agent_service.py  # Agent wrapper
│   ├── requirements.txt
│   └── README.md
│
├── frontend/                   # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/        # (as detailed above)
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── contexts/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── components.json         # shadcn config
│   └── README.md
│
├── src/                        # Existing Python agent code
├── examples/
├── docs/
├── UI_IMPLEMENTATION_PLAN.md   # This file
└── README.md
```

## Implementation Phases

### Phase 1: Backend Setup (MVP)
1. Create FastAPI application structure
2. Implement query endpoint with SSE streaming
3. Integrate with existing Buddy Fox agent
4. Add session management endpoints
5. Setup CORS for local development
6. Test streaming with curl/Postman

**Deliverable**: Working backend API that can stream agent responses

### Phase 2: Frontend Setup (MVP)
1. Initialize Vite + React + TypeScript project
2. Setup TailwindCSS
3. Install and configure shadcn/ui
4. Create basic layout components
5. Setup routing (if needed)

**Deliverable**: Frontend boilerplate with styling system

### Phase 3: Core UI Components (MVP)
1. Build ChatContainer and MessageList
2. Implement Message component with markdown
3. Create ChatInput with send functionality
4. Build SessionInfo display
5. Add loading states and indicators

**Deliverable**: Working chat interface (no backend connection)

### Phase 4: Integration (MVP)
1. Create API client in frontend
2. Implement SSE streaming hook
3. Connect ChatInput to API
4. Display streaming responses
5. Update session info in real-time
6. Handle errors gracefully

**Deliverable**: Fully functional chat interface with streaming

### Phase 5: Enhanced Features
1. Add statistics dashboard
2. Implement settings panel
3. Add source citations display
4. Implement query history
5. Add cache statistics
6. Theme switching

**Deliverable**: Production-ready application

### Phase 6: Polish & Deploy
1. Responsive design improvements
2. Accessibility enhancements
3. Performance optimization
4. Add loading skeletons
5. Error boundaries
6. Documentation
7. Docker setup
8. Deployment guide

**Deliverable**: Deployment-ready application

## Development Workflow

### Local Development

```bash
# Terminal 1: Backend
cd backend
uv pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

Access:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Environment Variables

**Backend (.env):**
```
ANTHROPIC_API_KEY=your_key_here
LOG_FORMAT=json
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5173
```

**Frontend (.env):**
```
VITE_API_URL=http://localhost:8000
```

## Security Considerations

1. **API Key Protection**: Never expose Anthropic API key to frontend
2. **CORS**: Properly configure CORS origins
3. **Rate Limiting**: Add rate limiting to prevent abuse
4. **Input Validation**: Validate all user inputs
5. **Session Security**: Use secure session IDs
6. **Error Handling**: Don't expose internal errors to users

## Performance Optimization

1. **Streaming**: Use SSE for real-time updates without polling
2. **Caching**: Leverage agent's caching system
3. **Code Splitting**: Lazy load routes and heavy components
4. **Debouncing**: Debounce input for better UX
5. **Virtual Scrolling**: For long message histories

## Testing Strategy

### Backend Tests
- Unit tests for API endpoints
- Integration tests with mock agent
- Load testing for streaming

### Frontend Tests
- Component unit tests (Vitest + React Testing Library)
- Integration tests for user flows
- E2E tests (Playwright optional)

## Success Metrics

1. **Functionality**
   - ✅ Users can send queries and receive streaming responses
   - ✅ Real-time tool usage indicators
   - ✅ Session statistics display correctly
   - ✅ Error handling works properly

2. **Performance**
   - ✅ First response within 1 second
   - ✅ Smooth streaming without lag
   - ✅ UI remains responsive during streaming

3. **UX**
   - ✅ Intuitive interface
   - ✅ Clear feedback for all actions
   - ✅ Accessible (keyboard navigation, screen readers)
   - ✅ Responsive on mobile/tablet/desktop

## Future Enhancements

1. **Authentication**: User login and multi-user support
2. **Workspace**: Multiple conversation threads
3. **Export**: Export conversations as PDF/MD
4. **Sharing**: Share conversations via link
5. **Voice Input**: Speech-to-text support
6. **Collaboration**: Real-time collaboration features
7. **Analytics**: Advanced usage analytics
8. **Plugins**: Plugin system for extensions

## Timeline Estimate

- **Phase 1** (Backend MVP): 1-2 days
- **Phase 2** (Frontend Setup): 0.5 days
- **Phase 3** (Core UI): 1-2 days
- **Phase 4** (Integration): 1 day
- **Phase 5** (Enhanced Features): 2-3 days
- **Phase 6** (Polish): 1-2 days

**Total**: ~7-10 days for full implementation

## Next Steps

1. ✅ Review and approve this plan
2. Create backend directory structure
3. Setup FastAPI application
4. Create frontend with Vite + React
5. Begin Phase 1 implementation

---

## Questions to Resolve

1. Do we want authentication/multi-user support?
2. Should we persist conversations to database?
3. Do we need real-time collaboration features?
4. Mobile-first or desktop-first design?
5. Deploy to cloud or local only?

