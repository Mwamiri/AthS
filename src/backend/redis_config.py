"""
Redis Configuration for AthSys
Handles caching, session management, and real-time features
"""

import redis
import os
import json
import time
import fnmatch
from functools import wraps
from flask import request
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

# Redis connection with optimized timeouts to prevent startup blocking
def _build_redis_url():
    explicit_url = os.getenv('REDIS_URL')
    if explicit_url:
        return explicit_url

    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = os.getenv('REDIS_PORT', '6379')
    redis_db = os.getenv('REDIS_DB', '0')
    redis_password = os.getenv('REDIS_PASSWORD', '').strip()

    if redis_password:
        return f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"

    return f"redis://{redis_host}:{redis_port}/{redis_db}"


REDIS_URL = _build_redis_url()
redis_client = redis.from_url(
    REDIS_URL, 
    decode_responses=True,
    socket_connect_timeout=1,  # Reduced from default for faster startup
    socket_timeout=1,           # Reduced from default for faster startup
    retry_on_timeout=False      # Don't retry on timeout during init
)

_memory_cache_store = {}
_memory_rate_limit_store = {}
_memory_session_store = {}


def _set_memory(store, key, value, expiry):
    expires_at = time.time() + max(1, int(expiry or 1))
    store[key] = (value, expires_at)


def _get_memory(store, key):
    record = store.get(key)
    if not record:
        return None

    value, expires_at = record
    if expires_at <= time.time():
        store.pop(key, None)
        return None

    return value


def _delete_memory(store, key):
    return store.pop(key, None) is not None


def _clear_memory_pattern(store, pattern):
    keys = [k for k in list(store.keys()) if fnmatch.fnmatch(k, pattern)]
    for key in keys:
        store.pop(key, None)
    return bool(keys)


class RedisCache:
    """Redis caching utilities"""
    
    @staticmethod
    def get(key):
        """Get value from cache"""
        try:
            value = redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Redis GET error: {e}")
            return _get_memory(_memory_cache_store, key)
    
    @staticmethod
    def set(key, value, expiry=300):
        """Set value in cache with expiry (default 5 minutes)"""
        try:
            redis_client.setex(key, expiry, json.dumps(value))
            return True
        except Exception as e:
            print(f"Redis SET error: {e}")
            _set_memory(_memory_cache_store, key, value, expiry)
            return True
    
    @staticmethod
    def delete(key):
        """Delete key from cache"""
        try:
            redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Redis DELETE error: {e}")
            return _delete_memory(_memory_cache_store, key)
    
    @staticmethod
    def clear_pattern(pattern):
        """Clear all keys matching pattern"""
        try:
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"Redis CLEAR PATTERN error: {e}")
            return _clear_memory_pattern(_memory_cache_store, pattern)


def cache_result(key_prefix, expiry=300):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{request.path}:{request.query_string.decode()}"
            
            # Try to get from cache
            cached = RedisCache.get(cache_key)
            if cached is not None:
                return cached
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            RedisCache.set(cache_key, result, expiry)
            return result
        return wrapper
    return decorator


class RateLimiter:
    """Rate limiting using Redis"""
    
    @staticmethod
    def check_rate_limit(identifier, max_requests=100, window=3600):
        """
        Check if request is within rate limit
        identifier: IP address or user ID
        max_requests: maximum requests allowed
        window: time window in seconds (default 1 hour)
        """
        try:
            key = f"rate_limit:{identifier}"
            current = redis_client.get(key)
            
            if current is None:
                # First request, set counter
                redis_client.setex(key, window, 1)
                return True, max_requests - 1
            
            count = int(current)
            if count >= max_requests:
                return False, 0
            
            # Increment counter
            redis_client.incr(key)
            return True, max_requests - count - 1
        except Exception as e:
            print(f"Rate limiter error: {e}")
            key = f"rate_limit:{identifier}"
            now = time.time()
            record = _memory_rate_limit_store.get(key)

            if not record or record['expires_at'] <= now:
                _memory_rate_limit_store[key] = {
                    'count': 1,
                    'expires_at': now + window
                }
                return True, max_requests - 1

            if record['count'] >= max_requests:
                return False, 0

            record['count'] += 1
            return True, max_requests - record['count']


