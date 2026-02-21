"""
Feature Flags System
Toggle features on/off without redeployment
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime
import logging


class FeatureStatus(Enum):
    """Feature status"""
    DISABLED = "disabled"
    ENABLED = "enabled"
    BETA = "beta"  # Enabled for beta testing users
    ROLLOUT = "rollout"  # Gradual rollout based on percentage


@dataclass
class Feature:
    """Feature flag definition"""
    name: str
    status: FeatureStatus
    description: str
    created_at: datetime
    rollout_percentage: int = 100  # For ROLLOUT status
    beta_user_ids: List[int] = None
    
    def __post_init__(self):
        if self.beta_user_ids is None:
            self.beta_user_ids = []


class FeatureFlagManager:
    """Manage feature flags"""
    
    def __init__(self):
        self.features: Dict[str, Feature] = {}
        self.logger = logging.getLogger('athsys.features')
        self._register_default_features()
    
    def _register_default_features(self):
        """Register default features"""
        features = [
            Feature(
                name='advanced_search',
                status=FeatureStatus.BETA,
                description='Full-text search and advanced filters',
                created_at=datetime.utcnow(),
                beta_user_ids=[1, 2, 3]  # Beta with selected users
            ),
            Feature(
                name='data_export',
                status=FeatureStatus.ENABLED,
                description='Export data to CSV/Excel',
                created_at=datetime.utcnow()
            ),
            Feature(
                name='admin_dashboard',
                status=FeatureStatus.ROLLOUT,
                description='Advanced admin dashboard',
                created_at=datetime.utcnow(),
                rollout_percentage=50  # Rollout to 50% of users
            ),
            Feature(
                name='webhooks',
                status=FeatureStatus.DISABLED,
                description='Webhook notifications',
                created_at=datetime.utcnow()
            ),
            Feature(
                name='real_time_updates',
                status=FeatureStatus.BETA,
                description='WebSocket real-time updates',
                created_at=datetime.utcnow()
            ),
            Feature(
                name='oauth_login',
                status=FeatureStatus.DISABLED,
                description='OAuth2 social login',
                created_at=datetime.utcnow()
            ),
            Feature(
                name='billing_system',
                status=FeatureStatus.DISABLED,
                description='Billing and payment processing',
                created_at=datetime.utcnow()
            ),
        ]
        
        for feature in features:
            self.features[feature.name] = feature
    
    def is_enabled(
        self,
        feature_name: str,
        user_id: Optional[int] = None
    ) -> bool:
        """Check if feature is enabled for user"""
        
        if feature_name not in self.features:
            self.logger.warning(f"Unknown feature: {feature_name}")
            return False
        
        feature = self.features[feature_name]
        
        if feature.status == FeatureStatus.DISABLED:
            return False
        
        if feature.status == FeatureStatus.ENABLED:
            return True
        
        if feature.status == FeatureStatus.BETA:
            # Check if user is beta tester
            return user_id in feature.beta_user_ids if user_id else False
        
        if feature.status == FeatureStatus.ROLLOUT:
            # Check if user is in rollout percentage
            if user_id is None:
                return False
            # Simple hash-based rollout
            return (user_id % 100) < feature.rollout_percentage
        
        return False
    
    def enable_feature(self, feature_name: str):
        """Enable feature globally"""
        if feature_name in self.features:
            self.features[feature_name].status = FeatureStatus.ENABLED
            self.logger.info(f"Feature enabled: {feature_name}")
    
    def disable_feature(self, feature_name: str):
        """Disable feature globally"""
        if feature_name in self.features:
            self.features[feature_name].status = FeatureStatus.DISABLED
            self.logger.info(f"Feature disabled: {feature_name}")
    
    def set_rollout(self, feature_name: str, percentage: int):
        """Set rollout percentage (0-100)"""
        if feature_name in self.features:
            if not 0 <= percentage <= 100:
                raise ValueError(f"Percentage must be 0-100, got {percentage}")
            self.features[feature_name].status = FeatureStatus.ROLLOUT
            self.features[feature_name].rollout_percentage = percentage
            self.logger.info(f"Feature {feature_name} set to {percentage}% rollout")
    
    def add_beta_user(self, feature_name: str, user_id: int):
        """Add user to beta test"""
        if feature_name in self.features:
            if user_id not in self.features[feature_name].beta_user_ids:
                self.features[feature_name].beta_user_ids.append(user_id)
                self.logger.info(f"User {user_id} added to beta: {feature_name}")
    
    def remove_beta_user(self, feature_name: str, user_id: int):
        """Remove user from beta test"""
        if feature_name in self.features:
            if user_id in self.features[feature_name].beta_user_ids:
                self.features[feature_name].beta_user_ids.remove(user_id)
                self.logger.info(f"User {user_id} removed from beta: {feature_name}")
    
    def get_all_features(self) -> Dict[str, Dict]:
        """Get all feature flags and status"""
        return {
            name: {
                'status': feature.status.value,
                'description': feature.description,
                'rollout_percentage': feature.rollout_percentage,
                'beta_user_ids': feature.beta_user_ids
            }
            for name, feature in self.features.items()
        }
    
    def export_flags(self) -> str:
        """Export flags as JSON"""
        return json.dumps(
            {
                name: {
                    'status': feature.status.value,
                    'rollout_percentage': feature.rollout_percentage,
                    'beta_user_ids': feature.beta_user_ids
                }
                for name, feature in self.features.items()
            },
            indent=2
        )


# Global feature flag manager
_feature_manager = None


def get_feature_manager() -> FeatureFlagManager:
    """Get or create feature manager"""
    global _feature_manager
    if _feature_manager is None:
        _feature_manager = FeatureFlagManager()
    return _feature_manager


# Decorator for feature-gated functions
def feature_gate(feature_name: str, fallback: Callable = None):
    """Decorator to gate functions behind feature flags"""
    from functools import wraps
    from flask import g, jsonify
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            manager = get_feature_manager()
            user_id = getattr(g, 'user_id', None)
            
            if not manager.is_enabled(feature_name, user_id):
                if fallback:
                    return fallback(*args, **kwargs)
                return jsonify({'error': f'Feature {feature_name} is currently disabled'}), 503
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
