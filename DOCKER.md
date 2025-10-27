# Buddy Fox - Docker Deployment Guide

This guide explains how to run Buddy Fox using Docker and Docker Compose.

## Quick Start

### Prerequisites

- Docker 20.10+ installed
- Docker Compose 2.0+ installed
- ANTHROPIC_API_KEY environment variable or .env file

### 1. Set up environment variables

Create a `.env` file in the project root (or copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```env
ANTHROPIC_API_KEY=your_api_key_here
```

### 2. Build and run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

### 3. Access the application

- **Frontend UI**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/api/health

### 4. Stop the application

```bash
# Stop and remove containers
docker-compose down

# Stop, remove containers, and remove volumes
docker-compose down -v
```

## Architecture

The Docker setup consists of two services:

```
┌─────────────────────────────────────────────┐
│  Frontend (nginx:alpine)                    │
│  http://localhost:80                        │
│  - Serves static React build                │
│  - Reverse proxy for API                    │
└──────────────┬──────────────────────────────┘
               │
               │ HTTP
               ▼
┌─────────────────────────────────────────────┐
│  Backend (python:3.12-slim)                 │
│  http://localhost:8000                      │
│  - FastAPI application                      │
│  - Buddy Fox Agent                          │
│  - SSE streaming                            │
└─────────────────────────────────────────────┘
```

## Services

### Backend Service

**Image**: Custom build from `python:3.12-slim`
**Port**: 8000
**Health Check**: `curl http://localhost:8000/api/health`

Features:
- FastAPI server running on uvicorn
- Buddy Fox AI agent with Claude SDK
- Server-Sent Events (SSE) for streaming
- Health check endpoint

### Frontend Service

**Image**: Custom build from `node:20-alpine` (build) + `nginx:alpine` (runtime)
**Port**: 80
**Health Check**: `wget http://localhost/health`

Features:
- React + TypeScript + Vite
- shadcn/ui components
- TailwindCSS styling
- Production-optimized nginx server

## Configuration

### Environment Variables

Backend service supports these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | *required* | Your Anthropic API key |
| `MAX_WEB_SEARCHES` | `10` | Max web searches per session |
| `CLAUDE_MODEL` | `claude-sonnet-4-5-20250929` | Claude model to use |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FORMAT` | `json` | Log format (json or text) |
| `LOG_TO_CONSOLE` | `true` | Enable console logging |
| `ALLOWED_DOMAINS` | *(empty)* | Comma-separated list of allowed domains |
| `BLOCKED_DOMAINS` | *(empty)* | Comma-separated list of blocked domains |

Frontend service:

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | Backend API URL |

### Custom Configuration

Edit `docker-compose.yml` to customize:

```yaml
services:
  backend:
    environment:
      - MAX_WEB_SEARCHES=20
      - LOG_LEVEL=DEBUG
```

## Building Images Separately

### Build backend only

```bash
docker build -t buddy-fox-backend -f backend/Dockerfile .
```

Note: The backend build context is the project root (`.`) because it needs access to both `src/` and `backend/` directories.

### Build frontend only

```bash
cd frontend
docker build -t buddy-fox-frontend .
```

### Run images manually

```bash
# Run backend
docker run -d \
  --name buddy-fox-backend \
  -p 8000:8000 \
  -e ANTHROPIC_API_KEY=your_key_here \
  buddy-fox-backend

# Run frontend
docker run -d \
  --name buddy-fox-frontend \
  -p 80:80 \
  buddy-fox-frontend
```

## Development vs Production

### Development Mode (Current Setup)

The current `docker-compose.yml` includes volume mounts for hot-reload:

```yaml
volumes:
  - ./backend/app:/app/backend/app:ro
  - ./src:/app/src:ro
```

**Pros**: Changes to source code reflect immediately
**Cons**: Requires source code on host machine

### Production Mode

For production, remove the volume mounts and use the copied code:

```yaml
# docker-compose.prod.yml
services:
  backend:
    # Remove volumes section
    restart: always

  frontend:
    restart: always
```

Run production setup:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Health Checks

Both services include health checks:

### Backend Health Check

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2025-10-27T15:00:00Z"
}
```

### Frontend Health Check

```bash
curl http://localhost/health
```

Expected response:
```
OK
```

## Logs and Debugging

### View logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Inspect containers

```bash
# List running containers
docker-compose ps

# Execute commands in backend container
docker-compose exec backend python --version

# Execute commands in frontend container
docker-compose exec frontend nginx -v
```

### Debug backend

```bash
# Access backend shell
docker-compose exec backend /bin/bash

# Check Python environment
docker-compose exec backend python -c "import anthropic; print(anthropic.__version__)"
```

## Networking

Services communicate via the `buddy-fox-network` bridge network:

- Services can reference each other by service name
- Backend is accessible from frontend at `http://backend:8000`
- Frontend is accessible from backend at `http://frontend:80`

## Volumes

The setup doesn't use named volumes by default. For persistent data:

```yaml
services:
  backend:
    volumes:
      - buddy-fox-cache:/app/cache
      - buddy-fox-logs:/app/logs

volumes:
  buddy-fox-cache:
  buddy-fox-logs:
```

## Security Best Practices

1. **Never commit `.env` file** - Use `.env.example` as template
2. **Use secrets in production** - Use Docker secrets or external secret managers
3. **Run as non-root user** - Consider adding USER directive in Dockerfiles
4. **Scan images for vulnerabilities** - Use `docker scan` or Trivy
5. **Update base images regularly** - Keep Python and Node images up to date
6. **Limit resource usage** - Add resource constraints in production

Example with resource limits:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## Troubleshooting

### Port already in use

```bash
# Check what's using port 8000
lsof -i :8000

# Or use different ports
docker-compose up --build -p 8080:8000
```

### Build fails

```bash
# Clear Docker cache
docker builder prune

# Rebuild from scratch
docker-compose build --no-cache
```

### Backend can't connect to Anthropic API

1. Check API key is set: `docker-compose exec backend env | grep ANTHROPIC`
2. Check network connectivity: `docker-compose exec backend curl https://api.anthropic.com`
3. Check logs: `docker-compose logs backend`

### Frontend can't reach backend

1. Verify backend is healthy: `curl http://localhost:8000/api/health`
2. Check CORS settings in `backend/app/main.py`
3. Verify network: `docker-compose exec frontend ping backend`

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Images

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build images
        run: docker-compose build

      - name: Run tests
        run: docker-compose up -d && sleep 10 && curl http://localhost:8000/api/health

      - name: Push to registry
        run: |
          docker tag buddy-fox-backend registry.example.com/buddy-fox-backend:latest
          docker push registry.example.com/buddy-fox-backend:latest
```

## Production Deployment

### Deploy to AWS ECS

1. Push images to ECR
2. Create ECS task definitions
3. Deploy services with load balancer

### Deploy to Kubernetes

```bash
# Convert docker-compose to k8s manifests
kompose convert -f docker-compose.yml

# Apply to cluster
kubectl apply -f .
```

### Deploy to Railway/Render

Both services can be deployed directly using their Docker support.

## Performance Optimization

### Multi-stage builds

The frontend already uses multi-stage builds. Backend can be optimized:

```dockerfile
# Use slim Python image
FROM python:3.12-slim

# Use BuildKit for caching
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

### Layer caching

Order Dockerfile instructions from least to most frequently changing:

1. System dependencies
2. Python/Node dependencies
3. Application code

## Monitoring

### Add Prometheus metrics

```yaml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

### Add Grafana dashboards

```yaml
services:
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [Nginx Docker Documentation](https://hub.docker.com/_/nginx)

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Verify health checks: `curl http://localhost:8000/api/health`
- Review environment variables: `docker-compose config`
- Open an issue on GitHub
