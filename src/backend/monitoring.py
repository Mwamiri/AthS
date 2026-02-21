"""
Application Monitoring and Metrics
Prometheus metrics collection and health checks
"""

from flask import Blueprint, jsonify, request
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from datetime import datetime
import time
import os


# Define metrics
request_count = Counter(
    'athsys_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

request_duration = Histogram(
    'athsys_http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0)
)

request_size = Histogram(
    'athsys_http_request_size_bytes',
    'HTTP request size',
    ['method', 'endpoint']
)

response_size = Histogram(
    'athsys_http_response_size_bytes',
    'HTTP response size',
    ['method', 'endpoint']
)

db_query_duration = Histogram(
    'athsys_db_query_duration_seconds',
    'Database query duration',
    ['operation', 'table'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0)
)

db_connection_pool = Gauge(
    'athsys_db_connection_pool_size',
    'Database connection pool size'
)

cache_hits = Counter(
    'athsys_cache_hits_total',
    'Cache hits',
    ['cache_name']
)

cache_misses = Counter(
    'athsys_cache_misses_total',
    'Cache misses',
    ['cache_name']
)

authentication_failures = Counter(
    'athsys_authentication_failures_total',
    'Authentication failures',
    ['reason']
)

rate_limit_exceeded = Counter(
    'athsys_rate_limit_exceeded_total',
    'Rate limit exceeded',
    ['endpoint']
)

active_users = Gauge(
    'athsys_active_users',
    'Number of active users'
)


def init_metrics(app):
    """Initialize metrics blueprint and middleware"""
    
    metrics_bp = Blueprint('metrics', __name__)
    
    @metrics_bp.route('/metrics', methods=['GET'])
    def metrics():
        """Expose Prometheus metrics"""
        return generate_latest()
    
    @metrics_bp.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        from datetime import datetime
        
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.1',
            'checks': {
                'database': check_database_health(),
                'redis': check_redis_health(),
                'api': 'ok'
            }
        }
        
        # Determine overall health
        all_healthy = all(v == 'ok' for v in health_status['checks'].values())
        health_status['status'] = 'healthy' if all_healthy else 'degraded'
        
        code = 200 if all_healthy else 503
        return jsonify(health_status), code
    
    @metrics_bp.route('/ready', methods=['GET'])
    def readiness():
        """Kubernetes readiness probe"""
        # Check if critical systems are ready
        db_ok = check_database_health() == 'ok'
        
        status = {'ready': db_ok}
        code = 200 if db_ok else 503
        return jsonify(status), code
    
    @metrics_bp.route('/live', methods=['GET'])
    def liveness():
        """Kubernetes liveness probe"""
        # Simple check that app is running
        return jsonify({'alive': True}), 200
    
    app.register_blueprint(metrics_bp)
    
    # Register before_request and after_request handlers
    @app.before_request
    def before_request():
        request.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """Record request metrics"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Record metrics (skip metrics and static endpoints)
            if not request.path.startswith('/metrics') and not request.path.startswith('/static'):
                request_count.labels(
                    method=request.method,
                    endpoint=request.path,
                    status_code=response.status_code
                ).inc()
                
                request_duration.labels(
                    method=request.method,
                    endpoint=request.path
                ).observe(duration)
                
                if request.content_length:
                    request_size.labels(
                        method=request.method,
                        endpoint=request.path
                    ).observe(request.content_length)
                
                if response.content_length:
                    response_size.labels(
                        method=request.method,
                        endpoint=request.path
                    ).observe(response.content_length)
        
        return response


def check_database_health() -> str:
    """Check database connectivity"""
    try:
        from models import get_db
        db = get_db()
        # Simple query to verify connection
        db.execute('SELECT 1')
        return 'ok'
    except Exception as e:
        return f'error: {str(e)}'


def check_redis_health() -> str:
    """Check Redis connectivity"""
    try:
        from redis_config import test_redis_connection
        if test_redis_connection():
            return 'ok'
        return 'error: connection failed'
    except Exception as e:
        return f'error: {str(e)}'


class MetricsContextManager:
    """Context manager for tracking metrics"""
    
    @staticmethod
    def track_db_query(operation: str, table: str, query_func):
        """Track database query with metrics"""
        start = time.time()
        try:
            result = query_func()
            duration = time.time() - start
            db_query_duration.labels(operation=operation, table=table).observe(duration)
            return result
        except Exception as e:
            duration = time.time() - start
            db_query_duration.labels(operation=operation, table=table).observe(duration)
            raise
    
    @staticmethod
    def track_cache_operation(cache_name: str, operation: str, func):
        """Track cache operation with metrics"""
        if operation == 'hit':
            cache_hits.labels(cache_name=cache_name).inc()
        elif operation == 'miss':
            cache_misses.labels(cache_name=cache_name).inc()
        
        return func()
    
    @staticmethod
    def record_auth_failure(reason: str):
        """Record authentication failure"""
        authentication_failures.labels(reason=reason).inc()
    
    @staticmethod
    def record_rate_limit(endpoint: str):
        """Record rate limit exceeded"""
        rate_limit_exceeded.labels(endpoint=endpoint).inc()


# Dashboard metrics for monitoring
def get_dashboard_metrics() -> dict:
    """Get metrics for dashboard display"""
    return {
        'requests_total': request_count,
        'avg_response_time': 'calculated from histogram',
        'cache_hit_rate': 'calculated from counters',
        'active_users': active_users._value.get(),
        'db_health': check_database_health(),
        'redis_health': check_redis_health(),
        'uptime': get_application_uptime()
    }


def get_application_uptime() -> str:
    """Get application uptime"""
    try:
        start_time = os.environ.get('APP_START_TIME')
        if start_time:
            elapsed = datetime.utcnow() - datetime.fromisoformat(start_time)
            return str(elapsed)
    except Exception:
        pass
    return 'unknown'
