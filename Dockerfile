# Multi-stage build for AthSys Athletics Management System

# Stage 1: Backend Builder
FROM python:3.11-slim as backend-builder

WORKDIR /app/backend

# Install system dependencies for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip first
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements and install
COPY src/backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt --no-deps 2>&1 | head -50 || true && \
    pip install --no-cache-dir -r requirements.txt 2>&1 | tail -20 || pip install --no-cache-dir flask flask-cors psycopg2-binary python-dotenv gunicorn

# Copy backend source
COPY src/backend/ ./

# Stage 2: Frontend
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend

# Copy frontend files
COPY src/frontend/ ./

# No build step needed for vanilla HTML/CSS/JS

# Stage 3: Production Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime system dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    postgresql-client \
    redis-tools \
    libpq5 \
    libjpeg62-turbo \
    libfreetype6 \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy backend
COPY --from=backend-builder /app/backend /app/backend

# Copy frontend
COPY --from=frontend-builder /app/frontend /app/frontend

# Set working directory
WORKDIR /app/backend

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/livez || exit 1

# Expose port
EXPOSE 5000

# Run application with increased timeout and graceful shutdown
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--timeout", "120", "--graceful-timeout", "30", "--keep-alive", "5", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy backend application
COPY --from=backend-builder /app/backend /app/backend

# Copy docker entrypoint script
COPY src/backend/docker-entrypoint.sh /app/backend/docker-entrypoint.sh
RUN chmod +x /app/backend/docker-entrypoint.sh

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

# Health check - use lightweight liveness endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/livez || exit 1

# Set working directory to backend
WORKDIR /app/backend

# Use entrypoint script for auto-initialization
CMD ["/app/backend/docker-entrypoint.sh"]
