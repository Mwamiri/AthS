"""
Audit Logging System
Comprehensive tracking of user actions, data changes, and system events
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass, asdict
import json
import logging


class AuditAction(Enum):
    """Audit action types"""
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    VIEW = "VIEW"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"
    PERMISSION_CHANGE = "PERMISSION_CHANGE"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    TWOFA_ENABLE = "TWOFA_ENABLE"
    TWOFA_DISABLE = "TWOFA_DISABLE"
    LOGIN_FAILED = "LOGIN_FAILED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    API_ERROR = "API_ERROR"


class AuditSeverity(Enum):
    """Audit severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class AuditLog:
    """Audit log entry"""
    timestamp: datetime
    user_id: Optional[int]
    user_email: Optional[str]
    action: AuditAction
    resource_type: str
    resource_id: Optional[int]
    details: Dict[str, Any]
    severity: AuditSeverity
    ip_address: str
    user_agent: str
    status: str  # "SUCCESS" or "FAILURE"
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit log to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['action'] = self.action.value
        data['severity'] = self.severity.value
        return data
    
    def to_json(self) -> str:
        """Convert audit log to JSON"""
        return json.dumps(self.to_dict(), default=str)


class AuditLogger:
    """Main audit logging class"""
    
    def __init__(self, logger_name: str = "athsys.audit"):
        self.logger = logging.getLogger(logger_name)
        self.audit_logs = []
    
    def log(
        self,
        user_id: Optional[int],
        user_email: Optional[str],
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[int],
        details: Dict[str, Any],
        severity: AuditSeverity,
        ip_address: str,
        user_agent: str,
        status: str,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Log an audit event"""
        
        log_entry = AuditLog(
            timestamp=datetime.utcnow(),
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            severity=severity,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            error_message=error_message
        )
        
        # Log to file
        self.logger.info(log_entry.to_json())
        
        # Store in memory (for dashboard)
        self.audit_logs.append(log_entry)
        
        return log_entry
    
    def get_user_activity(self, user_id: int, limit: int = 50) -> list:
        """Get audit logs for a specific user"""
        return [
            log.to_dict() for log in self.audit_logs
            if log.user_id == user_id
        ][-limit:]
    
    def get_resource_history(self, resource_type: str, resource_id: int, limit: int = 50) -> list:
        """Get change history for a resource"""
        return [
            log.to_dict() for log in self.audit_logs
            if log.resource_type == resource_type and log.resource_id == resource_id
        ][-limit:]
    
    def get_recent_logs(self, limit: int = 100) -> list:
        """Get recent audit logs"""
        return [log.to_dict() for log in self.audit_logs[-limit:]]
    
    def get_failed_logins(self, limit: int = 50) -> list:
        """Get failed login attempts"""
        return [
            log.to_dict() for log in self.audit_logs
            if log.action == AuditAction.LOGIN_FAILED
        ][-limit:]
    
    def get_critical_events(self, hours: int = 24) -> list:
        """Get critical events from the last N hours"""
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            log.to_dict() for log in self.audit_logs
            if log.severity == AuditSeverity.CRITICAL and log.timestamp >= cutoff
        ]
    
    def export_logs(self, format: str = "json") -> str:
        """Export audit logs in specified format"""
        if format == "json":
            return json.dumps(
                [log.to_dict() for log in self.audit_logs],
                default=str,
                indent=2
            )
        elif format == "csv":
            import csv
            import io
            output = io.StringIO()
            logs = [log.to_dict() for log in self.audit_logs]
            
            if not logs:
                return ""
            
            writer = csv.DictWriter(output, fieldnames=logs[0].keys())
            writer.writeheader()
            writer.writerows(logs)
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")


# Global audit logger instance
audit_logger = AuditLogger()


# Helper decorators for automatic audit logging
def audit_action(
    action: AuditAction,
    resource_type: str,
    severity: AuditSeverity = AuditSeverity.INFO
):
    """Decorator for automatic audit logging"""
    from functools import wraps
    from flask import request, g
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                
                # Log success
                audit_logger.log(
                    user_id=getattr(g, 'user_id', None),
                    user_email=getattr(g, 'user_email', None),
                    action=action,
                    resource_type=resource_type,
                    resource_id=kwargs.get('resource_id') or kwargs.get('id'),
                    details={'args': str(args), 'kwargs': str(kwargs)},
                    severity=severity,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', ''),
                    status="SUCCESS"
                )
                
                return result
            except Exception as e:
                # Log error
                audit_logger.log(
                    user_id=getattr(g, 'user_id', None),
                    user_email=getattr(g, 'user_email', None),
                    action=action,
                    resource_type=resource_type,
                    resource_id=kwargs.get('resource_id') or kwargs.get('id'),
                    details={'args': str(args), 'kwargs': str(kwargs)},
                    severity=AuditSeverity.ERROR,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', ''),
                    status="FAILURE",
                    error_message=str(e)
                )
                raise
        
        return wrapper
    return decorator