class SessionManager:
    """Session management using Redis"""
    
    @staticmethod
    def create_session(user_id, session_data, expiry=86400):
        """Create session (default 24 hours)"""
        try:
            session_key = f"session:{user_id}"
            redis_client.setex(session_key, expiry, json.dumps(session_data))
            return session_key
        except Exception as e:
            print(f"Session create error: {e}")
            session_key = f"session:{user_id}"
            _set_memory(_memory_session_store, session_key, session_data, expiry)
            return session_key
    
    @staticmethod
    def get_session(user_id):
        """Get session data"""
        try:
            session_data = redis_client.get(f"session:{user_id}")
            return json.loads(session_data) if session_data else None
        except Exception as e:
            print(f"Session get error: {e}")
            return _get_memory(_memory_session_store, f"session:{user_id}")
    
    @staticmethod
    def delete_session(user_id):
        """Delete session (logout)"""
        try:
            redis_client.delete(f"session:{user_id}")
            return True
        except Exception as e:
            print(f"Session delete error: {e}")
            return _delete_memory(_memory_session_store, f"session:{user_id}")
    
    @staticmethod
    def refresh_session(user_id, expiry=86400):
        """Extend session expiry"""
        try:
            key = f"session:{user_id}"
            redis_client.expire(key, expiry)
            return True
        except Exception as e:
            print(f"Session refresh error: {e}")
            session_data = _get_memory(_memory_session_store, f"session:{user_id}")
            if session_data is None:
                return False
            _set_memory(_memory_session_store, f"session:{user_id}", session_data, expiry)
            return True


class LeaderboardManager:
    """Real-time leaderboard management using Redis Sorted Sets"""
    
    @staticmethod
    def update_leaderboard(event_id, athlete_id, time_seconds):
        """Update leaderboard for an event"""
        try:
            key = f"leaderboard:event:{event_id}"
            # Store with score (time in seconds, lower is better)
            redis_client.zadd(key, {str(athlete_id): time_seconds})
            # Set expiry for 7 days
            redis_client.expire(key, 604800)
            return True
        except Exception as e:
            print(f"Leaderboard update error: {e}")
            return False
    
    @staticmethod
    def get_leaderboard(event_id, limit=10):
        """Get top performers for an event"""
        try:
            key = f"leaderboard:event:{event_id}"
            # Get top results (ascending order - lower time is better)
            results = redis_client.zrange(key, 0, limit - 1, withscores=True)
            return [{'athleteId': int(athlete_id), 'timeSeconds': score} 
                    for athlete_id, score in results]
        except Exception as e:
            print(f"Leaderboard get error: {e}")
            return []
    
    @staticmethod
    def get_athlete_rank(event_id, athlete_id):
        """Get athlete's rank in event"""
        try:
            key = f"leaderboard:event:{event_id}"
            rank = redis_client.zrank(key, str(athlete_id))
            return rank + 1 if rank is not None else None
        except Exception as e:
            print(f"Get rank error: {e}")
            return None


class PubSubManager:
    """Redis Pub/Sub for real-time updates"""
    
    @staticmethod
    def publish_event(channel, message):
        """Publish message to channel"""
        try:
            redis_client.publish(channel, json.dumps(message))
            return True
        except Exception as e:
            print(f"Publish error: {e}")
            return False
    
    @staticmethod
    def publish_race_update(race_id, update_type, data):
        """Publish race update"""
        channel = f"race:{race_id}"
        message = {
            'type': update_type,
            'data': data,
            'timestamp': str(redis_client.time()[0])
        }
        return PubSubManager.publish_event(channel, message)


# Test Redis connection
def test_redis_connection():
    """Test Redis connection"""
    try:
        redis_client.ping()
        print("✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False
