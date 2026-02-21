"""
Rate Limit Dashboard Backend
Expose rate limit info and analytics to frontend
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import redis
import json


class RateLimitDashboard:
    """Dashboard for rate limit analytics"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def get_user_usage(self, user_id: int, window_seconds: int = 3600) -> Dict[str, Any]:
        """Get rate limit usage for a user"""
        
        # Key format: ratelimit:userid:endpoint
        pattern = f"ratelimit:{user_id}:*"
        keys = self.redis.keys(pattern)
        
        usage_by_endpoint = {}
        total_requests = 0
        
        for key in keys:
            try:
                endpoint = key.decode().split(':')[2]
                count = self.redis.get(key)
                if count:
                    count = int(count)
                    usage_by_endpoint[endpoint] = count
                    total_requests += count
            except (IndexError, ValueError):
                pass
        
        return {
            'user_id': user_id,
            'total_requests': total_requests,
            'by_endpoint': usage_by_endpoint,
            'window_seconds': window_seconds,
            'checked_at': datetime.utcnow().isoformat()
        }
    
    def get_endpoint_usage(self, endpoint: str) -> Dict[str, Any]:
        """Get rate limit usage for an endpoint"""
        
        # Key format: ratelimit:*:endpoint
        pattern = f"ratelimit:*:{endpoint}"
        keys = self.redis.keys(pattern)
        
        usage_by_user = {}
        total_requests = 0
        
        for key in keys:
            try:
                user_id = int(key.decode().split(':')[1])
                count = self.redis.get(key)
                if count:
                    count = int(count)
                    usage_by_user[user_id] = count
                    total_requests += count
            except (IndexError, ValueError):
                pass
        
        # Find top users
        top_users = sorted(
            usage_by_user.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'endpoint': endpoint,
            'total_requests': total_requests,
            'unique_users': len(usage_by_user),
            'top_users': [
                {'user_id': uid, 'requests': count}
                for uid, count in top_users
            ],
            'checked_at': datetime.utcnow().isoformat()
        }
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global rate limit statistics"""
        
        # Get all rate limit keys
        keys = self.redis.keys("ratelimit:*:*")
        
        total_requests = 0
        unique_users = set()
        endpoints = {}
        
        for key in keys:
            try:
                parts = key.decode().split(':')
                user_id = int(parts[1])
                endpoint = parts[2]
                
                count = self.redis.get(key)
                if count:
                    count = int(count)
                    total_requests += count
                    unique_users.add(user_id)
                    endpoints[endpoint] = endpoints.get(endpoint, 0) + count
            except (IndexError, ValueError):
                pass
        
        # Top endpoints
        top_endpoints = sorted(
            endpoints.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'total_requests': total_requests,
            'unique_users': len(unique_users),
            'endpoints_tracked': len(endpoints),
            'top_endpoints': [
                {'endpoint': ep, 'requests': count}
                for ep, count in top_endpoints
            ],
            'checked_at': datetime.utcnow().isoformat()
        }
    
    def get_user_tier_limits(self, user_id: int) -> Dict[str, Any]:
        """Get user's rate limit tier and remaining quota"""
        
        # This would fetch from user profile/database
        # Example tier structure:
        tiers = {
            'free': {'requests_per_hour': 100, 'requests_per_day': 1000},
            'pro': {'requests_per_hour': 1000, 'requests_per_day': 50000},
            'enterprise': {'requests_per_hour': 10000, 'requests_per_day': 1000000},
        }
        
        # Placeholder: assume user is 'free' tier
        tier = 'free'
        limits = tiers[tier]
        
        # Calculate current usage
        usage = self.get_user_usage(user_id, window_seconds=3600)
        
        return {
            'user_id': user_id,
            'tier': tier,
            'limits': limits,
            'current_usage': usage['total_requests'],
            'remaining': limits['requests_per_hour'] - usage['total_requests'],
            'percentage_used': (usage['total_requests'] / limits['requests_per_hour']) * 100
        }


# Expose dashboard data as Flask blueprint
def create_rate_limit_dashboard_bp(redis_client: redis.Redis):
    """Create Flask blueprint for rate limit dashboard"""
    
    from flask import Blueprint, jsonify
    
    bp = Blueprint('ratelimit_dashboard', __name__, url_prefix='/api/dashboard/ratelimit')
    dashboard = RateLimitDashboard(redis_client)
    
    @bp.route('/user/<int:user_id>', methods=['GET'])
    def get_user_usage(user_id: int):
        """Get user's rate limit usage"""
        data = dashboard.get_user_usage(user_id)
        return jsonify(data)
    
    @bp.route('/endpoint/<endpoint>', methods=['GET'])
    def get_endpoint_stats(endpoint: str):
        """Get endpoint rate limit statistics"""
        data = dashboard.get_endpoint_usage(endpoint)
        return jsonify(data)
    
    @bp.route('/global', methods=['GET'])
    def get_global_stats():
        """Get global rate limit statistics"""
        data = dashboard.get_global_stats()
        return jsonify(data)
    
    @bp.route('/user/<int:user_id>/tier', methods=['GET'])
    def get_tier(user_id: int):
        """Get user's rate limit tier and quota"""
        data = dashboard.get_user_tier_limits(user_id)
        return jsonify(data)
    
    return bp
