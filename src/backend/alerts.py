"""
Enhanced Monitoring with Alerts
Slack/Email notifications for critical events
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import logging
import json
from prometheus_client import Counter, Gauge, Histogram


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Alert definition"""
    title: str
    message: str
    severity: AlertSeverity
    component: str  # "database", "redis", "api", "system"
    timestamp: datetime
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}


class AlertManager:
    """Manage system alerts and notifications"""
    
    # Metrics for tracking alerts
    alerts_total = Counter(
        'athsys_alerts_total',
        'Total alerts generated',
        ['severity', 'component']
    )
    
    critical_alerts_active = Gauge(
        'athsys_critical_alerts_active',
        'Active critical alerts'
    )
    
    def __init__(self):
        self.logger = logging.getLogger('athsys.alerts')
        self.alerts: List[Alert] = []
        self.webhooks: List[str] = []
    
    def add_webhook(self, webhook_url: str):
        """Add Slack/Discord webhook for alerts"""
        self.webhooks.append(webhook_url)
    
    def trigger_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity,
        component: str,
        tags: Optional[Dict[str, str]] = None
    ) -> Alert:
        """Trigger an alert"""
        
        alert = Alert(
            title=title,
            message=message,
            severity=severity,
            component=component,
            timestamp=datetime.utcnow(),
            tags=tags or {}
        )
        
        # Record metric
        self.alerts_total.labels(
            severity=severity.value,
            component=component
        ).inc()
        
        if severity == AlertSeverity.CRITICAL:
            self.critical_alerts_active.inc()
        
        # Store alert
        self.alerts.append(alert)
        
        # Log alert
        self.logger.warning(f"[{severity.value.upper()}] {component}: {title} - {message}")
        
        # Send notifications
        self._send_notifications(alert)
        
        return alert
    
    def _send_notifications(self, alert: Alert):
        """Send notifications to webhooks"""
        
        message = self._format_message(alert)
        
        for webhook_url in self.webhooks:
            self._send_webhook(webhook_url, message, alert.severity)
    
    def _format_message(self, alert: Alert) -> str:
        """Format alert message for slack"""
        
        colors = {
            AlertSeverity.INFO: "#4a90e2",      # Blue
            AlertSeverity.WARNING: "#f7931e",   # Orange
            AlertSeverity.ERROR: "#e63946",     # Red
            AlertSeverity.CRITICAL: "#d62828"   # Dark Red
        }
        
        return json.dumps({
            "attachments": [{
                "color": colors.get(alert.severity, "#999999"),
                "title": f"{alert.severity.value.upper()}: {alert.title}",
                "text": alert.message,
                "fields": [
                    {"title": "Component", "value": alert.component, "short": True},
                    {"title": "Time", "value": alert.timestamp.isoformat(), "short": True},
                ] + [
                    {"title": k, "value": v, "short": True}
                    for k, v in alert.tags.items()
                ]
            }]
        })
    
    def _send_webhook(self, webhook_url: str, message: str, severity: AlertSeverity):
        """Send message to webhook"""
        try:
            import requests
            requests.post(webhook_url, data=message, timeout=5)
        except Exception as e:
            self.logger.error(f"Failed to send alert to webhook: {e}")
    
    def resolve_alert(self, alert_id: int, resolved_by: str = "system"):
        """Mark alert as resolved"""
        if alert_id < len(self.alerts):
            alert = self.alerts[alert_id]
            if alert.severity == AlertSeverity.CRITICAL:
                self.critical_alerts_active.dec()
            
            self.logger.info(f"Alert resolved: {alert.title} (by {resolved_by})")


# Database health checks
class DatabaseHealthCheck:
    """Monitor database health"""
    
    db_connection_pool_usage = Gauge(
        'athsys_db_connection_pool_usage',
        'Database connection pool usage percentage'
    )
    
    db_query_duration = Histogram(
        'athsys_db_query_duration_seconds',
        'Database query duration'
    )
    
    def __init__(self, alert_manager: AlertManager):
        self.alert_manager = alert_manager
        self.logger = logging.getLogger('athsys.db_health')
    
    def check_connection_pool(self, used: int, total: int):
        """Check database connection pool health"""
        
        usage_percent = (used / total) * 100 if total > 0 else 0
        self.db_connection_pool_usage.set(usage_percent)
        
        if usage_percent > 90:
            self.alert_manager.trigger_alert(
                title="Database Connection Pool Critical",
                message=f"Connection pool at {usage_percent:.1f}% ({used}/{total})",
                severity=AlertSeverity.CRITICAL,
                component="database",
                tags={"usage": f"{usage_percent:.1f}%"}
            )
        elif usage_percent > 75:
            self.alert_manager.trigger_alert(
                title="Database Connection Pool Warning",
                message=f"Connection pool at {usage_percent:.1f}% ({used}/{total})",
                severity=AlertSeverity.WARNING,
                component="database",
                tags={"usage": f"{usage_percent:.1f}%"}
            )


# System health checks
class SystemHealthCheck:
    """Monitor system health"""
    
    cpu_usage = Gauge(
        'athsys_cpu_usage_percent',
        'CPU usage percentage'
    )
    
    memory_usage = Gauge(
        'athsys_memory_usage_percent',
        'Memory usage percentage'
    )
    
    def __init__(self, alert_manager: AlertManager):
        self.alert_manager = alert_manager
        self.logger = logging.getLogger('athsys.sys_health')
    
    def check_resources(self, cpu_percent: float, memory_percent: float):
        """Check system resource usage"""
        
        self.cpu_usage.set(cpu_percent)
        self.memory_usage.set(memory_percent)
        
        # CPU alerts
        if cpu_percent > 90:
            self.alert_manager.trigger_alert(
                title="High CPU Usage",
                message=f"CPU at {cpu_percent}%",
                severity=AlertSeverity.CRITICAL,
                component="system",
                tags={"cpu": f"{cpu_percent}%"}
            )
        
        # Memory alerts
        if memory_percent > 90:
            self.alert_manager.trigger_alert(
                title="High Memory Usage",
                message=f"Memory at {memory_percent}%",
                severity=AlertSeverity.CRITICAL,
                component="system",
                tags={"memory": f"{memory_percent}%"}
            )


# Global alert manager
_alert_manager = None


def get_alert_manager() -> AlertManager:
    """Get or create alert manager"""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager
