# AthSys Production Deployment Guide

## Prerequisites
- Docker and Docker Compose installed
- PostgreSQL 16 (if not using Docker)
- Redis 7 (if not using Docker)
- Python 3.10+

## Setup Instructions

### 1. Clone Repository
```bash
git clone <repository-url>
cd AthSys_ver1
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your production values
nano .env
```

**IMPORTANT**: Change these in production:
- `SECRET_KEY` - Generate with `python -c "import secrets; print(secrets.token_hex(32))"`
- `JWT_SECRET` - Generate with `python -c "import secrets; print(secrets.token_hex(32))"`
- Database passwords
- Redis password

### 3. Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# Initialize database
docker-compose exec backend python init_db.py

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

Services will be available at:
- Frontend: http://localhost:80 (via nginx)
- Backend API: http://localhost:5000
- PgAdmin: http://localhost:8080
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### 4. Manual Setup (Without Docker)

#### Install Python Dependencies
```bash
cd src/backend
pip install -r requirements.txt
```

#### Setup PostgreSQL
```bash
# Create database
createdb -U postgres athsys_db

# Create user
psql -U postgres -c "CREATE USER athsys_user WITH PASSWORD 'athsys_pass';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE athsys_db TO athsys_user;"
```

#### Setup Redis
```bash
# Install Redis (Ubuntu/Debian)
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server

# Set password
redis-cli
> CONFIG SET requirepass "athsys_redis_pass"
> AUTH athsys_redis_pass
> exit
```

#### Initialize Database
```bash
cd src/backend
python init_db.py
```

#### Start Backend
```bash
cd src/backend
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

### 5. Database Migrations with Alembic

```bash
cd src/backend

# Initialize Alembic (first time only)
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### 6. Production Checklist

- [ ] Change all default passwords
- [ ] Set strong SECRET_KEY and JWT_SECRET
- [ ] Enable HTTPS (configure nginx with SSL)
- [ ] Set DEBUG=False
- [ ] Configure firewall (only expose necessary ports)
- [ ] Setup regular database backups
- [ ] Configure monitoring and logging
- [ ] Test rate limiting
- [ ] Review and update CORS settings
- [ ] Setup email notifications
- [ ] Configure Redis persistence
- [ ] Enable database connection pooling

### 7. Default Login Credentials

After running `init_db.py`, you can login with:

- **Admin**: admin@athsys.com / Admin@123
- **Chief Registrar**: chief@athsys.com / Chief@123
- **Registrar**: registrar@athsys.com / Registrar@123
- **Starter**: starter@athsys.com / Starter@123
- **Athlete**: john@athsys.com / Athlete@123
- **Coach**: sarah@athsys.com / Coach@123
- **Viewer**: viewer@athsys.com / Viewer@123

**IMPORTANT**: Change these passwords immediately in production!

### 8. Backup and Restore

#### Backup
```bash
# PostgreSQL backup
docker-compose exec postgres pg_dump -U athsys_user athsys_db > backup.sql

# Or without Docker
pg_dump -U athsys_user athsys_db > backup.sql
```

#### Restore
```bash
# PostgreSQL restore
docker-compose exec -T postgres psql -U athsys_user athsys_db < backup.sql

# Or without Docker
psql -U athsys_user athsys_db < backup.sql
```

### 9. Monitoring

#### Check Service Health
```bash
# Backend health
curl http://localhost:5000/health

# Redis health
redis-cli -a athsys_redis_pass ping

# PostgreSQL health
docker-compose exec postgres pg_isready -U athsys_user
```

#### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f redis
```

### 10. Troubleshooting

#### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check connection string in .env
cat .env | grep DATABASE_URL

# Test connection manually
docker-compose exec postgres psql -U athsys_user -d athsys_db
```

#### Redis Connection Issues
```bash
# Check if Redis is running
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli -a athsys_redis_pass ping
```

#### Backend Not Starting
```bash
# Check logs
docker-compose logs backend

# Restart backend
docker-compose restart backend

# Rebuild if needed
docker-compose build backend
docker-compose up -d backend
```

### 11. Performance Tuning

#### PostgreSQL
- Increase `max_connections` if needed
- Configure `shared_buffers` (25% of RAM)
- Enable query logging for slow queries

#### Redis
- Enable AOF persistence for data durability
- Configure maxmemory policy
- Monitor memory usage

#### Backend
- Increase gunicorn workers (2-4 × CPU cores)
- Enable response compression
- Configure connection pooling

### 12. Security Hardening

1. **Firewall Rules**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw deny 5432/tcp  # PostgreSQL - only from localhost
   sudo ufw deny 6379/tcp  # Redis - only from localhost
   ```

2. **Nginx Configuration**
   - Enable SSL/TLS
   - Add security headers
   - Configure rate limiting

3. **Database Security**
   - Use strong passwords
   - Limit user privileges
   - Enable SSL connections

4. **Application Security**
   - Keep dependencies updated
   - Enable audit logging
   - Regular security scans

## Support

For issues or questions, contact the development team.
