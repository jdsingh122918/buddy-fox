# Backend Dockerfile for Buddy Fox API
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package management
RUN pip install --no-cache-dir uv

# Copy project dependency files
COPY pyproject.toml ./
COPY requirements.txt ./backend/

# Copy source code (needed as backend imports from src/)
COPY src/ ./src/

# Copy backend application
COPY backend/ ./backend/

# Install dependencies using uv
RUN uv pip install --system -r backend/requirements.txt
RUN uv pip install --system -e .

# Set Python path to include src directory
ENV PYTHONPATH=/app:/app/src:$PYTHONPATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
