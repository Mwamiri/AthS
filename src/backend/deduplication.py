"""
Request Deduplication Module
Prevent duplicate requests for idempotent operations
"""

import hashlib
from typing import Optional, Callable
from functools import wraps
from flask import request, jsonify, g
import redis
import json
from datetime import datetime, timedelta
import logging


class RequestDeduplicator:
    """Handle request deduplication"""
    
    def __init__(self, redis_client: redis.Redis, ttl_seconds: int = 300):
        """
        Initialize request deduplicator
        
        Args:
            redis_client: Redis client for storing request hashes
            ttl_seconds: Time to live for deduplication cache (default: 5 minutes)
        """
        self.redis = redis_client
        self.ttl = ttl_seconds
        self.logger = logging.getLogger('athsys.dedup')
    
    def _generate_request_hash(
        self,
        user_id: Optional[int],
        endpoint: str,
        method: str,
        body: Optional[dict] = None
    ) -> str:
        """Generate hash for request deduplication"""
        
        # Create string to hash
        hash_input = f"{user_id}:{endpoint}:{method}:{json.dumps(body, sort_keys=True)}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def is_duplicate(
        self,
        user_id: Optional[int],
        endpoint: str,
        method: str,
        body: Optional[dict] = None
    ) -> bool:
        """Check if request is duplicate"""
        
        request_hash = self._generate_request_hash(user_id, endpoint, method, body)
        
        # Check if hash exists in Redis
        exists = self.redis.exists(f"dedup:{request_hash}")
        
        return exists > 0
    
    def mark_request(
        self,
        user_id: Optional[int],
        endpoint: str,
        method: str,
        body: Optional[dict] = None
    ) -> str:
        """Mark request as processed"""
        
        request_hash = self._generate_request_hash(user_id, endpoint, method, body)
        
        # Store with TTL
        self.redis.setex(
            f"dedup:{request_hash}",
            self.ttl,
            str(datetime.utcnow())
        )
        
        return request_hash
    
    def clear_request(
        self,
        user_id: Optional[int],
        endpoint: str,
        method: str,
        body: Optional[dict] = None
    ):
        """Clear deduplication marker for request"""
        
        request_hash = self._generate_request_hash(user_id, endpoint, method, body)
        self.redis.delete(f"dedup:{request_hash}")


# Global deduplicator instance
_deduplicator = None


def get_deduplicator(redis_client: Optional[redis.Redis] = None) -> RequestDeduplicator:
    """Get or create deduplicator"""
    global _deduplicator
    
    if _deduplicator is None:
        import redis as redis_lib
        client = redis_client or redis_lib.from_url('redis://localhost:6379/0')
        _deduplicator = RequestDeduplicator(client)
    
    return _deduplicator


def deduplicate(
    methods: list = None,
    ttl_seconds: int = 300,
    on_duplicate: Optional[Callable] = None
):
    """
    Decorator for request deduplication
    
    Args:
        methods: HTTP methods to deduplicate (default: POST, PUT)
        ttl_seconds: Time to live for deduplication
        on_duplicate: Callback function when duplicate detected
    
    Example:
        @app.route('/api/data', methods=['POST'])
        @deduplicate(methods=['POST'])
        def create_data():
            return jsonify({'message': 'Created'})
    """
    
    if methods is None:
        methods = ['POST', 'PUT']
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Only deduplicate for specified methods
            if request.method not in methods:
                return func(*args, **kwargs)
            
            dedup = get_deduplicator()
            user_id = getattr(g, 'user_id', None)
            body = request.get_json() if request.is_json else None
            
            # Check if duplicate
            if dedup.is_duplicate(user_id, request.endpoint, request.method, body):
                # Log duplicate
                dedup.logger.warning(
                    f"Duplicate request detected: {request.endpoint} from user {user_id}"
                )
                
                # Call callback if provided
                if on_duplicate:
                    return on_duplicate()
                
                # Return 409 Conflict
                return jsonify({
                    'error': 'Duplicate request detected',
                    'message': 'This request was already processed. To retry, clear deduplication and try again.'
                }), 409
            
            try:
                # Mark request as processed
                dedup.mark_request(user_id, request.endpoint, request.method, body)
                
                # Execute function
                result = func(*args, **kwargs)
                
                return result
            except Exception as e:
                # Clear deduplication mark on error so retry will work
                dedup.clear_request(user_id, request.endpoint, request.method, body)
                raise
        
        return wrapper
    return decorator


# Example of custom duplicate handler
def handle_duplicate_payment():
    """Handler for duplicate payment requests"""
    return jsonify({
        'error': 'Duplicate payment detected',
        'message': 'This payment was already processed. Check your account for the charge.'
    }), 409
