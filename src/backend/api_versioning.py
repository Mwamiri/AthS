"""
API Versioning Support
Handle multiple API versions (v1, v2, etc.) with deprecation warnings
"""

import logging
from typing import Optional, Callable, Dict, Any
from functools import wraps
from flask import request, jsonify, g
from datetime import datetime


class APIVersion:
    """API version definition"""
    
    def __init__(self, version: str, release_date: datetime, deprecated: bool = False, 
                 deprecation_date: Optional[datetime] = None, sunset_date: Optional[datetime] = None):
        self.version = version
        self.release_date = release_date
        self.deprecated = deprecated
        self.deprecation_date = deprecation_date
        self.sunset_date = sunset_date
    
    def to_dict(self) -> Dict:
        return {
            'version': self.version,
            'release_date': self.release_date.isoformat(),
            'deprecated': self.deprecated,
            'deprecation_date': self.deprecation_date.isoformat() if self.deprecation_date else None,
            'sunset_date': self.sunset_date.isoformat() if self.sunset_date else None
        }


class APIVersionManager:
    """Manage API versions"""
    
    def __init__(self):
        self.logger = logging.getLogger('athsys.versioning')
        self.versions: Dict[str, APIVersion] = {}
        self.default_version = 'v1'
        self._register_default_versions()
    
    def _register_default_versions(self):
        """Register default API versions"""
        self.register_version(
            'v1',
            release_date=datetime(2024, 1, 1),
            deprecated=False
        )
        self.register_version(
            'v2',
            release_date=datetime(2025, 2, 1),
            deprecated=False
        )
    
    def register_version(self, version: str, release_date: datetime, deprecated: bool = False,
                        deprecation_date: Optional[datetime] = None, 
                        sunset_date: Optional[datetime] = None):
        """Register API version"""
        api_version = APIVersion(version, release_date, deprecated, deprecation_date, sunset_date)
        self.versions[version] = api_version
        self.logger.info(f"Registered API version: {version}")
    
    def get_version(self, version: str) -> Optional[APIVersion]:
        """Get version info"""
        return self.versions.get(version)
    
    def is_supported(self, version: str) -> bool:
        """Check if version is supported (not sunset)"""
        api_version = self.get_version(version)
        if not api_version:
            return False
        
        if api_version.sunset_date and datetime.utcnow() > api_version.sunset_date:
            return False
        
        return True
    
    def is_deprecated(self, version: str) -> bool:
        """Check if version is deprecated"""
        api_version = self.get_version(version)
        return api_version.deprecated if api_version else False
    
    def get_all_versions(self) -> Dict[str, Dict]:
        """Get all versions info"""
        return {v: self.get_version(v).to_dict() for v in self.versions}
    
    def get_latest_version(self) -> str:
        """Get latest version"""
        sorted_versions = sorted(self.versions.values(), key=lambda v: v.release_date, reverse=True)
        return sorted_versions[0].version if sorted_versions else self.default_version


# Global version manager
_version_manager = None


def get_version_manager() -> APIVersionManager:
    """Get or create version manager"""
    global _version_manager
    
    if _version_manager is None:
        _version_manager = APIVersionManager()
    
    return _version_manager


def extract_api_version(request_obj) -> str:
    """
    Extract API version from request
    Priority: URL > Header > Default
    """
    # Check URL path (e.g., /api/v2/athletes)
    if request_obj.path.startswith('/api/'):
        parts = request_obj.path.split('/')[2:4]
        if parts and len(parts) > 0:
            version_part = parts[0]
            if version_part.startswith('v') and version_part[1:].isdigit():
                return version_part
    
    # Check X-API-Version header
    api_version = request_obj.headers.get('X-API-Version')
    if api_version:
        return api_version
    
    # Default to latest
    manager = get_version_manager()
    return manager.default_version


def api_version(version: str, deprecated: bool = False, 
               deprecation_date: Optional[datetime] = None):
    """
    Decorator to mark endpoint with API version
    
    Example:
        @app.route('/api/v1/athletes')
        @api_version('v1')
        def get_athletes_v1():
            return jsonify({'message': 'API v1'})
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            manager = get_version_manager()
            
            # Check if version is supported
            if not manager.is_supported(version):
                return jsonify({
                    'error': f'API version {version} is no longer supported',
                    'latest_version': manager.get_latest_version()
                }), 410  # Gone
            
            # Add deprecation warning if needed
            if deprecated or manager.is_deprecated(version):
                g.deprecation_warning = {
                    'message': f'API version {version} is deprecated',
                    'deprecation_date': deprecation_date.isoformat() if deprecation_date else None,
                    'upgrade_url': f'/api/{manager.get_latest_version()}{request.path.replace(f"/{version}", "")}'
                }
            
            # Store version in g for access in handler
            g.api_version = version
            
            return func(*args, **kwargs)
        
        wrapper._api_version = version
        wrapper._deprecated = deprecated
        return wrapper
    
    return decorator


def version_compatibility(from_version: str, to_version: str = None):
    """
    Decorator to specify version compatibility/migration
    
    Example:
        @version_compatibility('v1', 'v2')
        def migrate_athlete_response_v1_to_v2(data):
            # Migration logic
            return data
    """
    def decorator(func: Callable) -> Callable:
        func._from_version = from_version
        func._to_version = to_version or to_version
        return func
    
    return decorator


def add_version_headers(response, version: str = None):
    """Add versioning headers to response"""
    manager = get_version_manager()
    
    api_version = version or getattr(g, 'api_version', manager.default_version)
    response.headers['X-API-Version'] = api_version
    response.headers['X-API-Latest'] = manager.get_latest_version()
    
    # Add deprecation header if needed
    if hasattr(g, 'deprecation_warning'):
        warning = g.deprecation_warning
        response.headers['Deprecation'] = 'true'
        response.headers['Sunset'] = warning.get('deprecation_date', '')
        response.headers['Link'] = f"<{warning['upgrade_url']}>; rel=\"successor-version\""
    
    return response
