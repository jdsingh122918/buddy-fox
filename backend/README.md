# Buddy Fox Backend API

FastAPI backend for the Buddy Fox AI web browsing agent with real-time Server-Sent Events streaming.

## Features

- **Real-time Streaming**: Server-Sent Events (SSE) for streaming responses
- **Session Management**: Track and manage multiple agent sessions
- **Statistics**: Monitor usage and performance metrics
- **CORS Enabled**: Ready for local frontend development
- **Auto Documentation**: Interactive API docs at `/docs`

## API Endpoints

### Query
- `POST /api/query` - Query the agent with SSE streaming

### Session Management
- `GET /api/session` - List all sessions
- `GET /api/session/{id}` - Get session info
- `DELETE /api/session/{id}` - Delete session

### Stats & Health
- `GET /api/health` - Health check
- `GET /api/stats` - Get statistics

## Installation

```bash
# From project root
cd backend

# Install dependencies (using uv)
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

## Configuration

Ensure you have `.env` file in the project root with:

```
ANTHROPIC_API_KEY=your_key_here
LOG_FORMAT=json
LOG_LEVEL=INFO
```

## Running the Server

### Development Mode (with hot reload)

```bash
# From backend directory
uvicorn app.main:app --reload --port 8000

# Or from project root
cd backend && python -m uvicorn app.main:app --reload --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/api/health

# Query with SSE streaming
curl -N -H "Content-Type: application/json" \
  -d '{"query":"What is AI?","stream":true}' \
  http://localhost:8000/api/query

# Get session info
curl http://localhost:8000/api/session

# Get stats
curl http://localhost:8000/api/stats
```

### Using httpie

```bash
# Health check
http GET :8000/api/health

# Query
http --stream POST :8000/api/query query="What is AI?" stream:=true

# Get sessions
http GET :8000/api/session
```

### Interactive API Docs

Visit http://localhost:8000/docs for interactive Swagger UI documentation.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── api/                 # API endpoints
│   │   ├── query.py         # Query endpoint with SSE
│   │   ├── session.py       # Session management
│   │   └── stats.py         # Statistics & health
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   └── services/
│       └── agent_service.py # Agent wrapper service
├── requirements.txt
└── README.md
```

## Development

### Adding New Endpoints

1. Create endpoint file in `app/api/`
2. Define router with `APIRouter()`
3. Add routes with appropriate HTTP methods
4. Include router in `app/main.py`

Example:
```python
from fastapi import APIRouter

router = APIRouter(prefix="/my-endpoint", tags=["my-tag"])

@router.get("/")
async def my_endpoint():
    return {"message": "Hello"}
```

### Error Handling

All endpoints include proper error handling with appropriate HTTP status codes:
- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

## Logging

The backend uses Python's logging module with JSON formatting when configured. Logs include:
- Request/response information
- Agent events
- Tool usage
- Errors and exceptions

## Docker Support

```bash
# Build image
docker build -t buddy-fox-backend .

# Run container
docker run -p 8000:8000 --env-file ../.env buddy-fox-backend
```

(Dockerfile to be created)

## Troubleshooting

### Agent not initializing

Make sure `ANTHROPIC_API_KEY` is set in your environment or `.env` file.

### CORS errors

Check that your frontend URL is added to `allow_origins` in `app/main.py`.

### Port already in use

Change the port with `--port` flag:
```bash
uvicorn app.main:app --reload --port 8001
```

## License

Same as main project.
