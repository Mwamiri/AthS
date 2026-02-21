# Multi-stage build for AthSys Athletics Management System

# Stage 1: Backend Development
FROM python:3.11-slim as backend-builder

WORKDIR /app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install dependencies
COPY src/backend/requirements.txt* ./
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; else pip install flask flask-cors psycopg2-binary python-dotenv gunicorn; fi

# Copy backend source
COPY src/backend/ ./

# Stage 2: Frontend Build
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY src/frontend/package*.json* ./
RUN if [ -f package.json ]; then npm install --production || true; else echo "{}"; fi

# Copy frontend source
COPY src/frontend/ ./

# No build step needed for simple HTML/CSS/JS

# Stage 3: Production Image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy backend application
COPY --from=backend-builder /app/backend /app/backend

# Copy frontend source files
COPY --from=frontend-builder /app/frontend /app/frontend

# Copy configuration files
COPY config/ /app/config/
COPY docker-compose.yml /app/

# Copy self-healing scripts
COPY self_healing/ /app/self_healing/

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/backups /app/results

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=5000
ENV NODE_ENV=production

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Set working directory to backend
WORKDIR /app/backend

# Default command - use Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
