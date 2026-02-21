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
DB_INITIALIZED=$(python -c "
try:
    from models import engine, User
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    # Check if users table exists and has data
    if 'users' in tables:
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine)
        session = Session()
        user_count = session.query(User).count()
        session.close()
        print('yes' if user_count > 0 else 'no')
    else:
        print('no')
except Exception as e:
    print('no')
" 2>/dev/null || echo "no")

if [ "$DB_INITIALIZED" = "no" ]; then
    echo "📊 Initializing database with demo data..."
    python init_db.py
    echo "✅ Database initialized successfully!"
else
    echo "✅ Database already initialized, skipping..."
fi

# Start the application
echo "🌐 Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:${PORT:-5000} \
    --workers 4 \
    --timeout 120 \
    --access-logfile /app/logs/access.log \
    --error-logfile /app/logs/error.log \
    --log-level info \
    app:app
