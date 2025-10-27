# Buddy Fox - Docker Makefile
# Simplifies common Docker operations

.PHONY: help build up down logs clean dev prod restart ps health test

# Default target
help:
	@echo "Buddy Fox Docker Management"
	@echo ""
	@echo "Available targets:"
	@echo "  make build      - Build all Docker images"
	@echo "  make up         - Start all services (production mode)"
	@echo "  make down       - Stop all services"
	@echo "  make logs       - Show logs from all services"
	@echo "  make clean      - Remove all containers, images, and volumes"
	@echo "  make dev        - Start services in development mode (hot-reload)"
	@echo "  make prod       - Start services in production mode"
	@echo "  make restart    - Restart all services"
	@echo "  make ps         - List running services"
	@echo "  make health     - Check health of all services"
	@echo "  make test       - Run health checks and basic tests"
	@echo ""
	@echo "Backend specific:"
	@echo "  make backend-logs    - Show backend logs"
	@echo "  make backend-shell   - Access backend shell"
	@echo "  make backend-restart - Restart backend service"
	@echo ""
	@echo "Frontend specific:"
	@echo "  make frontend-logs    - Show frontend logs"
	@echo "  make frontend-shell   - Access frontend shell"
	@echo "  make frontend-restart - Restart frontend service"

# Build all images
build:
	@echo "Building all Docker images..."
	docker-compose build

# Start services (production)
up:
	@echo "Starting services in production mode..."
	docker-compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

# Stop services
down:
	@echo "Stopping all services..."
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Clean everything
clean:
	@echo "Removing all containers, images, and volumes..."
	docker-compose down -v --rmi all
	@echo "Cleanup complete!"

# Development mode
dev:
	@echo "Starting services in development mode (hot-reload)..."
	docker-compose -f docker-compose.dev.yml up --build
	@echo "Development servers started!"
	@echo "Frontend: http://localhost:5173"
	@echo "Backend: http://localhost:8000"

# Production mode
prod:
	@echo "Starting services in production mode..."
	docker-compose -f docker-compose.prod.yml up -d --build
	@echo "Production services started!"
	@echo "Frontend: http://localhost"
	@echo "Backend: http://localhost:8000"

# Restart services
restart:
	@echo "Restarting services..."
	docker-compose restart
	@echo "Services restarted!"

# List running services
ps:
	docker-compose ps

# Health check
health:
	@echo "Checking service health..."
	@echo "\nBackend health:"
	@curl -f http://localhost:8000/api/health 2>/dev/null && echo "" || echo "Backend is not healthy"
	@echo "\nFrontend health:"
	@curl -f http://localhost/health 2>/dev/null && echo "" || echo "Frontend is not healthy"

# Run tests
test: health
	@echo "\nRunning basic tests..."
	@echo "Testing backend API..."
	@curl -f http://localhost:8000/docs 2>/dev/null > /dev/null && echo "✓ Backend API docs accessible" || echo "✗ Backend API docs not accessible"
	@echo "Testing frontend..."
	@curl -f http://localhost 2>/dev/null > /dev/null && echo "✓ Frontend accessible" || echo "✗ Frontend not accessible"

# Backend specific targets
backend-logs:
	docker-compose logs -f backend

backend-shell:
	docker-compose exec backend /bin/bash

backend-restart:
	docker-compose restart backend

# Frontend specific targets
frontend-logs:
	docker-compose logs -f frontend

frontend-shell:
	docker-compose exec frontend /bin/sh

frontend-restart:
	docker-compose restart frontend

# Quick rebuild and restart
rebuild:
	@echo "Rebuilding and restarting services..."
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d
	@echo "Services rebuilt and restarted!"
