# AthSys v2.1 Enterprise Architecture Guide

## Overview

AthSys v2.1 is an enterprise-grade Athletics Management System built with industry-leading standards for scalability, reliability, and maintainability.

## Table of Contents

1. [Backend Infrastructure](#backend-infrastructure)
2. [Frontend Architecture](#frontend-architecture)
3. [DevOps & Deployment](#devops--deployment)
4. [Monitoring & Observability](#monitoring--observability)
5. [Testing Strategy](#testing-strategy)
6. [Security Best Practices](#security-best-practices)
7. [Performance Optimization](#performance-optimization)
8. [Disaster Recovery](#disaster-recovery)

---

## Backend Infrastructure

### 1. Enterprise Configuration Management (`config.py`)

**Features:**
- Environment-based configuration (Development, Testing, Production)
- Centralized settings management
- Security credentials handling
- Rate limiting configuration
- Database and Redis connection pooling

**Usage:**
```python
from config import get_config

config = get_config('production')  # or 'development', 'testing'
app.config.from_object(config)
```

**Key Configurations:**
- `RATELIMIT_ENABLED`: Enable API rate limiting (default: True in prod)
- `RATELIMIT_DEFAULT`: Rate limit per endpoint (default: 1000/hour)
- `JWT_ACCESS_TOKEN_EXPIRES`: JWT token expiration (default: 24 hours)
- `DATABASE_POOL_SIZE`: DB connection pool size (default: 20)

### 2. Structured Logging (`logger.py`)

**Features:**
- JSON-formatted logs for production
- Text-formatted logs for development
- Multiple log handlers (console, file)
- Rotating file handler (10MB max per file)
- Structured logging with context

**Usage:**
```python
from logger import get_logger, APILogger, DatabaseLogger, AuditLogger

api_logger = APILogger()
api_logger.log_request('GET', '/api/races', user_id=123)
api_logger.log_response('GET', '/api/races', 200, 45.2)

db_logger = DatabaseLogger()
db_logger.log_query('SELECT * FROM races', 12.5)
db_logger.log_transaction('insert', 'races', user_id=123)

audit_logger = AuditLogger()
audit_logger.log_action('create', 'race', 1, 123, {'name': 'New Race'})
```

**Log Levels:**
- DEBUG: Development and detailed application flow
- INFO: General informational events
- WARNING: Warning events requiring attention
- ERROR: Error events that need handling
- CRITICAL: Critical system failures

**Log Files:**
- `logs/athsys.log`: Main application log
- `logs/test.log`: Test execution log
- Rotates at 10MB, keeps 10 backups

### 3. Request Validation Schema (`schemas.py`)

**Features:**
- Pydantic-based validation
- Type safety and automatic documentation
- Nested schema validation
- Custom validators
- Error details reporting

**Usage:**
```python
from schemas import LoginSchema, UserCreateSchema
from api_service import RequestValidator, APIResponse

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = RequestValidator.validate_json_body()
        validated = RequestValidator.validate_schema(LoginSchema, data)
        
        # validated is now a LoginSchema instance
        return APIResponse.success({ 'token': '...' })
    except ValidationError as e:
        return APIResponse.error(e.message, 400, 'ValidationError', e.details)
```

**Available Schemas:**
- Authentication: `LoginSchema`, `RegisterSchema`, `PasswordChangeSchema`
- Users: `UserCreateSchema`, `UserUpdateSchema`, `UserResponseSchema`
- Athletes: `AthleteCreateSchema`, `AthleteUpdateSchema`
- Races: `RaceCreateSchema`, `RaceUpdateSchema`
- Results: `ResultCreateSchema`, `ResultUpdateSchema`
- Pagination: `PaginationSchema`

### 4. Error Handling (`errors.py`)

**Features:**
- Custom exception hierarchy
- Structured error responses
- Automatic HTTP status code mapping
- Error tracking and logging

**Exception Classes:**
```python
from errors import (
    ValidationError,        # 400
    AuthenticationError,    # 401
    AuthorizationError,     # 403
    NotFoundError,         # 404
    ConflictError,         # 409
    RateLimitError,        # 429
    DatabaseError,         # 500
    ExternalServiceError   # 503
)
```

**Usage:**
```python
from errors import NotFoundError, ValidationError

try:
    race = db.query(Race).filter(Race.id == race_id).first()
    if not race:
        raise NotFoundError('Race')
except NotFoundError as e:
    return APIResponse.error(e.message, e.code, e.error_type), e.code
```

### 5. API Service Layer (`api_service.py`)

**Features:**
- Request validation and parsing
- Authentication token validation
- Role-based access control decorators
- Pagination helpers
- Request/response builders

**Authentication Decorator:**
```python
from api_service import require_auth, require_role

@app.route('/api/races/<race_id>', methods=['PUT'])
@require_auth
@require_role('admin', 'chief_registrar')
def update_race(race_id):
    # request.user_id and request.user_role are available
    pass
```

**Pagination:**
```python
from api_service import PaginationHelper, APIResponse

page, per_page = RequestValidator.get_pagination_params()
races, total = PaginationHelper.paginate(
    db.query(Race).order_by(Race.date.desc()),
    page, per_page
)

return APIResponse.paginated(
    [r.to_dict() for r in races],
    total, page, per_page
)
```

### 6. Monitoring & Metrics (`monitoring.py`)

**Features:**
- Prometheus metrics collection
- Health check endpoints
- Kubernetes liveness/readiness probes
- Performance tracking
- Error rate monitoring

**Metrics Exposed:**
- `athsys_http_requests_total`: Total HTTP requests by method, endpoint, status
- `athsys_http_request_duration_seconds`: Request latency histogram
- `athsys_db_query_duration_seconds`: Database query performance
- `athsys_cache_hits_total` / `athsys_cache_misses_total`: Cache effectiveness
- `athsys_authentication_failures_total`: Auth failures by reason

**Health Endpoints:**
```bash
# Check application health
curl http://localhost:5000/health

# Kubernetes liveness probe
curl http://localhost:5000/live

# Kubernetes readiness probe
curl http://localhost:5000/ready

# Prometheus metrics
curl http://localhost:5000/metrics
```

### 7. API Documentation (`swagger_docs.py`)

**Features:**
- Auto-generated Swagger/OpenAPI docs
- Endpoint documentation templates
- Request/response schema documentation
- Interactive API explorer

**Access:**
- Swagger UI: http://localhost:5000/api/docs
- Raw OpenAPI spec: http://localhost:5000/apispec.json

---

## Frontend Architecture

### 1. State Management with Pinia (`pinia-stores.js`)

**Store Modules:**

**Auth Store:**
```javascript
import { authStore } from './pinia-stores.js';

// Login
await authStore.actions.login('user@example.com', 'password');

// Check if authenticated
if (authStore.state.isAuthenticated) {
    // User is logged in
}

// Get user info
console.log(authStore.state.user);

// Logout
await authStore.actions.logout();
```

**Dashboard Store:**
```javascript
// Load statistics
await dashboardStore.actions.loadStats();
console.log(dashboardStore.state.stats);

// Auto-refresh every 30 seconds
dashboardStore.actions.startAutoRefresh(30000);
```

**UI Store:**
```javascript
// Toggle sidebar
uiStore.actions.toggleSidebar();

// Set theme
uiStore.actions.setTheme('dark');

// Add notification
uiStore.actions.addNotification({
    type: 'success',
    message: 'Operation completed',
    persistent: false
});
```

**API Store:**
```javascript
// Make API calls with automatic auth
const races = await apiStore.get('/races?page=1');
const race = await apiStore.post('/races', { name: 'New Race', ... });
await apiStore.put(`/races/${id}`, { name: 'Updated' });
await apiStore.delete(`/races/${id}`);
```

---

## DevOps & Deployment

### 1. Docker Compose Production (`docker-compose.prod.yml`)

**Services:**
- PostgreSQL: Database with health checks
- Redis: Cache and session store
- NGINX: Load balancer and reverse proxy
- Backend: Flask API (2+ replicas)
- Prometheus: Metrics collection
- Grafana: Dashboard visualization
- Elasticsearch: Log aggregation
- Kibana: Log visualization

**Usage:**
```bash
# Deploy with scaling
BACKEND_REPLICAS=3 docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Scale backend
docker-compose -f docker-compose.prod.yml up -d --scale backend=5
```

### 2. Kubernetes Manifests (`k8s-manifests.yaml`)

**Resources:**
- Namespace for isolation
- ConfigMap for configuration
- Secrets for sensitive data
- Deployments with rolling updates
- Services for load balancing
- PersistentVolumeClaims for data
- HorizontalPodAutoscaler for scaling (3-10 replicas)
- NetworkPolicy for security

**Deployment:**
```bash
# Create namespace and deploy
kubectl apply -f k8s-manifests.yaml

# Scale replicas
kubectl scale deployment athsys-backend -n athsys --replicas=5

# Monitor deployment
kubectl rollout status deployment/athsys-backend -n athsys

# Check logs
kubectl logs -f deployment/athsys-backend -n athsys
```

---

## Monitoring & Observability

### 1. Prometheus Metrics

**Dashboard Metrics:**
```bash
# Request rate
rate(athsys_http_requests_total[5m])

# Error rate
rate(athsys_http_requests_total{status_code=~"5.."}[5m])

# P95 latency
histogram_quantile(0.95, athsys_http_request_duration_seconds_bucket)

# Database query performance
rate(athsys_db_query_duration_seconds_sum[5m]) / rate(athsys_db_query_duration_seconds_count[5m])

# Cache hit rate
rate(athsys_cache_hits_total[5m]) / (rate(athsys_cache_hits_total[5m]) + rate(athsys_cache_misses_total[5m]))
```

### 2. Grafana Dashboards

**Pre-built Dashboards:**
- Application Performance: Request rate, latency, errors
- Database Performance: Query performance, connection pool
- Infrastructure: CPU, memory, disk usage
- Cache Performance: Hit/miss rates, evictions

**Access:**
- URL: http://localhost:3000
- Default credentials: admin/admin

### 3. ELK Stack Logging

**Elasticsearch:**
- Index per day: `logstash-2024.01.15`
- Retention: 30 days
- API: http://localhost:9200

**Kibana Visualization:**
- URL: http://localhost:5601
- Log search and analysis
- Custom dashboards

---

## Testing Strategy

### 1. Unit Tests

**Test Structure:**
```python
# tests/test_unit_auth.py
import pytest
from test_config import BaseAPITest, TestDataFactory

@pytest.mark.unit
class TestAuthentication(BaseAPITest):
    def test_login_success(self, client, db_session):
        # Create test user
        user = TestDataFactory.create_user(db_session, email='test@example.com')
        
        # Test login
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        self.assert_success(response)
        self.assert_has_field(response.get_json(), 'token')
    
    def test_login_invalid_credentials(self, client):
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'wrong'
        })
        
        self.assert_error(response, 401)
```

**Run Tests:**
```bash
# All tests
pytest

# Unit tests only
pytest -m unit

# Specific file
pytest tests/test_unit_auth.py

# With coverage
pytest --cov=src --cov-report=html
```

### 2. Integration Tests

```python
# tests/test_integration_races.py
@pytest.mark.integration
class TestRaceAPIs(BaseAPITest):
    def test_race_lifecycle(self, client, db_session, auth_headers):
        # Create race
        create_resp = client.post('/api/races',
            json={'name': 'Test Race', 'date': '2024-01-15T10:00:00'},
            headers=auth_headers
        )
        self.assert_success(create_resp)
        race_id = create_resp.get_json()['data']['id']
        
        # Read race
        read_resp = client.get(f'/api/races/{race_id}', headers=auth_headers)
        self.assert_success(read_resp)
        
        # Update race
        update_resp = client.put(f'/api/races/{race_id}',
            json={'name': 'Updated Race'},
            headers=auth_headers
        )
        self.assert_success(update_resp)
        
        # Delete race
        delete_resp = client.delete(f'/api/races/{race_id}', headers=auth_headers)
        self.assert_success(delete_resp)
```

### 3. End-to-End Tests

Uses Playwright for testing full user workflows:

```bash
# Install Playwright
npm install -D @playwright/test

# Run E2E tests
npx playwright test

# With UI mode
npx playwright test --ui
```

---

## Security Best Practices

### 1. Authentication & Authorization

**JWT Tokens:**
- Access token expires in 24 hours
- Refresh token expires in 30 days
- Signed with HS256 algorithm
- Always transmitted over HTTPS

**Role-Based Access Control (RBAC):**
- Admin: Full system access
- Chief Registrar: Event management, user management
- Registrar: Athlete registration, race management
- Starter: Start races, record results
- Coach: Manage team athletes
- Athlete: View own results
- Viewer: Read-only access

### 2. HTTP Security Headers

```nginx
# Added automatically by NGINX config
add_header X-Frame-Options "SAMEORIGIN";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
add_header Referrer-Policy "strict-origin-when-cross-origin";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
```

### 3. Rate Limiting

**By Endpoint:**
```python
from flask_limiter import Limiter

# Default: 1000 requests/hour
# Login endpoint: 5 attempts/hour
# API endpoints: flexible based on operation
```

### 4. Data Protection

- PostgreSQL with TLS support
- Redis with password authentication
- Environment variables for secrets
- No sensitive data in logs
- Audit logging for all changes

---

## Performance Optimization

### 1. Database Optimization

**Indexing:**
```sql
-- Indexes for common queries
CREATE INDEX idx_races_date ON races(date DESC);
CREATE INDEX idx_athletes_name ON athletes(first_name, last_name);
CREATE INDEX idx_results_race_id ON results(race_id);
CREATE INDEX idx_registrations_athlete_id ON registrations(athlete_id);
```

**Connection Pooling:**
- PostgreSQL: 20 connections in production
- Connection timeout: 30 seconds
- Idle timeout: 5 minutes

### 2. Caching Strategy

**Redis Caching Layers:**
1. Cache API responses (300 seconds default)
2. Cache race schedule (1 hour)
3. Cache athlete leaderboards (5 minutes)
4. Cache user permissions (1 hour)

**Cache Invalidation:**
- Automatic expiration
- Manual invalidation on updates
- Event-driven invalidation via pubsub

### 3. Query Optimization

**N+1 Query Prevention:**
```python
# Use joins instead of multiple queries
races = db.query(Race).outerjoin(Event).all()

# Use eager loading
athletes = db.query(Athlete).options(
    joinedload(Athlete.user),
    selectinload(Athlete.results)
).all()
```

**Pagination:**
- Default: 20 items per page
- Maximum: 100 items per page
- Always use pagination for large datasets

---

## Disaster Recovery

### 1. Database Backup Strategy

```bash
# Daily backups
0 2 * * * pg_dump athsys_db | gzip > /backups/athsys_$(date +%Y%m%d).sql.gz

# Keep 30 days of backups
find /backups -name "athsys_*.sql.gz" -mtime +30 -delete

# Restore from backup
gunzip /backups/athsys_20240115.sql.gz
psql athsys_db < /backups/athsys_20240115.sql
```

### 2. Kubernetes Persistent Volumes

All critical data stored on PersistentVolumeClaims:
- PostgreSQL: 20GB volume
- Redis: 5GB volume
- Logs: 10GB volume

### 3. High Availability Configuration

**Multi-AZ Deployment:**
```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchLabels:
            app: athsys-backend
        topologyKey: kubernetes.io/hostname
```

**Database Replication:**
- Use PostgreSQL streaming replication
- Primary-replica setup
- Automatic failover with Patroni

---

## Deployment Checklist

- [ ] Set strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Configure database credentials securely
- [ ] Enable HTTPS with valid certificates
- [ ] Set up monitoring and alerting
- [ ] Configure log aggregation (ELK)
- [ ] Set up automated backups
- [ ] Configure CORS for frontend domain
- [ ] Test disaster recovery procedures
- [ ] Set up CI/CD pipeline
- [ ] Configure resource limits and requests
- [ ] Set up horizontal auto-scaling
- [ ] Enable network policies
- [ ] Test failover scenarios

---

## Support & Documentation

- API Documentation: http://<your-domain>/api/docs
- Monitoring Dashboard: http://<your-domain>:3000 (Grafana)
- Log Visualization: http://<your-domain>:5601 (Kibana)
- Metrics: http://<your-domain>:9091 (Prometheus)
