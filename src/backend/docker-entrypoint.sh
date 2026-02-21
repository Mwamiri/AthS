#!/bin/bash
set -e

echo "🚀 Starting AthSys Backend..."

# Change to backend directory for Python imports
cd /app/backend

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
while ! pg_isready -h postgres -p 5432 -U ${DB_USER:-athsys_user} > /dev/null 2>&1; do
    sleep 1
done
echo "✅ PostgreSQL is ready!"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis..."
while ! redis-cli -h redis -p 6379 -a ${REDIS_PASSWORD:-athsys_redis_pass} ping > /dev/null 2>&1; do
    sleep 1
done
echo "✅ Redis is ready!"

# Check if database needs initialization
echo "🔍 Checking database status..."
DB_INITIALIZED="no"

# Try to check if database is initialized, but don't fail if it errors
if python -c "from models import engine, User; from sqlalchemy import inspect; inspector = inspect(engine); tables = inspector.get_table_names(); from sqlalchemy.orm import sessionmaker; Session = sessionmaker(bind=engine); session = Session(); user_count = session.query(User).count(); session.close(); exit(0 if user_count > 0 else 1)" 2>/dev/null; then
    DB_INITIALIZED="yes"
    echo "✅ Database already initialized, skipping..."
else
    echo "📊 Initializing database with demo data..."
    if python init_db.py 2>&1; then
        echo "✅ Database initialized successfully!"
    else
        echo "⚠️  Database initialization encountered issues, but continuing..."
    fi
fi

# Start the application
echo "🌐 Starting Gunicorn server on port ${PORT:-5000}..."
echo "📝 Logs will be written to /app/logs/"

# Ensure log directory exists and is writable
mkdir -p /app/logs
chmod 777 /app/logs

# Start Gunicorn with reduced workers for better stability
exec gunicorn --bind 0.0.0.0:${PORT:-5000} \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output \
    app:app
