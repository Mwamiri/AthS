"""
Enhanced Logging System with File Output and Analysis
Logs all system events, errors, API calls, and security events
"""

import os
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import traceback

# Create logs directory
LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
Path(LOGS_DIR).mkdir(parents=True, exist_ok=True)


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for easy parsing"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'process': record.process
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add custom fields
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'endpoint'):
            log_data['endpoint'] = record.endpoint
        if hasattr(record, 'method'):
            log_data['method'] = record.method
        if hasattr(record, 'status_code'):
            log_data['status_code'] = record.status_code
        
        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Format logs as readable text"""
    
    def format(self, record):
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] [{record.levelname}] {record.name}: {record.getMessage()}"
        
        if record.exc_info:
            log_msg += f"\n{traceback.format_exc()}"
        
        return log_msg


class LogManager:
    """Centralized log management"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.loggers: Dict[str, logging.Logger] = {}
        self.log_levels = {}
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Setup root logger with both file and console handlers"""
        root_logger = logging.getLogger('athsys')
        root_logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = TextFormatter()
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # Main log file (text format)
        main_log_file = os.path.join(LOGS_DIR, 'athsys.log')
        main_handler = RotatingFileHandler(main_log_file, maxBytes=10*1024*1024, backupCount=10)
        main_handler.setLevel(logging.DEBUG)
        main_handler.setFormatter(TextFormatter())
        root_logger.addHandler(main_handler)
        
        # JSON log file (structured format)
        json_log_file = os.path.join(LOGS_DIR, 'athsys.json')
        json_handler = RotatingFileHandler(json_log_file, maxBytes=10*1024*1024, backupCount=10)
        json_handler.setLevel(logging.DEBUG)
        json_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(json_handler)
        
        # Error log file
        error_log_file = os.path.join(LOGS_DIR, 'athsys-errors.log')
        error_handler = RotatingFileHandler(error_log_file, maxBytes=5*1024*1024, backupCount=5)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(TextFormatter())
        root_logger.addHandler(error_handler)
        
        # Security events log
        security_log_file = os.path.join(LOGS_DIR, 'athsys-security.log')
        security_handler = RotatingFileHandler(security_log_file, maxBytes=5*1024*1024, backupCount=5)
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(TextFormatter())
        root_logger.addHandler(security_handler)
        
        # API requests log
        api_log_file = os.path.join(LOGS_DIR, 'athsys-api.log')
        api_handler = RotatingFileHandler(api_log_file, maxBytes=10*1024*1024, backupCount=10)
        api_handler.setLevel(logging.DEBUG)
        api_handler.setFormatter(TextFormatter())
        root_logger.addHandler(api_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create logger"""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = logger
        return self.loggers[name]
    
    def log_api_request(self, method: str, endpoint: str, status_code: int, 
                       user_id: Optional[int] = None, duration_ms: float = 0):
        """Log API request"""
        logger = self.get_logger('athsys.api')
        logger.info(f"{method} {endpoint} -> {status_code} ({duration_ms:.2f}ms)", extra={
            'method': method,
            'endpoint': endpoint,
            'status_code': status_code,
            'user_id': user_id,
            'duration_ms': duration_ms
        })
    
    def log_security_event(self, event_type: str, severity: str, message: str, 
                          user_id: Optional[int] = None, details: Optional[Dict] = None):
        """Log security event"""
        logger = self.get_logger('athsys.security')
        level = getattr(logging, severity.upper(), logging.WARNING)
        logger.log(level, f"[{event_type}] {message}", extra={
            'user_id': user_id,
            'event_type': event_type,
            'details': details or {}
        })
    
    def log_database_event(self, operation: str, table: str, status: str, 
                          details: Optional[Dict] = None):
        """Log database event"""
        logger = self.get_logger('athsys.database')
        logger.info(f"{operation} on {table}: {status}", extra={
            'operation': operation,
            'table': table,
            'status': status,
            'details': details or {}
        })
    
    def log_error(self, exc: Exception, context: Optional[str] = None):
        """Log error with traceback"""
        logger = self.get_logger('athsys.errors')
        logger.error(f"Error: {context or 'Unknown context'}", exc_info=exc)
    
    def get_logs(self, log_type: str = 'all', limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Retrieve logs from file
        
        Args:
            log_type: 'all', 'errors', 'security', 'api', 'database'
            limit: Max number of lines to return
            offset: Skip first N lines
            
        Returns:
            List of log entries
        """
        logs_to_read = []
        
        if log_type == 'all':
            logs_to_read = ['athsys.log', 'athsys-errors.log', 'athsys-security.log']
        elif log_type == 'errors':
            logs_to_read = ['athsys-errors.log']
        elif log_type == 'security':
            logs_to_read = ['athsys-security.log']
        elif log_type == 'api':
            logs_to_read = ['athsys-api.log']
        
        all_lines = []
        for log_file in logs_to_read:
            log_path = os.path.join(LOGS_DIR, log_file)
            if os.path.exists(log_path):
                try:
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        all_lines.extend(lines)
                except Exception as e:
                    print(f"Error reading {log_file}: {e}")
        
        # Sort by timestamp (most recent first)
        all_lines.reverse()
        
        # Apply offset and limit
        selected_lines = all_lines[offset:offset + limit]
        
        # Parse log entries
        entries = []
        for line in selected_lines:
            line = line.strip()
            if not line:
                continue
            
            try:
                # Try to parse as JSON
                if line.startswith('{'):
                    entry = json.loads(line)
                else:
                    # Parse text format
                    entry = {'raw': line}
                entries.append(entry)
            except:
                entries.append({'raw': line})
        
        return entries
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get statistics about logs"""
        stats = {
            'total_logs': 0,
            'error_count': 0,
            'warning_count': 0,
            'security_events': 0,
            'log_files': {},
            'disk_usage_mb': 0
        }
        
        for file in os.listdir(LOGS_DIR):
            if file.startswith('athsys') and file.endswith('.log'):
                filepath = os.path.join(LOGS_DIR, file)
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                stats['log_files'][file] = f"{size_mb:.2f} MB"
                stats['disk_usage_mb'] += size_mb
                
                # Count entries
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                        stats['total_logs'] += lines
                        
                        if 'errors' in file:
                            stats['error_count'] += lines
                        if 'security' in file:
                            stats['security_events'] += lines
                except:
                    pass
        
        stats['disk_usage_mb'] = round(stats['disk_usage_mb'], 2)
        return stats
    
    def clear_old_logs(self, days: int = 30):
        """Clear logs older than N days"""
        import time
        cutoff_time = time.time() - (days * 86400)
        
        for file in os.listdir(LOGS_DIR):
            if file.startswith('athsys') and file.endswith('.log'):
                filepath = os.path.join(LOGS_DIR, file)
                if os.path.getmtime(filepath) < cutoff_time:
                    try:
                        os.remove(filepath)
                    except:
                        pass


# Singleton instance
log_manager = LogManager()


def get_log_manager() -> LogManager:
    """Get log manager instance"""
    return log_manager


def get_logger(name: str) -> logging.Logger:
    """Get named logger"""
    return log_manager.get_logger(name)
