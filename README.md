# 🦊 Buddy Fox AI Web Browsing Agent

An AI-powered web browsing agent with real-time webcast transcription capabilities.

## Features

- 🔍 **AI Web Browsing**: Intelligent web search and content analysis
- 🎙️ **Real-time Transcription**: Live webcast transcription using AssemblyAI
- 💬 **Chat Interface**: Interactive chat with the AI agent
- 🌐 **Browser Integration**: Automated web navigation
- 📊 **Session Management**: Track and manage conversation sessions

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd buddy-fox
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Configure environment variables**
   
   Copy `.env.example` to `.env` and add your API keys:
   ```bash
   cp .env.example .env
   ```
   
   Required environment variables:
   ```bash
   # Required
   ANTHROPIC_API_KEY=your_anthropic_api_key
   
   # Optional - for transcription feature
   ASSEMBLYAI_API_KEY=your_assemblyai_api_key
   ENABLE_TRANSCRIPTION=true
   TRANSCRIPTION_CHUNK_SIZE_MS=1000
   ```

---

## Running the Application

### Option 1: Using the startup scripts (Recommended)

**Terminal 1 - Backend:**
```bash
./start-backend.sh
```

**Terminal 2 - Frontend:**
```bash
./start-frontend.sh
```

### Option 2: Manual start

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

---

## Access the Application

- **Frontend UI**: http://localhost:3000/
- **Chat Interface**: http://localhost:3000/
- **Webcast Transcriber**: http://localhost:3000/transcribe
- **Backend API**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

---

## Project Structure

```
buddy-fox/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Pydantic models
│   │   └── services/     # Business logic
│   └── requirements.txt
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom hooks
│   │   ├── pages/        # Page components
│   │   └── lib/          # Utilities
│   └── package.json
├── src/                  # Core agent logic
│   ├── agent.py         # Main agent implementation
│   ├── config.py        # Configuration management
│   └── tools.py         # Tool definitions
├── requirements.txt      # Root Python dependencies
└── .env                 # Environment variables
```

---

## Environment Variables

### Core Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | - | **Required**: Your Anthropic API key |
| `CLAUDE_MODEL` | `claude-sonnet-4-5-20250929` | Claude model to use |
| `MAX_WEB_SEARCHES` | `10` | Max web searches per session |

### Transcription Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `ASSEMBLYAI_API_KEY` | - | AssemblyAI API key (for transcription) |
| `ENABLE_TRANSCRIPTION` | `false` | Enable transcription feature |
| `TRANSCRIPTION_CHUNK_SIZE_MS` | `1000` | Audio chunk size in milliseconds |
| `TRANSCRIPTION_LANGUAGE` | `en` | Language code for transcription |
| `MAX_AUDIO_DURATION_SECONDS` | `3600` | Max transcription duration |

### Logging Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FORMAT` | `json` | Log format (json or text) |
| `LOG_TO_CONSOLE` | `true` | Enable console logging |

---

## API Endpoints

### Chat & Query
- `POST /api/query` - Send query to agent (returns SSE stream)
- `GET /api/session/{session_id}` - Get session info
- `DELETE /api/session/{session_id}` - Delete session
- `GET /api/sessions` - List all sessions

### Webcast Transcription
- `POST /api/webcast/transcribe` - Start transcription (returns SSE stream)
- `WebSocket /api/webcast/audio/{session_id}` - Upload audio chunks
- `GET /api/webcast/session/{session_id}` - Get transcription session info
- `DELETE /api/webcast/session/{session_id}` - Stop transcription
- `GET /api/webcast/sessions` - List active transcription sessions

### System
- `GET /` - API information
- `GET /api/health` - Health check
- `GET /api/stats` - Usage statistics

---

## Troubleshooting

### Module Not Found Error

If you see `ModuleNotFoundError: No module named 'claude_agent_sdk'`:

```bash
# Install all dependencies
pip install -r requirements.txt
```

### Port Already in Use

If ports 3000 or 8000 are already in use:

```bash
# Find and kill processes on ports
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### CORS Issues

The backend is configured to accept requests from `localhost:3000`. If you change the frontend port, update `backend/app/main.py` CORS settings.

---

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Formatting
```bash
# Python
black .
ruff check .

# TypeScript
cd frontend
npm run lint
```

---

## Docker Support

```bash
# Development
docker-compose -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.prod.yml up
```

---

## License

MIT License - See LICENSE file for details

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## Support

For issues and questions, please open an issue on GitHub.
